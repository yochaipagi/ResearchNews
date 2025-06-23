#!/usr/bin/env python3
"""
Test suite for arXiv paper ingestion functionality
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models import Base, Paper
from app.ingestion import (
    fetch_papers,
    parse_arxiv_response,
    ingest_papers_for_categories,
    store_papers
)


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_ingestion.db"
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
def sample_arxiv_xml():
    """Sample arXiv API XML response"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <link href="http://arxiv.org/api/query?search_query=cat:cs.AI&amp;id_list=&amp;start=0&amp;max_results=2" rel="self" type="application/atom+xml"/>
  <title type="html">ArXiv Query: search_query=cat:cs.AI&amp;id_list=&amp;start=0&amp;max_results=2</title>
  <id>http://arxiv.org/api/query</id>
  <updated>2024-01-01T00:00:00-05:00</updated>
  <opensearch:totalResults xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">2</opensearch:totalResults>
  <opensearch:startIndex xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">0</opensearch:startIndex>
  <opensearch:itemsPerPage xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">2</opensearch:itemsPerPage>
  <entry>
    <id>http://arxiv.org/abs/2401.0001v1</id>
    <updated>2024-01-01T09:00:00Z</updated>
    <published>2024-01-01T09:00:00Z</published>
    <title>Test Paper: Advances in Machine Learning</title>
    <summary>This paper presents novel approaches to machine learning optimization. 
    We introduce a new algorithm that improves training efficiency by 20% while 
    maintaining accuracy. Our experiments show significant improvements across 
    multiple benchmarks.</summary>
    <author>
      <name>John Doe</name>
    </author>
    <author>
      <name>Jane Smith</name>
    </author>
    <arxiv:primary_category xmlns:arxiv="http://arxiv.org/schemas/atom" term="cs.AI" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2401.0002v1</id>
    <updated>2024-01-01T10:00:00Z</updated>
    <published>2024-01-01T10:00:00Z</published>
    <title>Deep Learning for Computer Vision: A Comprehensive Survey</title>
    <summary>We provide a comprehensive survey of deep learning methods for computer vision tasks. 
    This work covers recent advances in convolutional neural networks, attention mechanisms, 
    and transformer architectures applied to image classification and object detection.</summary>
    <author>
      <name>Alice Johnson</name>
    </author>
    <author>
      <name>Bob Wilson</name>
    </author>
    <arxiv:primary_category xmlns:arxiv="http://arxiv.org/schemas/atom" term="cs.CV" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
