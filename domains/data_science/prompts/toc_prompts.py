# ============================================================================
# File: domains/data_science/prompts/toc_prompts.py
# Generic prompt that passes user preferences to LLM without bias
# ============================================================================

# Single generic prompt that lets LLM decide based on user preferences
DATA_SCIENCE_TOC_PROMPT = """
Create a comprehensive Data Science curriculum Table of Contents based on the user's specific preferences and background.

User's Complete Profile:
{user_preferences}

Instructions:
1. Analyze the user's goals, experience level, learning style, time constraints, and technical background
2. Design a curriculum that EXACTLY matches their stated preferences
3. If they want career-focused content, emphasize job-ready skills
4. If they want hands-on learning, prioritize practical projects over theory
5. If they're a beginner, start with fundamentals; if advanced, focus on sophisticated topics
6. Respect their time constraints and daily commitment preferences
7. Build on their existing technical skills (programming, math, domain knowledge)

Generate topics that cover relevant areas of data science:
- Programming and tools
- Mathematics and statistics  
- Data manipulation and analysis
- Machine learning
- Data visualization
- Specialized domains (NLP, computer vision, etc.)
- Industry applications
- Portfolio/project work

Structure the curriculum to:
- Have logical progression and clear prerequisites
- Include realistic time estimates based on their availability
- Mark essential vs optional topics based on their goals
- Provide detailed subtopics that show learning value
- Match the complexity to their experience level

Let the user's stated preferences guide ALL decisions about:
- Depth vs breadth
- Theory vs practice ratio
- Beginner vs advanced content
- Career vs academic focus
- Time allocation per topic

Domain: data_science
"""

def get_toc_prompt(user_preferences: dict) -> str:
    """
    Format the generic prompt with user preferences
    No selection logic - just pass everything to LLM
    """
    # Convert user preferences to a readable format for the LLM
    formatted_preferences = []
    
    for key, value in user_preferences.items():
        if isinstance(value, list):
            formatted_preferences.append(f"- {key.replace('_', ' ').title()}: {', '.join(value) if value else 'None specified'}")
        else:
            formatted_preferences.append(f"- {key.replace('_', ' ').title()}: {value}")
    
    preferences_text = '\n'.join(formatted_preferences)
    
    return DATA_SCIENCE_TOC_PROMPT.format(user_preferences=preferences_text)