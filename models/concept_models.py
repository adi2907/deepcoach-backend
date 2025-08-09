# ============================================================================
# File: models/concept_models.py
# Enhanced models for concept-level content generation
# ============================================================================

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from models.module_models import EvaluationType

class ConceptStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class ContentBlock(BaseModel):
    id: str = Field(..., description="Unique identifier for the content block")
    type: str = Field(..., description="Type of content block (text, code, exercise, etc.)")
    content: str = Field(..., description="Markdown content for the block")
    order: int = Field(..., description="Order within the concept")
    estimated_minutes: float = Field(default=2.0, description="Time to complete this block")

class Concept(BaseModel):
    id: str = Field(..., description="Unique identifier for the concept")
    module_id: str = Field(..., description="ID of the parent module")
    name: str = Field(..., description="Name of the concept")
    description: str = Field(..., description="Brief description of the concept")
    estimated_minutes: float = Field(..., description="Estimated time to complete in minutes")
    learning_objectives: List[str] = Field(default=[], description="What learner will achieve")
    content_blocks: List[ContentBlock] = Field(default=[], description="Content blocks for this concept")
    evaluation_type: Optional[EvaluationType] = Field(None, description="Type of evaluation")
    evaluation_content: Optional[str] = Field(None, description="Evaluation questions/exercises")
    notes_summary: Optional[str] = Field(None, description="Key points and formulas")
    order: int = Field(..., description="Order within the module")
    status: ConceptStatus = Field(default=ConceptStatus.NOT_STARTED, description="Completion status")

class ModuleWithConcepts(BaseModel):
    module_id: str = Field(..., description="Module identifier")
    module_name: str = Field(..., description="Module name")
    module_description: str = Field(..., description="Module description")
    topic_id: str = Field(..., description="Parent topic ID")
    concepts: List[Concept] = Field(..., description="List of concepts for this module")
    total_estimated_minutes: float = Field(..., description="Total time for all concepts")
    current_concept_id: Optional[str] = Field(None, description="Currently active concept")

class ConceptGenerationRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    module_id: str = Field(..., description="Module ID to generate concepts for")

class ConceptGenerationResponse(BaseModel):
    success: bool = Field(default=True)
    data: ModuleWithConcepts = Field(..., description="Module with generated concepts")
    message: str = Field(default="Concepts generated successfully")

class ConceptContentRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    concept_id: str = Field(..., description="Concept ID to get content for")

class ConceptContentResponse(BaseModel):
    success: bool = Field(default=True)
    data: Concept = Field(..., description="Concept with full content")
    message: str = Field(default="Concept content retrieved successfully")

class ConceptNotesRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    concept_id: str = Field(..., description="Concept ID to generate notes for")

class ConceptNotesResponse(BaseModel):
    success: bool = Field(default=True)
    data: Dict[str, str] = Field(..., description="Generated notes content")
    message: str = Field(default="Notes generated successfully")

class ConceptNavigationResponse(BaseModel):
    success: bool = Field(default=True)
    data: Dict[str, Any] = Field(..., description="Navigation data with concepts")
    message: str = Field(default="Navigation data retrieved successfully")