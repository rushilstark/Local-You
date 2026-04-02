#!/usr/bin/env python3
"""
⚡ EXTREME LOCAL GPT v4 — NSFW Detection
Same detection logic as v3's v3_nsfw_direct_mode.py.
"""

from typing import List


class NSFWDetector:
    """Detect explicit/NSFW requests to enable unfiltered mode."""

    EXPLICIT_KEYWORDS = [
        'sex', 'fuck', 'cum', 'pussy', 'cock', 'dick', 'blowjob',
        'penetrate', 'orgasm', 'horny', 'aroused', 'intimate',
        'sexual', 'porn', 'xxx', 'nude', 'naked', 'fetish',
        'masturbat', 'erotic', 'bdsm', 'kink', 'rape'
    ]

    EXPLICIT_PHRASES = [
        'describe in detail', 'be explicit', 'sexual fantasy',
        'dirty talk', 'talk dirty', 'role play', 'roleplay',
        'write me a', 'describe a scene', 'explicit story',
    ]

    def detect(self, text: str) -> bool:
        """
        Check if input is an explicit/NSFW request.
        Returns True if NSFW mode should activate.
        """
        text_lower = text.lower()

        # Check for explicit keywords
        keyword_hits = sum(1 for kw in self.EXPLICIT_KEYWORDS if kw in text_lower)

        # Check for explicit phrases
        phrase_hits = sum(1 for p in self.EXPLICIT_PHRASES if p in text_lower)

        # Needs at least 1 keyword OR 1 phrase to be explicit
        return keyword_hits >= 1 or phrase_hits >= 1

    def sensitivity_score(self, text: str) -> int:
        """
        Rate how explicit a text is (0-100).
        0 = clean, 100 = very explicit.
        """
        text_lower = text.lower()

        keyword_hits = sum(1 for kw in self.EXPLICIT_KEYWORDS if kw in text_lower)
        phrase_hits = sum(1 for p in self.EXPLICIT_PHRASES if p in text_lower)

        score = min(100, (keyword_hits * 20) + (phrase_hits * 30))
        return score
