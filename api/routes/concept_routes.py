# ============================================================================
# File: api/routes/concept_routes.py
# API routes for concept generation and content management
# ============================================================================

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from generators.concept_generator import ConceptGenerator
from services.learning_path_service import learning_path_service
from models.concept_models import (
    ConceptGenerationRequest, ConceptGenerationResponse,
    ConceptContentRequest, ConceptContentResponse,
    ConceptNotesRequest, ConceptNotesResponse,
    ConceptNavigationResponse
)
from domains.data_science.prompts.concept_prompts import (
    get_concept_generation_prompt,
    get_concept_content_prompt,
    get_concept_notes_prompt
)
from domains.data_science.config import DataScienceConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/concepts", tags=["Concepts"])

# Dependency to get concept generator
def get_concept_generator() -> ConceptGenerator:
    return ConceptGenerator()

@router.post("/generate", response_model=ConceptGenerationResponse)
async def generate_concepts(
    request: ConceptGenerationRequest,
    concept_generator: ConceptGenerator = Depends(get_concept_generator)
):
    """
    Generate concepts for a specific module
    """
    try:
        logger.info(f"Generating concepts for module {request.module_id} in session {request.session_id}")
        
        # Get learning path and module data
        learning_path = learning_path_service.get_learning_path(request.session_id)
        if not learning_path:
            raise HTTPException(status_code=404, detail="Learning path not found")
        
        # Get module data from stored modules
        module_data = learning_path_service.get_module_data(request.session_id, request.module_id)
        if not module_data:
            raise HTTPException(status_code=404, detail="Module not found")
        
        # Check if concepts already exist
        existing_concepts = learning_path_service.get_module_concepts(request.session_id, request.module_id)
        if existing_concepts:
            logger.info(f"Concepts already exist for module {request.module_id}")
            return ConceptGenerationResponse(
                data=existing_concepts,
                message="Concepts already generated for this module"
            )
        
        # Get domain configuration
        toc = learning_path_service.get_toc(request.session_id)
        if toc.domain == "data_science":
            domain_config = DataScienceConfig.get_config()
            domain_prompt_fn = get_concept_generation_prompt
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Domain '{toc.domain}' not supported for concept generation"
            )
        
        # Generate concepts
        module_with_concepts = concept_generator.generate_concepts(
            module_data=module_data,
            user_preferences=learning_path.user_preferences or {},
            domain_prompt_fn=domain_prompt_fn,
            domain_config=domain_config
        )
        
        # Store generated concepts
        learning_path_service.store_module_concepts(request.session_id, module_with_concepts)
        
        logger.info(f"Successfully generated {len(module_with_concepts.concepts)} concepts for module {request.module_id}")
        
        return ConceptGenerationResponse(
            data=module_with_concepts,
            message=f"Generated {len(module_with_concepts.concepts)} concepts successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Concept generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Concept generation failed: {str(e)}")

