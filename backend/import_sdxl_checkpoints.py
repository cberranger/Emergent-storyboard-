import json
import os
import asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# MongoDB connection (same as server)
MONGODB_URL = "mongodb://192.168.1.10:27017"
DATABASE_NAME = "storyboard"

async def import_sdxl_checkpoints():
    """Import all SDXL checkpoints from JSON file to MongoDB"""
    
    # Load JSON file
    json_path = os.path.join(os.path.dirname(__file__), "utils", "sdxl_checkpoints.json")
    print(f"Loading JSON from: {json_path}")
    
    if not os.path.exists(json_path):
        print(f"Error: JSON file not found at {json_path}")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        checkpoints = json.load(f)
    
    print(f"Loaded {len(checkpoints)} checkpoints from JSON")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    collection = db.database_models
    
    # Clear existing Civitai models (optional - comment out if you want to keep them)
    print("Clearing existing Civitai models...")
    result = await collection.delete_many({"source": "civitai_sdxl"})
    print(f"Deleted {result.deleted_count} existing Civitai models")
    
    # Import checkpoints
    imported_count = 0
    skipped_count = 0
    
    for checkpoint in checkpoints:
        try:
            # Create a database model entry
            model_data = {
                "id": f"civitai_{checkpoint['id']}",  # Unique ID with Civitai prefix
                "name": checkpoint["name"],
                "type": checkpoint.get("type", "Checkpoint"),
                "model_type": checkpoint.get("type", "Checkpoint"),
                "source": "civitai_sdxl",
                "filename": checkpoint.get("modelVersions", [{}])[0].get("files", [{}])[0].get("name", "") if checkpoint.get("modelVersions") else "",
                "path": f"civitai_models/{checkpoint['id']}",
                "civitai_info": {
                    "modelId": str(checkpoint.get("id")),
                    "name": checkpoint.get("name"),
                    "description": checkpoint.get("description"),
                    "type": checkpoint.get("type"),
                    "tags": checkpoint.get("tags", []),
                    "modelVersions": checkpoint.get("modelVersions", []),
                    "images": checkpoint.get("modelVersions", [{}])[0].get("images", []) if checkpoint.get("modelVersions") else [],
                    "allowDerivatives": checkpoint.get("allowDerivatives"),
                    "sfwOnly": checkpoint.get("sfwOnly"),
                    "nsfw": checkpoint.get("nsfw"),
                    "nsfwLevel": checkpoint.get("nsfwLevel"),
                    "cosmetic": checkpoint.get("cosmetic"),
                    "stats": checkpoint.get("stats", {}),
                    "allowNoCredit": checkpoint.get("allowNoCredit"),
                    "allowCommercialUse": checkpoint.get("allowCommercialUse", []),
                    "availability": checkpoint.get("availability"),
                    "supportsGeneration": checkpoint.get("supportsGeneration"),
                    "downloadUrl": checkpoint.get("modelVersions", [{}])[0].get("files", [{}])[0].get("downloadUrl") if checkpoint.get("modelVersions") else None
                },
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Insert into database
            await collection.insert_one(model_data)
            imported_count += 1
            
            if imported_count % 100 == 0:
                print(f"Imported {imported_count} models...")
                
        except DuplicateKeyError:
            skipped_count += 1
            continue
        except Exception as e:
            print(f"Error importing model {checkpoint.get('name', 'Unknown')}: {e}")
            continue
    
    print(f"\nImport complete!")
    print(f"Successfully imported: {imported_count} models")
    print(f"Skipped (duplicates): {skipped_count} models")
    
    # Create indexes for better search performance
    print("\nCreating indexes...")
    await collection.create_index("name")
    await collection.create_index("source")
    await collection.create_index("civitai_info.modelId")
    await collection.create_index([("name", "text"), ("civitai_info.description", "text"), ("civitai_info.tags", "text")])
    print("Indexes created successfully!")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(import_sdxl_checkpoints())
