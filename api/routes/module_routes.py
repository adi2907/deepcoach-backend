# ============================================================================
# File: api/routes/module_routes.py
# API routes for module generation and management
# ============================================================================

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from generators.module_generator import ModuleGenerator
from services.learning_path_service import learning_path_service
from models.module_models import ModuleGenerationRequest, ModuleGenerationResponse
from domains.data_science.prompts.module_prompts import get_module_prompt
from domains.data_science.config import DataScienceConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/modules", tags=["Modules"])

# Dependency to get module generator
def get_module_generator() -> ModuleGenerator:
    return ModuleGenerator()

@router.post("/generate", response_model=ModuleGenerationResponse)
async def generate_modules(
    request: ModuleGenerationRequest,
    module_generator: ModuleGenerator = Depends(get_module_generator)
):
    """
    Generate modules for a specific topic
    """
    try:
        logger.info(f"Generating modules for topic {request.topic_id} in session {request.session_id}")
        
        # Get learning path and TOC data
        learning_path = learning_path_service.get_learning_path(request.session_id)
        if not learning_path:
            raise HTTPException(status_code=404, detail="Learning path not found")
        
        toc = learning_path_service.get_toc(request.session_id)
        if not toc:
            raise HTTPException(status_code=404, detail="TOC not found")
        
        # Validate topic ID is in learning path
        if request.topic_id not in learning_path.selected_topics:
            raise HTTPException(status_code=400, detail="Topic not in learning path")
        
        # Find topic data in TOC
        topic_data = None
        for topic in toc.topics:
            if topic.id == request.topic_id:
                topic_data = topic.dict()
                break
        
        if not topic_data:
            raise HTTPException(status_code=404, detail="Topic not found in TOC")
        
        # Check if modules already exist
        existing_modules = learning_path_service.get_topic_modules(request.session_id, request.topic_id)
        if existing_modules:
            logger.info(f"Modules already exist for topic {request.topic_id}")
            return ModuleGenerationResponse(
                data=existing_modules,
                message="Modules already generated for this topic"
            )
        
        # Get domain configuration
        if toc.domain == "data_science":
            domain_config = DataScienceConfig.get_config()
            domain_prompt_fn = get_module_prompt
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Domain '{toc.domain}' not supported for module generation"
            )
        
        # Generate modules
        topic_with_modules = module_generator.generate_modules(
            topic_data=topic_data,
            user_preferences=learning_path.user_preferences or {},
            domain_prompt_fn=domain_prompt_fn,
            domain_config=domain_config
        )
        
        # Store generated modules
        learning_path_service.store_topic_modules(request.session_id, topic_with_modules)
        
        logger.info(f"Successfully generated {len(topic_with_modules.modules)} modules for topic {request.topic_id}")
        
        return ModuleGenerationResponse(
            data=topic_with_modules,
            message=f"Generated {len(topic_with_modules.modules)} modules successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Module generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Module generation failed: {str(e)}")

@router.get("/session/{session_id}/topic/{topic_id}")
async def get_topic_modules(session_id: str, topic_id: str):
    """
    Get modules for a specific topic
    """
    try:
        topic_modules = learning_path_service.get_topic_modules(session_id, topic_id)
        if not topic_modules:
            raise HTTPException(status_code=404, detail="Modules not found for this topic")
        
        return ModuleGenerationResponse(
            data=topic_modules,
            message="Modules retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving modules: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}")
async def get_all_session_modules(session_id: str):
    """
    Get all generated modules for a session
    """
    try:
        all_modules = learning_path_service.get_all_session_modules(session_id)
        
        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "topics": all_modules,
                "total_topics_with_modules": len(all_modules)
            },
            "message": f"Retrieved modules for {len(all_modules)} topics"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving session modules: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/{session_id}/select")
async def update_current_selection(session_id: str, topic_id: str, module_id: str = None):
    """
    Update the current topic and module selection
    """
    try:
        # Validate session exists
        learning_path = learning_path_service.get_learning_path(session_id)
        if not learning_path:
            raise HTTPException(status_code=404, detail="Learning path not found")
        
        # Validate topic is in learning path
        if topic_id not in learning_path.selected_topics:
            raise HTTPException(status_code=400, detail="Topic not in learning path")
        
        # If module_id provided, validate it exists
        if module_id:
            topic_modules = learning_path_service.get_topic_modules(session_id, topic_id)
            if not topic_modules:
                raise HTTPException(status_code=404, detail="No modules found for this topic")
            
            module_exists = any(module.id == module_id for module in topic_modules.modules)
            if not module_exists:
                raise HTTPException(status_code=400, detail="Module not found in topic")
        
        # Update selection
        learning_path_service.set_current_selection(session_id, topic_id, module_id)
        
        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "current_topic_id": topic_id,
                "current_module_id": module_id
            },
            "message": "Selection updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating selection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/current")
async def get_current_selection(session_id: str):
    """
    Get current topic and module selection
    """
    try:
        current_selection = learning_path_service.get_current_selection(session_id)
        
        return {
            "success": True,
            "data": current_selection,
            "message": "Current selection retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving current selection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/navigation")
async def get_navigation_data(session_id: str):
    """
    Get complete navigation data for the learning path
    """
    try:
        navigation_data = learning_path_service.get_learning_path_with_modules(session_id)
        if not navigation_data:
            raise HTTPException(status_code=404, detail="Learning path not found")
        
        return {
            "success": True,
            "data": navigation_data,
            "message": "Navigation data retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving navigation data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))