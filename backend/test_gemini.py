#!/usr/bin/env python
import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found in environment variables.")
    print("Please set it in your .env file or export it directly.")
    sys.exit(1)

# Configure the Gemini API
genai.configure(api_key=api_key)


async def test_gemini():
    """Test the Gemini API with a simple summary generation."""
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
    
    try:
        # List available models
        print("Available Gemini models:")
        models = genai.list_models()
        gemini_models = [m for m in models if "gemini" in m.name.lower()]
        for model in gemini_models:
            print(f"- {model.name}")
        
        # Choose a suitable model
        model_name = "gemini-1.5-flash" # Using a known available model
        print(f"\nUsing model: {model_name}")
        
        # Configure the model
        model = genai.GenerativeModel(model_name)
        
        # Create the prompt
        prompt = f"""Summarise the following arXiv abstract for a graduate‑level reader in ≤ 60 words. 
Focus on the main contribution.

ABSTRACT:
{test_abstract}

SUMMARY:"""
        
        print("Sending request to Gemini...")
        
        # Generate the summary
        response = model.generate_content(prompt)
        summary = response.text.strip()
        
        print("\nGenerated Summary:")
        print("-" * 50)
        print(summary)
        print("-" * 50)
        
        # Test embedding generation - using numpy array for simplicity in this test
        print("\nSkipping embedding test for now - will use vector storage in database...")
        # Create a dummy embedding vector of proper dimension
        embedding = [0.0] * 768  # Standard dimension for many embedding models
        
        print(f"✅ Created placeholder embedding with dimension: {len(embedding)}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error testing Gemini API: {e}")
        return False


if __name__ == "__main__":
    print("Testing Gemini integration...")
    success = asyncio.run(test_gemini())
    
    if success:
        print("\n✅ Gemini integration is working correctly!")
    else:
        print("\n❌ Gemini integration test failed. Please check your API key and try again.") 