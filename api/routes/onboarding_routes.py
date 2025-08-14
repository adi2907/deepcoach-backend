# ============================================================================
# File: api/routes/onboarding_routes.py
# API routes for generic onboarding question generation
# ============================================================================

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel, Field
import logging
import json

from services.llm_service import LLMService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/onboarding", tags=["Onboarding"])

class QuestionGenerationRequest(BaseModel):
    learning_topic: str = Field(..., description="What the user wants to learn")
    daily_time: str = Field(..., description="Daily time commitment (e.g., '30min')")
    total_duration: str = Field(..., description="Total duration (e.g., '2weeks')")

class QuestionOption(BaseModel):
    value: str = Field(..., description="Option value")
    label: str = Field(..., description="Option display text")

class Question(BaseModel):
    id: str = Field(..., description="Unique question identifier")
    question: str = Field(..., description="Question text")
    type: str = Field(..., description="Question type: 'single_choice' or 'multiple_choice'")
    options: List[QuestionOption] = Field(..., description="Available answer options")

class QuestionGenerationResponse(BaseModel):
    success: bool = Field(default=True)
    questions: List[Question] = Field(..., description="Generated personalization questions")
    message: str = Field(default="Questions generated successfully")

def get_question_generation_prompt(learning_topic: str, daily_time: str, total_duration: str) -> str:
    """Generate prompt for LLM to create personalized questions"""
    
    return f"""
You are an expert curriculum designer. Generate exactly 4 personalized questions to help create the best learning experience for someone who wants to learn: "{learning_topic}"

Time commitment: {daily_time} daily for {total_duration}

Create questions that help determine:
1. Their current experience level with this topic
2. Their preferred learning style (hands-on vs theory)
3. Their specific goals or applications they're interested in
4. Their technical background relevant to this topic

IMPORTANT REQUIREMENTS:
- Generate exactly 4 questions (no more, no less)
- Each question must have 3-4 answer options
- Use only these question types: "single_choice" or "multiple_choice"
- Questions should be specific to "{learning_topic}" - not generic
- Include a mix of experience, learning style, and goal-oriented questions
- Make options realistic and cover the full spectrum (beginner to advanced)

Return ONLY valid JSON in this exact format:
{{
  "questions": [
    {{
      "id": "experience_level",
      "question": "What's your current experience with {learning_topic}?",
      "type": "single_choice",
      "options": [
        {{"value": "complete_beginner", "label": "Complete beginner - never worked with this before"}},
        {{"value": "some_exposure", "label": "Some exposure through courses or tutorials"}},
        {{"value": "practical_experience", "label": "Some practical experience in projects"}},
        {{"value": "advanced", "label": "Advanced - looking to deepen specific areas"}}
      ]
    }},
    {{
      "id": "learning_goals",
      "question": "What's your primary goal for learning {learning_topic}?",
      "type": "single_choice",
      "options": [
        {{"value": "career_change", "label": "Career change or new job opportunities"}},
        {{"value": "skill_enhancement", "label": "Enhance skills for current role"}},
        {{"value": "personal_projects", "label": "Work on personal projects and interests"}},
        {{"value": "academic", "label": "Academic or research purposes"}}
      ]
    }},
    {{
      "id": "learning_style",
      "question": "How do you learn best?",
      "type": "single_choice",
      "options": [
        {{"value": "hands_on", "label": "Hands-on practice - learn by doing (80% practice, 20% theory)"}},
        {{"value": "balanced", "label": "Balanced approach - mix of theory and practice (60% practice, 40% theory)"}},
        {{"value": "theory_first", "label": "Theory first - understand concepts deeply before applying (40% practice, 60% theory)"}}
      ]
    }},
    {{
      "id": "background_knowledge",
      "question": "What relevant background do you have for {learning_topic}?",
      "type": "multiple_choice",
      "options": [
        {{"value": "programming", "label": "Programming/coding experience"}},
        {{"value": "math_stats", "label": "Mathematics or statistics background"}},
        {{"value": "domain_experience", "label": "Experience in related field"}},
        {{"value": "none", "label": "No relevant background"}}
      ]
    }}
  ]
}}

Examples for different topics:

For "Machine Learning":
- Ask about programming experience (Python, R, etc.)
- Ask about math background (statistics, linear algebra)
- Ask about specific ML applications they're interested in
- Ask about their experience with data

For "Digital Marketing":
- Ask about current marketing experience
- Ask about specific channels they want to focus on
- Ask about business context (startup, enterprise, agency)
- Ask about technical comfort level

For "Project Management":
- Ask about current role and team size
- Ask about methodology preferences (Agile, Waterfall, etc.)
- Ask about industry context
- Ask about certification goals

Make the questions specific and relevant to "{learning_topic}".
"""

