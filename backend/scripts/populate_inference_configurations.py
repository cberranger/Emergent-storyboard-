"""
Script to populate inference_configurations collection with standard quality and speed presets
for all active models in the database.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone
import uuid

# Add backend directory to path
BACKEND_DIR = Path(__file__).parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from database import db_manager
from repositories.inference_configuration_repository import InferenceConfigurationRepository


# Standard inference configurations by base model type
INFERENCE_PRESETS = {
    "sdxl": {
        "quality": {
            "steps": 30,
            "cfg_scale": 7.5,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "width": 1024,
            "height": 1024,
            "clip_skip": -1,
            "denoise": 1.0
        },
        "speed": {
            "steps": 15,
            "cfg_scale": 6.0,
            "sampler": "euler_a",
            "scheduler": "normal",
            "width": 1024,
            "height": 1024,
            "clip_skip": -1,
            "denoise": 1.0
        }
    },
    "flux_dev": {
        "quality": {
            "steps": 25,
            "cfg_scale": 1.0,
            "sampler": "euler",
            "scheduler": "simple",
            "width": 1024,
            "height": 1024,
            "guidance": 3.5,
            "max_shift": 1.15,
            "base_shift": 0.5
        },
        "speed": {
            "steps": 12,
            "cfg_scale": 1.0,
            "sampler": "euler",
            "scheduler": "simple",
            "width": 1024,
            "height": 1024,
            "guidance": 3.5,
            "max_shift": 1.15,
            "base_shift": 0.5
        }
    },
    "flux_schnell": {
        "quality": {
            "steps": 8,
            "cfg_scale": 1.0,
            "sampler": "euler",
            "scheduler": "simple",
            "width": 1024,
            "height": 1024,
            "guidance": 3.5,
            "max_shift": 1.15,
            "base_shift": 0.5
        },
        "speed": {
            "steps": 4,
            "cfg_scale": 1.0,
            "sampler": "euler",
            "scheduler": "simple",
            "width": 1024,
            "height": 1024,
            "guidance": 3.5,
            "max_shift": 1.15,
            "base_shift": 0.5
        }
    },
    "flux_krea": {
        "quality": {
            "steps": 20,
            "cfg_scale": 1.0,
            "sampler": "euler",
            "scheduler": "simple",
            "width": 1024,
            "height": 1024,
            "guidance": 3.5,
            "krea_strength": 0.8
        },
        "speed": {
            "steps": 10,
            "cfg_scale": 1.0,
            "sampler": "euler",
            "scheduler": "simple",
            "width": 1024,
            "height": 1024,
            "guidance": 3.5,
            "krea_strength": 0.7
        }
    },
    "pony": {
        "quality": {
            "steps": 28,
            "cfg_scale": 7.0,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "width": 1024,
            "height": 1024,
            "clip_skip": -2
        },
        "speed": {
            "steps": 12,
            "cfg_scale": 6.5,
            "sampler": "euler_a",
            "scheduler": "normal",
            "width": 1024,
            "height": 1024,
            "clip_skip": -2
        }
    },
    "wan_2_1": {
        "quality": {
            "steps": 25,
            "cfg_scale": 7.5,
            "sampler": "ddim",
            "scheduler": "normal",
            "width": 512,
            "height": 512,
            "video_fps": 24,
            "video_frames": 25,
            "requires_vae": "wan_2.1_vae.safetensors",
            "text_encoder": "clip_l.safetensors"
        },
        "speed": {
            "steps": 15,
            "cfg_scale": 7.0,
            "sampler": "ddim",
            "scheduler": "normal",
            "width": 512,
            "height": 512,
            "video_fps": 24,
            "video_frames": 14,
            "requires_vae": "wan_2.1_vae.safetensors",
            "text_encoder": "clip_l.safetensors"
        }
    },
    "wan_2_2": {
        "quality": {
            "steps": 20,
            "cfg_scale": 7.5,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "width": 768,
            "height": 768,
            "video_fps": 24,
            "video_frames": 25,
            "requires_vae": "wan2.2_vae.safetensors",
            "text_encoder": "umt5_xxl_fp8_e4m3fn_scaled.safetensors"
        },
        "speed": {
            "steps": 8,
            "cfg_scale": 6.5,
            "sampler": "euler",
            "scheduler": "simple",
            "width": 768,
            "height": 768,
            "video_fps": 24,
            "video_frames": 14,
            "requires_vae": "wan2.2_vae.safetensors",
            "text_encoder": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
            "lightning_lora": "wan2.2_i2v_lightx2v_4steps_lora_v1"
        }
    },
    "hidream": {
        "quality": {
            "steps": 25,
            "cfg_scale": 7.0,
            "sampler": "euler",
            "scheduler": "simple",
            "width": 1024,
            "height": 1024,
            "guidance": 3.5
        },
        "speed": {
            "steps": 12,
            "cfg_scale": 6.5,
            "sampler": "euler",
            "scheduler": "simple",
            "width": 1024,
            "height": 1024,
            "guidance": 3.5
        }
    },
    "sd_1_5": {
        "quality": {
            "steps": 25,
            "cfg_scale": 7.5,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "width": 512,
            "height": 512,
            "clip_skip": -1
        },
        "speed": {
            "steps": 15,
            "cfg_scale": 7.0,
            "sampler": "euler_a",
            "scheduler": "normal",
            "width": 512,
            "height": 512,
            "clip_skip": -1
        }
    }
}


async def populate_configurations():
    """Populate inference configurations for all active models"""
    
    # Connect to database
    print("Connecting to database...")
    success = await db_manager.connect()
    if not success:
        print("Failed to connect to database")
        return
    
    db = db_manager.get_database()
    if not db:
        print("Failed to get database instance")
        return
    
    print("Connected to database successfully")
    
    # Initialize repository
    inference_config_repo = InferenceConfigurationRepository(
        db.inference_configurations
    )
    
    # Create indexes
    print("Creating indexes...")
    await inference_config_repo.create_index()
    print("Indexes created")
    
    # Get all active models
    print("Fetching active models...")
    active_models = await db.database_models.find({"is_active": True}).to_list(1000)
    print(f"Found {len(active_models)} active models")
    
    if not active_models:
        print("No active models found. Please ensure models collection is populated.")
        return
    
    # Process each active model
    created_count = 0
    skipped_count = 0
    
    for model in active_models:
        model_id = model.get("id")
        model_name = model.get("name", "Unknown")
        model_type = model.get("type", "checkpoint")
        
        # Determine base model from metadata or name
        base_model = None
        metadata = model.get("metadata", {})
        
        # Try to get base model from metadata
        if "base_model" in metadata:
            base_model = metadata["base_model"]
        elif "baseModel" in metadata:
            base_model = metadata["baseModel"]
        
        # Infer from model name if not in metadata
        if not base_model:
            name_lower = model_name.lower()
            if "flux" in name_lower:
                if "schnell" in name_lower:
                    base_model = "flux_schnell"
                elif "krea" in name_lower:
                    base_model = "flux_krea"
                else:
                    base_model = "flux_dev"
            elif "sdxl" in name_lower or "xl" in name_lower:
                base_model = "sdxl"
            elif "pony" in name_lower:
                base_model = "pony"
            elif "wan" in name_lower:
                if "2.2" in name_lower or "2_2" in name_lower:
                    base_model = "wan_2_2"
                else:
                    base_model = "wan_2_1"
            elif "hidream" in name_lower:
                base_model = "hidream"
            elif "sd15" in name_lower or "sd_15" in name_lower or "1.5" in name_lower:
                base_model = "sd_1_5"
            else:
                # Default to SDXL for unknown models
                base_model = "sdxl"
        
        # Get presets for this base model
        if base_model not in INFERENCE_PRESETS:
            print(f"  Skipping {model_name}: no presets for base_model '{base_model}'")
            skipped_count += 1
            continue
        
        presets = INFERENCE_PRESETS[base_model]
        
        print(f"\nProcessing: {model_name} (base_model: {base_model})")
        
        # Create quality and speed configurations
        for config_type in ["quality", "speed"]:
            # Check if configuration already exists
            existing = await inference_config_repo.find_by_model_and_type(
                model_id, config_type
            )
            
            if existing:
                print(f"  - {config_type}: already exists, skipping")
                skipped_count += 1
                continue
            
            # Create configuration document
            config_params = presets[config_type].copy()
            
            config_doc = {
                "id": str(uuid.uuid4()),
                "model_id": model_id,
                "base_model": base_model,
                "configuration_type": config_type,
                "steps": config_params.pop("steps"),
                "cfg_scale": config_params.pop("cfg_scale"),
                "sampler": config_params.pop("sampler"),
                "scheduler": config_params.pop("scheduler"),
                "model_specific_params": config_params,  # All remaining params
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Create in database
            await inference_config_repo.create(config_doc)
            print(f"  - {config_type}: created")
            created_count += 1
    
    print(f"\n{'='*60}")
    print(f"Population complete!")
    print(f"  Created: {created_count} configurations")
    print(f"  Skipped: {skipped_count} (already exist or no presets)")
    print(f"{'='*60}")
    
    # Disconnect
    await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(populate_configurations())
