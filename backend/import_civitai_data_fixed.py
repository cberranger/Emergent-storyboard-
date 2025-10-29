#!/usr/bin/env python3
"""
Import Civitai JSON data into MongoDB with error handling for partial files
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

def validate_json_file(json_file_path):
    """Validate and fix JSON file if possible"""
    print(f"🔍 Validating JSON file: {json_file_path}")
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse as-is
        try:
            data = json.loads(content)
            print("✅ JSON file is valid")
            return data
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON error: {e}")
            
            # Try to fix common issues
            if 'Expecting' in str(e) and 'delimiter' in str(e):
                print("🔧 Attempting to fix JSON structure...")
                
                # Find where the error occurs and try to close the structure
                lines = content.split('\n')
                error_pos = e.pos if hasattr(e, 'pos') else len(content)
                
                # Find the line with the error
                current_pos = 0
                error_line = 0
                for i, line in enumerate(lines):
                    if current_pos + len(line) >= error_pos:
                        error_line = i
                        break
                    current_pos += len(line) + 1
                
                print(f"📍 Error around line {error_line + 1}")
                
                # Try to fix by properly closing the JSON structure
                # Look for incomplete items array
                if '"items": [' in content and not content.rstrip().endswith('}'):
                    print("🔧 Fixing incomplete items array...")
                    
                    # Find the last complete item and close properly
                    last_complete_item = content.rfind('}')
                    if last_complete_item > 0:
                        # Close the items array and add metadata
                        fixed_content = content[:last_complete_item + 1] + '\n        }\n    ],\n    "metadata": {\n        "totalItems": ' + str(content.count('"id":')) + '\n    }\n}'
                        
                        try:
                            data = json.loads(fixed_content)
                            print("✅ JSON file fixed successfully")
                            return data
                        except json.JSONDecodeError as e2:
                            print(f"❌ Could not fix JSON: {e2}")
                
            return None
    
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

def import_civitai_models(db, json_file_path):
    """Import Civitai models from JSON to MongoDB with error handling"""
    
    # Validate and load JSON
    data = validate_json_file(json_file_path)
    if not data:
        print("❌ Could not load JSON data")
        return 0
    
    models = data.get('items', [])
    print(f"📊 Found {len(models)} models to import")
    
    if len(models) == 0:
        print("⚠️  No models found in JSON file")
        return 0
    
    # Create collection with indexes
    civitai_collection = db.civitai_models
    
    # Drop existing collection for clean import
    civitai_collection.drop()
    print("🗑️  Cleared existing civitai_models collection")
    
    # Create indexes for fast searching
    print("🔧 Creating database indexes...")
    
    # Text search index for names, descriptions, tags
    try:
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
    except Exception as e:
        print(f"⚠️  Could not create text index: {e}")
    
    # Exact match indexes
    civitai_collection.create_index("id", unique=True)
    civitai_collection.create_index("name")
    civitai_collection.create_index("type")
    civitai_collection.create_index("baseModel")
    civitai_collection.create_index("baseModelType")
    civitai_collection.create_index("nsfwLevel")
    
    print("✅ Indexes created successfully")
    
    # Import models in smaller batches to avoid memory issues
    batch_size = 500
    imported_count = 0
    error_count = 0
    
    for i in range(0, len(models), batch_size):
        batch = models[i:i + batch_size]
        
        # Add import metadata and validate each model
        valid_batch = []
        for model in batch:
            try:
                # Ensure required fields exist
                if 'id' not in model or 'name' not in model:
                    print(f"⚠️  Skipping invalid model: missing id or name")
                    error_count += 1
                    continue
                
                model['_imported_at'] = datetime.utcnow()
                model['_import_id'] = str(uuid.uuid4())
                valid_batch.append(model)
                
            except Exception as e:
                print(f"⚠️  Error processing model: {e}")
                error_count += 1
                continue
        
        if not valid_batch:
            continue
        
        try:
            result = civitai_collection.insert_many(valid_batch)
            imported_count += len(result.inserted_ids)
            
            progress = (i + batch_size) / len(models) * 100
            print(f"📈 Imported {imported_count:,} models ({progress:.1f}%)")
            
        except Exception as e:
            print(f"❌ Error importing batch {i//batch_size}: {e}")
            error_count += len(batch)
            continue
    
    print(f"🎉 Import completed!")
    print(f"✅ Successfully imported: {imported_count:,} models")
    print(f"❌ Errors/skipped: {error_count:,} models")
    
    return imported_count

def create_model_profile_system(db):
    """Create enhanced model-profile linking system"""
    
    print("🔗 Setting up model-profile linking system...")
    
    # Collection for direct model-profile links
    model_profiles = db.model_profiles
    
    # Drop and recreate
    model_profiles.drop()
    
    # Create indexes
    model_profiles.create_index("linked_model_ids")
    model_profiles.create_index("linked_base_models") 
    model_profiles.create_index("priority")
    
    print("✅ Model-profile system created")
    
    # Create example profiles
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
            "linked_base_models": ["SDXL 1.0-LCM", "SDXL Lightning", "SDXL"],
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
            "linked_base_models": ["Illustrious", "Illustrious V0.1", "Pony Diffusion"],
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
            "linked_base_models": ["RealVisXL", "SDXL"],
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
    
    # Try main JSON file first
    json_file = os.path.join(os.path.dirname(__file__), "civit-ai-json-models.json")
    
    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        sys.exit(1)
    
    model_count = import_civitai_models(db, json_file)
    
    if model_count == 0:
        print("❌ No models were imported")
        client.close()
        sys.exit(1)
    
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
    illustrious_models = civitai_collection.count_documents({"baseModel": {"$regex": "Illustrious|Pony", "$options": "i"}})
    
    print(f"✅ Total models in database: {total_models:,}")
    print(f"✅ RealVisXL models found: {realvisxl_models}")
    print(f"✅ Illustrious/Pony models found: {illustrious_models}")
    
    client.close()

if __name__ == "__main__":
    main()
