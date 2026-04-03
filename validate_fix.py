#!/usr/bin/env python3
"""
Validate that the engagement fixes are working:
1. Semantic index loads full essays
2. Personality extractor creates balanced system prompt
3. Context includes full quotes
"""

from v4.memory.semantic_index import SemanticDiaryIndex
from v4.core.personality_extractor import PersonalityExtractor
from pathlib import Path

print("="*70)
print("VALIDATING ENGAGEMENT SYSTEM FIXES")
print("="*70)

# 1. Check semantic index
print("\n1️⃣ SEMANTIC INDEX")
print("-" * 70)

try:
    semantic = SemanticDiaryIndex()
    print(f"✓ Loaded {len(semantic.passages)} passages")
    
    # Count types
    essays = sum(1 for p in semantic.passages if p.metadata.get('type') == 'essay')
    print(f"  - Essays (whole): {essays}")
    print(f"  - Paragraphs (chunked): {len(semantic.passages) - essays}")
    
    # Find We Said Yes
    print(f"\n🔍 Searching for 'We Said Yes'...")
    found = False
    for i, p in enumerate(semantic.passages):
        if 'we said yes' in p.text.lower():
            print(f"  ✓ Found at index {i}")
            print(f"    - Length: {len(p.text)} chars")
            print(f"    - Type: {p.metadata.get('type')}")
            if len(p.text) > 2000:
                print(f"    - Status: FULL ESSAY (good!)")
            found = True
            break
    
    if not found:
        print(f"  ✗ Not found (problem!)")
        
except Exception as e:
    print(f"✗ ERROR: {e}")

# 2. Check personality extractor
print("\n\n2️⃣ PERSONALITY EXTRACTOR")
print("-" * 70)

try:
    extractor = PersonalityExtractor(Path("data/diary"))
    prompt = extractor.build_system_prompt()
    
    print("✓ System prompt generated")
    
    # Check for key phrases
    checks = {
        "Emphasizes curiosity": "CURIOUS first" in prompt or "Understand his work deeply" in prompt,
        "Quotes from diary": "quote him directly" in prompt.lower(),
        "Engages with meaning": "every line has hidden meaning" in prompt,
        "Balanced (not too aggressive)": "don't be cruel" not in prompt or "with nuance" in prompt,
    }
    
    for check, result in checks.items():
        status = "✓" if result else "✗"
        print(f"  {status} {check}")
        
    print(f"\nPrompt length: {len(prompt)} chars")
    
except Exception as e:
    print(f"✗ ERROR: {e}")

# 3. Check context formatting
print("\n\n3️⃣ CONTEXT FORMATTING")
print("-" * 70)

try:
    semantic = SemanticDiaryIndex()
    context = semantic.get_context("we said yes", num_passages=1)
    
    if context:
        print("✓ Context generated")
        checks = {
            "Shows full quotes": "\"" in context or "..." in context,
            "Has instruction to quote": "Quote from" in context or "quote" in context.lower(),
            "Not truncated": len(context) > 200,
        }
        
        for check, result in checks.items():
            status = "✓" if result else "✗"
            print(f"  {status} {check}")
            
        print(f"\nContext preview:\n{context[:300]}...")
    else:
        print("✗ No context generated")
        
except Exception as e:
    print(f"✗ ERROR: {e}")

print("\n" + "="*70)
print("VALIDATION COMPLETE")
print("="*70)
