#!/usr/bin/env python3
"""
DIAGNOSTIC: Where is the response quality failure?
Tests each stage of the pipeline
"""

import sys
sys.path.insert(0, '.')

from v4.memory.semantic_index import SemanticDiaryIndex
from pathlib import Path

print("\n" + "="*80)
print("🔍 DIAGNOSTIC: WHERE IS THE FAILURE?")
print("="*80 + "\n")

# STEP 1: Check semantic index
print("STEP 1: Semantic Index Retrieval")
print("-" * 80)
index = SemanticDiaryIndex(Path('data/diary'), Path('.cache/semantic_embeddings'))
context = index.get_context("we said yes", num_passages=1)

print(f"✓ Context retrieved: {len(context)} chars")
print(f"✓ Contains intro: {('Did you ever wonder' in context)}")
print(f"✓ Contains thesis: {('swipe up' in context)}")
print(f"\nFirst 200 chars of context:")
print(context[:200])

# STEP 2: Check retrieval accuracy
print("\n\nSTEP 2: Title Matching Accuracy")
print("-" * 80)
retrieve_raw = index.retrieve("we said yes", top_k=1)
if retrieve_raw:
    essay = retrieve_raw[0]
    print(f"✓ Retrieved {len(essay)} chars")
    print(f"✓ Starts with: {essay[:80]}")
    print(f"✓ Contains central idea: {('swipe' in essay.lower())}")

# STEP 3: Check what metadata says
print("\n\nSTEP 3: Semantic Index Metadata")
print("-" * 80)
print(f"Total passages in index: {len(index.passages)}")
print(f"\nFirst 5 passages metadata:")
for i, passage in enumerate(index.passages[:5]):
    meta = passage.metadata
    section = meta.get('section', 'NO SECTION')
    word_count = meta.get('word_count', 0)
    print(f"  {i+1}. {section[:40]:40s} | {word_count:5d} words | {len(passage.text):6d} chars")

# STEP 4: Show what should be in the LLM prompt
print("\n\nSTEP 4: What Should LLM Receive")
print("-" * 80)
print(f"""
When user says "we said yes", the prompt to LLM should be:

[START CONTEXT]
╔════════════════════════════════════════╗
║ 📖 ESSAY: We Said Yes!!                 ║
╠════════════════════════════════════════╣
║                                        ║
╚════════════════════════════════════════╝

[FULL 13,000 CHARACTER ESSAY HERE]
   - Intro about "key to endless possibilities"
   - Content about swipe, dopamine, social media
   - Central thesis about "swipe up"
   - Discussion of trauma aesthetics
   - Conclusion about digital transformation

╔════════════════════════════════════════╗
║ ⚠️  READ THE ENTIRE ESSAY ABOVE CAREFULLY
║ RESPOND TO HIS ACTUAL QUESTION - Quote specific lines
╚════════════════════════════════════════╝

⚠️ CRITICAL BEFORE RESPONDING:

1. FIRST: READ ALL DIARY CONTENT ABOVE CAREFULLY
   - If there are diary quotes above, you MUST engage with them specifically
   
2. RESPOND TO HIS ACTUAL QUESTION
   - Reference specific ideas/phrases from his work
   
3. HOW TO RESPOND
   - Quote him back to show you read it
   
4. MOST IMPORTANT
   - If diary content is provided, your response MUST reference it
   - Quote at least one specific line from what he shared

User: what do you think of my latest piece we said yes!!
[END CONTEXT]

Then LLM should output something like:
"I just read through 'We Said Yes!!' and I'm struck by your central argument: 
'Our hard work, our creativity, our pain even our lives have become a swipe up.' 
That's the thesis that everything hinges on. You're saying that in the digital age, 
our most precious human qualities have been reduced to content that exists for 
a moment before disappearing. The Bo Burnham quote about the digital slaughterhouse...
you're building on that idea..."
""")

print("\n" + "="*80)
print("⚠️  THE ACTUAL PROBLEM")
print("="*80)
print("""
Hypothesis: The LLM is RECEIVING the context but NOT FOLLOWING THE INSTRUCTIONS

Why might this happen?

1. MODEL PARAMETER ISSUE
   - Temperature too high (0.8) → Model ignores instructions
   - Top-p too permissive (0.95) → Model generates randomness
   - Solution: Lower temperature to 0.3-0.5, top_p to 0.9

2. MODEL INSTRUCTION FOLLOWING
   - Abliterated Llama might not respect system prompts
   - Model might have been fine-tuned to ignore "read carefully"
   - Solution: Switch to non-abliterated Mistral or check model

3. PROMPT INJECTION FAILURE
   - System prompt might be getting overridden
   - Digital twin system prompt not being used
   - Solution: Verify engine.system_prompt is set BEFORE inference

4. CONTEXT LENGTH LIMITS
   - Max tokens might not account for diary + response
   - LLM truncating context internally
   - Solution: Check max_tokens config, verify model context window

5. TOKEN COUNTING
   - 13,000 chars ≈ 3,000 tokens
   - If max_tokens is 2,000 total, output only gets 1,000 tokens
   - LLM rushes through response
   - Solution: Increase max_tokens or reduce context

6. KNOWLEDGE GRAPH CONFLICT
   - Knowledge graph might be adding wrong context
   - Multiple contexts confusing the model
   - Solution: Disable knowledge graph, test with semantic only
""")

print("\n" + "="*80)
print("✅ IMMEDIATE TESTS TO RUN")
print("="*80)
print("""
1. Check engine.py temperature setting
   grep "temperature" v4/core/config.py

2. Verify system_prompt is being set
   Add print statements in engine._handle_chat()

3. Test with ONLY semantic index (no knowledge graph)
   Disable knowledge graph temporarily

4. Check model max_tokens configuration
   grep "max_tokens" v4/core/config.py

5. Try a simpler test prompt
   "Summarize the essay above in 2 sentences"

6. Test with different model
   Try Mistral or Qwen instead of Llama
""")

print("\n" + "="*80 + "\n")
