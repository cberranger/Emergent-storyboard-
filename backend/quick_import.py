import json
import os
from pymongo import MongoClient
from datetime import datetime

# Load big file with UTF-8 encoding
with open('civit-ai-json-models.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Loaded {len(data.get("items", []))} models from big file')

# Connect to MongoDB
client = MongoClient('mongodb://192.168.1.10:27017')
db = client['storyboard']

# Drop and recreate collection
civitai_collection = db.civitai_models
civitai_collection.drop()

# Create indexes
civitai_collection.create_index('id', unique=True)
civitai_collection.create_index('name')
civitai_collection.create_index('type')
civitai_collection.create_index('baseModel')

# Insert data
models = data['items']
result = civitai_collection.insert_many(models)
print(f'Successfully imported {len(result.inserted_ids)} models')

# Create model profiles
model_profiles = db.model_profiles
model_profiles.drop()

example_profiles = [
    {
        "_id": "sdxl_lightning_profile",
        "name": "SDXL Lightning Fast",
        "description": "Optimized for SDXL Lightning models",
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
print("Created model profiles")

# Test queries
total = civitai_collection.count_documents({})
realvisxl = civitai_collection.count_documents({'name': {'$regex': 'RealVisXL', '$options': 'i'}})
illustrious = civitai_collection.count_documents({'baseModel': {'$regex': 'Illustrious|Pony', '$options': 'i'}})

print(f'Total models: {total}')
print(f'RealVisXL models: {realvisxl}')
print(f'Illustrious/Pony models: {illustrious}')

client.close()
print("Import completed!")
