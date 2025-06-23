import time
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import httpx
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import text

from .settings import settings
from .models import Paper
from .database import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# XML namespaces in arXiv API
NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom"
}


async def fetch_papers(
    category: str, 
    max_results: int = 100, 
    start: int = 0,
    sort_by: str = "submittedDate",
    sort_order: str = "descending",
    max_retries: int = 3
) -> list:
    """
    Fetch papers from arXiv API for a specific category.
    Respects arXiv's rate limit of 1 request per 3 seconds.
    Implements retry mechanism for resilience.
    """
    url = settings.ARXIV_API_URL
    
    params = {
        "search_query": f"cat:{category}",
        "start": start,
        "max_results": max_results,
        "sortBy": sort_by,
        "sortOrder": sort_order
    }
    
    headers = {
        "User-Agent": settings.ARXIV_USER_AGENT
    }
    
    logger.info(f"Fetching papers from arXiv for category: {category}")
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=60.0, verify=True) as client:
                logger.info(f"Attempt {attempt+1}/{max_retries}: Sending request to {url} with params {params}")
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                
                # Log success
                logger.info(f"Successfully fetched {category} papers from arXiv (attempt {attempt+1})")
                
                # Respect arXiv rate limit
                time.sleep(3)
                
                return parse_arxiv_response(response.text)
        except httpx.TimeoutException as e:
            logger.warning(f"Timeout on attempt {attempt+1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                # Exponential backoff: 5s, 10s, 20s...
                wait_time = 5 * (2 ** attempt)
                logger.info(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Failed to fetch papers after {max_retries} attempts: {e}")
                return []
        except httpx.HTTPError as e:
            logger.error(f"HTTP error on attempt {attempt+1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                wait_time = 5 * (2 ** attempt)
                logger.info(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Failed to fetch papers after {max_retries} attempts: {e}")
                return []
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt+1}/{max_retries}: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            if attempt < max_retries - 1:
                wait_time = 5 * (2 ** attempt)
                logger.info(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Failed to fetch papers after {max_retries} attempts")
                return []
    
    return []


def parse_arxiv_response(xml_content: str) -> list:
    """Parse arXiv API XML response into a list of paper dictionaries."""
    root = ET.fromstring(xml_content)
    entries = root.findall(".//atom:entry", NAMESPACES)
    
    papers = []
    for entry in entries:
        # Extract arXiv ID from the ID field (format: http://arxiv.org/abs/XXXX.XXXXX)
        id_url = entry.find("atom:id", NAMESPACES).text
        arxiv_id = id_url.split("/")[-1]
        
        # Extract title and remove newlines
        title_elem = entry.find("atom:title", NAMESPACES)
        title = " ".join(title_elem.text.split()) if title_elem is not None and title_elem.text else ""
        
        # Extract and format authors
        author_elems = entry.findall("atom:author/atom:name", NAMESPACES)
        authors = ", ".join([author.text for author in author_elems if author.text])
        
        # Extract summary and remove newlines
        summary_elem = entry.find("atom:summary", NAMESPACES)
        summary = " ".join(summary_elem.text.split()) if summary_elem is not None and summary_elem.text else ""
        
        # Extract categories
        category_elems = entry.findall("arxiv:primary_category", NAMESPACES)
        categories = [cat.attrib.get("term") for cat in category_elems if "term" in cat.attrib]
        category = categories[0] if categories else None
        
        # Extract published date
        published_elem = entry.find("atom:published", NAMESPACES)
        published_str = published_elem.text if published_elem is not None and published_elem.text else None
        published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00")) if published_str else None
        
        # Create paper dictionary
        paper = {
            "arxiv_id": arxiv_id,
            "title": title,
            "authors": authors,
            "summary": summary,
            "category": category,
            "published_at": published_at,
        }
        
        papers.append(paper)
    
    return papers


async def ingest_papers_for_categories():
    """Ingest papers for all configured categories."""
    db = SessionLocal()
    try:
        for category in settings.ARXIV_CATEGORIES:
            papers = await fetch_papers(category)
            store_papers(papers, db)
    finally:
        db.close()


def store_papers(papers: list, db: Session):
    """Store papers in the database if they don't exist."""
    for paper_data in papers:
        # Check if paper already exists
        existing = db.query(Paper).filter(Paper.arxiv_id == paper_data["arxiv_id"]).first()
        if not existing:
            # Create new paper with embedding set to None for now
            # The embedding will be added later when vector type is available
            paper_dict = paper_data.copy()
            paper_dict["embedding"] = None
            paper = Paper(**paper_dict)
            db.add(paper)
            logger.info(f"Added new paper: {paper_data['arxiv_id']} - {paper_data['title'][:50]}...")
    
    # Commit all new papers
    try:
        db.commit()
    except Exception as e:
        logger.error(f"Error committing papers to database: {e}")
        # Rollback and try simplified approach
        db.rollback()
        # Try a simplified approach without vector column
        for paper_data in papers:
            try:
                # Simplified query to check existence
                existing = db.execute(
                    text("SELECT 1 FROM paper WHERE arxiv_id = :arxiv_id"),
                    {"arxiv_id": paper_data["arxiv_id"]}
                ).scalar()
                
                if not existing:
                    # Insert directly with SQL to avoid ORM issues with vector type
                    db.execute(
                        text("""
                            INSERT INTO paper 
                            (arxiv_id, title, authors, summary, category, published_at, fetched_at)
                            VALUES 
                            (:arxiv_id, :title, :authors, :summary, :category, :published_at, :fetched_at)
                        """),
                        {
                            "arxiv_id": paper_data["arxiv_id"],
                            "title": paper_data["title"],
                            "authors": paper_data["authors"],
                            "summary": paper_data["summary"],
                            "category": paper_data["category"],
                            "published_at": paper_data["published_at"],
                            "fetched_at": datetime.utcnow()
                        }
                    )
                    logger.info(f"Added new paper (fallback method): {paper_data['arxiv_id']} - {paper_data['title'][:50]}...")
            except Exception as inner_e:
                logger.error(f"Error adding paper {paper_data['arxiv_id']}: {inner_e}")
                continue
        
        # Final commit
        try:
            db.commit()
            logger.info("Papers committed successfully using fallback method")
        except Exception as commit_e:
            logger.error(f"Final commit error: {commit_e}")
            db.rollback() 