#!/usr/bin/env python3
"""Test semantic search for 'We Said Yes'"""

from v4.memory.semantic_index import SemanticDiaryIndex

index = SemanticDiaryIndex()

print("\n" + "="*80)
print("🔍 TEST: Retrieving 'we said yes' (should return We Said Yes!! essay)")
print("="*80 + "\n")

results = index.retrieve('we said yes', top_k=2)

for i, result in enumerate(results, 1):
    # Check key markers
    has_title = "We Said Yes" in result or "we said yes" in result.lower()
    has_algorithm = "Algorithm" in result
    has_dopamine = "dopamine" in result.lower()
    length = len(result)
    
    preview = result[:250] + "..." if len(result) > 250 else result
    
    print(f"\nResult {i}:")
    print(f"  Length: {length} chars")
    print(f"  ✓ Has 'We Said Yes': {has_title}")
    print(f"  ✓ Has 'Algorithm': {has_algorithm}")
    print(f"  ✓ Has dopamine/brain ref: {has_dopamine}")
    print(f"\n  Preview:\n  {preview}\n")
    print("-" * 80)

print("\n" + "="*80)
print("🔍 TEST: What does JARVIS see for engagement?")
print("="*80 + "\n")

context = index.get_context("tell me about we said yes", num_passages=1)
print("Context formatted for LLM:")
print(context[:600])
if len(context) > 600:
    print("...\n[Context truncated for display]\n")
