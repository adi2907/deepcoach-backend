# ============================================================================
# File: models/module_models.py
# Module models for the learning platform
# ============================================================================

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class ModuleStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class EvaluationType(str, Enum):
    CODING_EXERCISE = "coding_exercise"
    QUIZ = "quiz"
    PROJECT = "project"
    MIXED = "mixed"

class Module(BaseModel):
    id: str = Field(..., description="Unique identifier for the module")
    topic_id: str = Field(..., description="ID of the parent topic")
    name: str = Field(..., description="Name of the module")
    description: str = Field(..., description="Brief description of the module")
    estimated_hours: float = Field(..., description="Estimated time to complete in hours")
    learning_objectives: List[str] = Field(default=[], description="What learner will achieve")
    prerequisites: List[str] = Field(default=[], description="Prerequisites for this module")
    evaluation_type: EvaluationType = Field(..., description="Type of evaluation for this module")
    order: int = Field(..., description="Order within the topic")
    
class TopicWithModules(BaseModel):
    topic_id: str = Field(..., description="Topic identifier")
    topic_name: str = Field(..., description="Topic name")
    topic_description: str = Field(..., description="Topic description")
    modules: List[Module] = Field(..., description="List of modules for this topic")
    total_estimated_hours: float = Field(..., description="Total hours for all modules")
    
class ModuleGenerationRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    topic_id: str = Field(..., description="Topic ID to generate modules for")
    
class ModuleGenerationResponse(BaseModel):
    success: bool = Field(default=True)
    data: TopicWithModules = Field(..., description="Topic with generated modules")
    message: str = Field(default="Modules generated successfully")