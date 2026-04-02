#!/usr/bin/env python3
"""Test if digital twin is reading diary"""

from pathlib import Path
from digital_twin_diary_engine import PersonalizedFinetuningPipeline

# Load and test
pipeline = PersonalizedFinetuningPipeline(
    diary_folder=Path("data/diary"),
    data_folder=Path("data")
)

print("=" * 80)
print("DIARY READING TEST")
print("=" * 80)

# Load entries
entries = pipeline.load_diary_entries()
print(f"\n✓ Loaded {len(entries)} diary entries")
for i, entry in enumerate(entries):
    print(f"  Entry {i+1}: {len(entry)} characters")
    print(f"  Preview: {entry[:100]}...")

# Extract personality
print("\n" + "=" * 80)
print("PERSONALITY EXTRACTION")
print("=" * 80)

personality = pipeline.extract_personality()
print(f"\nTop traits: {personality.get('top_traits', [])}")
print(f"Personality scores: {personality.get('personality_scores', {})}")

# Generate system prompt
print("\n" + "=" * 80)
print("SYSTEM PROMPT (What JARVIS will use)")
print("=" * 80)

system_prompt = pipeline.generate_system_prompt()
print(f"\n{system_prompt}")
