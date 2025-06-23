import logging
import numpy as np
from sqlalchemy.orm import Session
import google.generativeai as genai
from openai import AsyncOpenAI

from .settings import settings
from .models import Paper
from .database import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients based on provider
if settings.LLM_PROVIDER == "gemini":
    genai.configure(api_key=settings.GOOGLE_API_KEY)
elif settings.LLM_PROVIDER == "openai":
    openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_summary_with_gemini(abstract: str) -> tuple[str, list[float]]:
    """Generate summary using Google's Gemini model."""
    try:
        # Configure the model
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        # Create the prompt
        prompt = f"""Summarise the following arXiv abstract for a graduate‑level reader in ≤ 60 words. 
Focus on the main contribution.

ABSTRACT:
{abstract}

SUMMARY:"""
        
        # Generate the summary
        response = model.generate_content(prompt)
        summary = response.text.strip()
        
        # Generate embedding for the summary
        embedding_model = genai.Embedding()
        result = embedding_model.embed_content(
            content={"text": summary},
            task_type="RETRIEVAL_DOCUMENT"
        )
        embedding = result["embedding"]
        
        return summary, embedding
    
    except Exception as e:
        logger.error(f"Error generating summary with Gemini: {e}")
        return "", []


async def generate_summary_with_openai(abstract: str) -> tuple[str, list[float]]:
    """Generate summary using OpenAI model."""
    try:
        # Generate summary
        system_prompt = "You are a scientific writing assistant."
        user_prompt = f"Summarise the following arXiv abstract for a graduate‑level reader in ≤ 60 words. Focus on the main contribution.\n<ABSTRACT>\n{abstract}\n</ABSTRACT>"
        
        completion = await openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        summary = completion.choices[0].message.content.strip()
        
        # Generate embedding for the summary
        embedding_response = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=summary
        )
        
        embedding = embedding_response.data[0].embedding
        
        return summary, embedding
    
    except Exception as e:
        logger.error(f"Error generating summary with OpenAI: {e}")
        return "", []


async def generate_summary(abstract: str) -> tuple[str, list[float]]:
    """
    Generate a summary for a paper abstract using the configured LLM provider.
    Returns the summary and embedding.
    """
    if settings.LLM_PROVIDER == "gemini":
        return await generate_summary_with_gemini(abstract)
    elif settings.LLM_PROVIDER == "openai":
        return await generate_summary_with_openai(abstract)
    else:
        logger.error(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
        return "", []


async def process_unsummarized_papers(limit: int = 10):
    """Process papers without summaries and generate them."""
    db = SessionLocal()
    try:
        # Get papers without summaries
        papers = db.query(Paper).filter(Paper.summary.is_(None)).limit(limit).all()
        
        for paper in papers:
            logger.info(f"Generating summary for paper: {paper.arxiv_id}")
            
            # Generate summary and embedding from the abstract (not the summary)
            summary, embedding = await generate_summary(paper.abstract)
            
            if summary:
                paper.summary = summary
                paper.embedding = embedding
                db.add(paper)
                logger.info(f"Added summary for paper: {paper.arxiv_id}")
        
        # Commit changes
        db.commit()
        
    except Exception as e:
        logger.error(f"Error processing unsummarized papers: {e}")
        db.rollback()
    finally:
        db.close() 