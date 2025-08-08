# ============================================================================
# File: generators/module_generator.py
# Generic module generator that works across domains
# ============================================================================

from typing import Dict, Any, List
from services.llm_service import LLMService
from models.module_models import TopicWithModules, Module
import logging
import uuid

logger = logging.getLogger(__name__)

class ModuleGenerator:
    def __init__(self, model: str = "openai/gpt-oss-20b:free"):
        self.llm = LLMService(model=model)
    
    def generate_modules(self, 
                        topic_data: Dict[str, Any],
                        user_preferences: Dict[str, Any],
                        domain_prompt_fn,
                        domain_config: Dict[str, Any]) -> TopicWithModules:
        """
        Generate modules for a topic using domain-specific prompts
        
        Args:
            topic_data: Topic information from TOC
            user_preferences: User preferences from onboarding
            domain_prompt_fn: Function to generate domain-specific prompt
            domain_config: Domain configuration
            
        Returns:
            TopicWithModules: Topic with generated modules
        """
        
        # Get domain-specific prompt
        domain_prompt = domain_prompt_fn(topic_data, user_preferences)
        
        # System prompt for module generation
        system_prompt = f"""You are an expert curriculum designer. 
        
        Break down the given topic into learning modules that create a coherent, 
        progressive learning experience.
        
        Follow the domain-specific guidelines and user preferences precisely.
        
        Return valid JSON that matches the required schema exactly."""
        
        logger.info(f"Generating modules for topic: {topic_data.get('name', 'Unknown')}")
        logger.debug(f"Topic difficulty: {topic_data.get('difficulty', 'Unknown')}")
        logger.debug(f"Topic hours: {topic_data.get('estimated_hours', 'Unknown')}")
        
        try:
            # Generate modules using structured output
            topic_with_modules = self.llm.generate_structured(
                system_prompt=system_prompt,
                user_prompt=domain_prompt,
                response_model=TopicWithModules,
                temperature=0.7
            )
            
            # Post-process: Add unique IDs and ensure proper ordering
            topic_with_modules = self._post_process_modules(
                topic_with_modules, 
                topic_data,
                domain_config
            )
            
            logger.info(f"Successfully generated {len(topic_with_modules.modules)} modules")
            logger.info(f"Total estimated hours: {topic_with_modules.total_estimated_hours}")
            
            return topic_with_modules
            
        except Exception as e:
            logger.error(f"Failed to generate modules: {str(e)}")
            raise Exception(f"Module generation failed: {str(e)}")
    
    def _post_process_modules(self, 
                            topic_with_modules: TopicWithModules,
                            original_topic_data: Dict[str, Any],
                            domain_config: Dict[str, Any]) -> TopicWithModules:
        """
        Post-process generated modules to ensure consistency and add missing data
        """
        
        # Ensure topic data is consistent
        topic_with_modules.topic_id = original_topic_data.get('id', str(uuid.uuid4()))
        
        # Process each module
        for i, module in enumerate(topic_with_modules.modules):
            # Ensure unique IDs
            if not module.id or module.id == "":
                module.id = f"mod_{topic_with_modules.topic_id}_{i+1}"
            
            # Ensure topic_id is set
            module.topic_id = topic_with_modules.topic_id
            
            # Ensure proper ordering
            module.order = i + 1
            
            # Validate estimated hours (set default if missing or unrealistic)
            if module.estimated_hours <= 0 or module.estimated_hours > 10:
                default_hours = domain_config.get('module_generation', {}).get('default_module_hours', 2.0)
                logger.warning(f"Adjusting unrealistic hours for module {module.name}: {module.estimated_hours} -> {default_hours}")
                module.estimated_hours = default_hours
        
        # Recalculate total estimated hours
        topic_with_modules.total_estimated_hours = sum(
            module.estimated_hours for module in topic_with_modules.modules
        )
        
        # Validate module count
        min_modules = domain_config.get('module_generation', {}).get('min_modules_per_topic', 2)
        max_modules = domain_config.get('module_generation', {}).get('max_modules_per_topic', 8)
        
        module_count = len(topic_with_modules.modules)
        if module_count < min_modules:
            logger.warning(f"Generated only {module_count} modules, minimum is {min_modules}")
        elif module_count > max_modules:
            logger.warning(f"Generated {module_count} modules, maximum is {max_modules}")
        
        return topic_with_modules
    
    def set_model(self, model: str):
        """Switch LLM model"""
        self.llm.set_model(model)
        logger.info(f"Module Generator switched to model: {model}")