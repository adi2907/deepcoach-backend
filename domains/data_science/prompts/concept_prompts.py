# ============================================================================
# File: domains/data_science/prompts/concept_prompts.py
# Data Science specific prompts for concept generation
# ============================================================================

CONCEPT_GENERATION_PROMPT = """
You are an expert Data Science instructor. Break down the following module into detailed learning concepts.

Module Information:
- Module Name: {module_name}
- Module Description: {module_description}
- Total Estimated Time: {total_estimated_minutes} minutes
- Learning Objectives: {learning_objectives}
- Evaluation Type: {evaluation_type}

User Context:
{user_preferences}

Instructions:
1. Break this module into 3-6 concepts, each taking 10-20 minutes to complete
2. Each concept should be focused on a single, digestible topic
3. Concepts should build on each other with clear progression
4. Match the user's experience level and learning preferences
5. Include practical examples relevant to their goals

For each concept, provide:
- Clear name and description
- Specific learning objectives 
- Estimated time in minutes
- Logical ordering within the module

Concept Breakdown Guidelines:
- Start with foundational understanding if the user is a beginner
- Include hands-on elements for practical learners
- Build complexity gradually across concepts
- End with application or integration exercises
- Consider real-world use cases aligned with their goals

Focus on creating concepts that prepare learners for the module's evaluation type: {evaluation_type}

Generate concepts that create a coherent learning experience where each concept builds toward mastering the module objectives.
"""

CONCEPT_CONTENT_PROMPT = """
You are an expert Data Science instructor. Generate detailed learning content for the following concept.

Concept Information:
- Concept Name: {concept_name}
- Concept Description: {concept_description}
- Estimated Time: {estimated_minutes} minutes
- Learning Objectives: {learning_objectives}
- Module Context: {module_name}

User Context:
{user_preferences}

Content Requirements:
1. Generate content as markdown that can be displayed on a web page
2. Break content into 3-5 content blocks, each taking 2-4 minutes to read
3. Include practical code examples using Python for data science
4. Use clear headings, bullet points, and code blocks for readability
5. Match the user's experience level - avoid concepts they already know
6. Include "Try This" exercises within the content

Content Structure:
- Introduction block: What they'll learn and why it matters
- Core explanation blocks: Step-by-step breakdown of the concept
- Practical example block: Real code example with explanation
- Summary block: Key takeaways and next steps

Formatting Guidelines:
- Use ## for main headings, ### for subheadings
- Include code blocks with ```python
- Use bullet points for key concepts
- Include callout boxes with > for important notes
- Keep paragraphs concise (2-3 sentences max)

Make the content engaging and practical for someone pursuing: {user_goal}
"""

CONCEPT_NOTES_PROMPT = """
You are an expert Data Science instructor. Generate concise study notes for the following concept.

Concept Information:
- Concept Name: {concept_name}
- Learning Objectives: {learning_objectives}
- Module Context: {module_name}

User Context:
{user_preferences}

Generate comprehensive study notes that include:

1. **Key Concepts** (3-5 bullet points)
   - Most important ideas from this concept
   - Definitions of critical terms

2. **Essential Formulas/Code Patterns** 
   - Important mathematical formulas (if applicable)
   - Key code snippets or patterns
   - Syntax reminders

3. **Quick Reference**
   - When to use this concept
   - Common parameters or options
   - Typical use cases

4. **Memory Aids**
   - Mnemonics or mental models
   - Visual analogies
   - Connection to previous concepts

5. **Common Mistakes to Avoid**
   - Typical errors beginners make
   - Debug tips

Format as clean markdown with clear sections. Keep it concise but comprehensive - should serve as a quick reference sheet they can return to later.

Target length: 200-400 words total.
"""

CONCEPT_EVALUATION_PROMPT = """
You are an expert Data Science instructor. Generate evaluation content for the following concept.

Concept Information:
- Concept Name: {concept_name}
- Learning Objectives: {learning_objectives}
- Evaluation Type: {evaluation_type}
- Module Context: {module_name}

User Context:
{user_preferences}

Based on the evaluation type, generate appropriate assessment:

For CODING_EXERCISE:
- Create 2-3 progressive coding challenges
- Start with a simple warm-up exercise
- Include a more complex application problem
- Provide starter code and clear instructions
- Include test cases and expected outputs

For QUIZ:
- Create 5-7 multiple choice questions
- Include questions at different difficulty levels
- Test both conceptual understanding and practical application
- Provide clear explanations for correct answers

For MIXED:
- Combine 1-2 coding exercises with 3-4 quiz questions
- Ensure both theory and practice are assessed

Evaluation Guidelines:
- Match the user's experience level
- Test the specific learning objectives of this concept
- Include realistic scenarios from their goal domain
- Provide immediate feedback opportunities
- Make exercises engaging and relevant

Format as structured JSON with clear sections for each type of evaluation content.
"""