@router.post("/generate-questions", response_model=QuestionGenerationResponse)
async def generate_personalization_questions(request: QuestionGenerationRequest):
    """
    Generate personalized questions for onboarding based on learning topic
    """
    try:
        logger.info(f"Generating questions for topic: {request.learning_topic}")
        
        # Validate learning topic (basic guardrails)
        topic_lower = request.learning_topic.lower().strip()
        
        # Basic content filtering
        invalid_patterns = ['cook', 'recipe', 'food', 'game', 'entertainment']
        if any(pattern in topic_lower for pattern in invalid_patterns):
            raise HTTPException(
                status_code=400, 
                detail="Please enter a professional skill or educational topic"
            )
        
        if len(request.learning_topic.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail="Learning topic must be at least 3 characters long"
            )
        
        # Generate prompt
        prompt = get_question_generation_prompt(
            request.learning_topic,
            request.daily_time,
            request.total_duration
        )
        
        # Call LLM service
        llm_service = LLMService()
        
        system_prompt = """You are an expert curriculum designer who creates personalized learning experiences. 
        
        Generate exactly 4 questions that will help personalize a learning curriculum for the given topic.
        
        Return ONLY valid JSON in the specified format. Do not include any explanation or additional text."""
        
        response = llm_service.generate(
            system_prompt=system_prompt,
            user_prompt=prompt,
            temperature=0.7
        )
        
        logger.info(f"LLM Raw response: {response}")
        
        # Parse the JSON response
        try:
            # Clean the response to extract JSON
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            
            json_str = json_str.strip()
            logger.info(f"Cleaned JSON string: {json_str}")
            
            questions_data = json.loads(json_str)
            
            # Validate the structure
            if "questions" not in questions_data:
                raise ValueError("Response missing 'questions' field")
            
            questions = []
            for i, q in enumerate(questions_data["questions"]):
                # Ensure required fields
                question = Question(
                    id=q.get("id", f"question_{i+1}"),
                    question=q["question"],
                    type=q["type"],
                    options=[
                        QuestionOption(value=opt["value"], label=opt["label"]) 
                        for opt in q["options"]
                    ]
                )
                questions.append(question)
            
            # Validate question count
            if len(questions) != 4:
                logger.warning(f"Generated {len(questions)} questions, expected exactly 4")
                # If we don't have exactly 4, fall back
                if len(questions) < 3:
                    return generate_fallback_questions(request.learning_topic)
            
            logger.info(f"Successfully generated {len(questions)} questions for {request.learning_topic}")
            
            return QuestionGenerationResponse(
                questions=questions,
                message=f"Generated {len(questions)} personalization questions"
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            logger.error(f"Raw response: {response}")
            
            # Fallback to generic questions
            return generate_fallback_questions(request.learning_topic)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Question generation failed: {str(e)}")
        
        # Fallback to generic questions
        return generate_fallback_questions(request.learning_topic)

def generate_fallback_questions(learning_topic: str) -> QuestionGenerationResponse:
    """Generate fallback questions when LLM fails"""
    
    questions = [
        Question(
            id="experience_level",
            question=f"What's your current experience level with {learning_topic}?",
            type="single_choice",
            options=[
                QuestionOption(value="beginner", label="Complete beginner"),
                QuestionOption(value="some_experience", label="Some experience"),
                QuestionOption(value="intermediate", label="Intermediate level"),
                QuestionOption(value="advanced", label="Advanced practitioner")
            ]
        ),
        Question(
            id="learning_style",
            question="How do you prefer to learn?",
            type="single_choice",
            options=[
                QuestionOption(value="hands_on", label="Hands-on practice (80% doing, 20% theory)"),
                QuestionOption(value="balanced", label="Balanced approach (60% doing, 40% theory)"),
                QuestionOption(value="theory_first", label="Theory first (40% doing, 60% theory)")
            ]
        ),
        Question(
            id="learning_goals",
            question=f"What's your primary goal for learning {learning_topic}?",
            type="single_choice",
            options=[
                QuestionOption(value="career", label="Career advancement or job opportunities"),
                QuestionOption(value="skills", label="Enhance skills for current role"),
                QuestionOption(value="personal", label="Personal projects and interests"),
                QuestionOption(value="academic", label="Academic or research purposes")
            ]
        ),
        Question(
            id="technical_background",
            question="What technical skills do you already have?",
            type="multiple_choice",
            options=[
                QuestionOption(value="programming", label="Programming experience"),
                QuestionOption(value="databases", label="Database knowledge"),
                QuestionOption(value="statistics", label="Statistics/Math background"),
                QuestionOption(value="none", label="No technical background")
            ]
        )
    ]
    
    return QuestionGenerationResponse(
        questions=questions,
        message=f"Generated fallback questions for {learning_topic}"
    )