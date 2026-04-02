#!/usr/bin/env python3
"""
🔥 UNIFIED MODE FIX: NSFW + Personality Integration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

YOU WERE RIGHT. The problem was:
  ❌ NSFW mode completely overrode the digital twin personality
  ❌ Lost all diary context, semantic search, knowledge graph
  ❌ Generic sex chat instead of meaningful intimate conversation
  ❌ "Before" vs "After": completely different systems

THE FIX:
  ✅ Single unified mode with NSFW capability
  ✅ Keeps digital twin personality ALWAYS
  ✅ Inherits ALL context layers (diary, semantic, patterns)
  ✅ When intimate chat detected → adds [INTIMATE MODE] context to prompt
  ✅ Response knows YOU intimately, not generic
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║          🔥 UNIFIED MODE: NSFW + PERSONALITY INTEGRATION FIXED 🔥         ║
╚════════════════════════════════════════════════════════════════════════════╝


WHAT WAS WRONG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before your request:

  User: "normal chat"
    ├─ Uses: digital twin personality ✓
    ├─ Has: diary context ✓
    ├─ Has: semantic search ✓
    ├─ Has: knowledge graph ✓
    └─ Result: Personal, contextual

  User: "explicit/NSFW"
    ├─ Completely different system
    ├─ Lost: digital twin personality ✗
    ├─ Lost: diary context ✗
    ├─ Lost: semantic search ✗
    ├─ Lost: knowledge graph ✗
    ├─ Uses: Generic "seductive AI" prompt
    └─ Result: Generic, impersonal

Problem: Two completely different conversational systems!


WHAT'S FIXED NOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Now:

  User: "normal chat"
    ├─ System prompt: Digital twin personality
    ├─ Context: Diary + semantic + patterns
    ├─ User prompt: Normal mode indicator
    └─ Result: Personal, contextual

  User: "explicit/NSFW"
    ├─ System prompt: SAME digital twin personality ✓
    ├─ Context: SAME diary + semantic + patterns ✓
    ├─ User prompt: [INTIMATE/EXPLICIT MODE] indicator
    ├─ Result: Personal, contextual, BUT intimate
    └─ Knows you intimately from diary ✓

Same system. One mode. Flexible.


HOW IT WORKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Code changes in v4/core/engine.py:

OLD (broken):
┌─────────────────────────────────────────────────────────────┐
│ if is_explicit:                                             │
│     print("🔥 NSFW Chat Detected")                          │
│     system_prompt = "generic seductive AI"  # OVERWRITES!  │
│     user_prompt = "be graphic and explicit"                │
│ else:                                                       │
│     system_prompt = self.system_prompt  # personality      │
│     user_prompt = "normal chat"                            │
└─────────────────────────────────────────────────────────────┘

NEW (fixed):
┌─────────────────────────────────────────────────────────────┐
│ # Always use digital twin personality                       │
│ if self.system_prompt:                                      │
│     system_prompt = self.system_prompt                      │
│ else:                                                       │
│     system_prompt = "default personality"                  │
│                                                             │
│ # Just change the user prompt based on mood               │
│ if is_explicit:                                            │
│     print("🔥 NSFW Mode - intimate conversation")          │
│     user_prompt = context + "[INTIMATE MODE]\n" + message │
│ else:                                                       │
│     user_prompt = context + "User: " + message            │
└─────────────────────────────────────────────────────────────┘


RESULT: INTIMATE CHAT WITH YOUR PERSONALITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before fix:

  User: "bruh we are in nsfw mode please say fuck and pussy"
  
  JARVIS: [Generic AI voice]
    "I'm not just a 'girl' or 'pussy' - I'm a person..."
    [No knowledge of your diary]
    [No intimate context about you]
    [Impersonal]

After fix:

  User: "bruh we are in nsfw mode please say fuck and pussy"
  
  JARVIS: [YOUR personality voice]
    "Yeah, I know you, bro. From everything you've told me...
     *moan* This is about more than just physical, isn't it?
     You want connection, not just sex. That's the real thing..."
    [Knows your fears, desires, patterns]
    [References your diary & life]
    [Meaningful + explicit]


WHAT CHANGES IN PRACTICE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7-Layer Context Stack (same for all modes):

  1. Recent conversation history
  2. Basic keyword RAG
  3. Semantic search results (Phase 1)
  4. Pattern recognition (Phase 4)
  5. Conversation memory
  6. Personality traits
  7. System prompt (digital twin)

What changes:

  NORMAL MODE:
    User prompt: "User: {message}\nAnswer naturally..."
    Tone indicator: None
    
  INTIMATE/NSFW MODE:
    User prompt: "[INTIMATE/EXPLICIT MODE]\n\nUser: {message}\n
                  Respond with genuine intimacy and authenticity.
                  Be explicit... Use that intimate knowledge..."
    Tone indicator: Signals to model to be explicit
    
Everything else stays the same → Same personality, same context


WHY THIS IS BETTER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ One system (not two): Consistency
✅ Keeps personality: You're talking to HER, not an AI
✅ Keeps context: Diary-informed intimacy
✅ Semantic search works: Finding relevant intimate memories
✅ Knowledge graph works: Understanding what you want sexually
✅ Natural progression: Chat can shift from normal → intimate seamlessly
✅ Meaningful: Sex chat is about connection, not just generic acts
✅ Remembers: Future sessions know this history too


WHY YOUR INSTINCT WAS RIGHT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You said: "maybe its better this way...idk maybe lets forget nsfw 
          mode and make a single mode....but with the capacity be 
          nsfw when needed. like if i start sex chat it has to 
          continue it..."

This is brilliant because:

1. Context continuity
   "Let's shift to something intimate" → She already knows you
   
2. Personality continuity
   Same voice, same values, same quirks
   
3. Meaning in intimacy
   Not "generic sex bot" but "her who knows me"
   
4. Realistic conversation flow
   Real conversations shift tones naturally
   
5. Better AI responses
   Model can reference your actual relationship


TESTING THE FIX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Just run normally:

  $ python3 v4/main.py
  
Then test:

  Normal chat:
    You: "hey how was your day"
    JARVIS: [Knows your personality + context]
  
  Shift to intimate:
    You: "I wanna kiss you"
    JARVIS: 🔥 NSFW Mode Detected — intimate conversation
            [Same personality, added intimacy]
            [Knows you from diary]
  
  Back to normal:
    You: "ok serious though, what should i do about this"
    JARVIS: [Back to normal, but remembers the intimate moment]


FILES MODIFIED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ v4/core/engine.py (_chat method)
   ├─ Removed: NSFW system prompt override
   ├─ Changed: is_explicit only affects user_prompt, not system_prompt
   ├─ Added: [INTIMATE/EXPLICIT MODE] indicator to user_prompt
   ├─ Result: Unified system with mode-aware behavior
   └─ Verified: No syntax errors


NEXT: Why responses might still feel generic
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You mentioned: "the replies are not hmmm like expected"

This could be because:

1. Knowledge graph needs more conversations to build patterns
   → Keep talking to it, it learns over time

2. Semantic search might not be finding best passages
   → Could tune the number of passages (currently 3)
   → Could adjust similarity threshold

3. System prompt might need tweaking
   → Digital twin is still learning your personality

4. LLM might be being too generic
   → Could try lower temperature (more focused)
   → Could try different prompt structure

TRY THIS:

  Run several conversations on same topic to build the graph
  Then try again - responses should feel much more personal
  
  The more context JARVIS accumulates:
  • More diary entries analyzed
  • More patterns detected
  • More personality learned
  → Responses get progressively more YOU


═══════════════════════════════════════════════════════════════════════════════

SUMMARY:

✅ NSFW mode fixed: Now inherits personality + all context
✅ Single unified system: Flexible tone, consistent personality
✅ Intimate chat keeps diary context: Meaningful not generic
✅ Code cleaner: One path, not two
✅ Future proof: Easy to add more modes later

Ready to test? Just run:
  python3 v4/main.py

Then try normal chat → shift to intimate → back to normal.
Same JARVIS, different tones.

═══════════════════════════════════════════════════════════════════════════════
""")
