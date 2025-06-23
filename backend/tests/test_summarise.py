#!/usr/bin/env python3
"""
Test suite for AI summarization functionality
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models import Base, Paper
from app.summarise import (
    generate_summary_with_gemini,
    generate_summary_with_openai,
    generate_summary,
    process_unsummarized_papers
)


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_summarise.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_database):
    """Create a database session for testing"""
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_abstract():
    """Sample academic abstract for testing"""
    return """
    Large language models (LLMs) have demonstrated remarkable capabilities in natural language 
    processing tasks. However, their performance often depends on the quality and relevance of 
    the prompts provided to them. In this paper, we introduce a novel approach to prompt 
    engineering that leverages the model's own outputs to iteratively refine prompts. Our method, 
    which we call Self-Refining Prompt Engineering (SRPE), uses an LLM to generate candidate 
    prompts, evaluate them, and select the most effective ones in a recursive manner. 
    Experimental results across multiple tasks and models show that SRPE consistently outperforms 
    traditional prompt engineering techniques, improving performance by an average of 15% on 
    benchmark datasets while reducing the need for human intervention in the prompt design process.
    """


class TestGeminiSummarization:
    """Test Gemini AI summarization"""
    
    @pytest.mark.asyncio
    async def test_generate_summary_with_gemini_success(self, sample_abstract):
        """Test successful Gemini summary generation"""
        # Mock the Gemini API
        mock_response = Mock()
        mock_response.text = "SRPE improves prompt engineering by using LLMs to iteratively refine prompts, achieving 15% better performance on benchmarks while reducing human intervention."
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        
        with patch('app.summarise.genai.GenerativeModel', return_value=mock_model):
            summary, embedding = await generate_summary_with_gemini(sample_abstract)
            
            assert len(summary) > 0
            assert len(summary.split()) <= 60  # Should be ≤ 60 words
            assert isinstance(embedding, list)
            assert len(embedding) > 0
    
    @pytest.mark.asyncio
    async def test_generate_summary_with_gemini_error(self, sample_abstract):
        """Test Gemini error handling"""
        with patch('app.summarise.genai.GenerativeModel', side_effect=Exception("API Error")):
            summary, embedding = await generate_summary_with_gemini(sample_abstract)
            
            assert summary == ""
            assert embedding == []
    
    @pytest.mark.asyncio
    async def test_gemini_prompt_format(self, sample_abstract):
        """Test that Gemini receives properly formatted prompt"""
        mock_response = Mock()
        mock_response.text = "Test summary"
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        
        with patch('app.summarise.genai.GenerativeModel', return_value=mock_model):
            await generate_summary_with_gemini(sample_abstract)
            
            # Verify the model was called with a prompt containing our requirements
            call_args = mock_model.generate_content.call_args[0][0]
            assert "≤ 60 words" in call_args
            assert "graduate‑level reader" in call_args
            assert "main contribution" in call_args
            assert sample_abstract.strip() in call_args


class TestOpenAISummarization:
    """Test OpenAI summarization"""
    
    @pytest.mark.asyncio
    async def test_generate_summary_with_openai_success(self, sample_abstract):
        """Test successful OpenAI summary generation"""
        # Mock OpenAI client and responses
        mock_completion_response = Mock()
        mock_completion_response.choices = [Mock()]
        mock_completion_response.choices[0].message.content = "SRPE uses LLMs to iteratively improve prompts, achieving 15% better performance while reducing human effort."
        
        mock_embedding_response = Mock()
        mock_embedding_response.data = [Mock()]
        mock_embedding_response.data[0].embedding = [0.1] * 768
        
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_completion_response
        mock_client.embeddings.create.return_value = mock_embedding_response
        
        with patch('app.summarise.openai_client', mock_client):
            summary, embedding = await generate_summary_with_openai(sample_abstract)
            
            assert len(summary) > 0
            assert len(summary.split()) <= 60
            assert isinstance(embedding, list)
            assert len(embedding) == 768
    
    @pytest.mark.asyncio
    async def test_generate_summary_with_openai_error(self, sample_abstract):
        """Test OpenAI error handling"""
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        with patch('app.summarise.openai_client', mock_client):
            summary, embedding = await generate_summary_with_openai(sample_abstract)
            
            assert summary == ""
            assert embedding == []
    
    @pytest.mark.asyncio
    async def test_openai_prompt_format(self, sample_abstract):
        """Test OpenAI prompt formatting"""
        mock_completion_response = Mock()
        mock_completion_response.choices = [Mock()]
        mock_completion_response.choices[0].message.content = "Test summary"
        
        mock_embedding_response = Mock()
        mock_embedding_response.data = [Mock()]
        mock_embedding_response.data[0].embedding = [0.1] * 768
        
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_completion_response
        mock_client.embeddings.create.return_value = mock_embedding_response
        
        with patch('app.summarise.openai_client', mock_client):
            await generate_summary_with_openai(sample_abstract)
            
            # Verify the completion call
            call_kwargs = mock_client.chat.completions.create.call_args.kwargs
            messages = call_kwargs['messages']
            user_message = messages[1]['content']
            
            assert "≤ 60 words" in user_message
            assert "graduate‑level reader" in user_message
            assert sample_abstract.strip() in user_message


class TestGenerateSummary:
    """Test the main generate_summary function"""
    
    @pytest.mark.asyncio
    async def test_generate_summary_gemini_provider(self, sample_abstract):
        """Test generate_summary with Gemini provider"""
        with patch('app.summarise.settings') as mock_settings:
            mock_settings.LLM_PROVIDER = "gemini"
            
            with patch('app.summarise.generate_summary_with_gemini', return_value=("Test summary", [0.1] * 768)) as mock_gemini:
                summary, embedding = await generate_summary(sample_abstract)
                
                mock_gemini.assert_called_once_with(sample_abstract)
                assert summary == "Test summary"
                assert len(embedding) == 768
    
    @pytest.mark.asyncio
    async def test_generate_summary_openai_provider(self, sample_abstract):
        """Test generate_summary with OpenAI provider"""
        with patch('app.summarise.settings') as mock_settings:
            mock_settings.LLM_PROVIDER = "openai"
            
            with patch('app.summarise.generate_summary_with_openai', return_value=("OpenAI summary", [0.2] * 768)) as mock_openai:
                summary, embedding = await generate_summary(sample_abstract)
                
                mock_openai.assert_called_once_with(sample_abstract)
                assert summary == "OpenAI summary"
                assert len(embedding) == 768
    
    @pytest.mark.asyncio
    async def test_generate_summary_unknown_provider(self, sample_abstract):
        """Test generate_summary with unknown provider"""
        with patch('app.summarise.settings') as mock_settings:
            mock_settings.LLM_PROVIDER = "unknown"
            
            summary, embedding = await generate_summary(sample_abstract)
            
            assert summary == ""
            assert embedding == []


class TestProcessUnsummarizedPapers:
    """Test processing unsummarized papers"""
    
    @pytest.mark.asyncio
    async def test_process_unsummarized_papers(self, db_session):
        """Test processing papers without summaries"""
        # Create test papers without summaries
        papers = [
            Paper(
                arxiv_id="2024.0001v1",
                title="Paper 1",
                authors="Author 1",
                abstract="Abstract 1 with enough content for summarization testing.",
                category="cs.AI"
            ),
            Paper(
                arxiv_id="2024.0002v1",
                title="Paper 2",
                authors="Author 2",
                abstract="Abstract 2 with different content for testing purposes.",
                category="cs.LG"
            )
        ]
        
        for paper in papers:
            db_session.add(paper)
        db_session.commit()
        
        # Mock the database session
        with patch('app.summarise.SessionLocal', return_value=db_session):
            with patch('app.summarise.generate_summary', return_value=("Generated summary", [0.1] * 768)) as mock_generate:
                await process_unsummarized_papers(limit=2)
                
                # Verify generate_summary was called for each paper
                assert mock_generate.call_count == 2
                
                # Verify papers now have summaries
                updated_papers = db_session.query(Paper).filter(Paper.summary.isnot(None)).all()
                assert len(updated_papers) == 2
                for paper in updated_papers:
                    assert paper.summary == "Generated summary"
    
    @pytest.mark.asyncio
    async def test_process_unsummarized_papers_limit(self, db_session):
        """Test processing with limit"""
        # Create 5 papers, but only process 3
        papers = []
        for i in range(5):
            paper = Paper(
                arxiv_id=f"2024.000{i+1}v1",
                title=f"Paper {i+1}",
                authors=f"Author {i+1}",
                abstract=f"Abstract {i+1} content.",
                category="cs.AI"
            )
            papers.append(paper)
            db_session.add(paper)
        db_session.commit()
        
        with patch('app.summarise.SessionLocal', return_value=db_session):
            with patch('app.summarise.generate_summary', return_value=("Summary", [0.1] * 768)) as mock_generate:
                await process_unsummarized_papers(limit=3)
                
                # Should only process 3 papers
                assert mock_generate.call_count == 3
                
                # Verify only 3 papers have summaries
                updated_papers = db_session.query(Paper).filter(Paper.summary.isnot(None)).all()
                assert len(updated_papers) == 3
    
    @pytest.mark.asyncio
    async def test_process_unsummarized_papers_error_handling(self, db_session):
        """Test error handling in processing"""
        paper = Paper(
            arxiv_id="2024.error.v1",
            title="Error Paper",
            authors="Error Author",
            abstract="This will cause an error.",
            category="cs.AI"
        )
        db_session.add(paper)
        db_session.commit()
        
        with patch('app.summarise.SessionLocal', return_value=db_session):
            with patch('app.summarise.generate_summary', side_effect=Exception("Processing error")):
                # Should not raise exception, should handle gracefully
                await process_unsummarized_papers(limit=1)
                
                # Paper should not have a summary due to error
                updated_paper = db_session.query(Paper).filter_by(arxiv_id="2024.error.v1").first()
                assert updated_paper.summary is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])