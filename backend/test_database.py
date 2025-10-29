from pymongo import MongoClient

client = MongoClient('mongodb://192.168.1.10:27017')
db = client['storyboard']

# Check for RealVisXL models
realvisxl = list(db.civitai_models.find({'name': {'$regex': 'RealVisXL', '$options': 'i'}}, {'name': 1, 'baseModel': 1, 'type': 1}))
print('RealVisXL models found:')
for model in realvisxl:
    print(f'  - {model["name"]} (Base: {model.get("baseModel", "N/A")})')

# Check all models with SDXL base
sdxl_models = list(db.civitai_models.find({'baseModel': {'$regex': 'SDXL', '$options': 'i'}}, {'name': 1, 'baseModel': 1}).limit(10))
print('\nSDXL models (first 10):')
for model in sdxl_models:
    print(f'  - {model["name"]} (Base: {model.get("baseModel")})')

# Check available profiles
profiles = list(db.model_profiles.find({}, {'name': 1, 'linked_base_models': 1}))
print('\nAvailable model profiles:')
for profile in profiles:
    print(f'  - {profile["name"]} -> {profile["linked_base_models"]}')

client.close()
print('\nDatabase test completed!')
