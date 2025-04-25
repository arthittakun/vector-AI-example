from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat_routes, vector_routes
import os

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="AI Chat API",
        description="AI Chat API with Vector DB support",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(chat_routes.router, prefix="/api/chat", tags=["Chat"])
    app.include_router(vector_routes.router, prefix="/api/vector", tags=["Vector DB"])

    return app

# Create WSGI application
app = create_app()

# Entry point for running the application
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Get environment mode
    env = os.environ.get("ENV", "development")
    debug = env == "development"
    
    # Configure uvicorn
    config = {
        "app": "app:app",
        "host": "0.0.0.0",
        "port": port,
        "reload": debug,
        "workers": 1 if debug else None,  # Auto workers in production
        "access_log": True,
        "log_level": "debug" if debug else "info"
    }
    
    print(f"Starting server in {env} mode")
    uvicorn.run(**config)
