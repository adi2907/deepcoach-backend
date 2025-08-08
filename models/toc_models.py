# ============================================================================
# File: models/toc_models.py
# Pydantic models for TOC and learning path structures
# ============================================================================

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class TopicType(str, Enum):
    THEORETICAL = "theoretical"
    PRACTICAL = "practical"
    MIXED = "mixed"

class SubTopic(BaseModel):
    id: str = Field(..., description="Unique identifier for the subtopic")
    name: str = Field(..., description="Name of the subtopic")
    description: str = Field(..., description="Brief description of what this subtopic covers")
    estimated_hours: float = Field(..., description="Estimated time to complete in hours")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level of this subtopic")
    prerequisites: List[str] = Field(default=[], description="List of prerequisite subtopic IDs")

class Topic(BaseModel):
    id: str = Field(..., description="Unique identifier for the topic")
    name: str = Field(..., description="Name of the topic")
    description: str = Field(..., description="Brief description of what this topic covers")
    estimated_hours: float = Field(..., description="Total estimated time for this topic in hours")
    difficulty: DifficultyLevel = Field(..., description="Overall difficulty level")
    topic_type: TopicType = Field(..., description="Type of topic (theoretical/practical/mixed)")
    subtopics: List[SubTopic] = Field(default=[], description="List of subtopics under this topic")
    prerequisites: List[str] = Field(default=[], description="List of prerequisite topic IDs")
    is_core: bool = Field(..., description="Whether this topic is core/essential for the domain")

class TableOfContents(BaseModel):
    domain: str = Field(..., description="The domain this TOC is for (e.g., 'data_science', 'cat_exam')")
    title: str = Field(..., description="Title of the course/curriculum")
    description: str = Field(..., description="Brief description of the overall curriculum")
    total_estimated_hours: float = Field(..., description="Total estimated time for all topics")
    topics: List[Topic] = Field(..., description="List of all topics in the curriculum")
    learning_path_suggestions: List[str] = Field(
        default=[], 
        description="Suggested topic IDs for different learning paths"
    )

class LearningPath(BaseModel):
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    domain: str = Field(..., description="Domain for this learning path")
    selected_topics: List[str] = Field(..., description="List of selected topic IDs")
    estimated_total_hours: float = Field(..., description="Total estimated hours for selected topics")
    created_at: str = Field(..., description="When this learning path was created")
    user_preferences: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="User preferences from onboarding"
    )

# Response models for API endpoints
class TOCResponse(BaseModel):
    success: bool = Field(default=True)
    data: TableOfContents = Field(..., description="Generated table of contents")
    message: str = Field(default="TOC generated successfully")

class LearningPathResponse(BaseModel):
    success: bool = Field(default=True)
    data: LearningPath = Field(..., description="Created learning path")
    message: str = Field(default="Learning path created successfully")