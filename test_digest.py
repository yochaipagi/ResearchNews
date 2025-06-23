#!/usr/bin/env python3
"""
Test script for the digest email functionality.
This script directly calls the functions from the backend to test the digest scheduler.
"""
import asyncio
import httpx
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8000"

async def register_test_user():
    """Register a test user with the system."""
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "categories": ["cs.AI", "cs.CL", "cs.LG"],
        "frequency": "DAILY"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BASE_URL}/register", json=user_data)
            response.raise_for_status()
            print(f"User registered successfully: {response.json()}")
            return response.json()
        except Exception as e:
            print(f"Error registering user: {e}")
            return None

async def trigger_fetch():
    """Trigger the paper fetch task."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BASE_URL}/trigger/fetch")
            response.raise_for_status()
            print(f"Paper fetch triggered: {response.json()}")
            return True
        except Exception as e:
            print(f"Error triggering fetch: {e}")
            return False

async def trigger_summarize():
    """Trigger the paper summarization task."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BASE_URL}/trigger/summarize", params={"limit": 10})
            response.raise_for_status()
            print(f"Summarization triggered: {response.json()}")
            return True
        except Exception as e:
            print(f"Error triggering summarization: {e}")
            return False

async def update_user_for_immediate_digest(user_id):
    """Update the user's next_digest_at to trigger an immediate digest."""
    auth_header = {"Authorization": f"Bearer test@example.com"}
    
    # First get the current user profile
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/profile", headers=auth_header)
            response.raise_for_status()
            user_data = response.json()
            
            # Set next_digest_at to now (do this by direct API call to the backend)
            # Since we don't have a direct API endpoint to set next_digest_at, we'll just
            # use an admin endpoint to see if the digest was sent
            print("User data fetched successfully, would now set next_digest_at to immediate")
            print(f"Current user data: {json.dumps(user_data, indent=2)}")
            
            return True
        except Exception as e:
            print(f"Error updating user for immediate digest: {e}")
            return False

async def main():
    # Register a test user
    user = await register_test_user()
    if not user:
        print("Failed to register test user, aborting test")
        return
    
    # Trigger paper fetch and summarization
    print("\nTriggering paper fetch...")
    await trigger_fetch()
    
    print("\nTriggering paper summarization...")
    await trigger_summarize()
    
    # Update user for immediate digest
    print("\nUpdating user for immediate digest testing...")
    await update_user_for_immediate_digest(user["id"])
    
    print("\nTest completed. Please check the logs to see if digests were sent.")
    print("You can also check the database directly to verify the next_digest_at field.")

if __name__ == "__main__":
    asyncio.run(main())