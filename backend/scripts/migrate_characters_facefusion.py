#!/usr/bin/env python3
"""
Migration script to add FaceFusion fields to existing character documents.

This script updates all character documents that don't have FaceFusion fields
by adding the following:
- facefusion_processing_history (empty array)
- facefusion_preferred_settings (null)
- facefusion_output_gallery (empty gallery structure)

Usage:
    python migrate_characters_facefusion.py
"""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError


logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("migrate_characters")


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


async def migrate_characters(db) -> None:
    """Add FaceFusion fields to character documents that don't have them"""
    
    collection = db.characters
    
    # Find characters without FaceFusion fields
    query = {"facefusion_processing_history": {"$exists": False}}
    
    try:
        count = await collection.count_documents(query)
        
        if count == 0:
            logger.info("No characters need migration (all have FaceFusion fields)")
            return
        
        logger.info(f"Found {count} character(s) that need FaceFusion fields")
        
        # Update documents
        result = await collection.update_many(
            query,
            {
                "$set": {
                    "facefusion_processing_history": [],
                    "facefusion_preferred_settings": None,
                    "facefusion_output_gallery": {
                        "enhanced_faces": [],
                        "age_variants": {},
                        "swapped_faces": [],
                        "edited_expressions": [],
                        "custom_outputs": []
                    }
                }
            }
        )
        
        logger.info(f"✓ Successfully migrated {result.modified_count} character(s)")
        
        # Verify migration
        remaining = await collection.count_documents(query)
        if remaining > 0:
            logger.warning(f"Warning: {remaining} character(s) still need migration")
        else:
            logger.info("✓ All characters now have FaceFusion fields")
            
    except PyMongoError as exc:
        logger.error(f"Migration failed: {exc}")
        raise


async def verify_characters(db) -> None:
    """Verify character schema after migration"""
    
    collection = db.characters
    
    try:
        total = await collection.count_documents({})
        with_history = await collection.count_documents({"facefusion_processing_history": {"$exists": True}})
        with_settings = await collection.count_documents({"facefusion_preferred_settings": {"$exists": True}})
        with_gallery = await collection.count_documents({"facefusion_output_gallery": {"$exists": True}})
        
        logger.info("")
        logger.info("Migration Verification:")
        logger.info(f"  Total characters: {total}")
        logger.info(f"  With processing_history: {with_history}")
        logger.info(f"  With preferred_settings: {with_settings}")
        logger.info(f"  With output_gallery: {with_gallery}")
        
        if total == with_history == with_settings == with_gallery:
            logger.info("  ✓ All characters have complete FaceFusion schema")
        else:
            logger.warning("  ⚠ Some characters have incomplete FaceFusion schema")
            
    except PyMongoError as exc:
        logger.error(f"Verification failed: {exc}")


async def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    backend_env = load_env_from_file(repo_root / "backend" / ".env")

    mongo_url = os.environ.get("MONGO_URL") or backend_env.get("MONGO_URL") or "mongodb://192.168.1.10:27017"
    db_name = os.environ.get("DB_NAME") or backend_env.get("DB_NAME") or "storyboard"

    logger.info("=" * 60)
    logger.info("Character FaceFusion Migration")
    logger.info("=" * 60)
    logger.info(f"MongoDB URL: {mongo_url}")
    logger.info(f"Database: {db_name}")
    logger.info("")

    client = AsyncIOMotorClient(mongo_url)
    try:
        await client.admin.command("ping")
        logger.info("✓ MongoDB connection successful")
    except Exception as exc:
        logger.critical(f"✗ Cannot connect to MongoDB at {mongo_url}: {exc}")
        raise SystemExit(2)

    db = client[db_name]

    logger.info("")
    logger.info("Starting migration...")
    await migrate_characters(db)
    
    await verify_characters(db)

    logger.info("")
    logger.info("=" * 60)
    logger.info("✓ Migration complete")
    logger.info("=" * 60)
    
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
