"""Database connection and initialization."""
import logging
from supabase import create_client, Client
from config import settings

logger = logging.getLogger(__name__)

supabase_client: Client = None

def init_supabase() -> Client:
    """Initialize Supabase client."""
    global supabase_client
    if supabase_client is None:
        supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )
        logger.info("Supabase client initialized")
    return supabase_client

def get_supabase() -> Client:
    """Get Supabase client."""
    if supabase_client is None:
        return init_supabase()
    return supabase_client

async def init_db():
    """Initialize database (run migrations, etc.)."""
    logger.info("Initializing database...")
    # Migrations will be run here
    pass
