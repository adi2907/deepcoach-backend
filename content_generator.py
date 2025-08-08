from typing import List, Dict
import uuid
from models import *
from backend.services.llm_service import LLMService
from prompts import *

class ContentGenerator:
    def __init__(self):
        self.llm = LLMService()
    
    def generate_course_structure(self, preferences: UserPreferences) -> Dict:
        """Generate complete course structure"""
        prompt = COURSE_STRUCTURE_PROMPT.format(
            topic=preferences.topic,
            level=preferences.learner_level,
            style=preferences.course_style,
            total_hours=preferences.total_hours,
            daily_minutes=preferences.daily_minutes
        )
        
        structure = self.llm.generate_json(
            "You are an expert curriculum designer for data science.",
            prompt
        )
        
        # Calculate number of sessions
        total_minutes = preferences.total_hours * 60
        sessions = total_minutes // preferences.daily_minutes
        
        print(f"Generated course with {len(structure['modules'])} modules for {sessions} sessions")
        return structure
    
    def generate_module_content(self, module: Dict, preferences: UserPreferences) -> Module:
        """Generate content for a single module"""
        # Calculate theory vs code percentages
        style_map = {
            CourseStyle.HANDS_ON: (20, 80),
            CourseStyle.BALANCED: (40, 60),
            CourseStyle.CONCEPT: (60, 40)
        }
        theory_percent, code_percent = style_map[preferences.course_style]
        
        prompt = MODULE_CONTENT_PROMPT.format(
            style=preferences.course_style,
            module_title=module['title'],
            topics=", ".join(module.get('topics', [])),
            objectives=", ".join(module.get('learning_objectives', [])),
            duration=module['estimated_minutes'],
            level=preferences.learner_level,
            theory_percent=theory_percent,
            code_percent=code_percent
        )
        
        content = self.llm.generate(
            "You are an expert data science instructor.",
            prompt
        )
        
        # Generate exercises for the module
        exercises = self.generate_exercises(
            module['title'], 
            preferences.learner_level
        )
        
        return Module(
            id=module['id'],
            title=module['title'],
            content=content,
            exercises=exercises,
            estimated_minutes=module['estimated_minutes'],
            order=module.get('order', 0)
        )
    
    def generate_exercises(self, topic: str, level: str, count: int = 2) -> List[Dict]:
        """Generate exercises for a topic"""
        exercises = []
        difficulty_map = {
            LearnerLevel.BEGINNER: ["easy", "easy"],
            LearnerLevel.INTERMEDIATE: ["easy", "medium"],
            LearnerLevel.ADVANCED: ["medium", "hard"]
        }
        
        for difficulty in difficulty_map.get(level, ["easy", "medium"]):
            prompt = EXERCISE_GENERATOR_PROMPT.format(
                topic=topic,
                difficulty=difficulty,
                focus_area="practical application"
            )
            
            exercise = self.llm.generate_json(
                "You are a coding exercise designer.",
                prompt
            )
            exercise['id'] = str(uuid.uuid4())[:8]
            exercises.append(exercise)
        
        return exercises
    
    def regenerate_exercise(self, topic: str, difficulty: str) -> Dict:
        """Generate a new exercise variant"""
        prompt = EXERCISE_GENERATOR_PROMPT.format(
            topic=topic,
            difficulty=difficulty,
            focus_area="different approach"
        )
        
        exercise = self.llm.generate_json(
            "Generate a NEW, different exercise. Don't repeat previous patterns.",
            prompt
        )
        exercise['id'] = str(uuid.uuid4())[:8]
        return exercise