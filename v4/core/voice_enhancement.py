#!/usr/bin/env python3
"""
🎙️ VOICE ENHANCEMENT SYSTEM — MULTI-AGENT IMPLEMENTATION
Ultimate Kokoro optimization with emotion detection, voice switching, 
dynamic speed, advanced fillers, emphasis, and punctuation awareness.

This system adds a NEW LAYER between AI response and Kokoro TTS:
  AI Response → Emotional Analysis → Text Enhancement → Kokoro Synthesis → Audio

SUBAGENT ARCHITECTURE:
  Agent 1: Emotion Detection (sentiment analysis, mood detection)
  Agent 2: Speed Variation (dynamic speed based on emotion)
  Agent 3: Voice Switching (select voice based on mood)
  Agent 4: Advanced Fillers (context-aware filler injection)
  Agent 5: Punctuation Awareness (pause lengths, intonation)
  Agent 6: Emphasis Injection (detect key emotional words)
  Agent 7: Phonetic Markers (prosody control)
  Agent 8: Audio Blending (mix effects for uniqueness)
"""

import re
import random
from typing import Tuple, Dict, List, Optional
from pathlib import Path

class EmotionDetector:
    """AGENT 1: Detect emotion/mood from text"""
    
    EMOTION_KEYWORDS = {
        "love": ["love", "adore", "cherish", "devoted", "passionate", "intimate"],
        "desire": ["want", "crave", "desire", "yearn", "long", "hunger"],
        "playful": ["tease", "playful", "cheeky", "wink", "giggle", "fun"],
        "intimate": ["whisper", "soft", "gentle", "tender", "close", "embrace"],
        "confident": ["know", "sure", "absolutely", "definitely", "certainly"],
        "uncertain": ["maybe", "perhaps", "might", "could", "seem", "think"],
        "dreamy": ["dream", "imagine", "wonder", "fantasy", "magical", "enchant"],
        "excited": ["amazing", "wonderful", "incredible", "fantastic", "beautiful"],
        "reflective": ["think", "realize", "understand", "know", "feel", "sense"],
    }
    
    def detect(self, text: str) -> Dict[str, float]:
        """Return emotion scores 0-1 for each emotion"""
        text_lower = text.lower()
        scores = {emotion: 0.0 for emotion in self.EMOTION_KEYWORDS}
        
        word_count = len(text_lower.split())
        
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            scores[emotion] = min(matches / max(word_count / 10, 1), 1.0)
        
        return scores
    
    def get_dominant_emotion(self, text: str) -> str:
        """Get primary emotion"""
        scores = self.detect(text)
        return max(scores, key=scores.get)
    
    def get_emotional_intensity(self, text: str) -> float:
        """0-1 scale of how emotional the text is"""
        scores = self.detect(text)
        return sum(scores.values()) / len(scores)


