# ============================================================================
# File: models.py (NEW FILE)
# Enhanced Pydantic models for onboarding data
# ============================================================================

from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from enum import Enum

class LearnerLevel(str, Enum):
    COMPLETE_BEGINNER = "complete-beginner"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class CourseStyle(str, Enum):
    HANDS_ON = "hands-on"
    BALANCED = "balanced"
    CONCEPT_HEAVY = "concept-heavy"

class TotalTime(str, Enum):
    FOUR_HOURS = "4-hours"
    ONE_TWO_WEEKS = "1-2-weeks"
    ONE_MONTH = "1-month"
    TWO_THREE_MONTHS = "2-3-months"

class DailyTime(str, Enum):
    THIRTY_MIN = "30-min"
    ONE_HOUR = "1-hour"
    TWO_THREE_HOURS = "2-3-hours"

class TechnicalBackground(BaseModel):
    programming: List[str] = []
    math: List[str] = []
    domain: List[str] = []

class OnboardingData(BaseModel):
    goal: Optional[str] = None
    learner_level_detailed: Optional[LearnerLevel] = None
    course_material_detailed: Optional[CourseStyle] = None
    total_time_detailed: Optional[TotalTime] = None
    daily_time_detailed: Optional[DailyTime] = None
    technical_background: Optional[TechnicalBackground] = None