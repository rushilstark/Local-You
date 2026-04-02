#!/usr/bin/env python3
"""
Quick test of Phase 1 & Phase 4 integration
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("🚀 TESTING PHASE 1 & PHASE 4 INTEGRATION")
print("=" * 80)

# Test Semantic Index
print("\n📊 PHASE 1: SEMANTIC INDEX\n")
try:
    from v4.memory.semantic_index import SemanticDiaryIndex
    
    print("  🔄 Initializing semantic index...")
    index = SemanticDiaryIndex(
        diary_folder=Path("data/diary"),
        cache_dir=Path(".cache/semantic_embeddings")
    )
    
    print(f"  ✅ Index ready: {len(index.passages)} passages indexed\n")
    
    # Test queries
    test_queries = [
        "procrastination anxiety",
        "fear of people",
        "addiction recovery",
        "sister support",
        "authenticity"
    ]
    
    for query in test_queries[:3]:  # Test first 3
        print(f"  🔍 Query: '{query}'")
        results = index.retrieve(query, top_k=2)
        for i, result in enumerate(results, 1):
            preview = result[:80] + "..." if len(result) > 80 else result
            print(f"     {i}. {preview}\n")

except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test Knowledge Graph
print("\n" + "=" * 80)
print("🧠 PHASE 4: KNOWLEDGE GRAPH\n")
try:
    from v4.memory.knowledge_graph import DiaryKnowledgeGraph
    
    print("  🔄 Building knowledge graph...")
    graph = DiaryKnowledgeGraph(
        diary_folder=Path("data/diary"),
        cache_file=Path(".cache/knowledge_graph.json")
    )
    
    print(f"  ✅ Graph ready: {len(graph.nodes)} nodes, {len(graph.edges)} edges\n")
    
    # Show summary
    summary = graph.visualize_summary()
    for line in summary.split('\n')[:10]:
        print(f"  {line}")
    
    # Test smart recall
    print(f"\n  🔍 Testing smart recall:\n")
    test_messages = [
        "I'm procrastinating again",
        "I'm scared"
    ]
    
    for msg in test_messages:
        print(f"  Message: '{msg}'")
        recall = graph.get_smart_recall(msg)
        if recall:
            for line in recall.split('\n')[:3]:
                print(f"    {line}")
        else:
            print(f"    (No patterns detected)")
        print()

except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 80)
print("✨ TESTS COMPLETE")
print("=" * 80)
