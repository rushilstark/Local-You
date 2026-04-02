#!/usr/bin/env python3
"""
⚡ EXTREME LOCAL GPT v4 — Profile Engine
Learns user values and thinking patterns from debate history.
Same core logic as v3's PersonalizationEngine.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from collections import Counter
from dataclasses import dataclass, field

from core.config import AppConfig, Color


@dataclass
class UserProfile:
    """What we know about the user."""
    primary_values: List[str] = field(default_factory=list)
    secondary_values: List[str] = field(default_factory=list)
    blind_spots: List[str] = field(default_factory=list)
    thinking_style: str = ""
    confidence_level: float = 0.0
    debate_count: int = 0


@dataclass
class DebateEntry:
    """Minimal debate record for personalization."""
    dilemma: str
    advocate: str
    critic: str
    synthesis: str
    themes: List[str] = field(default_factory=list)


class ProfileEngine:
    """
    Learns user values and patterns after enough debates.
    Same as v3's PersonalizationEngine.
    """

    def __init__(self, config: AppConfig):
        self.config = config
        self.profile_path = config.memory.resolved_data_dir / "profile.json"
        self.debates_history_path = config.memory.resolved_data_dir / "personalization_history.json"

        self.profile: Optional[UserProfile] = None
        self.debates: List[DebateEntry] = []

        self._load()

    def _load(self):
        """Load profile and debate history."""
        # Load profile
        if self.profile_path.exists():
            try:
                with open(self.profile_path, 'r') as f:
                    data = json.load(f)
                self.profile = UserProfile(
                    primary_values=data.get('primary_values', []),
                    secondary_values=data.get('secondary_values', []),
                    blind_spots=data.get('blind_spots', []),
                    thinking_style=data.get('thinking_style', ''),
                    confidence_level=data.get('confidence_level', 0),
                    debate_count=data.get('debate_count', 0),
                )
            except Exception:
                pass

        # Load debate history
        if self.debates_history_path.exists():
            try:
                with open(self.debates_history_path, 'r') as f:
                    data = json.load(f)
                self.debates = [
                    DebateEntry(
                        dilemma=d.get('dilemma', ''),
                        advocate=d.get('advocate', ''),
                        critic=d.get('critic', ''),
                        synthesis=d.get('synthesis', ''),
                        themes=d.get('themes', []),
                    )
                    for d in data
                ]
            except Exception:
                pass

    def _save(self):
        """Save profile and history."""
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)

        if self.profile:
            with open(self.profile_path, 'w') as f:
                json.dump({
                    'primary_values': self.profile.primary_values,
                    'secondary_values': self.profile.secondary_values,
                    'blind_spots': self.profile.blind_spots,
                    'thinking_style': self.profile.thinking_style,
                    'confidence_level': self.profile.confidence_level,
                    'debate_count': self.profile.debate_count,
                }, f, indent=2)

        with open(self.debates_history_path, 'w') as f:
            json.dump([
                {
                    'dilemma': d.dilemma,
                    'advocate': d.advocate,
                    'critic': d.critic,
                    'synthesis': d.synthesis,
                    'themes': d.themes,
                }
                for d in self.debates
            ], f, indent=2)

    def has_profile(self) -> bool:
        return self.profile is not None and self.profile.confidence_level > 0

    def confidence(self) -> float:
        return self.profile.confidence_level if self.profile else 0

    def debate_count(self) -> int:
        return len(self.debates)

    def add_debate(self, dilemma: str, advocate: str, critic: str, synthesis: str):
        """Add a debate to history."""
        themes = self._extract_themes(dilemma)
        self.debates.append(DebateEntry(
            dilemma=dilemma,
            advocate=advocate,
            critic=critic,
            synthesis=synthesis,
            themes=themes,
        ))
        self._save()

    def learn(self):
        """
        Analyze debate history and build/update profile.
        Called after reaching the minimum debate threshold.
        """
        if len(self.debates) < self.config.persona.min_debates_for_profile:
            return

        # Extract value hierarchy
        value_counter = Counter()
        value_keywords = {
            'growth': ['grow', 'develop', 'learn', 'improve', 'progress', 'potential'],
            'integrity': ['integrity', 'honest', 'authentic', 'principled', 'truth'],
            'connection': ['connection', 'relate', 'community', 'bond', 'together'],
            'security': ['security', 'safe', 'stable', 'certain', 'protected'],
            'freedom': ['freedom', 'autonomy', 'choice', 'independent', 'liberty'],
            'compassion': ['compassion', 'empathy', 'care', 'kind', 'understanding'],
            'justice': ['justice', 'fair', 'equitable', 'right', 'moral'],
            'wisdom': ['wisdom', 'wise', 'understanding', 'knowledge', 'insight'],
        }

        for debate in self.debates:
            all_text = f"{debate.dilemma} {debate.synthesis}".lower()
            for value, keywords in value_keywords.items():
                for kw in keywords:
                    value_counter[value] += all_text.count(kw)

        ranked_values = value_counter.most_common()

        # Determine thinking style
        advocate_lean = 0
        critic_lean = 0
        for debate in self.debates:
            synth_lower = debate.synthesis.lower()
            if any(w in synth_lower for w in ['advocate', 'growth', 'opportunity']):
                advocate_lean += 1
            if any(w in synth_lower for w in ['critic', 'caution', 'risk']):
                critic_lean += 1

        total = advocate_lean + critic_lean
        if total > 0:
            ratio = advocate_lean / total
            if 0.4 < ratio < 0.6:
                style = "Pragmatic with ethical foundation"
            elif ratio > 0.6:
                style = "Growth-oriented optimist"
            else:
                style = "Realistic cautious planner"
        else:
            style = "Balanced"

        # Build profile
        confidence = min(100, len(self.debates) * 10)

        self.profile = UserProfile(
            primary_values=[v for v, _ in ranked_values[:3]],
            secondary_values=[v for v, _ in ranked_values[3:6]],
            blind_spots=[],  # Populated by pattern analyzer
            thinking_style=style,
            confidence_level=confidence,
            debate_count=len(self.debates),
        )

        self._save()

    def get_prompt_context(self) -> Optional[str]:
        """Get personalization context for prompts."""
        if not self.profile:
            return None

        parts = [f"User's core values: {', '.join(self.profile.primary_values)}"]
        parts.append(f"Thinking style: {self.profile.thinking_style}")

        if self.profile.blind_spots:
            parts.append(f"Known blind spots: {', '.join(self.profile.blind_spots)}")

        return "\n".join(parts)

    def print_profile(self):
        """Pretty-print the user profile."""
        if not self.profile:
            print(f"{Color.DEBUG}No profile yet.{Color.RESET}")
            return

        print(f"\n{Color.BOLD}{Color.SYNTHESIS}✨ YOUR PROFILE ✨{Color.RESET}")
        print(f"  Core values: {', '.join(self.profile.primary_values)}")
        print(f"  Style: {self.profile.thinking_style}")
        print(f"  Confidence: {self.profile.confidence_level:.0f}%")
        print(f"  Debates analyzed: {self.profile.debate_count}")
        if self.profile.blind_spots:
            print(f"  Blind spots: {', '.join(self.profile.blind_spots)}")

    def _extract_themes(self, text: str) -> List[str]:
        """Extract themes from text."""
        text_lower = text.lower()
        themes = []
        theme_keywords = {
            'career': ['job', 'work', 'career'],
            'relationships': ['relationship', 'family', 'partner', 'love'],
            'ethics': ['moral', 'ethical', 'right', 'wrong'],
            'growth': ['grow', 'develop', 'learn', 'improve'],
            'honesty': ['truth', 'honest', 'lie'],
            'freedom': ['free', 'choice', 'autonomy'],
        }
        for theme, keywords in theme_keywords.items():
            if any(kw in text_lower for kw in keywords):
                themes.append(theme)
        return themes if themes else ['general']
