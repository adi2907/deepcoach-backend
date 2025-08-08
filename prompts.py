# ============================================================================
# File: prompts.py 
# Enhanced prompts that use rich onboarding data
# ============================================================================

COURSE_STRUCTURE_PROMPT = """
You are an expert data science educator. Create a course structure for: {topic}

Student Profile:
- Primary Goal: {goal}
- Experience Level: {level} (Detailed: {detailed_level})
- Learning Style: {style} (Detailed: {detailed_style})
- Total Time Available: {total_hours} hours ({detailed_total_time})
- Daily Commitment: {daily_minutes} minutes ({detailed_daily_time})

Technical Background Assessment:
Programming Experience: {programming_skills}
Mathematics Background: {math_background}  
Domain Knowledge: {domain_knowledge}

Based on this detailed profile:
1. Leverage their existing technical skills
2. Fill identified knowledge gaps
3. Adapt content complexity to their experience
4. Align projects with their stated goal
5. Structure modules to fit their time constraints

Create a modular course where each module is 30-60 minutes.

Return JSON:
{{
  "title": "Personalized Course Title",
  "total_modules": number,
  "student_profile_summary": "Brief summary of their background and goals",
  "learning_path_rationale": "Why this path was chosen for them",
  "modules": [
    {{
      "id": "mod_1",
      "title": "Module Title",
      "learning_objectives": ["objective1", "objective2"],
      "topics": ["topic1", "topic2"],
      "estimated_minutes": 45,
      "difficulty_level": "beginner|intermediate|advanced",
      "prerequisites_covered": ["skill1", "skill2"],
      "aligns_with_goal": "How this module helps their stated goal"
    }}
  ],
  "personalization_notes": {{
    "skipped_basics": ["concept1", "concept2"],
    "emphasis_areas": ["area1", "area2"],
    "recommended_pace": "Based on their time commitment"
  }}
}}
"""

MODULE_CONTENT_PROMPT = """
Create a {style} lesson for: {module_title}

Student Context:
- Goal: {goal}
- Experience Level: {level}
- Programming Skills: {programming_skills}
- Math Background: {math_background}
- Previous Knowledge: {domain_knowledge}

Module Details:
- Topics to cover: {topics}
- Learning objectives: {objectives}
- Target duration: {duration} minutes
- Difficulty level: {difficulty_level}

Personalization Instructions:
- Skip basics they already know: {skip_basics}
- Emphasize: {emphasis_areas}
- Connect to their goal: {goal_connection}

Format:
1. Start with personalized introduction acknowledging their background
2. Include {theory_percent}% theory and {code_percent}% hands-on code
3. Use examples relevant to their goal ({goal})
4. Add 2-3 exercises matching their programming level
5. Provide "next steps" that build toward their goal

Structure your response as:
## Personalized Introduction
[Acknowledge their background and connect to goals]

## Core Concepts  
[Theory explanation adapted to their math/programming level]

## Practical Application
[Code examples using libraries they're comfortable with]

## Hands-on Exercises
[2-3 exercises matching their skill level]

## Goal Connection
[How this module advances their stated goal]
"""

EXERCISE_GENERATOR_PROMPT = """
Create a Python coding exercise for: {topic}

Student Profile:
- Programming Level: {programming_level}
- Math Background: {math_level}
- Goal: {goal}
- Previous Domain Experience: {domain_experience}

Exercise Requirements:
- Difficulty: {difficulty}
- Focus: {focus_area}
- Time to complete: ~{estimated_minutes} minutes

Personalization:
- Use libraries they're familiar with: {familiar_libraries}
- Avoid concepts they haven't learned: {avoid_concepts}
- Connect to their goal: {goal}

Return JSON:
{{
  "title": "Exercise Title (Goal-Aligned)",
  "description": "What student needs to do (with goal context)",
  "starter_code": "def function_name():\\n    # Your code here\\n    # Hint: Use {familiar_concept} that you learned in {previous_experience}\\n    pass",
  "hints": [
    "Beginner-friendly hint based on their background",
    "Progressive hint building on their {programming_level} skills", 
    "Advanced hint connecting to their {goal}"
  ],
  "solution": "Complete solution with comments explaining concepts",
  "test_cases": [
    {{"input": "test input", "expected": "expected output"}},
    {{"input": "edge case relevant to {goal}", "expected": "expected output"}}
  ],
  "learning_notes": "What they should learn from this exercise",
  "goal_connection": "How this exercise helps achieve their {goal}"
}}
"""

COACH_HINT_PROMPT = """
Student Profile:
- Goal: {goal} 
- Experience: {experience_level}
- Programming Background: {programming_background}
- Math Background: {math_background}

Current Situation:
- Working on: {exercise_title}
- Their code: {user_code}
- Error (if any): {error}
- Attempt number: {attempt}
- Time spent: {time_spent} minutes

Coaching Instructions:
1. Reference their background knowledge positively
2. Connect hints to concepts they already understand
3. If attempt > 3, provide more specific guidance
4. Always encourage and relate back to their goal
5. Use their programming experience level to calibrate hint complexity

Provide a helpful, personalized hint that:
- Acknowledges their {experience_level} level
- Builds on their {programming_background} background  
- Connects to their goal of {goal}
- Is appropriately technical for their skill level
"""