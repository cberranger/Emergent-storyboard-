#!/usr/bin/env python3
"""Test script to verify .env configuration"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env the same way server.py does
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

print("🔍 Environment Configuration:")
print(f"MONGO_URL: {os.environ.get('MONGO_URL', 'NOT SET')}")
print(f"DB_NAME: {os.environ.get('DB_NAME', 'NOT SET')}")
print("CORS_POLICY: allow-all (no origin restrictions)")
print(f"PORT: {os.environ.get('PORT', 'NOT SET')}")

# Test database connection using same settings
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_connection():
    try:
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'storyboard')
        
        print(f"\n🔗 Testing connection to: {mongo_url}")
        print(f"📁 Database: {db_name}")
        
        client = AsyncIOMotorClient(mongo_url)
        await client.admin.command('ping')
        
        db = client[db_name]
        collections = await db.list_collection_names()
        
        print(f"✅ Connected successfully!")
        print(f"📊 Collections: {collections}")
        
        # Count documents
        for collection in ['projects', 'scenes', 'clips', 'comfyui_servers']:
            if collection in collections:
                count = await db[collection].count_documents({})
                print(f"   - {collection}: {count} documents")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
