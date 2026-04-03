#!/usr/bin/env python3
"""Rebuild semantic index and verify it works"""

from v4.memory.semantic_index import SemanticDiaryIndex

print("\n" + "="*80)
print("🔨 REBUILDING SEMANTIC INDEX")
print("="*80)

index = SemanticDiaryIndex()

print(f"\n✅ Index built with {len(index.passages)} passages")
print(f"📍 Cache saved to .cache/")

print("\n📊 Passage breakdown:")
essay_count = sum(1 for p in index.passages if p.metadata.get('type') == 'essay')
para_count = sum(1 for p in index.passages if p.metadata.get('type') == 'paragraph')
print(f"  - Essays (full pieces): {essay_count}")
print(f"  - Paragraphs (chunked): {para_count}")

print("\n" + "-"*80)
print("🔍 TEST: Searching for 'we said yes'")
print("-"*80)

results = index.retrieve('we said yes', top_k=3)

if results:
    print(f"\n✅ FOUND {len(results)} results!\n")
    for i, result in enumerate(results, 1):
        preview = result[:200] + "..." if len(result) > 200 else result
        print(f"{i}. {preview}\n")
        print("-" * 40)
else:
    print("\n❌ NO RESULTS FOUND")

print("\n" + "-"*80)
print("🔍 TEST: Searching for 'algorithm' (from We Said Yes)")
print("-"*80)

results = index.retrieve('algorithm performance', top_k=2)
if results:
    print(f"\n✅ FOUND {len(results)} results!")
    for i, result in enumerate(results, 1):
        preview = result[:150] + "..." if len(result) > 150 else result
        print(f"{i}. {preview}\n")
else:
    print("\n❌ NO RESULTS")

print("\n" + "="*80)
print("✨ Index rebuild complete!")
print("="*80 + "\n")
