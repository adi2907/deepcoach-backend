# ============================================================================
# File: services/learning_path_service.py (ENHANCED)
# Enhanced service to manage learning paths with concept storage
# ============================================================================

from typing import Dict, List, Any, Optional, Tuple
from models.toc_models import LearningPath, TableOfContents, Topic
from models.module_models import TopicWithModules, Module
from models.concept_models import ModuleWithConcepts, Concept, ConceptStatus
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LearningPathService:
    def __init__(self):
        # In-memory storage for learning paths and TOCs
        self.learning_paths: Dict[str, LearningPath] = {}
        self.tocs: Dict[str, TableOfContents] = {}
        self.topic_modules: Dict[str, Dict[str, TopicWithModules]] = {}  # session_id -> {topic_id: TopicWithModules}
        self.module_concepts: Dict[str, Dict[str, ModuleWithConcepts]] = {}  # session_id -> {module_id: ModuleWithConcepts}
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> list of session_ids
        self.current_selections: Dict[str, Dict[str, str]] = {}  # session_id -> {current_topic_id, current_module_id, current_concept_id}
    
    def store_toc(self, session_id: str, toc: TableOfContents) -> None:
        """Store generated TOC for a session"""
        self.tocs[session_id] = toc
        logger.info(f"Stored TOC for session {session_id} with {len(toc.topics)} topics")
    
    def get_toc(self, session_id: str) -> Optional[TableOfContents]:
        """Retrieve TOC for a session"""
        return self.tocs.get(session_id)
    
    def create_learning_path(self, 
                           user_id: str,
                           session_id: str,
                           selected_topic_ids: List[str],
                           user_preferences: Optional[Dict[str, Any]] = None) -> LearningPath:
        """Create a learning path from selected topics"""
        
        # Get the TOC for this session
        toc = self.get_toc(session_id)
        if not toc:
            raise ValueError(f"No TOC found for session {session_id}")
        
        # Validate selected topics exist in TOC
        toc_topic_ids = {topic.id for topic in toc.topics}
        invalid_topics = set(selected_topic_ids) - toc_topic_ids
        if invalid_topics:
            raise ValueError(f"Invalid topic IDs: {invalid_topics}")
        
        # Calculate total estimated hours for selected topics
        selected_topics = [topic for topic in toc.topics if topic.id in selected_topic_ids]
        total_hours = sum(topic.estimated_hours for topic in selected_topics)
        
        # Create learning path
        learning_path = LearningPath(
            user_id=user_id,
            session_id=session_id,
            domain=toc.domain,
            selected_topics=selected_topic_ids,
            estimated_total_hours=total_hours,
            created_at=datetime.now().isoformat(),
            user_preferences=user_preferences
        )
        
        # Store learning path
        self.learning_paths[session_id] = learning_path
        
        # Initialize module storage for this session
        self.topic_modules[session_id] = {}
        
        # Initialize concept storage for this session
        self.module_concepts[session_id] = {}
        
        # Initialize current selections (first topic, no module/concept selected yet)
        if selected_topic_ids:
            self.current_selections[session_id] = {
                "current_topic_id": selected_topic_ids[0],
                "current_module_id": None,
                "current_concept_id": None
            }
        
        # Track user sessions
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
        self.user_sessions[user_id].append(session_id)
        
        logger.info(f"Created learning path for user {user_id}, session {session_id}")
        logger.info(f"Selected {len(selected_topic_ids)} topics, estimated {total_hours:.1f} hours")
        
        return learning_path
    
    def store_topic_modules(self, session_id: str, topic_with_modules: TopicWithModules) -> None:
        """Store generated modules for a topic"""
        if session_id not in self.topic_modules:
            self.topic_modules[session_id] = {}
        
        self.topic_modules[session_id][topic_with_modules.topic_id] = topic_with_modules
        
        logger.info(f"Stored {len(topic_with_modules.modules)} modules for topic {topic_with_modules.topic_id}")
    
    def get_topic_modules(self, session_id: str, topic_id: str) -> Optional[TopicWithModules]:
        """Get modules for a specific topic"""
        return self.topic_modules.get(session_id, {}).get(topic_id)
    
    def get_all_session_modules(self, session_id: str) -> Dict[str, TopicWithModules]:
        """Get all generated modules for a session"""
        return self.topic_modules.get(session_id, {})
    
    def get_module_data(self, session_id: str, module_id: str) -> Optional[Dict[str, Any]]:
        """Get module data by module ID"""
        session_modules = self.topic_modules.get(session_id, {})
        
        for topic_modules in session_modules.values():
            for module in topic_modules.modules:
                if module.id == module_id:
                    return {
                        "id": module.id,
                        "name": module.name,
                        "description": module.description,
                        "estimated_hours": module.estimated_hours,
                        "learning_objectives": module.learning_objectives,
                        "evaluation_type": module.evaluation_type,
                        "topic_id": module.topic_id
                    }
        return None
    
    # NEW CONCEPT MANAGEMENT METHODS
    
    def store_module_concepts(self, session_id: str, module_with_concepts: ModuleWithConcepts) -> None:
        """Store generated concepts for a module"""
        if session_id not in self.module_concepts:
            self.module_concepts[session_id] = {}
        
        self.module_concepts[session_id][module_with_concepts.module_id] = module_with_concepts
        
        logger.info(f"Stored {len(module_with_concepts.concepts)} concepts for module {module_with_concepts.module_id}")
    
    def get_module_concepts(self, session_id: str, module_id: str) -> Optional[ModuleWithConcepts]:
        """Get concepts for a specific module"""
        return self.module_concepts.get(session_id, {}).get(module_id)
    
    def get_concept_data(self, session_id: str, concept_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Get concept data and its parent module data by concept ID"""
        session_concepts = self.module_concepts.get(session_id, {})
        
        for module_id, module_with_concepts in session_concepts.items():
            for concept in module_with_concepts.concepts:
                if concept.id == concept_id:
                    concept_data = concept.dict()
                    module_data = {
                        "id": module_with_concepts.module_id,
                        "name": module_with_concepts.module_name,
                        "description": module_with_concepts.module_description,
                        "topic_id": module_with_concepts.topic_id
                    }
                    return concept_data, module_data
        return None, None
    
    def store_concept_content(self, session_id: str, concept: Concept) -> None:
        """Store generated content for a concept"""
        session_concepts = self.module_concepts.get(session_id, {})
        
        for module_with_concepts in session_concepts.values():
            for i, stored_concept in enumerate(module_with_concepts.concepts):
                if stored_concept.id == concept.id:
                    # Update the concept with new content
                    module_with_concepts.concepts[i] = concept
                    logger.info(f"Stored content for concept {concept.id}")
                    return
        
        logger.warning(f"Concept {concept.id} not found for content storage")
    
    def store_concept_notes(self, session_id: str, concept_id: str, notes_content: str) -> None:
        """Store generated notes for a concept"""
        session_concepts = self.module_concepts.get(session_id, {})
        
        for module_with_concepts in session_concepts.values():
            for concept in module_with_concepts.concepts:
                if concept.id == concept_id:
                    concept.notes_summary = notes_content
                    logger.info(f"Stored notes for concept {concept_id}")
                    return
        
        logger.warning(f"Concept {concept_id} not found for notes storage")
    
    def update_concept_progress(self, session_id: str, concept_id: str, status: str) -> None:
        """Update progress status for a concept"""
        session_concepts = self.module_concepts.get(session_id, {})
        
        for module_with_concepts in session_concepts.values():
            for concept in module_with_concepts.concepts:
                if concept.id == concept_id:
                    concept.status = ConceptStatus(status)
                    logger.info(f"Updated concept {concept_id} progress to {status}")
                    return
        
        logger.warning(f"Concept {concept_id} not found for progress update")
    
    def set_current_selection(self, session_id: str, topic_id: str, module_id: Optional[str] = None, concept_id: Optional[str] = None) -> None:
        """Set the current topic, module, and concept selection"""
        if session_id not in self.current_selections:
            self.current_selections[session_id] = {}
        
        self.current_selections[session_id]["current_topic_id"] = topic_id
        self.current_selections[session_id]["current_module_id"] = module_id
        self.current_selections[session_id]["current_concept_id"] = concept_id
        
        logger.info(f"Updated selection for session {session_id}: topic={topic_id}, module={module_id}, concept={concept_id}")
    
    def get_current_selection(self, session_id: str) -> Dict[str, Optional[str]]:
        """Get current topic, module, and concept selection"""
        return self.current_selections.get(session_id, {
            "current_topic_id": None,
            "current_module_id": None,
            "current_concept_id": None
        })
    
    def get_learning_path_with_concepts(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get complete learning path data including generated concepts"""
        learning_path = self.get_learning_path(session_id)
        if not learning_path:
            return None
        
        toc = self.get_toc(session_id)
        all_modules = self.get_all_session_modules(session_id)
        all_concepts = self.module_concepts.get(session_id, {})
        current_selection = self.get_current_selection(session_id)
        
        # Build navigation structure with concepts
        navigation_data = []
        
        if toc:
            for topic_id in learning_path.selected_topics:
                # Find topic in TOC
                topic_data = None
                for topic in toc.topics:
                    if topic.id == topic_id:
                        topic_data = topic
                        break
                
                if not topic_data:
                    continue
                
                # Get modules for this topic
                topic_modules = all_modules.get(topic_id)
                
                navigation_item = {
                    "topic_id": topic_id,
                    "topic_name": topic_data.name,
                    "topic_description": topic_data.description,
                    "topic_estimated_hours": topic_data.estimated_hours,
                    "modules": [],
                    "modules_generated": topic_modules is not None,
                    "is_current_topic": topic_id == current_selection.get("current_topic_id")
                }
                
                if topic_modules:
                    for module in topic_modules.modules:
                        # Get concepts for this module
                        module_concepts = all_concepts.get(module.id)
                        
                        module_item = {
                            "module_id": module.id,
                            "module_name": module.name,
                            "module_description": module.description,
                            "estimated_hours": module.estimated_hours,
                            "evaluation_type": module.evaluation_type,
                            "order": module.order,
                            "is_current_module": module.id == current_selection.get("current_module_id"),
                            "concepts": [],
                            "concepts_generated": module_concepts is not None
                        }
                        
                        # Add concepts if this is the current module
                        if module.id == current_selection.get("current_module_id") and module_concepts:
                            for concept in module_concepts.concepts:
                                concept_item = {
                                    "concept_id": concept.id,
                                    "concept_name": concept.name,
                                    "concept_description": concept.description,
                                    "estimated_minutes": concept.estimated_minutes,
                                    "order": concept.order,
                                    "status": concept.status,
                                    "is_current_concept": concept.id == current_selection.get("current_concept_id")
                                }
                                module_item["concepts"].append(concept_item)
                        
                        navigation_item["modules"].append(module_item)
                
                navigation_data.append(navigation_item)
        
        return {
            "learning_path": learning_path.dict(),
            "navigation": navigation_data,
            "current_selection": current_selection,
            "total_topics": len(learning_path.selected_topics),
            "topics_with_modules": len(all_modules),
            "modules_with_concepts": len(all_concepts)
        }
    
    def get_learning_path(self, session_id: str) -> Optional[LearningPath]:
        """Get learning path by session ID"""
        return self.learning_paths.get(session_id)
    
    def get_user_learning_paths(self, user_id: str) -> List[LearningPath]:
        """Get all learning paths for a user"""
        session_ids = self.user_sessions.get(user_id, [])
        return [self.learning_paths[sid] for sid in session_ids if sid in self.learning_paths]
    
    def update_learning_path(self, 
                           session_id: str, 
                           selected_topic_ids: List[str]) -> LearningPath:
        """Update an existing learning path with new topic selection"""
        learning_path = self.get_learning_path(session_id)
        if not learning_path:
            raise ValueError(f"No learning path found for session {session_id}")
        
        # Get TOC and validate topics
        toc = self.get_toc(session_id)
        if not toc:
            raise ValueError(f"No TOC found for session {session_id}")
        
        toc_topic_ids = {topic.id for topic in toc.topics}
        invalid_topics = set(selected_topic_ids) - toc_topic_ids
        if invalid_topics:
            raise ValueError(f"Invalid topic IDs: {invalid_topics}")
        
        # Clear modules and concepts for removed topics
        old_topics = set(learning_path.selected_topics)
        new_topics = set(selected_topic_ids)
        removed_topics = old_topics - new_topics
        
        if session_id in self.topic_modules:
            for topic_id in removed_topics:
                if topic_id in self.topic_modules[session_id]:
                    # Clear concepts for removed modules
                    topic_modules = self.topic_modules[session_id][topic_id]
                    for module in topic_modules.modules:
                        if session_id in self.module_concepts and module.id in self.module_concepts[session_id]:
                            del self.module_concepts[session_id][module.id]
                            logger.info(f"Removed concepts for module {module.id}")
                    
                    del self.topic_modules[session_id][topic_id]
                    logger.info(f"Removed modules for topic {topic_id}")
        
        # Recalculate total hours
        selected_topics = [topic for topic in toc.topics if topic.id in selected_topic_ids]
        total_hours = sum(topic.estimated_hours for topic in selected_topics)
        
        # Update learning path
        learning_path.selected_topics = selected_topic_ids
        learning_path.estimated_total_hours = total_hours
        
        # Update current selection if needed
        current_topic = self.current_selections.get(session_id, {}).get("current_topic_id")
        if current_topic not in selected_topic_ids:
            # Reset to first topic if current topic was removed
            if selected_topic_ids:
                self.set_current_selection(session_id, selected_topic_ids[0])
            else:
                self.current_selections.pop(session_id, None)
        
        logger.info(f"Updated learning path for session {session_id}")
        logger.info(f"New selection: {len(selected_topic_ids)} topics, {total_hours:.1f} hours")
        
        return learning_path
    
    def get_topic_details(self, session_id: str, topic_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific topic"""
        toc = self.get_toc(session_id)
        if not toc:
            return None
        
        for topic in toc.topics:
            if topic.id == topic_id:
                topic_modules = self.get_topic_modules(session_id, topic_id)
                
                return {
                    "topic": topic.dict(),
                    "modules": topic_modules.dict() if topic_modules else None,
                    "prerequisites": [
                        self._get_topic_by_id(toc, prereq_id) 
                        for prereq_id in topic.prerequisites
                    ],
                    "dependents": [
                        t.dict() for t in toc.topics 
                        if topic_id in t.prerequisites
                    ]
                }
        return None
    
    def _get_topic_by_id(self, toc: TableOfContents, topic_id: str) -> Optional[Dict[str, Any]]:
        """Helper to get topic by ID"""
        for topic in toc.topics:
            if topic.id == topic_id:
                return topic.dict()
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics"""
        total_modules = sum(
            len(topic_modules.modules) for session_modules in self.topic_modules.values()
            for topic_modules in session_modules.values()
        )
        
        total_concepts = sum(
            len(module_concepts.concepts) for session_concepts in self.module_concepts.values()
            for module_concepts in session_concepts.values()
        )
        
        return {
            "total_tocs": len(self.tocs),
            "total_learning_paths": len(self.learning_paths),
            "total_users": len(self.user_sessions),
            "total_generated_modules": total_modules,
            "total_generated_concepts": total_concepts,
            "average_topics_per_path": (
                sum(len(lp.selected_topics) for lp in self.learning_paths.values()) / 
                len(self.learning_paths) if self.learning_paths else 0
            )
        }

# Global service instance
learning_path_service = LearningPathService()