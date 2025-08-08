# ============================================================================
# File: services/learning_path_service.py
# Service to manage learning paths with in-memory storage
# ============================================================================

from typing import Dict, List, Any, Optional
from models.toc_models import LearningPath, TableOfContents
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LearningPathService:
    def __init__(self):
        # In-memory storage for learning paths and TOCs
        self.learning_paths: Dict[str, LearningPath] = {}
        self.tocs: Dict[str, TableOfContents] = {}
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> list of session_ids
    
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
        """
        Create a learning path from selected topics
        
        Args:
            user_id: User identifier
            session_id: Session identifier 
            selected_topic_ids: List of topic IDs selected by user
            user_preferences: User preferences from onboarding
            
        Returns:
            LearningPath: Created learning path object
        """
        
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
        
        # Track user sessions
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
        self.user_sessions[user_id].append(session_id)
        
        logger.info(f"Created learning path for user {user_id}, session {session_id}")
        logger.info(f"Selected {len(selected_topic_ids)} topics, estimated {total_hours:.1f} hours")
        
        return learning_path
    
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
        """
        Update an existing learning path with new topic selection
        """
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
        
        # Recalculate total hours
        selected_topics = [topic for topic in toc.topics if topic.id in selected_topic_ids]
        total_hours = sum(topic.estimated_hours for topic in selected_topics)
        
        # Update learning path
        learning_path.selected_topics = selected_topic_ids
        learning_path.estimated_total_hours = total_hours
        
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
                return {
                    "topic": topic.dict(),
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
        return {
            "total_tocs": len(self.tocs),
            "total_learning_paths": len(self.learning_paths),
            "total_users": len(self.user_sessions),
            "average_topics_per_path": (
                sum(len(lp.selected_topics) for lp in self.learning_paths.values()) / 
                len(self.learning_paths) if self.learning_paths else 0
            )
        }

# Global service instance
learning_path_service = LearningPathService()