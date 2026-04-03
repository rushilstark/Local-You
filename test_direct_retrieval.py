#!/usr/bin/env python3
"""Direct retrieval test"""
from v4.memory.semantic_index import SemanticDiaryIndex

idx = SemanticDiaryIndex()
print(f"\nLoaded {len(idx.passages)} passages\n")

# Simulate the user query
query = "what did you think of my latest piece we said yes"
results = idx.retrieve(query, top_k=3)

print("RETRIEVAL TEST")
print("="*100)
print(f"Query: '{query}'\n")

for i, result in enumerate(results, 1):
    preview = result[:150] + "..." if len(result) > 150 else result
    has_yes = "We Said Yes" in result or "said yes" in result.lower()
    has_algo = "algorithm" in result.lower()
    has_curve = "curve" in result.lower()
    
    print(f"\n{i}. Length: {len(result)} chars")
    print(f"   'We Said Yes': {has_yes}")
    print(f"   'Algorithm': {has_algo}")
    print(f"   'Curve': {has_curve}")
    print(f"   Preview: {preview}\n")

print("="*100)

# Also test the context formatting
context = idx.get_context(query, num_passages=1)
print(f"\n\nCONTEXT FORMATTED FOR LLM:\n{context}")
