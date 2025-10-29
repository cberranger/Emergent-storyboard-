from pymongo import MongoClient

client = MongoClient('mongodb://192.168.1.10:27017')
db = client['storyboard']

# Get all model names
all_models = list(db.civitai_models.find({}, {'name': 1, 'baseModel': 1, 'type': 1}))
print(f'Total models in database: {len(all_models)}')
print('\nAll models:')
for i, model in enumerate(all_models[:20]):  # Show first 20
    print(f'  {i+1:2d}. {model["name"]} (Base: {model.get("baseModel", "N/A")})')

if len(all_models) > 20:
    print(f'  ... and {len(all_models) - 20} more models')

# Search for any model with "Real" in the name
real_models = list(db.civitai_models.find({'name': {'$regex': 'Real', '$options': 'i'}}, {'name': 1, 'baseModel': 1}))
print(f'\nModels with "Real" in name: {len(real_models)}')
for model in real_models:
    print(f'  - {model["name"]} (Base: {model.get("baseModel", "N/A")})')

client.close()
