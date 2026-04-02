#!/usr/bin/env python3
"""
🚀 JARVIS DIGITAL TWIN — Main Orchestrator
Everything integrated. Just use v4/main.py
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from digital_twin_diary_engine import PersonalizedFinetuningPipeline
from jarvis_honest_feedback_engine import HonestFeedbackEngine


class JARVISDigitalTwin:
    """Complete JARVIS system - knows YOU, is HONEST, remembers conversations"""
    
    def __init__(self, diary_folder: Path = None, data_folder: Path = None):
        self.diary_folder = Path(diary_folder) if diary_folder else Path("data/diary")
        self.data_folder = Path(data_folder) if data_folder else Path("data")
        self.conversation_history = []
        self.personality_profile = {}
        self.system_prompt = ""
        self._initialize_personality()
    
    def _initialize_personality(self):
        """Load or create personality from diary"""
        pipeline = PersonalizedFinetuningPipeline(self.diary_folder)
        personality, training_data = pipeline.process_diary()
        
        if personality:
            self.personality_profile = personality
            self.system_prompt = pipeline.generate_system_prompt(personality)
    
    def get_system_prompt(self) -> str:
        """Get the system prompt that defines VIRTUAL YOU for the LLM"""
        return self.system_prompt
    
    def process_response(self, user_input: str, ai_response: str) -> Dict:
        """
        Process AI response with honest feedback and personalization
        Called AFTER model generates response
        """
        feedback = HonestFeedbackEngine.generate_honest_feedback(user_input)
        
        result = {
            "response": ai_response,
            "honest_feedback": feedback.get("honest_assessment", ""),
            "has_concerns": feedback.get("has_bs", False),
        }
        
        return result
    
    def remember_conversation(self, user_input: str, response: str):
        """Store conversation for future context"""
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat(),
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat(),
        })


# Global instance
_digital_twin = None

def initialize_digital_twin(diary_folder: Path = None, data_folder: Path = None) -> JARVISDigitalTwin:
    """Initialize the digital twin (called from v4/main.py)"""
    global _digital_twin
    _digital_twin = JARVISDigitalTwin(diary_folder, data_folder)
    return _digital_twin

def get_digital_twin() -> Optional[JARVISDigitalTwin]:
    """Get the global digital twin instance"""
    return _digital_twin
