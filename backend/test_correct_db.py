#!/usr/bin/env python3
"""Test script to check MongoDB connection using your .env configuration"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_databases():
    try:
        # Connect to MongoDB using your .env configuration
        client = AsyncIOMotorClient("mongodb://192.168.1.10:27017")
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB at 192.168.1.10:27017 successfully")
        
        # List all databases
        databases = await client.list_database_names()
        print(f"\n📁 Found {len(databases)} databases:")
        for db_name in sorted(databases):
            print(f"  - {db_name}")
        
        # Check the storyboard database (correct name from .env)
        if "storyboard" in databases:
            print(f"\n🔍 Checking 'storyboard' database:")
            db = client["storyboard"]
            
            # List collections
            collections = await db.list_collection_names()
            print(f"  Collections: {len(collections)}")
            
            for collection_name in sorted(collections):
                count = await db[collection_name].count_documents({})
                print(f"    - {collection_name}: {count} documents")
                
                # Show sample data if collection exists
                if count > 0 and collection_name in ["comfyui_servers", "projects", "scenes", "clips"]:
                    sample = await db[collection_name].find_one()
                    if sample:
                        print(f"      Sample keys: {list(sample.keys())}")
        else:
            print(f"\n❌ 'storyboard' database not found!")
            
            # Check if there are other databases that might contain the data
            print("\n🔍 Checking other potential databases:")
            potential_names = ["Storyboard", "emergent_storyboard", "app", "test"]
            for potential_name in potential_names:
                if potential_name in databases:
                    print(f"  Found potential database: {potential_name}")
                    db = client[potential_name]
                    collections = await db.list_collection_names()
                    print(f"    Collections: {collections}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB at 192.168.1.10:27017: {e}")
        print("\n🔧 Possible solutions:")
        print("1. Make sure MongoDB is running on 192.168.1.10:27017")
        print("2. Check if the IP address is correct")
        print("3. Verify network connectivity to the MongoDB server")
        print("4. Check if MongoDB accepts remote connections")

if __name__ == "__main__":
    asyncio.run(test_databases())
