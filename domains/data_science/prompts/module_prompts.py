# ============================================================================
# File: domains/data_science/prompts/module_prompts.py
# Data Science specific prompts for module generation
# ============================================================================

DATA_SCIENCE_MODULE_PROMPT = """
You are an expert Data Science curriculum designer. Break down the following topic into detailed learning modules.

Topic Information:
- Topic Name: {topic_name}
- Topic Description: {topic_description}
- Estimated Hours: {topic_hours}
- Difficulty Level: {topic_difficulty}
- Prerequisites: {topic_prerequisites}

User Context:
{user_preferences}

Instructions:
1. Create 2-5 modules that logically break down this topic
2. Each module should be max 30 min of focussed learning
3. Modules should build on each other with clear progression
4. Include practical coding exercises and theoretical understanding
5. Match the user's experience level and learning preferences
6. Ensure modules align with their stated goals

For each module, specify:
- Clear learning objectives (what they'll be able to do after completion)
- Appropriate evaluation method (coding exercises, quizzes, or mixed)
- Logical ordering and dependencies
- Realistic time estimates

Topic Breakdown Guidelines:
- Start with foundational concepts if the user is a beginner
- Include hands-on practice for practical learners
- Build complexity gradually
- End with application or integration exercises
- Consider real-world use cases aligned with their goals

Generate modules that create a coherent learning experience where each module prepares the learner for the next while building practical skills.
"""

def get_module_prompt(topic_data: dict, user_preferences: dict) -> str:
    """
    Format the module generation prompt with topic and user data
    
    Args:
        topic_data: Dictionary containing topic information
        user_preferences: User preferences from onboarding
        
    Returns:
        Formatted prompt string
    """
    
    # Format user preferences for the prompt
    preferences_text = []
    
    if user_preferences:
        for key, value in user_preferences.items():
            if isinstance(value, list):
                preferences_text.append(f"- {key.replace('_', ' ').title()}: {', '.join(value) if value else 'None specified'}")
            else:
                preferences_text.append(f"- {key.replace('_', ' ').title()}: {value}")
    
    user_context = '\n'.join(preferences_text) if preferences_text else "No specific user preferences provided"
    
    return DATA_SCIENCE_MODULE_PROMPT.format(
        topic_name=topic_data.get('name', 'Unknown Topic'),
        topic_description=topic_data.get('description', 'No description provided'),
        topic_hours=topic_data.get('estimated_hours', 'Not specified'),
        topic_difficulty=topic_data.get('difficulty', 'Not specified'),
        topic_prerequisites=', '.join(topic_data.get('prerequisites', [])) or 'None',
        user_preferences=user_context
    )