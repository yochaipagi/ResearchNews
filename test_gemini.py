#!/usr/bin/env python
import os
import sys
import time
import asyncio
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import necessary libraries
try:
    import google.generativeai as genai
    from openai import AsyncOpenAI
except ImportError:
    logger.error("Missing required packages. Install with: pip install google-generativeai openai")
    sys.exit(1)

# Get API keys from environment
google_api_key = os.getenv("GOOGLE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Validate API keys
if not google_api_key:
    logger.error("Error: GOOGLE_API_KEY not found in environment variables.")
    logger.error("Please set it in your .env file or export it directly.")
    sys.exit(1)

# Configure the Gemini API
genai.configure(api_key=google_api_key)

# Initialize OpenAI client if API key is available
openai_client = None
if openai_api_key:
    openai_client = AsyncOpenAI(api_key=openai_api_key)


async def test_gemini_models():
    """List and test available Gemini models."""
    try:
        logger.info("Listing available Gemini models:")
        models = genai.list_models()
        gemini_models = [m for m in models if "gemini" in m.name.lower()]
        
        if not gemini_models:
            logger.error("No Gemini models found. Check your API key and permissions.")
            return False
        
        for i, model in enumerate(gemini_models, 1):
            logger.info(f"{i}. {model.name}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error listing Gemini models: {e}")
        return False


async def generate_summary_with_gemini(abstract: str, model_name: str = "gemini-2.0-flash-lite"):
    """Generate summary using Google's Gemini model."""
    try:
        start_time = time.time()
        
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
        
        # Create a placeholder embedding (as embedding generation is different in Gemini)
        embedding = [0.0] * 768  # Standard dimension for many embedding models
        
        elapsed_time = time.time() - start_time
        
        return {
            "summary": summary,
            "elapsed_time": elapsed_time,
            "model": model_name,
            "embedding_size": len(embedding)
        }
    
    except Exception as e:
        logger.error(f"Error generating summary with Gemini: {e}")
        return {"summary": "", "elapsed_time": 0, "model": model_name, "error": str(e)}


async def generate_summary_with_openai(abstract: str, model_name: str = "gpt-4o-mini"):
    """Generate summary using OpenAI's models."""
    if not openai_client:
        return {"summary": "", "elapsed_time": 0, "model": model_name, "error": "OpenAI API key not configured"}
    
    try:
        start_time = time.time()
        
        # Create the prompt
        prompt = f"""Summarise the following arXiv abstract for a graduate‑level reader in ≤ 60 words. 
Focus on the main contribution.

ABSTRACT:
{abstract}

SUMMARY:"""
        
        # Generate the summary
        response = await openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a research assistant that summarizes academic papers concisely."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        summary = response.choices[0].message.content.strip()
        
        # Get embedding for the summary
        embedding_response = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=summary
        )
        
        embedding = embedding_response.data[0].embedding
        
        elapsed_time = time.time() - start_time
        
        return {
            "summary": summary,
            "elapsed_time": elapsed_time,
            "model": model_name,
            "embedding_size": len(embedding)
        }
    
    except Exception as e:
        logger.error(f"Error generating summary with OpenAI: {e}")
        return {"summary": "", "elapsed_time": 0, "model": model_name, "error": str(e)}


async def run_comparison_test():
    """Run a side-by-side comparison of Gemini and OpenAI for summary generation."""
    test_abstract = """
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
    
    logger.info("Running comparison test between Gemini and OpenAI...")
    
    # Test Gemini summary generation
    gemini_result = await generate_summary_with_gemini(test_abstract)
    
    # Test OpenAI summary generation if API key is available
    openai_result = {"summary": "OpenAI test skipped - API key not configured", "model": "none"}
    if openai_api_key:
        openai_result = await generate_summary_with_openai(test_abstract)
    
    # Print results side by side
    logger.info("\n" + "="*80)
    logger.info("COMPARISON RESULTS")
    logger.info("="*80)
    
    logger.info(f"GEMINI ({gemini_result.get('model', 'unknown')})")
    logger.info(f"Time: {gemini_result.get('elapsed_time', 0):.2f} seconds")
    logger.info("-"*50)
    logger.info(gemini_result.get('summary', 'Error generating summary'))
    logger.info("-"*50)
    
    logger.info(f"\nOPENAI ({openai_result.get('model', 'unknown')})")
    logger.info(f"Time: {openai_result.get('elapsed_time', 0):.2f} seconds")
    logger.info("-"*50)
    logger.info(openai_result.get('summary', 'Error generating summary'))
    logger.info("-"*50)
    
    return "gemini" in gemini_result.get('summary', '').lower() or len(gemini_result.get('summary', '')) > 10


async def main():
    """Main test function for Gemini integration."""
    logger.info("Testing Gemini API integration...")
    
    # Test model listing
    models_available = await test_gemini_models()
    if not models_available:
        return False
    
    # Run comparison test
    comparison_success = await run_comparison_test()
    
    return comparison_success


if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        logger.info("\n✅ Gemini integration is working correctly!")
        sys.exit(0)
    else:
        logger.error("\n❌ Gemini integration test failed. Please check your API key and try again.")
        sys.exit(1) 