def get_concept_generation_prompt(module_data: dict, user_preferences: dict) -> str:
    """
    Format the concept generation prompt with module and user data
    """
    preferences_text = []
    
    if user_preferences:
        for key, value in user_preferences.items():
            if isinstance(value, list):
                preferences_text.append(f"- {key.replace('_', ' ').title()}: {', '.join(value) if value else 'None specified'}")
            else:
                preferences_text.append(f"- {key.replace('_', ' ').title()}: {value}")
    
    user_context = '\n'.join(preferences_text) if preferences_text else "No specific user preferences provided"
    
    return CONCEPT_GENERATION_PROMPT.format(
        module_name=module_data.get('name', 'Unknown Module'),
        module_description=module_data.get('description', 'No description provided'),
        total_estimated_minutes=int((module_data.get('estimated_hours', 2) * 60)),
        learning_objectives=', '.join(module_data.get('learning_objectives', [])) or 'Not specified',
        evaluation_type=module_data.get('evaluation_type', 'mixed'),
        user_preferences=user_context
    )

def get_concept_content_prompt(concept_data: dict, module_data: dict, user_preferences: dict) -> str:
    """
    Format the concept content generation prompt
    """
    preferences_text = []
    
    if user_preferences:
        for key, value in user_preferences.items():
            if isinstance(value, list):
                preferences_text.append(f"- {key.replace('_', ' ').title()}: {', '.join(value) if value else 'None specified'}")
            else:
                preferences_text.append(f"- {key.replace('_', ' ').title()}: {value}")
    
    user_context = '\n'.join(preferences_text) if preferences_text else "No specific user preferences provided"
    user_goal = user_preferences.get('goal', 'general learning')
    
    return CONCEPT_CONTENT_PROMPT.format(
        concept_name=concept_data.get('name', 'Unknown Concept'),
        concept_description=concept_data.get('description', 'No description provided'),
        estimated_minutes=int(concept_data.get('estimated_minutes', 15)),
        learning_objectives=', '.join(concept_data.get('learning_objectives', [])) or 'Not specified',
        module_name=module_data.get('name', 'Unknown Module'),
        user_preferences=user_context,
        user_goal=user_goal
    )

def get_concept_notes_prompt(concept_data: dict, module_data: dict, user_preferences: dict) -> str:
    """
    Format the concept notes generation prompt
    """
    preferences_text = []
    
    if user_preferences:
        for key, value in user_preferences.items():
            if isinstance(value, list):
                preferences_text.append(f"- {key.replace('_', ' ').title()}: {', '.join(value) if value else 'None specified'}")
            else:
                preferences_text.append(f"- {key.replace('_', ' ').title()}: {value}")
    
    user_context = '\n'.join(preferences_text) if preferences_text else "No specific user preferences provided"
    
    return CONCEPT_NOTES_PROMPT.format(
        concept_name=concept_data.get('name', 'Unknown Concept'),
        learning_objectives=', '.join(concept_data.get('learning_objectives', [])) or 'Not specified',
        module_name=module_data.get('name', 'Unknown Module'),
        user_preferences=user_context
    )

def get_concept_evaluation_prompt(concept_data: dict, module_data: dict, user_preferences: dict) -> str:
    """
    Format the concept evaluation generation prompt
    """
    preferences_text = []
    
    if user_preferences:
        for key, value in user_preferences.items():
            if isinstance(value, list):
                preferences_text.append(f"- {key.replace('_', ' ').title()}: {', '.join(value) if value else 'None specified'}")
            else:
                preferences_text.append(f"- {key.replace('_', ' ').title()}: {value}")
    
    user_context = '\n'.join(preferences_text) if preferences_text else "No specific user preferences provided"
    
    return CONCEPT_EVALUATION_PROMPT.format(
        concept_name=concept_data.get('name', 'Unknown Concept'),
        learning_objectives=', '.join(concept_data.get('learning_objectives', [])) or 'Not specified',
        evaluation_type=concept_data.get('evaluation_type', 'mixed'),
        module_name=module_data.get('name', 'Unknown Module'),
        user_preferences=user_context
    )