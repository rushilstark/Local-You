#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from v4.memory.semantic_index import SemanticDiaryIndex
from pathlib import Path

index = SemanticDiaryIndex(Path('data/diary'), Path('.cache/semantic_embeddings'))

# Test the improved formatting
print("\n" + "="*80)
print("TESTING IMPROVED CONTEXT FORMATTING")
print("="*80 + "\n")

context = index.get_context('we said yes', num_passages=1)
print("First 900 chars:\n")
print(context[:900])
print("\n... [middle section omitted] ...\n")
print(f"\nLast 400 chars:\n")
print(context[-400:])
print(f"\n\nTOTAL LENGTH: {len(context)} characters")
print("✓ Test complete")