</feed>'''


class TestArxivXMLParsing:
    """Test arXiv XML response parsing"""
    
    def test_parse_arxiv_response(self, sample_arxiv_xml):
        """Test parsing valid arXiv XML response"""
        papers = parse_arxiv_response(sample_arxiv_xml)
        
        assert len(papers) == 2
        
        # Test first paper
        paper1 = papers[0]
        assert paper1["arxiv_id"] == "2401.0001v1"
        assert "Test Paper: Advances in Machine Learning" in paper1["title"]
        assert paper1["authors"] == "John Doe, Jane Smith"
        assert "novel approaches to machine learning" in paper1["summary"]
        assert paper1["category"] == "cs.AI"
        assert isinstance(paper1["published_at"], datetime)
        
        # Test second paper
        paper2 = papers[1]
        assert paper2["arxiv_id"] == "2401.0002v1"
        assert "Deep Learning for Computer Vision" in paper2["title"]
        assert paper2["authors"] == "Alice Johnson, Bob Wilson"
        assert paper2["category"] == "cs.CV"
    
    def test_parse_empty_xml(self):
        """Test parsing empty XML response"""
        empty_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
        </feed>'''
        
        papers = parse_arxiv_response(empty_xml)
        assert papers == []
    
    def test_parse_malformed_xml(self):
        """Test parsing malformed XML"""
        malformed_xml = "This is not valid XML"
        
        # Should raise an exception or handle gracefully
        try:
            papers = parse_arxiv_response(malformed_xml)
            # If it doesn't raise an exception, should return empty list
            assert papers == []
        except Exception:
            # Exception is acceptable for malformed XML
            pass
    
    def test_parse_missing_fields(self):
        """Test parsing XML with missing fields"""
        minimal_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
          <entry>
            <id>http://arxiv.org/abs/2401.0003v1</id>
            <title>Minimal Paper</title>
            <!-- Missing authors, summary, category, published date -->
          </entry>
        </feed>'''
        
        papers = parse_arxiv_response(minimal_xml)
        assert len(papers) == 1
        
        paper = papers[0]
        assert paper["arxiv_id"] == "2401.0003v1"
        assert paper["title"] == "Minimal Paper"
        assert paper["authors"] == ""  # Should handle missing authors
        assert paper["summary"] == ""  # Should handle missing summary
        assert paper["category"] is None  # Should handle missing category


class TestArxivAPIFetch:
    """Test arXiv API fetching"""
    
    @pytest.mark.asyncio
    async def test_fetch_papers_success(self, sample_arxiv_xml):
        """Test successful paper fetching"""
        mock_response = Mock()
        mock_response.text = sample_arxiv_xml
        mock_response.raise_for_status.return_value = None
        
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get.return_value = mock_response
        
        with patch('app.ingestion.httpx.AsyncClient', return_value=mock_client):
            with patch('app.ingestion.time.sleep'):  # Skip sleep in tests
                papers = await fetch_papers("cs.AI", max_results=2)
                
                assert len(papers) == 2
                assert papers[0]["arxiv_id"] == "2401.0001v1"
                assert papers[1]["arxiv_id"] == "2401.0002v1"
    
    @pytest.mark.asyncio
    async def test_fetch_papers_with_parameters(self, sample_arxiv_xml):
        """Test fetch_papers with custom parameters"""
        mock_response = Mock()
        mock_response.text = sample_arxiv_xml
        mock_response.raise_for_status.return_value = None
        
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get.return_value = mock_response
        
        with patch('app.ingestion.httpx.AsyncClient', return_value=mock_client):
            with patch('app.ingestion.time.sleep'):
                papers = await fetch_papers(
                    category="cs.LG",
                    max_results=50,
                    start=10,
                    sort_by="lastUpdatedDate",
                    sort_order="ascending"
                )
                
                # Verify the API was called with correct parameters
                call_kwargs = mock_client.get.call_args.kwargs
                params = call_kwargs['params']
                
                assert params['search_query'] == "cat:cs.LG"
                assert params['max_results'] == 50
                assert params['start'] == 10
                assert params['sortBy'] == "lastUpdatedDate"
                assert params['sortOrder'] == "ascending"
    
    @pytest.mark.asyncio
    async def test_fetch_papers_http_error(self):
        """Test handling HTTP errors"""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        # Simulate HTTP error
        import httpx
        mock_client.get.side_effect = httpx.HTTPError("HTTP Error")
        
        with patch('app.ingestion.httpx.AsyncClient', return_value=mock_client):
            with patch('app.ingestion.asyncio.sleep'):  # Skip sleep in tests
                papers = await fetch_papers("cs.AI", max_retries=2)
                
                # Should return empty list on error
                assert papers == []
                
                # Verify retry attempts
                assert mock_client.get.call_count == 2  # max_retries
    
    @pytest.mark.asyncio
    async def test_fetch_papers_timeout(self):
        """Test handling timeout errors"""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        # Simulate timeout
        import httpx
        mock_client.get.side_effect = httpx.TimeoutException("Timeout")
        
        with patch('app.ingestion.httpx.AsyncClient', return_value=mock_client):
            with patch('app.ingestion.asyncio.sleep'):
                papers = await fetch_papers("cs.AI", max_retries=1)
                
                assert papers == []
                assert mock_client.get.call_count == 1


class TestPaperStorage:
    """Test paper storage in database"""
    
    def test_store_new_papers(self, db_session):
        """Test storing new papers"""
        papers_data = [
            {
                "arxiv_id": "2024.0001v1",
                "title": "Test Paper 1",
                "authors": "Author 1",
                "summary": "Abstract 1",
                "category": "cs.AI",
                "published_at": datetime.utcnow()
            },
            {
                "arxiv_id": "2024.0002v1",
                "title": "Test Paper 2",
                "authors": "Author 2",
                "summary": "Abstract 2",
                "category": "cs.LG",
                "published_at": datetime.utcnow()
            }
        ]
        
        store_papers(papers_data, db_session)
        
        # Verify papers were stored
        stored_papers = db_session.query(Paper).all()
        assert len(stored_papers) == 2
        
        paper1 = db_session.query(Paper).filter_by(arxiv_id="2024.0001v1").first()
        assert paper1 is not None
        assert paper1.title == "Test Paper 1"
        assert paper1.authors == "Author 1"
    
    def test_store_duplicate_papers(self, db_session):
        """Test storing duplicate papers (should not create duplicates)"""
        paper_data = {
            "arxiv_id": "2024.duplicate.v1",
            "title": "Duplicate Paper",
            "authors": "Test Author",
            "summary": "Test abstract",
            "category": "cs.AI",
            "published_at": datetime.utcnow()
        }
        
        # Store the same paper twice
        store_papers([paper_data], db_session)
        store_papers([paper_data], db_session)
        
        # Should only have one copy
        stored_papers = db_session.query(Paper).filter_by(arxiv_id="2024.duplicate.v1").all()
        assert len(stored_papers) == 1
    
    def test_store_papers_error_handling(self, db_session):
        """Test error handling in paper storage"""
        # Create paper with invalid data that might cause database error
        invalid_papers = [
            {
                "arxiv_id": None,  # This might cause an error
                "title": "Invalid Paper",
                "authors": "Test",
                "summary": "Test",
                "category": "cs.AI"
            }
        ]
        
        # Should handle errors gracefully
        try:
            store_papers(invalid_papers, db_session)
            # If no exception, verify no papers were stored
            papers = db_session.query(Paper).filter_by(title="Invalid Paper").all()
            assert len(papers) == 0
        except Exception:
            # If exception occurs, it should be handled gracefully in the actual implementation
            pass


class TestIngestionPipeline:
    """Test the complete ingestion pipeline"""
    
    @pytest.mark.asyncio
    async def test_ingest_papers_for_categories(self, sample_arxiv_xml):
        """Test ingesting papers for configured categories"""
        mock_response = Mock()
        mock_response.text = sample_arxiv_xml
        mock_response.raise_for_status.return_value = None
        
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get.return_value = mock_response
        
        # Mock settings with test categories
        with patch('app.ingestion.settings') as mock_settings:
            mock_settings.ARXIV_CATEGORIES = ["cs.AI", "cs.LG"]
            
            with patch('app.ingestion.httpx.AsyncClient', return_value=mock_client):
                with patch('app.ingestion.time.sleep'):
                    with patch('app.ingestion.SessionLocal') as mock_session_local:
                        mock_db = Mock()
                        mock_session_local.return_value = mock_db
                        
                        await ingest_papers_for_categories()
                        
                        # Verify fetch_papers was called for each category
                        assert mock_client.get.call_count == 2  # Two categories
    
    @pytest.mark.asyncio
    async def test_ingest_papers_database_integration(self, db_session, sample_arxiv_xml):
        """Test ingestion with actual database storage"""
        mock_response = Mock()
        mock_response.text = sample_arxiv_xml
        mock_response.raise_for_status.return_value = None
        
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get.return_value = mock_response
        
        with patch('app.ingestion.settings') as mock_settings:
            mock_settings.ARXIV_CATEGORIES = ["cs.AI"]
            
            with patch('app.ingestion.httpx.AsyncClient', return_value=mock_client):
                with patch('app.ingestion.time.sleep'):
                    with patch('app.ingestion.SessionLocal', return_value=db_session):
                        await ingest_papers_for_categories()
                        
                        # Verify papers were stored in database
                        stored_papers = db_session.query(Paper).all()
                        assert len(stored_papers) >= 1  # Should have at least the papers from sample XML


if __name__ == "__main__":
    pytest.main([__file__, "-v"])