class SpeedVaration:
    """AGENT 2: Calculate dynamic speed based on emotion"""
    
    @staticmethod
    def get_speed_for_emotion(emotion: str, base_speed: float = 0.8) -> float:
        """Get speed multiplier for emotion"""
        speed_map = {
            "love": 0.70,        # Slow for intimacy
            "desire": 0.75,      # Very slow, sultry
            "playful": 0.85,     # Faster, energetic
            "intimate": 0.70,    # Slowest for softness
            "confident": 0.82,   # Moderate, assured
            "uncertain": 0.78,   # Slightly slower for hesitation
            "dreamy": 0.72,      # Slow, ethereal
            "excited": 0.88,     # Faster for energy
            "reflective": 0.80,  # Thoughtful pace
        }
        return speed_map.get(emotion, base_speed)
    
    @staticmethod
    def vary_speed_per_sentence(text: str, base_emotion: str) -> str:
        """Add speed variation markers per sentence"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        detector = EmotionDetector()
        varied = []
        
        for sent in sentences:
            if not sent.strip():
                continue
            emotion = detector.get_dominant_emotion(sent)
            speed = SpeedVaration.get_speed_for_emotion(emotion)
            # Store speed in marker for subprocess to use
            varied.append(f"[SPEED:{speed:.2f}]{sent}[/SPEED]")
        
        return " ".join(varied)


class VoiceSwitcher:
    """AGENT 3: Switch voices based on emotion"""
    
    VOICE_MAP = {
        "love": "af_heart",         # Warm, intimate
        "desire": "af_bella",       # Soft, sensual
        "playful": "af_sarah",      # Conversational, playful
        "intimate": "af_bella",     # Gentle, soft
        "confident": "af_heart",    # Warm, assured
        "uncertain": "af_sarah",    # Natural, conversational
        "dreamy": "af_bella",       # Dreamy, ethereal
        "excited": "af_nicole",     # Bright, energetic
        "reflective": "af_sarah",   # Natural, thoughtful
    }
    
    @staticmethod
    def get_voice_for_emotion(emotion: str, default: str = "af_heart") -> str:
        """Get best voice for emotion"""
        return VoiceSwitcher.VOICE_MAP.get(emotion, default)
    
    @staticmethod
    def switch_voices_mid_conversation(text: str) -> str:
        """Add voice switch markers for emotion transitions"""
        detector = EmotionDetector()
        sentences = re.split(r'(?<=[.!?])\s+', text)
        result = []
        current_voice = "af_heart"
        
        for sent in sentences:
            if not sent.strip():
                continue
            emotion = detector.get_dominant_emotion(sent)
            new_voice = VoiceSwitcher.get_voice_for_emotion(emotion)
            
            if new_voice != current_voice:
                result.append(f"[VOICE:{new_voice}]")
                current_voice = new_voice
            
            result.append(sent)
        
        return " ".join(result)


class AdvancedFillers:
    """AGENT 4: Context-aware filler injection"""
    
    FILLER_PATTERNS = {
        "love": ["you know", "really", "deeply", "so much"],
        "desire": ["I mean", "like", "really want", "desperately"],
        "uncertain": ["maybe", "I think", "possibly", "perhaps"],
        "confident": ["absolutely", "definitely", "clearly", "obviously"],
        "reflective": ["actually", "you know", "I realize", "I think"],
        "playful": ["like", "totally", "pretty much", "kind of"],
    }
    
    @staticmethod
    def inject_context_aware_fillers(text: str) -> str:
        """Inject fillers based on emotion context"""
        detector = EmotionDetector()
        emotion = detector.get_dominant_emotion(text)
        fillers = AdvancedFillers.FILLER_PATTERNS.get(emotion, ["you know"])
        
        sentences = re.split(r'(?<=[.!?])\s+', text)
        enhanced = []
        
        for i, sent in enumerate(sentences):
            if i > 0 and random.random() < 0.35 and sent.strip():  # 35% injection
                if sent[0].isupper():
                    filler = random.choice(fillers)
                    sent = filler.capitalize() + ", " + sent[0].lower() + sent[1:]
                else:
                    sent = random.choice(fillers) + " " + sent
            enhanced.append(sent)
        
        return " ".join(enhanced)


class PunctuationAwareness:
    """AGENT 5: Punctuation-aware phrasing"""
    
    @staticmethod
    def enhance_punctuation(text: str) -> str:
        """Add markers for different punctuation"""
        # Questions: more dramatic pause, rise at end
        text = re.sub(r'\?', '[Q_MARK]', text)  # Marker for questions
        
        # Exclamations: shorter pauses, more energy
        text = re.sub(r'!', '[EXCLAIM]', text)
        
        # Ellipses: extended pauses, thoughtfulness
        text = re.sub(r'\.\.\.', '[ELLIPSIS]', text)
        
        # Add pauses after colons/semicolons
        text = re.sub(r':', ': [PAUSE_MED]', text)
        text = re.sub(r';', '; [PAUSE_SHORT]', text)
        
        return text
    
    @staticmethod
    def apply_pause_lengths(text: str) -> str:
        """Convert punctuation markers to speed adjustments"""
        # Questions get slowed down for emphasis
        text = text.replace('[Q_MARK]', '... ')
        # Exclamations get faster
        text = text.replace('[EXCLAIM]', '! ')
        # Ellipsis stays as is (breathing)
        text = text.replace('[ELLIPSIS]', '... *breath* ... ')
        
        return text


class EmphasisInjection:
    """AGENT 6: Detect and emphasize key emotional words"""
    
    KEY_WORDS = {
        "love": ["love", "adore", "cherish"],
        "desire": ["want", "crave", "yearn"],
        "passion": ["passionate", "burning", "intense"],
        "intimate": ["close", "tender", "soft"],
        "beautiful": ["beautiful", "gorgeous", "stunning"],
    }
    
    @staticmethod
    def inject_emphasis(text: str) -> str:
        """Add emphasis to key emotional words"""
        for category, words in EmphasisInjection.KEY_WORDS.items():
            for word in words:
                # Add *emphasis* markers around key words
                pattern = r'\b' + word + r'\b'
                replacement = f"*emphasis* {word} *emphasis*"
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text


class PhoneticMarkers:
    """AGENT 7: Inject phonetic-level prosody control"""
    
    @staticmethod
    def add_phonetic_markers(text: str) -> str:
        """Add markers for phonetic control"""
        # Vowel elongation for emphasis
        text = re.sub(r'\b(love|desire|passionate)\b', r'\1: *linger*', text, flags=re.IGNORECASE)
        
        # Stress markers for important words
        detector = EmotionDetector()
        emotion = detector.get_dominant_emotion(text)
        
        if emotion in ["love", "desire", "intimate"]:
            # Add breathing before/after emotional peaks
            text = text.replace(". ", "... *breathe* ... ")
        
        return text


class AudioBlending:
    """AGENT 8: Prepare audio blending markers"""
    
    @staticmethod
    def add_blend_markers(text: str) -> str:
        """Add markers for optional audio effects blending"""
        # Detect emotional peaks
        if any(word in text.lower() for word in ["love", "adore", "passionate"]):
            text = "[BLEND:intimate]" + text + "[/BLEND]"
        
        if any(word in text.lower() for word in ["playful", "teasing", "fun"]):
            text = "[BLEND:playful]" + text + "[/BLEND]"
        
        if any(word in text.lower() for word in ["soft", "gentle", "whisper"]):
            text = "[BLEND:ethereal]" + text + "[/BLEND]"
        
        return text


class VoiceEnhancementPipeline:
    """Master orchestrator combining all agents"""
    
    def __init__(self):
        self.emotion_detector = EmotionDetector()
        self.speed_agent = SpeedVaration()
        self.voice_agent = VoiceSwitcher()
        self.filler_agent = AdvancedFillers()
        self.punctuation_agent = PunctuationAwareness()
        self.emphasis_agent = EmphasisInjection()
        self.phonetic_agent = PhoneticMarkers()
        self.audio_agent = AudioBlending()
    
    def enhance_text(self, text: str) -> Tuple[str, Dict]:
        """
        Run all agents in sequence to maximize voice quality
        Returns: (enhanced_text, metadata)
        """
        metadata = {}
        
        # AGENT 1: Analyze emotion
        emotion = self.emotion_detector.get_dominant_emotion(text)
        intensity = self.emotion_detector.get_emotional_intensity(text)
        metadata["emotion"] = emotion
        metadata["intensity"] = intensity
        
        # AGENT 2: Add speed variation per sentence
        text = self.speed_agent.vary_speed_per_sentence(text, emotion)
        
        # AGENT 3: Switch voices mid-conversation
        text = self.voice_agent.switch_voices_mid_conversation(text)
        
        # AGENT 4: Inject advanced fillers
        text = self.filler_agent.inject_context_aware_fillers(text)
        
        # AGENT 5: Punctuation awareness
        text = self.punctuation_agent.enhance_punctuation(text)
        text = self.punctuation_agent.apply_pause_lengths(text)
        
        # AGENT 6: Emphasis on key words
        text = self.emphasis_agent.inject_emphasis(text)
        
        # AGENT 7: Phonetic markers
        text = self.phonetic_agent.add_phonetic_markers(text)
        
        # AGENT 8: Audio blending
        text = self.audio_agent.add_blend_markers(text)
        
        # Add natural breathing (existing system)
        text = text.replace(". ", "... ")
        text = text.replace("...", "... *breath* ... ")
        
        metadata["enhanced_text"] = text
        metadata["agents_used"] = 8
        
        return text, metadata


# Example usage
if __name__ == "__main__":
    pipeline = VoiceEnhancementPipeline()
    
    test_text = "I love you so much. You make me so happy. I think about you constantly."
    
    enhanced, meta = pipeline.enhance_text(test_text)
    
    print("ORIGINAL:")
    print(test_text)
    print("\nENHANCED:")
    print(enhanced)
    print("\nMETADATA:")
    for k, v in meta.items():
        if k != "enhanced_text":
            print(f"  {k}: {v}")
