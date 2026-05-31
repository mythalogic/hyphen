import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/hyphen")
    
    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # JWT
    jwt_secret: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    
    # Anthropic
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Cloudflare R2
    cloudflare_r2_bucket: str = os.getenv("CLOUDFLARE_R2_BUCKET", "")
    cloudflare_r2_endpoint: str = os.getenv("CLOUDFLARE_R2_ENDPOINT", "")
    cloudflare_r2_access_key: str = os.getenv("CLOUDFLARE_R2_ACCESS_KEY", "")
    cloudflare_r2_secret_key: str = os.getenv("CLOUDFLARE_R2_SECRET_KEY", "")
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    class Config:
        env_file = ".env"

settings = Settings()
