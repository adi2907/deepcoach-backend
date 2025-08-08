# ============================================================================
# File: services/learning_path_service.py (ENHANCED)
# Enhanced service to manage learning paths with module storage
# ============================================================================

from typing import Dict, List, Any, Optional
from models.toc_models import LearningPath, TableOfContents, Topic
from models.module_models import TopicWithModules, Module
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LearningPathService:
    def __init__(self):
        # In-memory storage for learning paths and TOCs
        self.learning_paths: Dict[str, LearningPath] = {}
        self.tocs: Dict[str, TableOfContents] = {}
        self.topic_modules: Dict[str, TopicWithModules] = {}  # session_id -> {topic_id: TopicWithModules}
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> list of session_ids
        self.current_selections: Dict[str, Dict[str, str]] = {}  # session_id -> {current_topic_id, current_module_id}
    
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
        
        # Initialize current selections (first topic, no module selected yet)
        if selected_topic_ids:
            self.current_selections[session_id] = {
                "current_topic_id": selected_topic_ids[0],
                "current_module_id": None
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
    
    def set_current_selection(self, session_id: str, topic_id: str, module_id: Optional[str] = None) -> None:
        """Set the current topic and module selection"""
        if session_id not in self.current_selections:
            self.current_selections[session_id] = {}
        
        self.current_selections[session_id]["current_topic_id"] = topic_id
        self.current_selections[session_id]["current_module_id"] = module_id
        
        logger.info(f"Updated selection for session {session_id}: topic={topic_id}, module={module_id}")
    
    def get_current_selection(self, session_id: str) -> Dict[str, Optional[str]]:
        """Get current topic and module selection"""
        return self.current_selections.get(session_id, {
            "current_topic_id": None,
            "current_module_id": None
        })
    
    def get_learning_path_with_modules(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get complete learning path data including generated modules"""
        learning_path = self.get_learning_path(session_id)
        if not learning_path:
            return None
        
        toc = self.get_toc(session_id)
        all_modules = self.get_all_session_modules(session_id)
        current_selection = self.get_current_selection(session_id)
        
        # Build navigation structure
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
                        navigation_item["modules"].append({
                            "module_id": module.id,
                            "module_name": module.name,
                            "module_description": module.description,
                            "estimated_hours": module.estimated_hours,
                            "evaluation_type": module.evaluation_type,
                            "order": module.order,
                            "is_current_module": module.id == current_selection.get("current_module_id")
                        })
                
                navigation_data.append(navigation_item)
        
        return {
            "learning_path": learning_path.dict(),
            "navigation": navigation_data,
            "current_selection": current_selection,
            "total_topics": len(learning_path.selected_topics),
            "topics_with_modules": len(all_modules)
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
        
        # Clear modules for removed topics
        old_topics = set(learning_path.selected_topics)
        new_topics = set(selected_topic_ids)
        removed_topics = old_topics - new_topics
        
        if session_id in self.topic_modules:
            for topic_id in removed_topics:
                if topic_id in self.topic_modules[session_id]:
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
            len(topic_modules) for session_modules in self.topic_modules.values()
            for topic_modules in session_modules.values()
        )
        
        return {
            "total_tocs": len(self.tocs),
            "total_learning_paths": len(self.learning_paths),
            "total_users": len(self.user_sessions),
            "total_generated_modules": total_modules,
            "average_topics_per_path": (
                sum(len(lp.selected_topics) for lp in self.learning_paths.values()) / 
                len(self.learning_paths) if self.learning_paths else 0
            )
        }

# Global service instance
learning_path_service = LearningPathService()