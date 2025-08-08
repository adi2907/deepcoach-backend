# ============================================================================
# File: coach_service.py
# Enhanced coach service with personalization
# ============================================================================

from typing import Optional, List, Dict 
from backend.services.llm_service import LLMService
from prompts import COACH_HINT_PROMPT

class CoachService:
    def __init__(self, model: str = "openai/gpt-oss-20b:free"):
        self.llm = LLMService(model=model)
        self.motivation_messages = [
            "Great progress! You're {percent}% through this module!",
            "Keep going! Just {remaining} minutes left in this session.", 
            "Nice work! You've completed {count} exercises so far.",
            "You're doing great! Remember, every expert was once a beginner.",
            "Stuck? That's normal! Try breaking down the problem into smaller steps."
        ]
    
    def set_model(self, model: str):
        """Switch models for the coach service"""
        self.llm.set_model(model)

    def get_hint(self, exercise: Dict, user_code: str, attempt: int, 
                 student_context: Dict = None, error: Optional[str] = None) -> str:
        """Generate contextual hint using student background"""
        
        # Use student context if available, otherwise use defaults
        context = student_context or {
            'goal': 'general learning',
            'experience_level': 'beginner',
            'programming_skills': ['basic'],
            'math_background': ['high-school'],
            'time_spent': 0
        }
        
        prompt = COACH_HINT_PROMPT.format(
            goal=context.get('goal', 'general learning'),
            experience_level=context.get('experience_level', 'beginner'),
            programming_background=', '.join(context.get('programming_skills', [])) or 'basic',
            math_background=', '.join(context.get('math_background', [])) or 'high school level',
            exercise_title=exercise.get('title', ''),
            user_code=user_code,
            error=error or "No error",
            attempt=attempt,
            time_spent=context.get('time_spent', 0)
        )
        
        hint = self.llm.generate(
            "You are a supportive, personalized coding tutor. Adapt your teaching style to the student's background.",
            prompt,
            temperature=0.6
        )
        return hint
    
    def answer_question(self, question: str, context: Dict, student_context: Dict = None) -> str:
        """Answer conceptual questions with personalization"""
        
        student_info = ""
        if student_context:
            student_info = f"""
            Student Background:
            - Goal: {student_context.get('goal', 'general learning')}
            - Experience: {student_context.get('experience_level', 'beginner')}
            - Programming: {', '.join(student_context.get('programming_skills', [])) or 'basic'}
            """
        
        prompt = f"""
        {student_info}
        
        Current Context: {context.get('module_title', 'Unknown')}
        Student Question: {question}
        
        Provide a clear, personalized answer that:
        1. Matches their experience level
        2. References concepts they already know
        3. Connects to their learning goal
        4. Uses appropriate technical depth
        
        Keep it under 200 words and be encouraging.
        """
        
        answer = self.llm.generate(
            "You are a knowledgeable data science tutor who personalizes explanations.",
            prompt
        )
        return answer
    
    def get_motivation(self, progress: float, time_spent: int, exercises_done: int, 
                      student_context: Dict = None) -> str:
        """Generate motivational message with personalization"""
        
        goal = student_context.get('goal', 'learning') if student_context else 'learning'
        
        if progress < 0.3:
            return f"Great start on your {goal} journey! You're {int(progress*100)}% through this module."
        elif progress < 0.7:
            return f"Halfway there! You're making excellent progress toward your {goal} goal."
        elif progress < 0.9:
            return f"Almost done! Just a little more to master this concept for your {goal}."
        else:
            return f"Fantastic! You're about to complete this module. Your {goal} skills are growing!"
    
    def check_understanding(self, module_content: str, user_responses: List[str], 
                           student_context: Dict = None) -> Dict:
        """Personalized comprehension check"""
        
        context_info = ""
        if student_context:
            context_info = f"Student goal: {student_context.get('goal', 'learning')}, Experience: {student_context.get('experience_level', 'beginner')}"
        
        prompt = f"""
        {context_info}
        Module covered: {module_content[:500]}...
        Student responses to exercises: {user_responses}
        
        Based on their background and responses, assess:
        1. Understanding level (1-5) 
        2. Areas needing reinforcement
        3. Readiness for next concepts
        4. Personalized feedback for their goal
        
        Return JSON: {{"understanding": 1-5, "weak_areas": [], "feedback": "...", "next_recommendations": []}}
        """
        
        assessment = self.llm.generate_json(
            "Assess student understanding with personalized recommendations.",
            prompt
        )
        return assessment