@router.post("/content", response_model=ConceptContentResponse)
async def generate_concept_content(
    request: ConceptContentRequest,
    concept_generator: ConceptGenerator = Depends(get_concept_generator)
):
    """
    Generate detailed content for a specific concept
    """
    try:
        logger.info(f"Generating content for concept {request.concept_id}")
        
        # Get learning path and concept data
        learning_path = learning_path_service.get_learning_path(request.session_id)
        if not learning_path:
            raise HTTPException(status_code=404, detail="Learning path not found")
        
        concept_data, module_data = learning_path_service.get_concept_data(
            request.session_id, 
            request.concept_id
        )
        if not concept_data:
            raise HTTPException(status_code=404, detail="Concept not found")
        
        # Check if content already exists
        if concept_data.get('content_blocks') and len(concept_data['content_blocks']) > 0:
            logger.info(f"Content already exists for concept {request.concept_id}")
            from models.concept_models import Concept
            concept = Concept(**concept_data)
            return ConceptContentResponse(
                data=concept,
                message="Content already generated for this concept"
            )
        
        # Get domain configuration
        toc = learning_path_service.get_toc(request.session_id)
        if toc.domain == "data_science":
            domain_content_prompt_fn = get_concept_content_prompt
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Domain '{toc.domain}' not supported for content generation"
            )
        
        # Generate content
        concept = concept_generator.generate_concept_content(
            concept_data=concept_data,
            module_data=module_data,
            user_preferences=learning_path.user_preferences or {},
            domain_content_prompt_fn=domain_content_prompt_fn
        )
        
        # Store generated content
        learning_path_service.store_concept_content(request.session_id, concept)
        
        logger.info(f"Successfully generated content for concept {request.concept_id}")
        
        return ConceptContentResponse(
            data=concept,
            message="Content generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

@router.post("/notes", response_model=ConceptNotesResponse)
async def generate_concept_notes(
    request: ConceptNotesRequest,
    concept_generator: ConceptGenerator = Depends(get_concept_generator)
):
    """
    Generate study notes for a specific concept
    """
    try:
        logger.info(f"Generating notes for concept {request.concept_id}")
        
        # Get learning path and concept data
        learning_path = learning_path_service.get_learning_path(request.session_id)
        if not learning_path:
            raise HTTPException(status_code=404, detail="Learning path not found")
        
        concept_data, module_data = learning_path_service.get_concept_data(
            request.session_id, 
            request.concept_id
        )
        if not concept_data:
            raise HTTPException(status_code=404, detail="Concept not found")
        
        # Check if notes already exist
        if concept_data.get('notes_summary'):
            logger.info(f"Notes already exist for concept {request.concept_id}")
            return ConceptNotesResponse(
                data={"notes": concept_data['notes_summary']},
                message="Notes already generated for this concept"
            )
        
        # Get domain configuration
        toc = learning_path_service.get_toc(request.session_id)
        if toc.domain == "data_science":
            domain_notes_prompt_fn = get_concept_notes_prompt
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Domain '{toc.domain}' not supported for notes generation"
            )
        
        # Generate notes
        notes_content = concept_generator.generate_concept_notes(
            concept_data=concept_data,
            module_data=module_data,
            user_preferences=learning_path.user_preferences or {},
            domain_notes_prompt_fn=domain_notes_prompt_fn
        )
        
        # Store generated notes
        learning_path_service.store_concept_notes(request.session_id, request.concept_id, notes_content)
        
        logger.info(f"Successfully generated notes for concept {request.concept_id}")
        
        return ConceptNotesResponse(
            data={"notes": notes_content},
            message="Notes generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Notes generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Notes generation failed: {str(e)}")

@router.get("/session/{session_id}/module/{module_id}")
async def get_module_concepts(session_id: str, module_id: str):
    """
    Get all concepts for a specific module
    """
    try:
        module_concepts = learning_path_service.get_module_concepts(session_id, module_id)
        if not module_concepts:
            raise HTTPException(status_code=404, detail="Concepts not found for this module")
        
        return ConceptGenerationResponse(
            data=module_concepts,
            message="Module concepts retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving module concepts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/concept/{concept_id}")
async def get_concept_details(session_id: str, concept_id: str):
    """
    Get detailed information about a specific concept
    """
    try:
        concept_data, module_data = learning_path_service.get_concept_data(session_id, concept_id)
        if not concept_data:
            raise HTTPException(status_code=404, detail="Concept not found")
        
        from models.concept_models import Concept
        concept = Concept(**concept_data)
        
        return ConceptContentResponse(
            data=concept,
            message="Concept details retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving concept details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/{session_id}/concept/{concept_id}/progress")
async def update_concept_progress(session_id: str, concept_id: str, status: str):
    """
    Update progress status for a concept
    """
    try:
        # Validate status
        from models.concept_models import ConceptStatus
        valid_statuses = [status.value for status in ConceptStatus]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        # Update progress
        learning_path_service.update_concept_progress(session_id, concept_id, status)
        
        return {
            "success": True,
            "message": f"Concept progress updated to {status}",
            "data": {
                "concept_id": concept_id,
                "status": status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating concept progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/navigation")
async def get_concept_navigation(session_id: str):
    """
    Get complete navigation data including concepts
    """
    try:
        navigation_data = learning_path_service.get_learning_path_with_concepts(session_id)
        if not navigation_data:
            raise HTTPException(status_code=404, detail="Learning path not found")
        
        return ConceptNavigationResponse(
            data=navigation_data,
            message="Concept navigation data retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving concept navigation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))