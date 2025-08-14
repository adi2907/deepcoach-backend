# ============================================================================
# File: main.py (UPDATED)
# Updated FastAPI app with onboarding question generation routes
# ============================================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from dotenv import load_dotenv

# Import route modules
from api.routes.toc_routes import router as toc_router
from api.routes.module_routes import router as module_router
from api.routes.concept_routes import router as concept_router
from api.routes.onboarding_routes import router as onboarding_router  # NEW: Added onboarding routes

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
    version="4.1.0"  # UPDATED: Version bump for onboarding
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", 
                   "http://127.0.0.1:3000",
                   "https://deepcoach.vercel.app",
                   "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(toc_router)
app.include_router(module_router)
app.include_router(concept_router)
app.include_router(onboarding_router)  # NEW: Added onboarding router

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Learning Platform API v4.1",  # UPDATED: Version
        "features": [
            "Modular TOC generation",
            "Domain-specific prompts", 
            "Structured LLM output",
            "Learning path management",
            "Module generation with navigation",
            "Concept-level content generation",
            "Tabbed content interface",
            "Coach sidebar with concept tracking",
            "Generic onboarding with LLM question generation"  # NEW: Added onboarding feature
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
        "version": "4.1.0",  # UPDATED: Version
        "api_configured": api_configured,
        "features": {
            "toc_generation": True,
            "learning_path_management": True,
            "structured_output": True,
            "domain_prompts": True,
            "module_generation": True,
            "concept_generation": True,
            "content_blocks": True,
            "notes_generation": True,
            "navigation_system": True,
            "coach_sidebar": True,
            "tabbed_interface": True,
            "generic_onboarding": True,  # NEW: Added generic onboarding
            "question_generation": True  # NEW: Added question generation
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
                    "id": "generic",  # NEW: Added generic domain
                    "name": "Any Topic",
                    "description": "AI-generated curriculum for any learning topic",
                    "status": "active",
                    "features": {
                        "toc_generation": True,
                        "module_generation": True,
                        "concept_generation": True,
                        "content_generation": True,
                        "notes_generation": True,
                        "question_generation": True,  # NEW: Added question generation
                        "navigation_hierarchy": ["topic", "module", "concept"],
                        "evaluation_types": ["coding_exercise", "quiz", "mixed"],
                        "content_types": ["markdown_lessons", "code_examples", "interactive_exercises"]
                    }
                },
                {
                    "id": "data_science",
                    "name": "Data Science",
                    "description": "Comprehensive data science curriculum with ML, statistics, and programming",
                    "status": "active",
                    "features": {
                        "toc_generation": True,
                        "module_generation": True,
                        "concept_generation": True,
                        "content_generation": True,
                        "notes_generation": True,
                        "navigation_hierarchy": ["topic", "module", "concept"],
                        "evaluation_types": ["coding_exercise", "quiz", "mixed"],
                        "content_types": ["markdown_lessons", "code_examples", "interactive_exercises"]
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
                        "concept_generation": "planned",
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
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",  # Import string instead of app object
        host="0.0.0.0", 
        port=port, 
        log_level="info",
        reload=True  # Enable auto-reload during development
    )