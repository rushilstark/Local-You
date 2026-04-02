# 🚀 JARVIS - Your Personal AI Digital Twin

A local, honest, diary-trained AI that **knows YOU** and won't be a yes-man.

## Why JARVIS Over Claude/Gemini?

| Feature | Claude/GPT | JARVIS |
|---------|-----------|--------|
| **Knows YOU** | ✗ Generic | ✓ Trained on your diary |
| **Honest Feedback** | ✗ Always agrees | ✓ Calls out BS patterns |
| **Your Voice** | ✗ Generic tone | ✓ Your personality |
| **Privacy** | ✗ Cloud/Logging | ✓ 100% Local |
| **Memory** | ✗ Limited | ✓ Persistent across sessions |
| **Costs Money** | ✓ Yes | ✓ FREE |

---

## 🎯 What JARVIS Does

### 1. **Reads Your Diary**
- Automatically loads all `.txt` files from `/data/diary/`
- Extracts personality traits: passion, honesty, independence, etc.
- Finds memorable quotes and philosophy from your entries

### 2. **Knows You Deeply**
- Digital Twin trained on your diary entries
- Remembers all conversations
- Retrieves relevant diary passages during conversation (RAG)
- Speaks like YOU would

### 3. **Gives HONEST Feedback**
- **NOT a yes-man** - calls out procrastination, perfectionism, victim mentality
- Example:
  ```
  You: "I'll start next week"
  JARVIS: "No, you won't. You're procrastinating. What's stopping you TODAY?"
  ```

### 4. **Quality Voice (Kokoro)**
- 44.1kHz CD quality audio
- Natural breathing pauses based on punctuation
- Vocal fillers: *giggle*, *moan*, *whimper*, *gasp*, *sigh*
- Sounds intimate and human

### 5. **Conversation Memory**
- Saves every conversation to SQLite
- Builds context across sessions
- Remembers your past goals and struggles

---

## 🏗️ System Architecture

```
JARVIS = Digital Twin + Honest Feedback + Voice + Memory + RAG

┌─────────────────────────────────────────────────────────┐
│                    USER INPUT                           │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────┼──────────────┐
         │             │              │
         ▼             ▼              ▼
    ┌────────────┐ ┌───────┐ ┌──────────────┐
    │  Diary RAG │ │Memoir │ │Digital Twin  │
    │ (179 psgs) │ │(Memory)│ │ (Personality)│
    └────────────┘ └───────┘ └──────────────┘
         │             │              │
         └─────────────┼──────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  LLM (Llama 3.1 8B MLX)       │
        │  + System Prompt (Diary-Based)
        │  + Context (RAG + Memory)     │
        └──────────────────────────────┘
                       │
         ┌─────────────┼──────────────┐
         │             │              │
         ▼             ▼              ▼
    ┌────────────┐ ┌────────┐ ┌─────────┐
    │  Voice TTS │ │ Memory │ │Feedback │
    │ (Kokoro)   │ │(SQLite)│ │Engine   │
    └────────────┘ └────────┘ └─────────┘
         │             │              │
         └─────────────┴──────────────┘
                       │
                       ▼
              ┌──────────────────┐
              │   USER HEARS     │
              │   JARVIS RESPOND │
              └──────────────────┘
```

---

## 🚀 Quick Start

### 1. Add Your Diary
Create text files in `/data/diary/`:
```
/data/diary/my_thoughts.txt
/data/diary/lessons.txt
/data/diary/dreams.txt
```

Just put your real thoughts. JARVIS will learn from them.

### 2. Run It
```bash
python3 v4/main.py
```

JARVIS loads:
- ✓ Your diary (179 passages indexed)
- ✓ Personality extraction (passion, honesty, independence)
- ✓ LLM (Llama 3.1 8B)
- ✓ Voice (Kokoro TTS)
- ✓ Memory system (SQLite)
- ✓ Honest Feedback Engine

### 3. Chat
```
You: What do you think about my diary?

JARVIS: [Reads your actual diary entries and quotes them back]
Your diary shows passion, honesty, and independence. 
But I see you struggling with procrastination patterns:
  • "I'll start next week" (repeated in entries 5, 12, 67)
  • Fear of people holding you back
  • Using addiction as escape instead of action

Here's the truth: You have potential but you're using fear as an excuse.
Start TODAY, not next week. 15 minutes on what matters.
```

---

## 📊 Key Features

### Diary-Based Personality
- **Extracted from your entries:**
  - Passion: 7/10
  - Honesty: 6/10
  - Independence: 6/10
  - Growth mindset: 6/10
  - Ambition: 6/10
  - Vulnerability: 6/10

### Retrieval Augmented Generation (RAG)
- 179 diary passages indexed
- Dynamically retrieved during conversation
- Example:
  ```
  User: "I'm scared of failure"
  [JARVIS retrieves 2 related diary passages]
  [Includes them in context]
  JARVIS: "You wrote about this before: '[diary quote]'
  You're repeating the same fear pattern."
  ```

### Honest Feedback Patterns
Detects and calls out:
- ✓ Procrastination ("I'll do it later")
- ✓ Perfectionism ("It has to be perfect")
- ✓ Victim mentality ("Everyone has it worse")
- ✓ False confidence ("I'm definitely right")

