#!/usr/bin/env python3
"""
Honest feedback engine - detects BS and provides real feedback
"""

from typing import Dict, Tuple, Optional


class HonestFeedbackEngine:
    """Detects BS patterns and provides honest feedback"""
    
    BS_PATTERNS = {
        "procrastination": {
            "keywords": ["later", "tomorrow", "next week", "eventually", "someday", "when i", "when things"],
            "response": "That's procrastination. The right time is NOW, even for 15 minutes. Start today."
        },
        "perfectionism_paralysis": {
            "keywords": ["perfect", "until it's perfect", "until i'm ready", "100%", "completely", "flawless"],
            "response": "Perfectionism is paralysis. 80% done and shipped beats 100% planned and frozen."
        },
        "victim_mentality": {
            "keywords": ["they won't", "they don't let", "it's not fair", "bad luck", "not my fault", "i can't"],
            "response": "You're more powerful than this. What can YOU control and change RIGHT NOW?"
        },
        "false_confidence": {
            "keywords": ["definitely", "100% sure", "no doubt", "guaranteed", "obviously", "of course"],
            "response": "What could go wrong? What are you NOT considering? Be honest with yourself."
        }
    }
    
    def detect_bs_pattern(self, text: str) -> Optional[Tuple[str, str]]:
        """Detect if text contains BS patterns"""
        text_lower = text.lower()
        
        for pattern_name, pattern_info in self.BS_PATTERNS.items():
            keywords = pattern_info["keywords"]
            for keyword in keywords:
                if keyword in text_lower:
                    return (pattern_name, keyword)
        
        return None
    
    def generate_honest_feedback(self, text: str) -> Dict:
        """Generate honest feedback for user input"""
        bs_result = self.detect_bs_pattern(text)
        
        if bs_result:
            pattern_name, keyword = bs_result
            pattern_info = self.BS_PATTERNS[pattern_name]
            return {
                "has_bs": True,
                "pattern": pattern_name,
                "keyword_found": keyword,
                "honest_assessment": pattern_info["response"],
                "red_flags": [keyword],
            }
        
        return {
            "has_bs": False,
            "pattern": None,
            "honest_assessment": None,
            "red_flags": [],
        }
