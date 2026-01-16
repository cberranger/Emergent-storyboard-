"""Database connection management with error handling and retry logic"""
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, PyMongoError
import asyncio
from typing import Optional, List

logger = logging.getLogger(__name__)


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


class DatabaseManager:
    """Manages MongoDB connection with retry logic and health checks"""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.mongo_url = self._get_mongo_url()
        self.db_name = os.environ.get('DB_NAME', 'storyboard')
        self.max_retries = 5
        self.retry_delay = 3  # seconds
        self._collections_validated = False

    def _get_mongo_url(self) -> str:
        """Get MongoDB URL from environment with validation"""
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')

        # Validate URL format
        if not mongo_url or not mongo_url.startswith(('mongodb://', 'mongodb+srv://')):
            logger.warning(f"Invalid MONGO_URL format: {mongo_url}, using default")
            mongo_url = 'mongodb://localhost:27017'

        return mongo_url

    async def connect(self) -> bool:
        """
        Connect to MongoDB with retry logic

        Returns:
            bool: True if connection successful, False otherwise
        """
        # Refresh configuration in case environment variables changed
        self.mongo_url = self._get_mongo_url()
        self.db_name = os.environ.get('DB_NAME', 'storyboard')
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempting to connect to MongoDB (attempt {attempt + 1}/{self.max_retries})")
                logger.info(f"MongoDB URL: {self.mongo_url.replace('mongodb://', 'mongodb://***@')}")

                # Create client with timeout
                self.client = AsyncIOMotorClient(
                    self.mongo_url,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                    socketTimeoutMS=10000,
                    retryWrites=True,
                    retryReads=True
                )

                # Test connection
                await self.client.admin.command('ping')

                # Set database
                self.db = self.client[self.db_name]

                logger.info(f"Successfully connected to MongoDB database: {self.db_name}")
                
                # Validate and create collections if needed
                if not self._collections_validated:
                    await self._validate_collections()
                    self._collections_validated = True
                
                return True

            except ServerSelectionTimeoutError as e:
                logger.error(f"MongoDB server selection timeout (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.critical("Failed to connect to MongoDB after all retries")

            except ConnectionFailure as e:
                logger.error(f"MongoDB connection failure (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.critical("Failed to connect to MongoDB after all retries")

            except Exception as e:
                logger.error(f"Unexpected error connecting to MongoDB: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.critical("Failed to connect to MongoDB due to unexpected error")

        return False

    async def health_check(self) -> bool:
        """
        Check if database connection is healthy

        Returns:
            bool: True if healthy, False otherwise
        """
        if self.client is None or self.db is None:
            logger.warning("Database connection not initialized")
            return False

        try:
            # Ping the database
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    async def _validate_collections(self) -> None:
        """Validate that all required collections exist and create missing ones"""
        try:
            existing_collections = set(await self.db.list_collection_names())
            missing_collections = set(REQUIRED_COLLECTIONS) - existing_collections
            
            if missing_collections:
                logger.warning(f"Missing collections detected: {', '.join(sorted(missing_collections))}")
                logger.info("Creating missing collections...")
                
                for col in sorted(missing_collections):
                    try:
                        await self.db.create_collection(col)
                        logger.info(f"Created collection: {col}")
                        
                        # Create indexes for newly created collections
                        await self._ensure_collection_indexes(col)
                        
                    except PyMongoError as e:
                        logger.error(f"Failed to create collection {col}: {e}")
                
                logger.info("Collection validation complete")
            else:
                logger.info("All required collections exist")
                
        except Exception as e:
            logger.error(f"Collection validation failed: {e}")

    async def _ensure_collection_indexes(self, collection_name: str) -> None:
        """Create indexes for a specific collection"""
        try:
            col = self.db[collection_name]
            
            # Core Collections
            if collection_name == "projects":
                await col.create_index([("id", ASCENDING)], unique=True)
                await col.create_index([("created_at", DESCENDING)])
            
            elif collection_name == "scenes":
                await col.create_index([("id", ASCENDING)], unique=True)
                await col.create_index([("project_id", ASCENDING), ("order", ASCENDING)])
                await col.create_index([("parent_scene_id", ASCENDING)])
                await col.create_index([("is_alternate", ASCENDING)])
            
            elif collection_name == "clips":
                await col.create_index([("id", ASCENDING)], unique=True)
                await col.create_index([("scene_id", ASCENDING), ("order", ASCENDING)])
                await col.create_index([("scene_id", ASCENDING), ("timeline_position", ASCENDING)])
            
            elif collection_name == "characters":
                await col.create_index([("id", ASCENDING)], unique=True)
                await col.create_index([("project_id", ASCENDING), ("name", ASCENDING)])
            
            elif collection_name == "style_templates":
                await col.create_index([("id", ASCENDING)], unique=True)
                await col.create_index([("project_id", ASCENDING), ("name", ASCENDING)])
            
            elif collection_name == "comfyui_servers":
                await col.create_index([("id", ASCENDING)], unique=True)
                await col.create_index([("url", ASCENDING)], unique=True)
                await col.create_index([("is_active", ASCENDING)])
            
            elif collection_name == "generation_batches":
                await col.create_index([("id", ASCENDING)], unique=True)
                await col.create_index([("project_id", ASCENDING), ("created_at", DESCENDING)])
                await col.create_index([("status", ASCENDING)])
            
            # FaceFusion Collections
            elif collection_name == "facefusion_jobs":
                await col.create_index([("id", ASCENDING)], unique=True)
                await col.create_index([("status", ASCENDING), ("priority", DESCENDING), ("created_at", ASCENDING)])
                await col.create_index([("character_id", ASCENDING)])
                await col.create_index([("project_id", ASCENDING), ("created_at", DESCENDING)])
            
            elif collection_name == "facefusion_presets":
                await col.create_index([("id", ASCENDING)], unique=True)
                await col.create_index([("name", ASCENDING)])
                await col.create_index([("operation_type", ASCENDING), ("is_public", ASCENDING)])
            
            # Model Management Collections
            elif collection_name == "database_models":
                await col.create_index([("id", ASCENDING)], unique=True)
                await col.create_index([("is_active", ASCENDING), ("type", ASCENDING)])
                await col.create_index([("base_model", ASCENDING), ("is_active", ASCENDING)])
            
            elif collection_name == "inference_configurations":
                await col.create_index([("model_id", ASCENDING), ("preset_type", ASCENDING)], unique=True)
            
            elif collection_name == "civitai_models":
                await col.create_index([("id", ASCENDING)], unique=True)
                await col.create_index([("type", ASCENDING), ("nsfw", ASCENDING)])
            
            # Authentication Collections
            elif collection_name == "users":
                await col.create_index([("id", ASCENDING)], unique=True)
                await col.create_index([("username", ASCENDING)], unique=True)
                await col.create_index([("email", ASCENDING)], unique=True)
            
            logger.info(f"Indexes created for collection: {collection_name}")
            
        except PyMongoError as e:
            logger.error(f"Failed to create indexes for {collection_name}: {e}")

    async def disconnect(self):
        """Close database connection gracefully"""
        if self.client:
            logger.info("Closing MongoDB connection")
            self.client.close()
            self.client = None
            self.db = None
            self._collections_validated = False

    def get_database(self):
        """
        Get database instance

        Returns:
            Database instance or None if not connected
        """
        if self.db is None:
            logger.error("Database not connected. Call connect() first.")
            return None
        return self.db


# Global database manager instance
db_manager = DatabaseManager()


async def get_database():
    """
    FastAPI dependency for database access

    Usage:
        @app.get("/items")
        async def get_items(db = Depends(get_database)):
            items = await db.items.find().to_list(100)
            return items
    """
    if db_manager.db is None:
        logger.error("Database not initialized. Attempting reconnection...")
        success = await db_manager.connect()
        if not success:
            raise ConnectionError("Database not available")

    return db_manager.db
