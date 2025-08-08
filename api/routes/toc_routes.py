# ============================================================================
# File: api/routes/toc_routes.py
# API routes for TOC generation and learning path creation
# ============================================================================

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel, Field
import uuid
import logging

from generators.toc_generator import TOCGenerator
from services.learning_path_service import learning_path_service
from models.toc_models import TOCResponse, LearningPathResponse
from domains.data_science.prompts.toc_prompts import get_toc_prompt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/toc", tags=["Table of Contents"])

# Request models
class TOCRequest(BaseModel):
    domain: str = Field(..., description="Domain for curriculum (e.g., 'data_science')")
    user_preferences: Dict[str, Any] = Field(..., description="User preferences from onboarding")

class LearningPathRequest(BaseModel):
    session_id: str = Field(..., description="Session ID from TOC generation")
    user_id: str = Field(..., description="User identifier")
    selected_topic_ids: List[str] = Field(..., description="List of selected topic IDs")

class LearningPathUpdateRequest(BaseModel):
    session_id: str = Field(..., description="Session ID")
    selected_topic_ids: List[str] = Field(..., description="Updated list of selected topic IDs")

# Dependency to get TOC generator
def get_toc_generator() -> TOCGenerator:
    return TOCGenerator()

@router.post("/generate", response_model=TOCResponse)
async def generate_toc(
    request: TOCRequest,
    toc_generator: TOCGenerator = Depends(get_toc_generator)
):
    """
    Generate Table of Contents based on domain and user preferences
    """
    try:
        session_id = str(uuid.uuid4())
        
        logger.info(f"Generating TOC for domain: {request.domain}")
        logger.info(f"Session ID: {session_id}")
        
        # Get domain-specific prompt
        if request.domain == "data_science":
            domain_prompt = get_toc_prompt(request.user_preferences)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Domain '{request.domain}' not supported yet"
            )
        
        # Generate TOC
        toc = toc_generator.generate_toc(
            domain=request.domain,
            user_preferences=request.user_preferences,
            domain_prompt=domain_prompt
        )
        
        # Store TOC in learning path service
        learning_path_service.store_toc(session_id, toc)
        
        logger.info(f"Successfully generated TOC with {len(toc.topics)} topics")
        
        return TOCResponse(
            data=toc,
            message=f"TOC generated successfully for {request.domain}"
        )
        
    except Exception as e:
        logger.error(f"TOC generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TOC generation failed: {str(e)}")

@router.get("/session/{session_id}")
async def get_toc_by_session(session_id: str):
    """
    Retrieve TOC by session ID
    """
    try:
        toc = learning_path_service.get_toc(session_id)
        if not toc:
            raise HTTPException(status_code=404, detail="TOC not found")
        
        return TOCResponse(
            data=toc,
            message="TOC retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving TOC: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/learning-path", response_model=LearningPathResponse)
async def create_learning_path(request: LearningPathRequest):
    """
    Create learning path from selected topics
    """
    try:
        logger.info(f"Creating learning path for user {request.user_id}")
        logger.info(f"Selected topics: {request.selected_topic_ids}")
        
        learning_path = learning_path_service.create_learning_path(
            user_id=request.user_id,
            session_id=request.session_id,
            selected_topic_ids=request.selected_topic_ids
        )
        
        return LearningPathResponse(
            data=learning_path,
            message=f"Learning path created with {len(request.selected_topic_ids)} topics"
        )
        
    except ValueError as e:
        logger.error(f"Invalid learning path request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Learning path creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/learning-path", response_model=LearningPathResponse)
async def update_learning_path(request: LearningPathUpdateRequest):
    """
    Update existing learning path with new topic selection
    """
    try:
        logger.info(f"Updating learning path for session {request.session_id}")
        
        learning_path = learning_path_service.update_learning_path(
            session_id=request.session_id,
            selected_topic_ids=request.selected_topic_ids
        )
        
        return LearningPathResponse(
            data=learning_path,
            message=f"Learning path updated with {len(request.selected_topic_ids)} topics"
        )
        
    except ValueError as e:
        logger.error(f"Invalid learning path update: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Learning path update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning-path/{session_id}")
async def get_learning_path(session_id: str):
    """
    Get learning path by session ID
    """
    try:
        learning_path = learning_path_service.get_learning_path(session_id)
        if not learning_path:
            raise HTTPException(status_code=404, detail="Learning path not found")
        
        return LearningPathResponse(
            data=learning_path,
            message="Learning path retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving learning path: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/learning-paths")
async def get_user_learning_paths(user_id: str):
    """
    Get all learning paths for a user
    """
    try:
        learning_paths = learning_path_service.get_user_learning_paths(user_id)
        
        return {
            "success": True,
            "data": learning_paths,
            "count": len(learning_paths),
            "message": f"Retrieved {len(learning_paths)} learning paths"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving user learning paths: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/topic/{session_id}/{topic_id}")
async def get_topic_details(session_id: str, topic_id: str):
    """
    Get detailed information about a specific topic
    """
    try:
        topic_details = learning_path_service.get_topic_details(session_id, topic_id)
        if not topic_details:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        return {
            "success": True,
            "data": topic_details,
            "message": "Topic details retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving topic details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_toc_statistics():
    """
    Get TOC service statistics
    """
    try:
        stats = learning_path_service.get_statistics()
        return {
            "success": True,
            "data": stats,
            "message": "Statistics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))