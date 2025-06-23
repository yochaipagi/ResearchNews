#!/usr/bin/env python
import asyncio
import sys
from app.summarise import process_unsummarized_papers

if __name__ == "__main__":
    # Get limit from command line argument or use default
    limit = 10
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print(f"Invalid limit: {sys.argv[1]}. Using default: 10")
    
    print(f"Starting paper summarization process (limit: {limit})...")
    asyncio.run(process_unsummarized_papers(limit))
    print("Paper summarization process completed!") 