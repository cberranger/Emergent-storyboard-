
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
    except Exception as exc:  # best-effort
        logger.warning("Failed to read .env at %s: %s", env_path, exc)
    return values


async def ensure_indexes(db) -> None:
    async def ensure(col: str, keys: Any, **opts: Any) -> None:
        try:
            name = await db[col].create_index(keys, **opts)
            logger.info("Index ensured on %s: %s (%s)", col, keys, name)
        except PyMongoError as exc:
            logger.error("Failed index on %s %s: %s", col, keys, exc)

    # projects
    await ensure("projects", [("id", ASCENDING)], unique=True)
    await ensure("projects", [("created_at", DESCENDING)])

    # scenes
    await ensure("scenes", [("id", ASCENDING)], unique=True)
    await ensure("scenes", [("project_id", ASCENDING), ("order", ASCENDING)])
    await ensure("scenes", [("parent_scene_id", ASCENDING)])
    await ensure("scenes", [("is_alternate", ASCENDING)])

    # clips
    await ensure("clips", [("id", ASCENDING)], unique=True)
    await ensure("clips", [("scene_id", ASCENDING), ("order", ASCENDING)])
    await ensure("clips", [("scene_id", ASCENDING), ("timeline_position", ASCENDING)])

    # characters
    await ensure("characters", [("id", ASCENDING)], unique=True)
    await ensure("characters", [("project_id", ASCENDING), ("name", ASCENDING)])

    # style templates
    await ensure("style_templates", [("id", ASCENDING)], unique=True)
    await ensure("style_templates", [("project_id", ASCENDING), ("name", ASCENDING)])

    # comfyui servers
    await ensure("comfyui_servers", [("id", ASCENDING)], unique=True)
    await ensure("comfyui_servers", [("url", ASCENDING)], unique=True)

    # generation batches
    await ensure("generation_batches", [("id", ASCENDING)], unique=True)
    await ensure("generation_batches", [("project_id", ASCENDING), ("created_at", DESCENDING)])


async def main() -> None:
    # Prefer environment, fall back to backend/.env
    repo_root = Path(__file__).resolve().parents[2]
    backend_env = load_env_from_file(repo_root / "backend" / ".env")

    mongo_url = os.environ.get("MONGO_URL") or backend_env.get("MONGO_URL") or "mongodb://192.168.1.10:27017"
    db_name = os.environ.get("DB_NAME") or backend_env.get("DB_NAME") or "storyboard"

    logger.info("Connecting to MongoDB: %s", mongo_url)
    client = AsyncIOMotorClient(mongo_url)
    try:
        # ping
        await client.admin.command("ping")
    except Exception as exc:
        logger.critical("Cannot connect to MongoDB at %s: %s", mongo_url, exc)
        raise SystemExit(2)

    db = client[db_name]

    # Proactively create collections (optional; index creation also suffices)
    for col in [
        "projects",
        "scenes",
        "clips",
        "characters",
        "style_templates",
        "comfyui_servers",
        "generation_batches",
    ]:
        try:
            if col not in (await db.list_collection_names()):
                await db.create_collection(col)
                logger.info("Collection created: %s", col)
            else:
                logger.info("Collection exists: %s", col)
        except PyMongoError as exc:
            logger.warning("Skipping create for %s: %s", col, exc)

    await ensure_indexes(db)
    logger.info("Initialization complete for DB '%s'", db_name)


if __name__ == "__main__":
    asyncio.run(main())
