#!/usr/bin/env python3
"""
⚡ EXTREME LOCAL GPT v4 — Knowledge Base
Merges v3's WisdomLibrary + PatternAnalyzer into one module.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import Counter
from dataclasses import dataclass

from core.config import AppConfig, Color


@dataclass
class WisdomEntry:
    """Historical/mythological wisdom entry."""
    name: str
    source: str
    dilemma: str
    context: str
    resolution: str
    lesson: str
    themes: List[str]


class KnowledgeBase:
    """
    Combined wisdom library + pattern analyzer.
    Same data and logic as v3's v3_wisdom.py + v3_patterns.py.
    """

    def __init__(self, config: AppConfig):
        self.config = config
        self.wisdom_path = config.memory.wisdom_file_path
        self.patterns_path = config.memory.patterns_file_path
        self.wisdom_entries: List[WisdomEntry] = []
        self.patterns: Dict = {
            'decision_patterns': [],
            'blind_spots': [],
            'thinking_style': {},
            'recurring_themes': [],
            'value_hierarchy': [],
        }

        self._load_or_build_wisdom()
        self._load_patterns()

    # ================================================================
    # WISDOM LIBRARY (from v3_wisdom.py)
    # ================================================================

    def _load_or_build_wisdom(self):
        """Load wisdom from file or build defaults."""
        if self.wisdom_path.exists():
            try:
                with open(self.wisdom_path, 'r') as f:
                    data = json.load(f)
                self.wisdom_entries = [
                    WisdomEntry(**entry) for entry in data
                ]
                return
            except Exception:
                pass

        # Build default wisdom library (same as v3)
        self.wisdom_entries = [
            WisdomEntry(
                name="Arjuna's Dilemma", source="Bhagavad Gita",
                dilemma="Should I go to war against my own family?",
                context="Arjuna faces battling his cousins in a righteous war.",
                resolution="Krishna teaches duty (dharma) transcends personal attachment.",
                lesson="Duty may require sacrifice. Hiding from hard choices is not virtue.",
                themes=["duty", "family", "principle", "sacrifice", "growth"],
            ),
            WisdomEntry(
                name="Odysseus and the Sirens", source="Greek Mythology",
                dilemma="How do I stay true to my path when temptation is irresistible?",
                context="Odysseus must sail past Sirens whose song causes sailors to crash.",
                resolution="He had his men tie him to the mast and fill their ears with wax.",
                lesson="Sometimes you must remove yourself from temptation.",
                themes=["temptation", "discipline", "goal", "self-awareness", "wisdom"],
            ),
            WisdomEntry(
                name="Prometheus's Sacrifice", source="Greek Mythology",
                dilemma="Should I defy authority to help others if it costs me?",
                context="Prometheus steals fire from the gods for humanity.",
                resolution="He chooses humanity's need over personal safety.",
                lesson="Compassion sometimes demands sacrifice.",
                themes=["compassion", "principle", "defiance", "progress", "sacrifice"],
            ),
            WisdomEntry(
                name="Marcus Aurelius on Duty", source="Meditations (Stoicism)",
                dilemma="How do I do the right thing when it's unpopular?",
                context="Marcus Aurelius chose duty and virtue despite cost.",
                resolution="Virtue is its own reward. Your responsibility is your character.",
                lesson="You cannot control outcomes, only your integrity.",
                themes=["duty", "virtue", "courage", "principle", "character"],
            ),
            WisdomEntry(
                name="The Middle Way", source="Buddhist Philosophy",
                dilemma="Do I pursue pleasure or deny myself?",
                context="Siddhartha tried extreme asceticism and indulgence.",
                resolution="The Middle Way balances discipline with compassion.",
                lesson="The wisest path often transcends the binary choice.",
                themes=["balance", "wisdom", "growth", "compassion", "understanding"],
            ),
            WisdomEntry(
                name="The Good Samaritan", source="Christian Parable",
                dilemma="Do I help a stranger when it costs me?",
                context="A man is beaten. A priest passes by. A Samaritan helps.",
                resolution="Compassion transcends social boundaries.",
                lesson="Compassion isn't about convenience — it's about action.",
                themes=["compassion", "courage", "connection", "principle", "action"],
            ),
            WisdomEntry(
                name="Epictetus: Master and Slave", source="Stoic Philosophy",
                dilemma="How do I maintain dignity when I have no power?",
                context="Epictetus was a slave. His master threatened him.",
                resolution="His master could break his body but never his will.",
                lesson="No one can control your mind. That's where freedom lies.",
                themes=["freedom", "dignity", "character", "courage", "inner strength"],
            ),
            WisdomEntry(
                name="Wu Wei", source="Tao Te Ching",
                dilemma="Should I force change or align with what is?",
                context="Taoism teaches acting in harmony with the nature of things.",
                resolution="Water flows around mountains yet shapes stone.",
                lesson="Fighting reality exhausts you. Wisdom means understanding flow.",
                themes=["wisdom", "balance", "acceptance", "growth", "power"],
            ),
            WisdomEntry(
                name="Hillel's Teachings", source="Pirkei Avot (Jewish Ethics)",
                dilemma="How do I balance self-interest with community?",
                context="If I am not for myself, who will be? If only for myself, what am I?",
                resolution="Integration — self-care while serving others.",
                lesson="Self-care and service aren't opposed — they're interdependent.",
                themes=["balance", "community", "self-worth", "connection", "wisdom"],
            ),
            WisdomEntry(
                name="Sartre: Freedom", source="Existentialism",
                dilemma="If I'm truly free to choose, how do I know what's right?",
                context="We are 'condemned to be free' — no external authority decides.",
                resolution="With freedom comes radical responsibility.",
                lesson="Your freedom is your burden and your dignity. Own it.",
                themes=["freedom", "responsibility", "courage", "authenticity", "choice"],
            ),
            WisdomEntry(
                name="Aristotle's Phronesis", source="Virtue Ethics",
                dilemma="How do I know what virtue requires here?",
                context="Virtue isn't rules. Courage looks different in different contexts.",
                resolution="Practical wisdom perceives the right action in the specific moment.",
                lesson="Maturity is learning to perceive what the moment requires.",
                themes=["wisdom", "virtue", "discernment", "growth", "character"],
            ),
            WisdomEntry(
                name="Seventh Generation Principle", source="Indigenous Wisdom",
                dilemma="Who am I responsible to in my decisions?",
                context="Decisions should consider impact seven generations forward.",
                resolution="You are responsible to those who inherit your choices.",
                lesson="Think beyond your lifetime. You are part of a chain.",
                themes=["responsibility", "justice", "community", "future", "wisdom"],
            ),
        ]

        self._save_wisdom()

    def _save_wisdom(self):
        """Save wisdom to JSON."""
        self.wisdom_path.parent.mkdir(parents=True, exist_ok=True)
        data = [
            {
                'name': e.name, 'source': e.source, 'dilemma': e.dilemma,
                'context': e.context, 'resolution': e.resolution,
                'lesson': e.lesson, 'themes': e.themes,
            }
            for e in self.wisdom_entries
        ]
        with open(self.wisdom_path, 'w') as f:
            json.dump(data, f, indent=2)

    def wisdom_count(self) -> int:
        return len(self.wisdom_entries)

    def get_wisdom_for(self, dilemma: str, top_k: int = 2) -> Optional[str]:
        """Find wisdom entries related to a dilemma."""
        themes = self._extract_themes(dilemma)

        scored = []
        for entry in self.wisdom_entries:
            theme_matches = len(set(entry.themes) & set(themes))
            if theme_matches > 0:
                scored.append((entry, theme_matches))

        scored.sort(key=lambda x: x[1], reverse=True)

        if not scored:
            return None

        parts = ["📜 Ancient wisdom that echoes your dilemma:\n"]
        for entry, _ in scored[:top_k]:
            parts.append(f"🏛️  {entry.source}: {entry.name}")
            parts.append(f"   Their dilemma: {entry.dilemma}")
            parts.append(f"   Their insight: {entry.resolution}")
            parts.append(f"   For you: {entry.lesson}\n")

        return "\n".join(parts)

    # ================================================================
    # PATTERN ANALYSIS (from v3_patterns.py)
    # ================================================================

    def _load_patterns(self):
        """Load existing patterns from file."""
        if self.patterns_path.exists():
            try:
                with open(self.patterns_path, 'r') as f:
                    self.patterns = json.load(f)
            except Exception:
                pass

    def _save_patterns(self):
        """Save patterns to file."""
        self.patterns_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.patterns_path, 'w') as f:
            json.dump(self.patterns, f, indent=2)

    def pattern_count(self) -> int:
        return sum(
            len(v) for k, v in self.patterns.items()
            if isinstance(v, list)
        )

    def update_patterns(self, dilemma: str, debate_result):
        """Update patterns with a new debate."""
        themes = self._extract_themes(dilemma)

        # Update recurring themes
        if 'recurring_themes' not in self.patterns:
            self.patterns['recurring_themes'] = []

        current = dict(self.patterns['recurring_themes'])
        for theme in themes:
            current[theme] = current.get(theme, 0) + 1
        self.patterns['recurring_themes'] = sorted(
            current.items(), key=lambda x: x[1], reverse=True
        )[:10]

        # Detect blind spots (same logic as v3)
        advocate = debate_result.advocate_text.lower()
        critic = debate_result.critic_text.lower()

        blind_spots = self.patterns.get('blind_spots', [])

        emotion_words = ['emotion', 'feel', 'pain', 'hurt']
        if any(w in critic for w in emotion_words) and not any(w in advocate for w in emotion_words):
            blind_spots.append('Underestimate emotional costs')

        perspective_words = ['other', 'perspective', 'view', 'others']
        if any(w in critic for w in perspective_words) and not any(w in advocate for w in perspective_words):
            blind_spots.append("Don't fully consider others' perspectives")

        longterm_words = ['long', 'future', 'later', 'eventually']
        if any(w in critic for w in longterm_words) and not any(w in advocate for w in longterm_words):
            blind_spots.append('Underestimate long-term consequences')

        # Deduplicate and count
        spot_counter = Counter(blind_spots)
        self.patterns['blind_spots'] = [
            {'spot': spot, 'frequency': count}
            for spot, count in spot_counter.most_common(5)
            if count > 1
        ]

        self._save_patterns()

    def get_key_patterns(self) -> List[str]:
        """Get human-readable pattern insights."""
        insights = []

        themes = self.patterns.get('recurring_themes', [])
        if themes:
            top = ', '.join(f"{t} ({c})" for t, c in themes[:3])
            insights.append(f"📌 You frequently debate: {top}")

        blind_spots = self.patterns.get('blind_spots', [])
        for spot in blind_spots[:2]:
            if isinstance(spot, dict):
                insights.append(f"⚠️  Blind spot: {spot['spot']} (seen {spot['frequency']}x)")

        style = self.patterns.get('thinking_style', {})
        if style and 'description' in style:
            insights.append(f"🧠 Thinking style: {style['description']}")

        return insights

    # ================================================================
    # SHARED HELPERS
    # ================================================================

    def _extract_themes(self, text: str) -> List[str]:
        """Extract themes from text."""
        text_lower = text.lower()
        themes = []

        theme_keywords = {
            'duty': ['duty', 'obligation', 'responsibility', 'should'],
            'family': ['family', 'parent', 'child', 'love'],
            'principle': ['principle', 'moral', 'right', 'wrong', 'ethics'],
            'sacrifice': ['sacrifice', 'cost', 'price', 'give up'],
            'truth': ['truth', 'honest', 'lie', 'deceive'],
            'courage': ['courage', 'fear', 'brave', 'stand'],
            'wisdom': ['wisdom', 'understand', 'learn', 'knowledge'],
            'freedom': ['free', 'choice', 'autonomy', 'independence'],
            'compassion': ['compassion', 'care', 'help', 'empathy'],
            'growth': ['grow', 'develop', 'improve', 'potential'],
        }

        for theme, keywords in theme_keywords.items():
            if any(kw in text_lower for kw in keywords):
                themes.append(theme)

        return themes if themes else ['wisdom']
