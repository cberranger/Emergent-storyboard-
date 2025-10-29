#!/usr/bin/env python3
"""Test script to check MongoDB connection and databases"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_databases():
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        
        # List all databases
        databases = await client.list_database_names()
        print(f"\n📁 Found {len(databases)} databases:")
        for db_name in sorted(databases):
            print(f"  - {db_name}")
        
        # Check the Storyboard database
        if "Storyboard" in databases:
            print(f"\n🔍 Checking 'Storyboard' database:")
            db = client["Storyboard"]
            
            # List collections
            collections = await db.list_collection_names()
            print(f"  Collections: {len(collections)}")
            
            for collection_name in sorted(collections):
                count = await db[collection_name].count_documents({})
                print(f"    - {collection_name}: {count} documents")
                
                # Show sample data if collection exists
                if count > 0:
                    sample = await db[collection_name].find_one()
                    if sample:
                        print(f"      Sample keys: {list(sample.keys())}")
        else:
            print(f"\n❌ 'Storyboard' database not found!")
            
            # Check if there are other databases that might contain the data
            print("\n🔍 Checking other potential databases:")
            potential_names = ["storyboard", "emergent_storyboard", "app", "test"]
            for potential_name in potential_names:
                if potential_name in databases:
                    print(f"  Found potential database: {potential_name}")
                    db = client[potential_name]
                    collections = await db.list_collection_names()
                    print(f"    Collections: {collections}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")

if __name__ == "__main__":
    asyncio.run(test_databases())
