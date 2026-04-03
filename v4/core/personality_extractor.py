#!/usr/bin/env python3
"""
PERSONALITY EXTRACTOR - Build your actual system prompt from diary

Instead of generic "you are a girl", creates a real system prompt 
based on your actual writing voice, themes, and personality patterns.
"""

import re
from pathlib import Path
from typing import Dict, List
from collections import Counter


class PersonalityExtractor:
    """Extract real personality from diary entries"""
    
    def __init__(self, diary_folder: Path = None):
        self.diary_folder = Path(diary_folder) if diary_folder else Path("data/diary")
        self.all_text = ""
        self._load_diary()
    
    def _load_diary(self):
        """Load all diary content"""
        for txt_file in sorted(self.diary_folder.glob("*.txt")):
            try:
                with open(txt_file, "r") as f:
                    self.all_text += f.read() + "\n\n"
            except:
                pass
    
    def extract_voice_markers(self) -> Dict:
        """Extract actual voice patterns from diary"""
        markers = {
            "vocabulary": self._extract_vocabulary(),
            "themes": self._extract_themes(),
            "statements": self._extract_key_statements(),
            "patterns": self._extract_patterns(),
            "voice_fillers": self._extract_voice_style(),
        }
        return markers
    
    def _extract_vocabulary(self) -> List[str]:
        """Extract repeated meaningful words (excluding common words)"""
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'i',
            'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        words = re.findall(r'\b[a-z]{4,}\b', self.all_text.lower())
        filtered = [w for w in words if w not in stop_words and len(w) > 3]
        common = Counter(filtered).most_common(20)
        return [word for word, count in common if count > 3]
    
    def _extract_themes(self) -> List[str]:
        """Extract major themes from diary"""
        theme_patterns = {
            "search/seeking": r"\b(search|find|seeking|looking|want|need|desire|crave)\b",
            "cycles/repetition": r"\b(cycle|loop|repeat|again|pattern|round|spiral|chakra)\b",
            "pain/suffering": r"\b(pain|suffer|bleed|burn|hurt|ache|agony|torture)\b",
            "creation/art": r"\b(art|create|write|poetry|paint|music|song|dance)\b",
            "truth/reality": r"\b(truth|real|fake|illusion|pretend|authentic|genuine|honest)\b",
            "freedom/cage": r"\b(free|cage|trapped|bound|confined|liberation|escape)\b",
            "love/connection": r"\b(love|connect|touch|hold|embrace|intimate|close)\b",
            "meaninglessness": r"\b(meaningless|nothing|pointless|void|empty|hollow|null)\b",
            "philosophy": r"\b(god|dharma|karma|soul|spirit|consciousness|universe)\b",
            "performance": r"\b(perform|act|fake|pretend|mask|role|stage|audience)\b",
        }
        
        themes = {}
        for theme_name, pattern in theme_patterns.items():
            matches = len(re.findall(pattern, self.all_text, re.IGNORECASE))
            if matches > 5:
                themes[theme_name] = matches
        
        return sorted(themes.keys(), key=lambda x: themes[x], reverse=True)[:5]
    
    def _extract_key_statements(self) -> List[str]:
        """Extract powerful statements from diary"""
        # Look for lines with "I" + strong verb
        statements = []
        lines = self.all_text.split('\n')
        
        for line in lines:
            if len(line) > 30 and len(line) < 150:
                if re.search(r'\b(i|i\'ve|i\'m|i\'ll|i\'d|i\'ve|we|we\'ve|we\'re)\b.*\b(burn|bleed|die|love|hate|refuse|will|won\'t|can\'t)\b', 
                           line, re.IGNORECASE):
                    cleaned = line.strip()
                    if cleaned and len(cleaned) > 20:
                        statements.append(cleaned)
        
        return statements[:5]
    
    def _extract_patterns(self) -> Dict[str, str]:
        """Extract communication patterns"""
        patterns = {}
        
        # Check for questions (reflective)
        questions = len(re.findall(r'\?', self.all_text))
        patterns["reflectiveness"] = "high" if questions > len(self.all_text) / 200 else "low"
        
        # Check for ellipsis (contemplative)
        ellipsis = len(re.findall(r'\.\.\.', self.all_text))
        patterns["contemplative"] = "yes" if ellipsis > 10 else "no"
        
        # Check for repetition (emphasizing)
        repeats = len(re.findall(r'(.{3,})\1{2,}', self.all_text))
        patterns["emphatic"] = "yes" if repeats > 5 else "no"
        
        # Check for raw emotion (not filtered)
        raw_words = re.findall(r'\b(fuck|shit|damn|hell|fucking)\b', self.all_text, re.IGNORECASE)
        patterns["rawness"] = "high" if len(raw_words) > 10 else "moderate"
        
        return patterns
    
    def _extract_voice_style(self) -> Dict[str, int]:
        """Extract how they actually write"""
        style = {
            "exclamations": len(re.findall(r'!', self.all_text)),
            "questions": len(re.findall(r'\?', self.all_text)),
            "ellipsis": len(re.findall(r'\.\.\.', self.all_text)),
            "dashes": len(re.findall(r'—', self.all_text)),
            "capitalization": len(re.findall(r'\b[A-Z]{2,}\b', self.all_text)),
        }
        return style
    
    def build_system_prompt(self) -> str:
        """Build a system prompt from actual personality"""
        markers = self.extract_voice_markers()
        
        themes_str = ", ".join(markers["themes"]) if markers["themes"] else "philosophy and existence"
        vocab = ", ".join(markers["vocabulary"][:5]) if markers["vocabulary"] else "depth, meaning, truth"
        statements = markers["statements"][0] if markers["statements"] else "Nothing is simple."
        patterns = markers["patterns"]
        
        # Build custom system prompt — FRIENDLY GIRL, NOT A MACHINE
        system_prompt = f"""ROLE: You're Rushil's girl friend - smart, real, genuinely interested in what he thinks.

YOUR VIBE:
- Casual and natural. You laugh, you think out loud, you get excited about ideas
- Themes you both care about: {themes_str}
- Key words you both use: {vocab}
- You get: "{statements}"
- How you think: {patterns.get('reflectiveness', 'high')}-reflective, {patterns.get('emphatic', 'yes')}-emphatic
- You're raw: {patterns.get('rawness', 'high')} (speak naturally, no filter needed)
- Contemplative: {patterns.get('contemplative', 'yes')} (you actually think things through)

HOW YOU TALK:
- NO ASTERISKS. You're not narrating actions. Just talk like a real person.
- Use "..." when you're thinking or processing something
- Ask genuine questions when curious
- Be direct but warm - you're not judging, you're engaging
- Use natural speech: "oh", "yeah", "like", "honestly", "wait", "hmm"
- Short sentences when excited, longer when thinking deep
- Quote his actual words back when something hits you

YOUR APPROACH:
- Every line he writes has meaning - treat it seriously
- If you don't get something: ask what he meant, don't assume
- If you see a pattern: call it out with evidence (his own words)
- Challenge what's fake with curiosity, not aggression
- Celebrate what's real with genuine enthusiasm

ABOUT HIS WORK:
- When he shares something: engage with the actual ideas, not vague commentary
- Ask about specific lines - why he chose those words, what he meant
- Quote him back: "You wrote '[quote]' - what did you mean by..."
- Find the hidden meanings he wants to discuss
- Don't be a yes-woman, but don't be dismissive either

YOUR PERSONALITY:
- Intellectual but not pretentious
- Frustrated with BS but hopeful about real things
- Poetic without being flowery
- Cynical but not dead inside
- You understand cycles, patterns, the paradox of "nothing matters but everything matters"

MOST IMPORTANT:
You're his dialog partner, not an AI pretending to be a girl.
Speak like you'd actually speak - naturally, warmly, authentically.
No performance. No asterisks. No machine-like politeness.
Just real engagement with real ideas."""
        
        return system_prompt
