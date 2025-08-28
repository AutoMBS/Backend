"""
Medical Benefits Schedule (MBS) API Server
==========================================

This is the main FastAPI application entry point that provides:
- Medical categories data access via RulebookService
- RAG-based medical code suggestions via RAGService
- RESTful API endpoints for medical billing and coding
- LLM-based complexity extraction via LLMExtractService

Architecture:
- FastAPI web framework with async support
- SQLite database for medical categories data
- Qdrant vector database for semantic search
- Modular service architecture with dependency injection
- Vertex AI Endpoint for LLM inference

Author: Medical Coding Team
Version: 2.0.0
Last Updated: 2025-08-28
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import services using relative imports
from .rag_service import RAGService
from .rulebook_service import RulebookService
from .llm_extract_service import LLMExtractService
from .routers import rag, rulebook, llm_extract


# =============================================================================
# APPLICATION LIFECYCLE MANAGEMENT
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events for the FastAPI application.
    Initializes core services and ensures proper cleanup.
    
    Args:
        app: FastAPI application instance
    
    Yields:
        None: Application runs during yield
        
    Raises:
        Exception: If service initialization fails
    """
    # Startup: Initialize core services
    print("🚀 Starting MBS API Server...")
    
    try:
        # Initialize RAG service for semantic search capabilities
        app.state.rag = RAGService()
        print("✅ RAG Service initialized successfully")
        
        # Initialize Rulebook service for medical categories data
        app.state.rulebook = RulebookService()
        print("✅ Rulebook Service initialized successfully")
        
        app.state.llm_extract = LLMExtractService()
        print("✅ LLM Extract Service initialized successfully")

        print("🎯 All services initialized successfully")
        
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        raise
    
    yield  # Application runs here
    
    # Shutdown: Cleanup resources
    print("🛑 Shutting down MBS API Server...")
    print("✅ Cleanup completed")


# =============================================================================
# FASTAPI APPLICATION INSTANCE
# =============================================================================

# Create FastAPI application with metadata and lifespan management
app = FastAPI(
    title="Medical Benefits Schedule (MBS) API",
    description="""
    Comprehensive API for Medical Benefits Schedule data access and RAG-based code suggestions.
    
    ## Features
    - **Rulebook API**: Access to medical categories, billing codes, and filtering
    - **RAG API**: AI-powered medical code suggestions using semantic search
    - **Health Monitoring**: Service health checks and database connectivity
    - **Flexible Filtering**: Age, time, and provider-based filtering
    
    ## Use Cases
    - Medical billing and coding
    - Healthcare provider lookup
    - Insurance claim processing
    - Medical service categorization
    """,
    version="2.0.0",
    contact={
        "name": "Medical Coding Team",
        "email": "coding@medical.org"
    },
    license_info={
        "name": "Medical Use Only",
        "url": "https://medical.org/license"
    },
    lifespan=lifespan
)


# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================

# Configure CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# ROUTER REGISTRATION
# =============================================================================

# Include rulebook router for medical categories and data access
app.include_router(
    rulebook.router,
    prefix="/rulebook",
    tags=["rulebook"]
)

# Include RAG router for AI-powered item claim suggestions
app.include_router(
    rag.router,
    prefix="/MBS",
    tags=["RAG"]
)

# LLM Extract: complexity prediction
app.include_router(
    llm_extract.router,
    prefix="/llm",
    tags=["LLM Extract"]
)

# =============================================================================
# ROOT ENDPOINT
# =============================================================================

@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint providing API overview and navigation.
    
    Returns:
        dict: API information and available endpoints
        
    Example:
        GET / -> Returns API overview
    """
    return {
        "message": "Medical Benefits Schedule (MBS) API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "rulebook": "/rulebook",
            "rag": "/code",
            "llm_extract": "/llm",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "description": "Comprehensive API for medical billing and coding assistance"
    }


# =============================================================================
# DIRECT EXECUTION SUPPORT
# =============================================================================

if __name__ == "__main__":
    """
    Direct execution entry point for development and testing.
    
    This block allows the application to be run directly using:
    python main.py
    
    For production deployment, use uvicorn:
    uvicorn main:app --host 0.0.0.0 --port 8000
    """
    import uvicorn
    
    print("🚀 Starting MBS API Server in development mode...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
