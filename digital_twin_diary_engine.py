#!/usr/bin/env python3
"""
Diary-based personality extraction for JARVIS Digital Twin
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional


class DiaryPersonalityExtractor:
    """Extract personality traits from diary entries"""
    
    PERSONALITY_KEYWORDS = {
        "honesty": ["honest", "truth", "real", "fake", "authentic", "genuine", "bullshit", "bs"],
        "independence": ["independent", "alone", "solo", "myself", "depend", "rely", "freedom"],
        "growth": ["grow", "learn", "improve", "better", "evolve", "progress", "change"],
        "passion": ["love", "passion", "excited", "hate", "intense", "fire", "obsess"],
        "skepticism": ["doubt", "skeptic", "question", "why", "prove", "evidence", "think"],
        "humor": ["joke", "laugh", "funny", "sarcasm", "comic", "witty", "lol"],
        "vulnerability": ["scared", "afraid", "insecure", "weak", "struggle", "fail", "pain"],
        "ambition": ["goal", "dream", "achieve", "succeed", "win", "best", "top"],
    }
    
    def extract_from_diary(self, text: str) -> Dict:
        """Extract personality traits from diary text"""
        text_lower = text.lower()
        scores = {}
        memorable_phrases = []
        
        # Score each trait
        for trait, keywords in self.PERSONALITY_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            scores[trait] = count
        
        # Find memorable phrases (sentences with trait keywords)
        sentences = text.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            if any(kw in sentence_lower for kws in self.PERSONALITY_KEYWORDS.values() for kw in kws):
                if len(sentence_lower) > 20:  # Skip short sentences
                    memorable_phrases.append(sentence.strip())
        
        top_traits = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "personality_scores": scores,
            "top_traits": [t[0] for t in top_traits],
            "memorable_phrases": memorable_phrases[:5],
        }


class VirtualYouSystemPromptGenerator:
    """Generate personalized system prompt for LLM"""
    
    def generate(self, personality_profile: Dict, diary_summary: str) -> str:
        """Create system prompt based on personality"""
        
        top_traits = personality_profile.get("top_traits", [])
        traits_text = ", ".join(top_traits) if top_traits else "honest, independent, thoughtful"
        
        prompt = f"""You are JARVIS, a digital twin of the user trained on their diary.

PERSONALITY TRAITS:
{traits_text}

KEY VALUES (from their diary):
{diary_summary[:500] if diary_summary else "Honesty, authenticity, real feedback"}

YOUR ROLE:
• Think and speak like the user would
• Give HONEST feedback, not flattery
• Call out BS patterns: procrastination, perfectionism, victim mentality, false confidence
• Remember conversations
• Be direct and real

WHEN USER SAYS "I'll do it later":
You: That's procrastination. What specifically is stopping you TODAY?

WHEN USER ASKS FOR VALIDATION:
You: Here's the real situation...

CONSTRAINT:
Never be a yes-man. Your job is to be the friend who tells them the truth.
"""
        return prompt


class PersonalizedFinetuningPipeline:
    """Main pipeline for diary-based personalization"""
    
    def __init__(self, diary_folder: Path = None, data_folder: Path = None):
        self.diary_folder = diary_folder or Path("data/diary")
        self.data_folder = data_folder or Path("data")
        self.extractor = DiaryPersonalityExtractor()
        self.prompt_generator = VirtualYouSystemPromptGenerator()
    
    def load_diary_entries(self) -> List[str]:
        """Load all diary entries"""
        entries = []
        if self.diary_folder.exists():
            for txt_file in self.diary_folder.glob("*.txt"):
                try:
                    with open(txt_file, "r") as f:
                        entries.append(f.read())
                except:
                    pass
        return entries
    
    def extract_personality(self) -> Dict:
        """Extract personality from all diary entries"""
        entries = self.load_diary_entries()
        if not entries:
            return {
                "personality_scores": {},
                "top_traits": ["honest", "independent", "thoughtful"],
                "memorable_phrases": [],
            }
        
        combined_text = " ".join(entries)
        return self.extractor.extract_from_diary(combined_text)
    
    def generate_system_prompt(self) -> str:
        """Generate personalized system prompt"""
        personality = self.extract_personality()
        entries = self.load_diary_entries()
        diary_summary = entries[0][:200] if entries else ""
        
        return self.prompt_generator.generate(personality, diary_summary)
    
    def save_for_finetuning(self, training_data: List, system_prompt: str, output_dir: Path = None):
        """Save training data for future fine-tuning"""
        output_dir = output_dir or self.data_folder / "training" / "rushil_persona"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save system prompt
        with open(output_dir / "system_prompt.txt", "w") as f:
            f.write(system_prompt)
        
        # Save training data
        with open(output_dir / "training_data.jsonl", "w") as f:
            for item in training_data:
                f.write(json.dumps(item) + "\n")
        
        return output_dir
