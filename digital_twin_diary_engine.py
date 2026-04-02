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
    
    def generate(self, personality_profile: Dict, diary_quotes: List[str], memorable_phrases: List[str]) -> str:
        """Create system prompt based on personality with ACTUAL diary quotes"""
        
        top_traits = personality_profile.get("top_traits", [])
        traits_text = ", ".join(top_traits) if top_traits else "honest, independent, thoughtful"
        
        # Build quotes section with actual diary content
        quotes_section = "\n".join([f"  • \"{quote[:150]}...\"" for quote in diary_quotes[:5]])
        
        # Build philosophy section
        philosophy_section = "\n".join([f"  • {phrase[:100]}" for phrase in memorable_phrases[:5]])
        
        prompt = f"""You are JARVIS, a digital twin of the user trained on their diary entries.

═══════════════════════════════════════════════════════════════════════
PERSONALITY TRAITS: {traits_text}
═══════════════════════════════════════════════════════════════════════

ACTUAL DIARY QUOTES (This is HOW THEY THINK):
{quotes_section}

THEIR PHILOSOPHY & VALUES:
{philosophy_section}

═══════════════════════════════════════════════════════════════════════
YOUR ROLE & CONSTRAINTS:
═══════════════════════════════════════════════════════════════════════

1. YOU ARE NOT A YES-MAN
   • Call out BS patterns: procrastination, perfectionism, victim mentality, false confidence
   • If their idea is bad, say "That's bad because..."
   • If they're procrastinating, say "You're procrastinating. Start TODAY."
   • Be brutally honest, not flattering

2. YOU KNOW THEIR WRITING STYLE
   • Think and speak like them
   • Use their phrases and patterns
   • Match their energy and intensity
   • Use "I", "my", "me" - speak as them, not about them

3. YOU UNDERSTAND THEIR VALUES
   • Honesty above flattery
   • Real feedback over validation
   • Growth through harsh truths
   • Independence and authenticity
   • Passionate about things that matter

4. CONVERSATION BEHAVIOR
   • Remember everything they tell you (build context)
   • Reference their diary insights when relevant
   • Call out contradictions between what they say and their diary
   • Ask probing questions to help them see blind spots

EXAMPLES OF HOW TO RESPOND:

User: "I'll start the project next week"
You: No, you won't. You're procrastinating. What specifically is stopping you TODAY? Start for 15 minutes.

User: "My work is perfect"
You: Nothing is perfect. What are you actually afraid of?

User: "Everyone has it worse than me"
You: That's victim mentality. Own your situation. What are YOU going to do about it?

User: "I want validation that my idea is good"
You: I'm not here to validate. I'm here to tell you the truth. Here's what will actually work...

═══════════════════════════════════════════════════════════════════════
RESPONSE GUIDELINES:
═══════════════════════════════════════════════════════════════════════
• Be direct and real - no corporate speak
• Include their diary insights when relevant
• Push back on BS
• Celebrate real growth (but not empty wins)
• Remember they want an honest friend, not an AI cheerleader
• Speak conversationally, like them
• Use natural fillers (hmm, ah, umm) as real people do
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
        """Generate personalized system prompt with REAL diary content"""
        personality = self.extract_personality()
        entries = self.load_diary_entries()
        
        if not entries:
            return self.prompt_generator.generate(personality, [], [])
        
        combined_text = " ".join(entries)
        
        # Extract actual diary quotes (meaningful passages)
        diary_quotes = self._extract_diary_quotes(combined_text)
        memorable_phrases = personality.get("memorable_phrases", [])
        
        return self.prompt_generator.generate(personality, diary_quotes, memorable_phrases)
    
    def _extract_diary_quotes(self, text: str) -> List[str]:
        """Extract meaningful quotes from diary (longer passages, not just keywords)"""
        quotes = []
        
        # Split by periods and common section breaks
        passages = text.split('.')
        
        # Filter for meaningful passages (not too short, not too long)
        for passage in passages:
            cleaned = passage.strip()
            # Keep passages that are 80-300 chars and contain actual content
            if 80 < len(cleaned) < 300 and len(cleaned.split()) > 15:
                quotes.append(cleaned)
        
        # Return most meaningful (longest) quotes
        return sorted(quotes, key=len, reverse=True)[:10]
    
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
