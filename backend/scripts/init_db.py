from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, Any

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import PyMongoError


logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("init_db")


REQUIRED_COLLECTIONS = [
    "projects",
    "scenes",
    "clips",
    "characters",
    "style_templates",
    "comfyui_servers",
    "generation_batches",
    "facefusion_jobs",
    "facefusion_presets",
    "database_models",
    "inference_configurations",
    "civitai_models",
    "users",
]


def load_env_from_file(env_path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    try:
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                values[k.strip()] = v.strip()
    except Exception as exc:
        logger.warning("Failed to read .env at %s: %s", env_path, exc)
    return values


async def verify_and_create_collections(db) -> None:
    """Verify all required collections exist and create missing ones"""
    existing_collections = set(await db.list_collection_names())
    
    for col in REQUIRED_COLLECTIONS:
        if col not in existing_collections:
            try:
                await db.create_collection(col)
                logger.info("✓ Collection created: %s", col)
            except PyMongoError as exc:
                logger.error("✗ Failed to create collection %s: %s", col, exc)
        else:
            logger.info("✓ Collection exists: %s", col)
    
    missing = set(REQUIRED_COLLECTIONS) - existing_collections
    if missing:
        logger.warning("Missing collections were created: %s", ", ".join(sorted(missing)))


async def ensure_indexes(db) -> None:
    """Create indexes for all collections with proper error handling"""
    async def ensure(col: str, keys: Any, **opts: Any) -> None:
        try:
            name = await db[col].create_index(keys, **opts)
            logger.info("  Index ensured on %s: %s (%s)", col, keys, name)
        except PyMongoError as exc:
            logger.error("  Failed index on %s %s: %s", col, keys, exc)

    logger.info("Creating indexes...")
    
    # Core Collections
    logger.info("Projects...")
    await ensure("projects", [("id", ASCENDING)], unique=True)
    await ensure("projects", [("created_at", DESCENDING)])

    logger.info("Scenes...")
    await ensure("scenes", [("id", ASCENDING)], unique=True)
    await ensure("scenes", [("project_id", ASCENDING), ("order", ASCENDING)])
    await ensure("scenes", [("parent_scene_id", ASCENDING)])
    await ensure("scenes", [("is_alternate", ASCENDING)])

    logger.info("Clips...")
    await ensure("clips", [("id", ASCENDING)], unique=True)
    await ensure("clips", [("scene_id", ASCENDING), ("order", ASCENDING)])
    await ensure("clips", [("scene_id", ASCENDING), ("timeline_position", ASCENDING)])

    logger.info("Characters...")
    await ensure("characters", [("id", ASCENDING)], unique=True)
    await ensure("characters", [("project_id", ASCENDING), ("name", ASCENDING)])

    logger.info("Style templates...")
    await ensure("style_templates", [("id", ASCENDING)], unique=True)
    await ensure("style_templates", [("project_id", ASCENDING), ("name", ASCENDING)])

    logger.info("ComfyUI servers...")
    await ensure("comfyui_servers", [("id", ASCENDING)], unique=True)
    await ensure("comfyui_servers", [("url", ASCENDING)], unique=True)
    await ensure("comfyui_servers", [("is_active", ASCENDING)])

    logger.info("Generation batches...")
    await ensure("generation_batches", [("id", ASCENDING)], unique=True)
    await ensure("generation_batches", [("project_id", ASCENDING), ("created_at", DESCENDING)])
    await ensure("generation_batches", [("status", ASCENDING)])

    # FaceFusion Collections
    logger.info("FaceFusion jobs...")
    await ensure("facefusion_jobs", [("id", ASCENDING)], unique=True)
    await ensure("facefusion_jobs", [("status", ASCENDING), ("priority", DESCENDING), ("created_at", ASCENDING)])
    await ensure("facefusion_jobs", [("character_id", ASCENDING)])
    await ensure("facefusion_jobs", [("project_id", ASCENDING), ("created_at", DESCENDING)])

    logger.info("FaceFusion presets...")
    await ensure("facefusion_presets", [("id", ASCENDING)], unique=True)
    await ensure("facefusion_presets", [("name", ASCENDING)])
    await ensure("facefusion_presets", [("operation_type", ASCENDING), ("is_public", ASCENDING)])

    # Model Management Collections
    logger.info("Database models...")
    await ensure("database_models", [("id", ASCENDING)], unique=True)
    await ensure("database_models", [("is_active", ASCENDING), ("type", ASCENDING)])
    await ensure("database_models", [("base_model", ASCENDING), ("is_active", ASCENDING)])

    logger.info("Inference configurations...")
    await ensure("inference_configurations", [("model_id", ASCENDING), ("preset_type", ASCENDING)], unique=True)

    logger.info("CivitAI models...")
    await ensure("civitai_models", [("id", ASCENDING)], unique=True)
    await ensure("civitai_models", [("type", ASCENDING), ("nsfw", ASCENDING)])

    # Authentication Collections
    logger.info("Users...")
    await ensure("users", [("id", ASCENDING)], unique=True)
    await ensure("users", [("username", ASCENDING)], unique=True)
    await ensure("users", [("email", ASCENDING)], unique=True)


async def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    backend_env = load_env_from_file(repo_root / "backend" / ".env")

    mongo_url = os.environ.get("MONGO_URL") or backend_env.get("MONGO_URL") or "mongodb://192.168.1.10:27017"
    db_name = os.environ.get("DB_NAME") or backend_env.get("DB_NAME") or "storyboard"

    logger.info("=" * 60)
    logger.info("Database Initialization")
    logger.info("=" * 60)
    logger.info("MongoDB URL: %s", mongo_url)
    logger.info("Database: %s", db_name)
    logger.info("")

    client = AsyncIOMotorClient(mongo_url)
    try:
        await client.admin.command("ping")
        logger.info("✓ MongoDB connection successful")
    except Exception as exc:
        logger.critical("✗ Cannot connect to MongoDB at %s: %s", mongo_url, exc)
        raise SystemExit(2)

    db = client[db_name]

    logger.info("")
    logger.info("Verifying collections...")
    await verify_and_create_collections(db)

    logger.info("")
    await ensure_indexes(db)

    logger.info("")
    logger.info("=" * 60)
    logger.info("✓ Database initialization complete")
    logger.info("=" * 60)
    
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
