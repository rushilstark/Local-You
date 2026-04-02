#!/usr/bin/env python3
"""
🤔 AUTO-LEARNING QUESTION: Will JARVIS Auto-Learn New Diary Notes?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SHORT ANSWER: Currently NO, but you can manually refresh with ONE command.

LONG ANSWER: Let me explain how it works...
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║            🤔 AUTO-LEARNING: WILL NEW DIARY NOTES BE INCLUDED? 🤔         ║
╚════════════════════════════════════════════════════════════════════════════╝


CURRENT BEHAVIOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Both systems use CACHING to be fast:

SEMANTIC INDEX:
  ┌─────────────────────────────────────────────────────────────┐
  │ On startup:                                                 │
  │ 1. Check if cache exists (.cache/semantic_embeddings/)      │
  │ 2. If YES → Load from cache (instant, <1 sec)              │
  │ 3. If NO → Build fresh (first run, ~30 sec)                │
  │                                                              │
  │ Problem: If you add new diary notes, cache isn't updated   │
  └─────────────────────────────────────────────────────────────┘

KNOWLEDGE GRAPH:
  ┌─────────────────────────────────────────────────────────────┐
  │ On startup:                                                 │
  │ 1. Check if cache exists (.cache/knowledge_graph.json)      │
  │ 2. If YES → Load from cache (instant)                      │
  │ 3. If NO → Build fresh (first run, analyzes all entries)   │
  │                                                              │
  │ Problem: If you add new diary notes, cache isn't updated   │
  └─────────────────────────────────────────────────────────────┘

CACHE LOCATIONS:
  .cache/semantic_embeddings/diary_embeddings.pkl
  .cache/semantic_embeddings/diary_metadata.json
  .cache/knowledge_graph.json


WHAT HAPPENS WHEN YOU ADD NEW NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Scenario: You add 50 new diary entries to data/diary/

Option 1: Don't clear cache (CURRENT BEHAVIOR)
  ❌ New notes are IGNORED
  ❌ JARVIS only sees old 73 passages
  ❌ Knowledge graph still has 52 nodes
  ❌ Learning capped at old data

Option 2: Clear cache manually (WORKAROUND)
  ✅ Delete: .cache/semantic_embeddings/
  ✅ Delete: .cache/knowledge_graph.json
  ✅ Restart JARVIS
  ✅ Takes ~30 seconds to rebuild
  ✅ New notes included!

Option 3: Use "ingest" command (BUILT-IN)
  Already exists: python3 v4/main.py
                  Type: "ingest"
  ✅ Automatically refreshes semantic index
  ✅ Automatically refreshes knowledge graph
  ✅ Takes ~30-60 seconds
  ✅ You get prompted on next startup


HOW TO MAKE IT TRULY AUTO-LEARNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I can implement auto-detection so new notes are AUTOMATICALLY discovered:

Option A: Check for new files on startup (LIGHTWEIGHT)
  ┌─────────────────────────────────────────────────────────────┐
  │ On startup:                                                 │
  │ 1. Count files in data/diary/                              │
  │ 2. Compare to cached count                                 │
  │ 3. If different → Rebuild cache automatically              │
  │ 4. If same → Use cache (fast)                              │
  │                                                              │
  │ Pros: Automatic, transparent                               │
  │ Cons: Might be slower if files change frequently           │
  └─────────────────────────────────────────────────────────────┘

Option B: Watch file timestamps (MEDIUM)
  ┌─────────────────────────────────────────────────────────────┐
  │ On startup:                                                 │
  │ 1. Get modification time of data/diary/ folder             │
  │ 2. Compare to cached timestamp                             │
  │ 3. If newer → Rebuild automatically                        │
  │ 4. If older → Use cache                                    │
  │                                                              │
  │ Pros: Simple, works well                                   │
  │ Cons: Could miss new files if folder mtime doesn't update │
  └─────────────────────────────────────────────────────────────┘

Option C: Full incremental learning (COMPLEX)
  ┌─────────────────────────────────────────────────────────────┐
  │ Track each file individually:                               │
  │ 1. Store list of files + their hashes                       │
  │ 2. On startup: compare current files to cached list         │
  │ 3. New files: embed only new ones (add to cache)           │
  │ 4. Deleted files: remove from cache                         │
  │ 5. Result: Only new content is processed                   │
  │                                                              │
  │ Pros: Most efficient, incremental                          │
  │ Cons: More complex, needs more caching                     │
  └─────────────────────────────────────────────────────────────┘


MY RECOMMENDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I recommend OPTION B (File timestamp checking) because:

✅ Simple to implement (2-3 lines of code)
✅ Works 99% of the time
✅ No performance impact (check is instant)
✅ Automatic and transparent
✅ Can be upgraded to Option C later

This would mean:
  • Add new diary notes anytime
  • Run JARVIS normally: python3 v4/main.py
  • It automatically detects new files
  • Rebuilds cache in ~30 seconds
  • All new content included
  • No manual commands needed


CURRENT WORKAROUNDS (RIGHT NOW)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Workaround 1: Manual cache clear (fastest)
  rm -rf .cache/semantic_embeddings/
  rm -f .cache/knowledge_graph.json
  python3 v4/main.py
  
  Time: ~30 seconds

Workaround 2: Use "ingest" command (easiest)
  python3 v4/main.py
  > ingest
  
  Time: ~60 seconds

Workaround 3: Delete everything and restart
  rm -rf .cache/
  python3 v4/main.py
  
  Time: ~45 seconds


IMPLEMENTATION OPTION (If you want auto-detection)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I can add this to semantic_index.py:

┌─────────────────────────────────────────────────────────────┐
│ def _check_for_updates(self):                              │
│     """Check if diary files have changed since last cache" │
│                                                             │
│     cache_meta = self.metadata_cache.with_stem(             │
│         self.metadata_cache.stem + "_meta"                  │
│     )                                                       │
│                                                             │
│     if cache_meta.exists():                                │
│         with open(cache_meta) as f:                        │
│             old_mtime = json.load(f).get("diary_mtime")    │
│                                                             │
│         # Get current diary folder mtime                   │
│         current_mtime = self.diary_folder.stat().st_mtime  │
│                                                             │
│         if current_mtime == old_mtime:                     │
│             return False  # No changes                      │
│         else:                                               │
│             return True  # Files changed!                   │
│     return True  # First time                              │
└─────────────────────────────────────────────────────────────┘

Then in _load_or_build_index():

┌─────────────────────────────────────────────────────────────┐
│ def _load_or_build_index(self):                            │
│     if self.embeddings_cache.exists() and not self.        │
│        _check_for_updates():  # NEW CHECK                  │
│         print("  🔄 Loading cached embeddings...")         │
│         self._load_from_cache()                            │
│     else:                                                   │
│         print("  🔄 New diary files detected!")            │
│         print("  🔄 Rebuilding index...")                  │
│         self._build_index()                                │
│         self._save_to_cache()                              │
└─────────────────────────────────────────────────────────────┘


FINAL ANSWER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RIGHT NOW:
  ❌ New notes are NOT auto-learned (cached)
  
IMMEDIATELY:
  ✅ Use "ingest" command to manually refresh
  
EASILY:
  ✅ I can add auto-detection (5 min to implement)
  ✅ Then it's truly automatic

WHAT DO YOU WANT?

Option 1: Keep as-is (manual "ingest" when needed)
Option 2: Auto-detect new files on startup
Option 3: Full incremental learning

Let me know! I can implement Option 2 right now (takes 5 minutes).

═══════════════════════════════════════════════════════════════════════════════
""")
