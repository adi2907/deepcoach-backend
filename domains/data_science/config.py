# ============================================================================
# File: domains/data_science/config.py
# Data Science domain configuration
# ============================================================================

from typing import Dict, Any, List
from models.module_models import EvaluationType

class DataScienceConfig:
    """Configuration for Data Science domain learning"""
    
    # Domain identifier
    DOMAIN_ID = "data_science"
    DOMAIN_NAME = "Data Science"
    
    # Hierarchy configuration
    HIERARCHY = {
        "levels": ["topic", "module"],  # Only Topic -> Module for now
        "show_levels": ["topic", "module"],  # What to show in navigation
        "expandable_levels": ["topic"],  # Which levels can be expanded/collapsed
    }
    
    # Navigation configuration
    NAVIGATION = {
        "default_expanded_topics": 1,  # Only first topic expanded by default
        "show_progress_indicators": True,
        "show_estimated_time": True,
        "auto_expand_on_select": True
    }
    
    # Module generation defaults
    MODULE_GENERATION = {
        "default_modules_per_topic": 4,  # Suggested number of modules per topic
        "min_modules_per_topic": 2,
        "max_modules_per_topic": 8,
        "default_module_hours": 2.0,  # Default hours per module if not specified
        "evaluation_types": [
            EvaluationType.CODING_EXERCISE,
            EvaluationType.QUIZ,
            EvaluationType.MIXED
        ]
    }
    
    # Coach configuration
    COACH = {
        "width_percentage": 25,  # 25% of screen width
        "navigation_section_height": "50%",  # Top half for navigation
        "motivation_section_height": "50%",  # Bottom half for motivation
        "show_motivation_messages": True,
        "motivation_update_interval": 300  # seconds
    }
    
    # Sidebar layout configuration
    SIDEBAR_LAYOUT = {
        "hierarchy": [
            {
                "level": "topic",
                "expandable": True,
                "show_progress": True,
                "show_estimated_time": True,
                "default_expanded": "first_only"  # "first_only", "all", "none"
            },
            {
                "level": "module", 
                "expandable": False,
                "show_progress": True,
                "show_estimated_time": True,
                "selectable": True,
                "show_under_parent": True
            }
        ]
    }
    
    # Motivation messages for different progress stages
    MOTIVATION_MESSAGES = {
        "start": [
            "🚀 Ready to dive into your first topic? Let's start building your data science expertise!",
            "💪 Your personalized learning journey begins now. Every expert was once a beginner!",
            "🎯 Focus on one module at a time - consistency beats intensity!"
        ],
        "progress": [
            "🔥 Great momentum! You're making real progress toward your goals.",
            "📈 Each module completed brings you closer to data science mastery!",
            "⚡ Keep going! Your future self will thank you for this dedication.",
            "🧠 Your brain is building new neural pathways with every concept you learn!"
        ],
        "completion": [
            "🎉 Module completed! Take a moment to appreciate your progress.",
            "✅ Another step closer to your data science goals. Well done!",
            "🏆 Excellent work! Ready for the next challenge?"
        ]
    }
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get complete configuration as dictionary"""
        return {
            "domain_id": cls.DOMAIN_ID,
            "domain_name": cls.DOMAIN_NAME,
            "hierarchy": cls.HIERARCHY,
            "navigation": cls.NAVIGATION,
            "module_generation": cls.MODULE_GENERATION,
            "coach": cls.COACH,
            "sidebar_layout": cls.SIDEBAR_LAYOUT,
            "motivation_messages": cls.MOTIVATION_MESSAGES
        }
    
    @classmethod
    def get_sidebar_hierarchy(cls) -> List[Dict[str, Any]]:
        """Get sidebar hierarchy configuration"""
        return cls.SIDEBAR_LAYOUT["hierarchy"]
    
    @classmethod
    def get_evaluation_types(cls) -> List[EvaluationType]:
        """Get supported evaluation types for this domain"""
        return cls.MODULE_GENERATION["evaluation_types"]