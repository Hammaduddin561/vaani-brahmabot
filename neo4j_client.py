# neo4j_client.py

import os
import logging
from dotenv import load_dotenv
try:
    from neo4j import AsyncGraphDatabase
    try:
        from neo4j.exceptions import Neo4jError, ServiceUnavailable, AuthError
    except ImportError:
        # Fallback for older neo4j versions
        from neo4j import Neo4jError, ServiceUnavailable, AuthError
except ImportError:
    # If neo4j is not available, create dummy classes
    class AsyncGraphDatabase:
        @staticmethod
        def driver(*args, **kwargs):
            return None
    
    class Neo4jError(Exception):
        pass
    
    class ServiceUnavailable(Exception):
        pass
    
    class AuthError(Exception):
        pass

# Load environment variables from .env file
load_dotenv(override=True)

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
)
logger.addHandler(handler)

# Read connection settings - using consistent env var names with .env file
URI      = os.getenv("NEO_URI", "bolt://localhost:7687")
USER     = os.getenv("NEO_USER")
PASSWORD = os.getenv("NEO_PASS")

if not USER or not PASSWORD:
    logger.warning("NEO_USER or NEO_PASS not set in environment; authentication may fail")

# Initialize the async driver
driver = AsyncGraphDatabase.driver(URI, auth=(USER, PASSWORD))


async def run_cypher(cypher: str, parameters: dict = None) -> list[dict]:
    """
    Executes a Cypher query against Neo4j and returns all records as a list of dicts.
    
    :param cypher: The Cypher query string.
    :param parameters: Optional dict of parameters to pass to the query.
    :return: List of result records, each as a dict.
    """
    logger.debug("Running Cypher:\n%s\nWith parameters: %s", cypher, parameters)
    try:
        async with driver.session() as session:
            result = await session.run(cypher, parameters or {})
            records = await result.data()
            logger.debug("Records returned: %s", records)
            return records

    except Neo4jError as err:
        logger.error("Neo4jError while running Cypher: %s", err)
        return []
    except Exception as e:
        logger.exception("Unexpected error in run_cypher: %s", e)
        return []


async def close_driver():
    """
    Gracefully close the Neo4j driver connection. Call this on application shutdown.
    """
    logger.info("Closing Neo4j driver")
    await driver.close()


class Neo4jClient:
    """Simple wrapper class for Neo4j operations"""
    
    def __init__(self):
        self.driver = driver
        logger.info("Neo4jClient initialized with driver")
    
    async def run_query(self, cypher: str, parameters: dict = None) -> list[dict]:
        """Run a cypher query and return results"""
        return await run_cypher(cypher, parameters)
    
    async def close(self):
        """Close the driver connection"""
        await close_driver()
    
    def is_connected(self) -> bool:
        """Check if driver is available"""
        return self.driver is not None