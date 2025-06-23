#!/usr/bin/env python
"""
Gemini Examples for Research Feed Platform

This script demonstrates different ways to use Google's Gemini models
for various research paper summarization tasks.
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check for required API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    logger.error("GOOGLE_API_KEY not found in environment variables")
    logger.error("Please set it in your .env file or export it directly")
    sys.exit(1)

try:
    import google.generativeai as genai
except ImportError:
    logger.error("google-generativeai package not installed")
    logger.error("Install with: pip install google-generativeai")
    sys.exit(1)

# Configure Gemini
genai.configure(api_key=api_key)

# Sample research paper abstract
SAMPLE_ABSTRACT = """
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

SAMPLE_ABSTRACT_2 = """
Most machine learning systems assume that the world is static and the underlying data distribution doesn't change, but reality is often more complex. This paper introduces a novel framework for Continuous Learning in Dynamic Environments (CLDE) that enables models to adapt to evolving data patterns without catastrophic forgetting. We develop a hybrid architecture combining memory replay mechanisms with a meta-learning approach that explicitly models distribution shifts. Evaluations on both synthetic datasets with controlled drift patterns and real-world temporal datasets demonstrate that CLDE achieves 37% better performance retention compared to state-of-the-art continual learning methods when facing distribution shifts. Our approach requires minimal computational overhead while providing robust adaptation capabilities for deployment in non-stationary environments.
"""


async def list_available_models():
    """List all available Gemini models."""
    logger.info("Available Gemini models:")
    
    try:
        models = genai.list_models()
        gemini_models = [m for m in models if "gemini" in m.name.lower()]
        
        for i, model in enumerate(gemini_models, 1):
            # Get model details
            model_details = f"{model.name}"
            if hasattr(model, "description") and model.description:
                model_details += f" - {model.description}"
            logger.info(f"{i}. {model_details}")
            
        return gemini_models
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return []


async def generate_basic_summary(abstract: str, model_name: str = "gemini-2.0-flash-lite") -> Dict[str, Any]:
    """Generate a basic summary of a research paper abstract."""
    try:
        # Configure the model
        model = genai.GenerativeModel(model_name)
        
        # Create the prompt
        prompt = f"""Summarise the following arXiv abstract for a graduate‑level reader in ≤ 60 words. 
Focus on the main contribution.

ABSTRACT:
{abstract}

SUMMARY:"""
        
        # Generate the summary
        response = model.generate_content(prompt)
        summary = response.text.strip()
        
        return {
            "summary": summary,
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "type": "basic_summary"
        }
    except Exception as e:
        logger.error(f"Error generating basic summary: {e}")
        return {"error": str(e)}


async def generate_detailed_summary(abstract: str, model_name: str = "gemini-2.0-flash-lite") -> Dict[str, Any]:
    """Generate a more detailed summary with methodology and results."""
    try:
        # Configure the model
        model = genai.GenerativeModel(model_name)
        
        # Create the prompt
        prompt = f"""Create a detailed summary of the following research paper abstract.
Include: 
1) The main problem being addressed
2) The proposed method/approach
3) Key results and their significance

ABSTRACT:
{abstract}

DETAILED SUMMARY:"""
        
        # Generate the summary
        response = model.generate_content(prompt)
        summary = response.text.strip()
        
        return {
            "summary": summary,
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "type": "detailed_summary"
        }
    except Exception as e:
        logger.error(f"Error generating detailed summary: {e}")
        return {"error": str(e)}


async def extract_key_points(abstract: str, model_name: str = "gemini-2.0-flash-lite") -> Dict[str, Any]:
    """Extract key points from a research paper abstract."""
    try:
        # Configure the model
        model = genai.GenerativeModel(model_name)
        
        # Create the prompt
        prompt = f"""Extract the 3-5 most important key points from this research paper abstract.
Format as a bullet list.

ABSTRACT:
{abstract}

KEY POINTS:"""
        
        # Generate the key points
        response = model.generate_content(prompt)
        key_points = response.text.strip()
        
        return {
            "key_points": key_points,
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "type": "key_points"
        }
    except Exception as e:
        logger.error(f"Error extracting key points: {e}")
        return {"error": str(e)}


async def create_placeholder_embedding(content: str) -> List[float]:
    """Create a placeholder embedding for content."""
    # Note: In production, you should use a real embedding model
    # This is just a placeholder as the embedding API has changed
    return [0.0] * 768  # Standard dimension for many embedding models


async def run_examples(model_name: str = "gemini-2.0-flash-lite"):
    """Run all example functions."""
    logger.info("\n" + "="*80)
    logger.info(f"RUNNING EXAMPLES WITH MODEL: {model_name}")
    logger.info("="*80)
    
    # Generate basic summary for the first abstract
    logger.info("\n1. BASIC SUMMARY (ABSTRACT 1)")
    basic_result = await generate_basic_summary(SAMPLE_ABSTRACT, model_name)
    logger.info("-"*50)
    logger.info(basic_result.get("summary", "Error generating summary"))
    logger.info("-"*50)
    
    # Generate detailed summary for the first abstract
    logger.info("\n2. DETAILED SUMMARY (ABSTRACT 1)")
    detailed_result = await generate_detailed_summary(SAMPLE_ABSTRACT, model_name)
    logger.info("-"*50)
    logger.info(detailed_result.get("summary", "Error generating detailed summary"))
    logger.info("-"*50)
    
    # Extract key points from the first abstract
    logger.info("\n3. KEY POINTS (ABSTRACT 1)")
    key_points_result = await extract_key_points(SAMPLE_ABSTRACT, model_name)
    logger.info("-"*50)
    logger.info(key_points_result.get("key_points", "Error extracting key points"))
    logger.info("-"*50)
    
    # Generate basic summary for the second abstract
    logger.info("\n4. BASIC SUMMARY (ABSTRACT 2)")
    basic_result_2 = await generate_basic_summary(SAMPLE_ABSTRACT_2, model_name)
    logger.info("-"*50)
    logger.info(basic_result_2.get("summary", "Error generating summary"))
    logger.info("-"*50)
    
    # Placeholder for embeddings
    logger.info("\n5. EMBEDDINGS (PLACEHOLDER)")
    logger.info("-"*50)
    embedding = await create_placeholder_embedding(basic_result.get("summary", ""))
    logger.info(f"Created placeholder embedding with dimension: {len(embedding)}")
    logger.info("Note: In production, use a real embedding model or store in your vector database")
    logger.info("-"*50)


def main():
    """Main function to run example scripts."""
    parser = argparse.ArgumentParser(description="Run Gemini examples for Research Feed platform")
    parser.add_argument("--model", type=str, default="gemini-2.0-flash-lite",
                        help="Gemini model to use for examples")
    parser.add_argument("--list-models", action="store_true",
                        help="List available Gemini models and exit")
    args = parser.parse_args()
    
    if args.list_models:
        asyncio.run(list_available_models())
        return
    
    asyncio.run(run_examples(args.model))


if __name__ == "__main__":
    main() 