### Voice Enhancement
- Natural breathing pauses (ellipsis expansion: `. ` → `... `)
- Vocal fillers matching emotion
- 44.1kHz CD quality
- Female voice option (Bella, Sarah, Heart)

### Persistent Memory
- SQLite stores all conversations
- Builds context over time
- References past goals and patterns
- 10 message history window

---

## 🛠️ Advanced Features

### Fine-Tuning (Future)
JARVIS can be fine-tuned on your conversations using LoRA:
```bash
python3 v4/train/mlx_lora_train.py
```

Will create personalized adapter weights that make JARVIS sound even more like you.

### Semantic Memory
When enabled, debates/conversations are indexed for semantic search.

### Training Data Collection
System automatically collects high-quality conversation pairs for fine-tuning.

---

## 📁 File Structure

```
gpt-from-scratch/
├── data/
│   └── diary/
│       ├── Google Keep Document.txt     (Your diary entries)
│       ├── my_thoughts.txt              (Add more here)
│       └── ...
│
├── digital_twin_diary_engine.py         (Personality extraction)
├── jarvis_honest_feedback_engine.py     (BS pattern detection)
├── jarvis_digital_twin.py               (Digital twin orchestrator)
├── diary_rag.py                         (Retrieval system)
│
├── v4/
│   ├── main.py                          (Start here)
│   ├── config.yaml                      (Configuration)
│   ├── core/
│   │   ├── engine.py                    (Main orchestrator)
│   │   ├── inference.py                 (LLM inference)
│   │   ├── voice.py                     (Kokoro TTS)
│   │   └── config.py                    (Configuration loading)
│   ├── memory/
│   │   └── conversation.py              (SQLite memory)
│   ├── debate/
│   │   └── pipeline.py                  (Debate mode)
│   └── train/
│       └── mlx_lora_train.py            (Fine-tuning)
│
└── START_JARVIS.py                      (Quick reference)
```

---

## 💻 System Requirements

- **Mac with Apple Silicon** (M1, M2, M3, etc.)
- **16GB+ RAM** (recommended)
- **Python 3.9+**

### Dependencies
```bash
pip install mlx mlx-lm
pip install torch-tts  # For Kokoro
```

---

## 🎓 How JARVIS Learns

### Phase 1: Initialization
1. Reads all diary entries
2. Extracts personality traits
3. Creates digital twin system prompt
4. Indexes 179+ diary passages

### Phase 2: First Conversation
1. LLM loads (Llama 3.1 8B)
2. Your personality injected into system prompt
3. Diary RAG ready for context
4. Conversation memory initialized

### Phase 3: Ongoing Learning
1. Every conversation saved to SQLite
2. Patterns detected (procrastination, etc.)
3. Personality refined with new data
4. Future responses become more personalized

### Phase 4: Fine-Tuning (Optional)
1. Collect 50+ high-quality conversations
2. Run LoRA training on your speech patterns
3. Create personalized adapter weights
4. JARVIS sounds exactly like you

---

## 🔒 Privacy

- ✓ 100% local (no cloud)
- ✓ Your diary never leaves your machine
- ✓ No tracking, no analytics
- ✓ No API calls
- ✓ All data stored locally in SQLite + txt files

---

## 📝 Commands

In the chat:
```
help              - Show all commands
voice on/off      - Toggle TTS voice output
voice list        - List available voices
voice [name]      - Change voice (bella, sarah, heart, etc)
quit / exit       - Close app
```

Just type normally to chat.

---

## 🚨 Troubleshooting

### "Digital Twin initialized but not using personality"
→ Check `/data/diary/` has `.txt` files
→ Run `python3 test_diary_reading.py` to verify

### "Responses are generic"
→ Add more diary entries
→ Run `python3 diary_rag.py` to verify RAG indexed passages
→ System improves with more context

### "Voice not working"
→ Check Kokoro installed: `pip install torch-tts`
→ Try toggling: `voice off` then `voice on`
→ System falls back to text if voice fails

### "Token limits too low"
→ Edit `v4/core/config.py`
→ Increase `max_tokens` (currently 2000 for chat)

---

## 🎯 Next Steps

1. **Add Your Diary** → Create `/data/diary/` files
2. **Start Chatting** → `python3 v4/main.py`
3. **Test Honesty** → Ask "I'll do this later"
4. **Reference Diary** → Ask "What did I write about fear?"
5. **Fine-Tune** → After 50+ conversations

---

## 📖 Philosophy

JARVIS is built on one principle:

> **You deserve an AI that knows you and tells you the truth.**
> 
> Not a yes-man. Not a generic chatbot.
> 
> A digital twin that reflects your values, remembers your struggles,
> and pushes you to grow.

---

## 🙏 Built With

- **MLX** - Apple Silicon optimization
- **Llama 3.1 8B** - Fast, capable LLM
- **Kokoro** - High-quality voice synthesis
- **Python** - 100% local, no dependencies on cloud

---

**Made for people who value honesty over flattery.**

`python3 v4/main.py`

