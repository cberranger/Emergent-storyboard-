import requests
import json
import time

BASE_URL = 'https://civitai.com/api/v1/models'

def get_all_sdxl_checkpoints():
    all_models = []
    next_cursor = None
    page = 0
    
    while True:
        page += 1
        params = {
            'limit': 100,
            'types': 'Checkpoint',
            'baseModels': 'SDXL 1.0',
            'sort': 'Newest',
            'nsfw': False
        }
        
        if next_cursor:
            params['cursor'] = next_cursor
        
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        all_models.extend(data['items'])
        next_cursor = data['metadata'].get('nextCursor')
        
        print(f"Page {page}: Fetched {len(data['items'])} models. Total: {len(all_models)}")
        
        # No more pages
        if not next_cursor:
            break
        
        # Be respectful to the API
        time.sleep(1)
    
    # Write to file
    with open('sdxl_checkpoints.json', 'w') as f:
        json.dump(all_models, f, indent=2)
    
    print(f"\nDone! Saved {len(all_models)} models to sdxl_checkpoints.json")
    return all_models

# Run it
if __name__ == '__main__':
    models = get_all_sdxl_checkpoints()