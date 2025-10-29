#!/usr/bin/env python3
"""
Import Civitai JSON data into MongoDB with enhanced model-profile linking
"""

import json
import os
import sys
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import uuid

# Database configuration
MONGO_URL = "mongodb://192.168.1.10:27017"
DB_NAME = "storyboard"

def connect_to_mongodb():
    """Connect to MongoDB"""
    try:
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print(f"✅ Connected to MongoDB at {MONGO_URL}")
        return client
    except ConnectionFailure as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)

def import_civitai_models(db, json_file_path):
    """Import Civitai models from JSON to MongoDB"""
    
    print(f"📁 Loading Civitai data from {json_file_path}")
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    models = data.get('items', [])
    print(f"📊 Found {len(models)} models to import")
    
    # Create collection with indexes
    civitai_collection = db.civitai_models
    
    # Drop existing collection for clean import
    civitai_collection.drop()
    print("🗑️  Cleared existing civitai_models collection")
    
    # Create indexes for fast searching
    print("🔧 Creating database indexes...")
    
    # Text search index for names, descriptions, tags
    civitai_collection.create_index([
        ("name", "text"),
        ("description", "text"), 
        ("tags", "text"),
        ("modelVersions.name", "text"),
        ("modelVersions.description", "text")
    ], weights={
        "name": 10,
        "modelVersions.name": 8,
        "tags": 5,
        "description": 3,
        "modelVersions.description": 2
    })
    
    # Exact match indexes
    civitai_collection.create_index("id", unique=True)
    civitai_collection.create_index("type")
    civitai_collection.create_index("baseModel")
    civitai_collection.create_index("baseModelType")
    civitai_collection.create_index("nsfwLevel")
    civitai_collection.create_index("allowDerivatives")
    civitai_collection.create_index("allowCommercialUse")
    
    # Compound indexes for common queries
    civitai_collection.create_index([("type", 1), ("baseModel", 1)])
    civitai_collection.create_index([("baseModel", 1), ("nsfwLevel", 1)])
    
    print("✅ Indexes created successfully")
    
    # Import models in batches
    batch_size = 1000
    imported_count = 0
    
    for i in range(0, len(models), batch_size):
        batch = models[i:i + batch_size]
        
        # Add import metadata
        for model in batch:
            model['_imported_at'] = datetime.utcnow()
            model['_import_id'] = str(uuid.uuid4())
        
        try:
            result = civitai_collection.insert_many(batch)
            imported_count += len(result.inserted_ids)
            
            progress = (i + batch_size) / len(models) * 100
            print(f"📈 Imported {imported_count:,} models ({progress:.1f}%)")
            
        except Exception as e:
            print(f"❌ Error importing batch {i//batch_size}: {e}")
            continue
    
    print(f"🎉 Successfully imported {imported_count:,} Civitai models!")
    return imported_count

def create_model_profile_system(db):
    """Create enhanced model-profile linking system"""
    
    print("🔗 Setting up model-profile linking system...")
    
    # Collection for direct model-profile links
    model_profiles = db.model_profiles
    
    # Drop and recreate
    model_profiles.drop()
    
    # Schema:
    # {
    #   "_id": "profile_id",
    #   "name": "Profile Name",
    #   "description": "Profile description", 
    #   "settings": { cfg_scale, steps, sampler, etc },
    #   "linked_model_ids": ["model_id_1", "model_id_2"],  # Direct links
    #   "linked_base_models": ["SDXL 1.0", "Illustrious"],  # Base model links
    #   "priority": "exact" | "base_model" | "generic",
    #   "created_at": datetime,
    #   "updated_at": datetime
    # }
    
    model_profiles.create_index("linked_model_ids")
    model_profiles.create_index("linked_base_models") 
    model_profiles.create_index("priority")
    model_profiles.create_index([("linked_model_ids", 1), ("priority", 1)])
    
    print("✅ Model-profile system created")
    
    # Create some example profiles
    example_profiles = [
        {
            "_id": "sdxl_lightning_profile",
            "name": "SDXL Lightning Fast",
            "description": "Optimized for SDXL Lightning models with fast generation",
            "settings": {
                "cfg_scale": 1.5,
                "steps": 4,
                "sampler": "euler",
                "scheduler": "normal",
                "clip_skip": -1
            },
            "linked_model_ids": [],
            "linked_base_models": ["SDXL 1.0-LCM", "SDXL Lightning"],
            "priority": "base_model",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": "illustrious_profile", 
            "name": "Illustrious Anime",
            "description": "Optimized for Illustrious-based anime models",
            "settings": {
                "cfg_scale": 7.0,
                "steps": 28,
                "sampler": "dpmpp_2m",
                "scheduler": "karras",
                "clip_skip": 2
            },
            "linked_model_ids": [],
            "linked_base_models": ["Illustrious", "Illustrious V0.1"],
            "priority": "base_model", 
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": "realvisxl_profile",
            "name": "RealVisXL Photorealistic",
            "description": "Optimized for RealVisXL photorealistic models",
            "settings": {
                "cfg_scale": 7.5,
                "steps": 30,
                "sampler": "dpmpp_2m",
                "scheduler": "karras",
                "clip_skip": 2
            },
            "linked_model_ids": [],
            "linked_base_models": ["RealVisXL"],
            "priority": "base_model",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    model_profiles.insert_many(example_profiles)
    print("📝 Created example model profiles")

def main():
    """Main import process"""
    print("🚀 Starting Civitai database import...")
    
    # Connect to database
    client = connect_to_mongodb()
    db = client[DB_NAME]
    
    # Import Civitai models
    json_file = os.path.join(os.path.dirname(__file__), "civit-ai-json-models.json")
    
    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        sys.exit(1)
    
    model_count = import_civitai_models(db, json_file)
    
    # Create model-profile system
    create_model_profile_system(db)
    
    print("\n🎊 Import completed successfully!")
    print(f"📊 Total models imported: {model_count:,}")
    print(f"🗄️  Database: {DB_NAME}")
    print(f"📋 Collections: civitai_models, model_profiles")
    
    # Test the import
    print("\n🧪 Testing database queries...")
    
    civitai_collection = db.civitai_models
    total_models = civitai_collection.count_documents({})
    realvisxl_models = civitai_collection.count_documents({"name": {"$regex": "RealVisXL", "$options": "i"}})
    illustrious_models = civitai_collection.count_documents({"baseModel": {"$regex": "Illustrious", "$options": "i"}})
    
    print(f"✅ Total models in database: {total_models:,}")
    print(f"✅ RealVisXL models found: {realvisxl_models}")
    print(f"✅ Illustrious models found: {illustrious_models}")
    
    client.close()

if __name__ == "__main__":
    main()
