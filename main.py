# ============================================================================
# File: main.py (MINIMAL CHANGES)
# Updated FastAPI app with concept generation routes added
# ============================================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from dotenv import load_dotenv

# Import route modules
from api.routes.toc_routes import router as toc_router
from api.routes.module_routes import router as module_router
from api.routes.concept_routes import router as concept_router  # NEW: Added concept routes

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Learning Platform API",
    description="Modular learning platform with domain-specific curriculum generation",
    version="4.0.0"  # UPDATED: Version bump
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(toc_router)
app.include_router(module_router)
app.include_router(concept_router)  # NEW: Added concept router

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Learning Platform API v4.0",  # UPDATED: Version
        "features": [
            "Modular TOC generation",
            "Domain-specific prompts", 
            "Structured LLM output",
            "Learning path management",
            "Module generation with navigation",
            "Concept-level content generation",  # NEW: Added concept feature
            "Tabbed content interface",  # NEW: Added tabbed interface
            "Coach sidebar with concept tracking"  # UPDATED: Enhanced coach sidebar
        ]
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    
    # Check if OpenRouter API key is configured
    api_key = os.getenv("OPENROUTER_API_KEY")
    api_configured = bool(api_key and api_key != "your-key-here")
    
    return {
        "status": "healthy",
        "version": "4.0.0",  # UPDATED: Version
        "api_configured": api_configured,
        "features": {
            "toc_generation": True,
            "learning_path_management": True,
            "structured_output": True,
            "domain_prompts": True,
            "module_generation": True,
            "concept_generation": True,  # NEW: Added concept generation
            "content_blocks": True,  # NEW: Added content blocks
            "notes_generation": True,  # NEW: Added notes generation
            "navigation_system": True,
            "coach_sidebar": True,
            "tabbed_interface": True  # NEW: Added tabbed interface
        }
    }

@app.get("/api/domains")
async def get_supported_domains():
    """Get list of supported domains"""
    return {
        "success": True,
        "data": {
            "supported_domains": [
                {
                    "id": "data_science",
                    "name": "Data Science",
                    "description": "Comprehensive data science curriculum with ML, statistics, and programming",
                    "status": "active",
                    "features": {
                        "toc_generation": True,
                        "module_generation": True,
                        "concept_generation": True,  # NEW: Added concept generation
                        "content_generation": True,  # NEW: Added content generation
                        "notes_generation": True,  # NEW: Added notes generation
                        "navigation_hierarchy": ["topic", "module", "concept"],  # UPDATED: Added concept level
                        "evaluation_types": ["coding_exercise", "quiz", "mixed"],
                        "content_types": ["markdown_lessons", "code_examples", "interactive_exercises"]  # NEW: Added content types
                    }
                }
            ],
            "coming_soon": [
                {
                    "id": "cat_exam", 
                    "name": "CAT Exam Preparation",
                    "description": "Quantitative Aptitude, Verbal Ability, and Logical Reasoning",
                    "status": "development",
                    "features": {
                        "toc_generation": "planned",
                        "module_generation": "planned",
                        "concept_generation": "planned",  # NEW: Added concept generation
                        "navigation_hierarchy": ["topic", "module", "concept", "sub_concept"],
                        "evaluation_types": ["mcq", "timed_test"]
                    }
                }
            ]
        },
        "message": "Supported domains retrieved successfully"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return HTTPException(
        status_code=500,
        detail=f"Internal server error: {str(exc)}"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",  # Import string instead of app object
        host="0.0.0.0", 
        port=8000, 
        log_level="info",
        reload=True  # Enable auto-reload during development
    )