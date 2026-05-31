from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
from jose import JWTError, jwt
from typing import Optional

from config import settings
from routers import auth, haiku, profile, feed, resonance, admin
from db.database import init_supabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Hyphen API",
    description="A haiku-based social platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (allow frontend and local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:5174",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600
)

# Auth middleware — validate Supabase JWT on protected routes
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Extract and validate JWT token from Authorization header."""
    # Skip auth for health check and docs
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    # Skip auth for public routes (auth endpoints)
    if request.url.path.startswith("/api/auth/"):
        return await call_next(request)
    
    # All other routes require authentication
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "Missing authorization header",
                "code": "MISSING_AUTH_HEADER"
            }
        )
    
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "Invalid authorization scheme",
                    "code": "INVALID_SCHEME"
                }
            )
        
        # For development, accept any token
        # In production, verify against Supabase's public key
        # For now, just extract the user_id from the token
        # Supabase JWT contains: {"sub": "<user_id>", ...}
        
        if settings.environment == "production":
            # Verify JWT signature against Supabase public key
            # This is a placeholder — implement with Supabase SDK
            try:
                payload = jwt.decode(
                    token,
                    settings.jwt_secret,
                    algorithms=["HS256"]
                )
                user_id = payload.get("sub")
            except JWTError as e:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": "Invalid token",
                        "code": "INVALID_TOKEN"
                    }
                )
        else:
            # Development: extract user_id from token (basic JWT decode)
            try:
                # Try to decode without verification in dev
                payload = jwt.get_unverified_claims(token)
                user_id = payload.get("sub")
            except Exception:
                # Fallback: treat token as user_id (for testing)
                user_id = token
        
        if not user_id:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "Token missing user ID",
                    "code": "INVALID_TOKEN"
                }
            )
        
        # Store user_id in request state for downstream handlers
        request.state.user_id = user_id
        request.state.token = token
        
    except ValueError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "Malformed authorization header",
                "code": "MALFORMED_AUTH"
            }
        )
    
    return await call_next(request)

# Initialize database on startup
@app.on_event("startup")
async def startup():
    logger.info("Starting Hyphen API...")
    logger.info(f"Environment: {settings.environment}")
    try:
        init_supabase()
        logger.info("Supabase client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase: {e}")
        # Don't fail startup, allow graceful degradation

@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down Hyphen API...")

# Health check
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "environment": settings.environment,
        "version": "0.1.0"
    }

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(haiku.router, prefix="/api/haiku", tags=["haiku"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(feed.router, prefix="/api/feed", tags=["feed"])
app.include_router(resonance.router, prefix="/api/resonance", tags=["resonance"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    errors = exc.errors()
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "code": "VALIDATION_ERROR",
            "details": [
                {
                    "field": ".".join(str(x) for x in error["loc"][1:]),
                    "message": error["msg"]
                }
                for error in errors
            ]
        }
    )

# Global error handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "code": f"HTTP_{exc.status_code}"
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "code": "INTERNAL_ERROR"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="info")
