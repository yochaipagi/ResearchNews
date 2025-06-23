#!/usr/bin/env python
import asyncio
from app.ingestion import ingest_papers_for_categories

if __name__ == "__main__":
    print("Starting paper ingestion process...")
    asyncio.run(ingest_papers_for_categories())
    print("Paper ingestion process completed!") 