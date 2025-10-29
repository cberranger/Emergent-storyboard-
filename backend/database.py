"""Database connection management with error handling and retry logic"""
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages MongoDB connection with retry logic and health checks"""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.mongo_url = self._get_mongo_url()
        self.db_name = os.environ.get('DB_NAME', 'storyboard')
        self.max_retries = 5
        self.retry_delay = 3  # seconds

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

    async def disconnect(self):
        """Close database connection gracefully"""
        if self.client:
            logger.info("Closing MongoDB connection")
            self.client.close()
            self.client = None
            self.db = None

    def get_database(self):
        """
        Get database instance

        Returns:
            Database instance or None if not connected
        """
        if not self.db:
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
    if not db_manager.db:
        logger.error("Database not initialized. Attempting reconnection...")
        success = await db_manager.connect()
        if not success:
            raise ConnectionError("Database not available")

    return db_manager.db
