#!/usr/bin/env python3
"""Rebuild and test - minimal output"""

from pathlib import Path
from v4.memory.semantic_index import SemanticDiaryIndex
import json

# Rebuild
print("Building index...")
index = SemanticDiaryIndex()
print(f"✓ Built with {len(index.passages)} passages")

# Test retrieval
results = index.retrieve('we said yes', top_k=1)

if results:
    text = results[0]
    # Check if it's the right essay
    has_we_said_yes = "We Said Yes" in text or "we said yes" in text.lower()
    has_algorithm = "Algorithm" in text or "algorithm" in text.lower()
    is_long = len(text) > 1000
    
    print(f"\n✅ RETRIEVED!")
    print(f"   Length: {len(text)} chars")
    print(f"   Has 'We Said Yes': {has_we_said_yes}")
    print(f"   Has 'Algorithm': {has_algorithm}")
    print(f"   Is essay (>1000 chars): {is_long}")
    print(f"\n   Preview: {text[:200]}...")
else:
    print("❌ Not found!")

# Save status
status = {
    "passages": len(index.passages),
    "essays": sum(1 for p in index.passages if p.metadata.get('type') == 'essay'),
    "paragraphs": sum(1 for p in index.passages if p.metadata.get('type') == 'paragraph'),
    "we_said_yes_found": len(results) > 0 and ("We Said Yes" in results[0] or "we said yes" in results[0].lower())
}

Path(".cache/rebuild_status.json").write_text(json.dumps(status, indent=2))
print(f"\nStatus saved: {status}")
