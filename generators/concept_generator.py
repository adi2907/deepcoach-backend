# ============================================================================
# File: generators/concept_generator.py
# Generic concept generator that works across domains
# ============================================================================

from typing import Dict, Any, List
from services.llm_service import LLMService
from models.concept_models import ModuleWithConcepts, Concept, ContentBlock
import logging
import uuid
import re

logger = logging.getLogger(__name__)

class ConceptGenerator:
    def __init__(self, model: str = "openai/gpt-oss-20b:free"):
        self.llm = LLMService(model=model)
    
    def generate_concepts(self, 
                         module_data: Dict[str, Any],
                         user_preferences: Dict[str, Any],
                         domain_prompt_fn,
                         domain_config: Dict[str, Any]) -> ModuleWithConcepts:
        """
        Generate concepts for a module using domain-specific prompts
        
        Args:
            module_data: Module information
            user_preferences: User preferences from onboarding
            domain_prompt_fn: Function to generate domain-specific prompt
            domain_config: Domain configuration
            
        Returns:
            ModuleWithConcepts: Module with generated concepts
        """
        
        # Get domain-specific prompt for concept generation
        domain_prompt = domain_prompt_fn(module_data, user_preferences)
        
        # System prompt for concept generation
        system_prompt = f"""You are an expert curriculum designer. 
        
        Break down the given module into learning concepts that create a coherent, 
        progressive learning experience.
        
        Each concept should be focused and digestible (10-20 minutes).
        
        Follow the domain-specific guidelines and user preferences precisely.
        
        Return valid JSON that matches the required schema exactly."""
        
        logger.info(f"Generating concepts for module: {module_data.get('name', 'Unknown')}")
        logger.debug(f"Module estimated time: {module_data.get('estimated_hours', 'Unknown')} hours")
        
        try:
            # Generate concepts using structured output
            module_with_concepts = self.llm.generate_structured(
                system_prompt=system_prompt,
                user_prompt=domain_prompt,
                response_model=ModuleWithConcepts,
                temperature=0.7
            )
            
            # Post-process: Add unique IDs and ensure proper ordering
            module_with_concepts = self._post_process_concepts(
                module_with_concepts, 
                module_data,
                domain_config
            )
            
            logger.info(f"Successfully generated {len(module_with_concepts.concepts)} concepts")
            logger.info(f"Total estimated time: {module_with_concepts.total_estimated_minutes} minutes")
            
            return module_with_concepts
            
        except Exception as e:
            logger.error(f"Failed to generate concepts: {str(e)}")
            raise Exception(f"Concept generation failed: {str(e)}")
    
    def generate_concept_content(self,
                               concept_data: Dict[str, Any],
                               module_data: Dict[str, Any],
                               user_preferences: Dict[str, Any],
                               domain_content_prompt_fn) -> Concept:
        """
        Generate detailed content for a specific concept
        """
        
        # Get domain-specific content prompt
        domain_prompt = domain_content_prompt_fn(concept_data, module_data, user_preferences)
        
        system_prompt = """You are an expert instructor. Generate detailed learning content for the given concept.
        
        Create engaging, practical content that matches the user's learning style and goals.
        
        Return markdown content structured in logical blocks for easy consumption.
        
        Focus on practical application and real-world relevance."""
        
        logger.info(f"Generating content for concept: {concept_data.get('name', 'Unknown')}")
        
        try:
            # Generate content as text (markdown)
            content_text = self.llm.generate(
                system_prompt=system_prompt,
                user_prompt=domain_prompt,
                temperature=0.7
            )
            
            # Parse content into blocks
            content_blocks = self._parse_content_into_blocks(content_text)
            
            # Update concept with content
            concept = Concept(**concept_data)
            concept.content_blocks = content_blocks
            
            logger.info(f"Generated content with {len(content_blocks)} blocks")
            
            return concept
            
        except Exception as e:
            logger.error(f"Failed to generate concept content: {str(e)}")
            raise Exception(f"Concept content generation failed: {str(e)}")
    
    def generate_concept_notes(self,
                             concept_data: Dict[str, Any],
                             module_data: Dict[str, Any],
                             user_preferences: Dict[str, Any],
                             domain_notes_prompt_fn) -> str:
        """
        Generate concise study notes for a concept
        """
        
        # Get domain-specific notes prompt
        domain_prompt = domain_notes_prompt_fn(concept_data, module_data, user_preferences)
        
        system_prompt = """You are an expert instructor. Generate concise, comprehensive study notes.
        
        Create notes that serve as a quick reference and study aid.
        
        Include key concepts, formulas, examples, and memory aids.
        
        Format as clean markdown for easy reading and reference."""
        
        logger.info(f"Generating notes for concept: {concept_data.get('name', 'Unknown')}")
        
        try:
            notes_content = self.llm.generate(
                system_prompt=system_prompt,
                user_prompt=domain_prompt,
                temperature=0.6
            )
            
            logger.info(f"Generated notes for concept")
            
            return notes_content
            
        except Exception as e:
            logger.error(f"Failed to generate concept notes: {str(e)}")
            raise Exception(f"Concept notes generation failed: {str(e)}")
    
    def _post_process_concepts(self, 
                             module_with_concepts: ModuleWithConcepts,
                             original_module_data: Dict[str, Any],
                             domain_config: Dict[str, Any]) -> ModuleWithConcepts:
        """
        Post-process generated concepts to ensure consistency and add missing data
        """
        
        # Ensure module data is consistent
        module_with_concepts.module_id = original_module_data.get('id', str(uuid.uuid4()))
        module_with_concepts.topic_id = original_module_data.get('topic_id', '')
        
        # Process each concept
        for i, concept in enumerate(module_with_concepts.concepts):
            # Ensure unique IDs
            if not concept.id or concept.id == "":
                concept.id = f"concept_{module_with_concepts.module_id}_{i+1}"
            
            # Ensure module_id is set
            concept.module_id = module_with_concepts.module_id
            
            # Ensure proper ordering
            concept.order = i + 1
            
            # Validate estimated time (should be 10-20 minutes per concept)
            if concept.estimated_minutes <= 5 or concept.estimated_minutes > 30:
                default_minutes = 15  # Default 15 minutes per concept
                logger.warning(f"Adjusting unrealistic time for concept {concept.name}: {concept.estimated_minutes} -> {default_minutes}")
                concept.estimated_minutes = default_minutes
        
        # Recalculate total estimated time
        module_with_concepts.total_estimated_minutes = sum(
            concept.estimated_minutes for concept in module_with_concepts.concepts
        )
        
        # Set first concept as current
        if module_with_concepts.concepts:
            module_with_concepts.current_concept_id = module_with_concepts.concepts[0].id
        
        # Validate concept count
        concept_count = len(module_with_concepts.concepts)
        if concept_count < 2:
            logger.warning(f"Generated only {concept_count} concepts, recommend 3-6")
        elif concept_count > 8:
            logger.warning(f"Generated {concept_count} concepts, may be too many")
        
        return module_with_concepts
    
    def _parse_content_into_blocks(self, content_text: str) -> List[ContentBlock]:
        """
        Parse markdown content into logical blocks for progressive display
        """
        
        # Split content by main headings (##)
        blocks = []
        current_block = ""
        block_counter = 1
        
        lines = content_text.split('\n')
        
        for line in lines:
            if line.strip().startswith('## ') and current_block:
                # Save previous block
                if current_block.strip():
                    blocks.append(ContentBlock(
                        id=f"block_{block_counter}",
                        type="content",
                        content=current_block.strip(),
                        order=block_counter,
                        estimated_minutes=2.0
                    ))
                    block_counter += 1
                
                # Start new block
                current_block = line + '\n'
            else:
                current_block += line + '\n'
        
        # Add final block
        if current_block.strip():
            blocks.append(ContentBlock(
                id=f"block_{block_counter}",
                type="content", 
                content=current_block.strip(),
                order=block_counter,
                estimated_minutes=2.0
            ))
        
        # If no main headings found, create single block
        if not blocks:
            blocks.append(ContentBlock(
                id="block_1",
                type="content",
                content=content_text.strip(),
                order=1,
                estimated_minutes=5.0
            ))
        
        return blocks
    
    def set_model(self, model: str):
        """Switch LLM model"""
        self.llm.set_model(model)
        logger.info(f"Concept Generator switched to model: {model}")