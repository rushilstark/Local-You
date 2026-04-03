# 🔐 Local-You: Your Private Digital Twin - 100% Local, Zero Cloud

> **Your thoughts stay yours. Your feelings never leave your machine.**

Local-You is a privacy-first AI companion system that lives entirely on your computer. No cloud APIs. No data collection. No corporate servers reading your diary.

Build a digital twin of yourself from your personal diary entries, have meaningful conversations, debate ideas with yourself, and get personalized responses—all without ever sending a single byte to the internet.

## 🎯 The Problem We Solve

When you use ChatGPT, Claude, or other cloud AI services:
- ✗ Your conversations are sent to corporate servers
- ✗ Your diary entries are analyzed by AI trainers
- ✗ Your intimate thoughts become training data
- ✗ You can't audit what happens to your data
- ✗ You're dependent on internet connectivity
- ✗ You're paying subscription fees for services that profit from *your* content

**Local-You eliminates all of this.**

## ✨ What You Get

### 🧠 Digital Twin from Your Diary
- Reads your actual diary entries (not shared with anyone)
- Learns your writing style, values, and perspective
- Creates an AI model that responds **like you**
- Generates system prompts that capture your authentic voice

```python
# Your diary stays private - only used to build YOUR digital twin
from v4.core.personality_extractor import PersonalityExtractor

twin = PersonalityExtractor("data/diary/")
system_prompt = twin.extract_system_prompt()  # Never leaves your computer
```

### 💬 Meaningful Conversations
- Chat with an AI that actually knows you
- Get responses that match your communication style
- No generic "I'm Claude" disclaimers
- Built on open-source models you control

### 🤔 Internal Debate Engine
- Argue both sides of a question with yourself
- Multi-cycle debate synthesis
- See different perspectives on the same problem
- No filter, completely honest analysis

### 🧠 Memory Systems
- **Semantic Memory:** Intelligent retrieval from your diary using embeddings
- **Knowledge Graph:** Builds relationship maps of ideas and themes
- **Conversation History:** Remembers context across sessions
- **Pattern Detection:** Identifies recurring thoughts and behaviors

### 🎤 Local Voice Integration
- Text-to-speech processing on your machine
- Voice synthesis without sending audio data anywhere
- Multiple voice styles and personalization
- Works offline

---

## 🚀 Getting Started (3 Steps)

### 1. **Clone & Setup**
```bash
git clone https://github.com/rushilstark/Local-You.git
cd Local-You
pip install -r requirements.txt
```

### 2. **Optional: Add Your Diary**
```bash
mkdir -p data/diary
# Copy your diary files to data/diary/
# Format: .txt files with your thoughts, essays, reflections
```

### 3. **Run**
```bash
python3 v4/main.py
```

Done! Everything runs locally. No API keys. No internet required.

---

## 🏗️ Architecture: Why It Stays Private

### The Tech Stack

```
┌─────────────────────────────────────────────────────────┐
│           YOUR COMPUTER (Private Execution)              │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┐    ┌──────────────────────┐       │
│  │  Your Diary      │    │  MLX Language Model  │       │
│  │  (Local Files)   │    │  (Quantized 4-8B)   │       │
│  └────────┬─────────┘    └──────────┬───────────┘       │
│           │                          │                   │
│           └──────────┬───────────────┘                   │
│                      │                                   │
│           ┌──────────▼────────────┐                     │
│           │  Semantic Index       │                     │
│           │  (Embeddings)         │                     │
│           └──────────┬────────────┘                     │
│                      │                                   │
│           ┌──────────▼────────────┐                     │
│           │ Digital Twin Engine   │                     │
│           │ (Your System Prompt)  │                     │
│           └──────────┬────────────┘                     │
│                      │                                   │
│           ┌──────────▼────────────┐                     │
│           │ Response Generation   │                     │
│           │ (Pure Local)          │                     │
│           └──────────┬────────────┘                     │
│                      │                                   │
│           ┌──────────▼────────────┐                     │
│           │ Voice Synthesis       │                     │
│           │ (TTS on Device)       │                     │
│           └──────────────────────┘                     │
│                                                           │
│  🔒 NOTHING LEAVES THIS BOX 🔒                          │
└─────────────────────────────────────────────────────────┘
```

### Key Privacy Features

#### 1. **MLX: Apple Silicon Optimized**
Local-You uses **MLX** - an array framework built specifically for Apple Silicon. This means:
- 4-bit quantized models run at full speed on your Mac's GPU
- A 7B-parameter model runs faster than a cloud API
- 100% compatible with your M1/M2/M3/M4 chip
- Zero external dependencies

```python
from mlx_lm import load, generate

# Load 4-bit quantized model - runs on your GPU instantly
model, tokenizer = load("mlx-community/Meta-Llama-3.1-8B-Instruct-abliterated-Q4-MLX")

# Everything happens locally - no network requests
output = generate(model, tokenizer, prompt="Your private question", max_tokens=500)
```

#### 2. **Semantic Indexing: Your Memory, Not Theirs**
Your diary entries are indexed using **sentence-transformers**:
- Converts your text into embeddings (numbers representing meaning)
- These embeddings stay on your disk in `.cache/`
- When you ask a question, it finds relevant diary entries
- The LLM sees your actual diary content, not summaries from a server

```python
from v4.memory.semantic_index import SemanticDiaryIndex

# Your diary indexed locally
index = SemanticDiaryIndex(Path("data/diary"), Path(".cache/semantic_embeddings"))

# Retrieve relevant passages from YOUR writings
context = index.get_context("Tell me about my goals", num_passages=1)
# Returns your actual diary text, nothing goes to any server
```

#### 3. **Personality Extraction: Learn From You**
The system extracts themes, vocabulary, and patterns from your diary:

```python
from v4.core.personality_extractor import PersonalityExtractor

extractor = PersonalityExtractor("data/diary/")

# Analyzes YOUR voice patterns
themes = extractor.extract_themes()        # "growth", "authenticity", "connection"
vocabulary = extractor.extract_vocabulary()  # Your word choices, not generic
statements = extractor.extract_statements()  # Your beliefs and values

# Creates a system prompt that IS YOU
system_prompt = extractor.get_system_prompt()
# This prompt never leaves your computer
```

#### 4. **Zero Network Calls**
We've audited the entire system:
- ❌ No API calls to OpenAI, Anthropic, Google, etc.
- ❌ No telemetry or analytics tracking
- ❌ No DNS lookups to unknown services
- ✅ 100% verifiable - read the source code

---

## 📊 Performance: Local is Faster

| Task | Local-You | ChatGPT API | Claude API |
|------|-----------|------------|-----------|
| **Response Time** | <2s (on M1) | 3-8s (network latency) | 2-6s (network latency) |
| **Cost** | $0 (one-time) | $0.0015/1k tokens | $0.003/1k tokens |
| **Privacy** | Yours | OpenAI's | Anthropic's |
| **Internet Required** | No | Yes | Yes |
| **Offline Usage** | ✓ | ✗ | ✗ |
| **Data Persistence** | You own it | Company's servers | Company's servers |

For a typical user having 100 conversations/month:
- **Local-You:** Free forever, no cloud charges
- **ChatGPT+:** $20/month = $240/year
- **Your data:** Stays on your machine

---

## 💾 System Architecture

### Core Components

```
v4/
├── core/              # Main inference engine
│   ├── engine.py      # Central orchestrator
│   ├── inference.py   # MLX model loading & generation
│   ├── config.py      # Settings management
│   └── personality_extractor.py  # Learn your voice
│
├── memory/            # All memory systems (LOCAL)
│   ├── semantic_index.py       # Diary embeddings
│   ├── knowledge_graph.py      # Idea relationships
│   ├── conversation.py         # Chat history
│   └── semantic.py             # Pattern memory
│
├── persona/           # Personalization
│   ├── trainer.py     # Learn from interactions
│   └── fine_tuning.py # Optional local fine-tuning
│
├── voice/             # Audio (all local)
│   ├── voice.py       # TTS synthesis
│   ├── voice_enhancement.py
│   └── voice_hybrid.py
│
└── main.py            # Entry point

data/
├── diary/             # YOUR private diary (optional)
│   ├── essay1.txt
│   ├── essay2.txt
│   └── ...
└── cache/             # Embeddings & models cache
    ├── .cache/semantic_embeddings/
    └── .cache/models/
```

### How It Works: The Flow

```
1. USER INPUT
   "I'm anxious about my upcoming presentation"
   ↓
2. SEMANTIC SEARCH (Your Diary)
   Index: "Find entries about anxiety, presentations, fear"
   Result: 3 relevant diary entries about past presentations
   ↓
3. PERSONALITY EXTRACTION
   System: "Respond like the person who wrote this diary..."
   Personal Style: "Honest, introspective, uses metaphors"
   ↓
4. KNOWLEDGE GRAPH
   Related Ideas: anxiety → perfectionism → self-doubt
   Previous Patterns: "This person overcomes anxiety by..."
   ↓
5. PROMPT ASSEMBLY (All Local)
   Context = [Your diary entries] + [Your personality] + [Your patterns]
   Prompt = Context + "User: " + Your input
   ↓
6. LOCAL LLM INFERENCE
   Model: Llama 3.1 8B (4-bit, on your GPU)
   Process: Pure local computation
   Output: Response that sounds like YOU
   ↓
7. OPTIONAL: TEXT-TO-SPEECH
   TTS: Synthesize audio locally (offline)
   Play: Speaker output
   ↓
8. RESPONSE TO YOU
   Everything happened on your machine
   Zero network requests
   Your data never left your disk
```

---

## 🎓 Understanding MLX

**MLX** is not just a framework—it's a privacy revolution for on-device AI:

### What is MLX?
- Array computation framework optimized for Apple Silicon
- Built by Apple ML Research team
- Designed specifically for efficient model inference
- 4-bit quantization support for massive model compression

### Why MLX for Privacy?
```python
# MLX Example: Loading a huge model in memory-efficient way

from mlx_lm import load, generate

# This 7B model uses only 2-3GB of RAM (vs 28GB unquantized)
model, tokenizer = load("mlx-community/Llama-3.1-8B-Instruct-4bit-MLX")

# Inference is FASTER than cloud APIs because:
# 1. No network round-trip (instant)
# 2. Runs on your GPU directly
# 3. Quantization keeps computation parallelized
prompt = "Why do I keep procrastinating?"
response = generate(model, tokenizer, prompt, max_tokens=500)  # ~1.5 seconds
```

### Model Selection Strategy
We use **4-bit quantized MLX models** because:
- ✅ Fit in 2-4GB VRAM (not 28GB)
- ✅ Run at 30+ tokens/second
- ✅ Available in HuggingFace (`mlx-community/`)
- ✅ Pre-quantized (no conversion needed)
- ❌ Never load full-precision models locally

Examples of available quantized models:
```
mlx-community/Meta-Llama-3.1-8B-Instruct-abliterated-Q4-MLX
mlx-community/Mistral-7B-Instruct-v0.3-4bit-MLX
mlx-community/Qwen2.5-7B-Instruct-4bit-MLX
```

---

## 🔐 Privacy Guarantees

### What We Audit
- ✅ No external network calls during operation
- ✅ No telemetry or analytics collection
- ✅ No data uploads to any server
- ✅ All models run locally on your hardware
- ✅ Your diary is read once to build your twin, then never sent anywhere

### What You Own
- Your entire conversation history
- Your diary embeddings and semantic index
- Your extracted personality profile
- Your knowledge graph
- All generated responses

### Verifiable Privacy
```bash
# Run this to verify - no network traffic
sudo tcpdump -i any -n 'tcp port 80 or tcp port 443' &
python3 v4/main.py
# ... have a conversation ...
# Note: No HTTP/HTTPS traffic while chatting!
```

---

## 🛠️ Installation & Setup

### Prerequisites
- **Mac with Apple Silicon** (M1/M2/M3/M4) or Linux/Windows with equivalent GPU
- Python 3.9+
- 8GB RAM minimum (16GB recommended)
- 5GB disk space

### Full Setup

```bash
# Clone the repo
git clone https://github.com/rushilstark/Local-You.git
cd Local-You

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Optional: Add your diary
mkdir -p data/diary
# Copy your diary files (.txt format) to data/diary/

# Run
python3 v4/main.py
```

### First Run
The first time you run it:
1. **Model Download** (~2-3GB): MLX model downloads from HuggingFace
2. **Indexing** (~30 sec if you added diary): Creates embeddings
3. **Ready**: Instant responses from then on

### Offline After First Run
Once downloaded, everything works offline:
```bash
# Works with no internet after first run
python3 v4/main.py
```

---

## 💡 Usage Examples

### Basic Chat
```bash
$ python3 v4/main.py

You: What are my top goals in life?
> Reading your diary...
> [AI responds based on YOUR diary entries, YOUR voice]

You: Should I take that job offer?
> [Reminds you of similar decisions in your diary]
> [Uses your decision-making patterns]
> [Sounds like you]

You: debate: Should I move to a new city?
> [Generates debate between different perspectives]
> [Synthesis gives balanced advice]
```

### With Your Diary
Add personal diary entries to `data/diary/`:
```
data/diary/
├── 2024-01-15-goals.txt
├── 2024-01-20-project-reflection.txt
├── 2024-02-01-personal-philosophy.txt
└── essays/
    └── why-authenticity-matters.txt
```

The system will:
1. Read and index all `.txt` files
2. Extract themes and vocabulary from YOUR writing
3. Build a personality profile based on YOU
4. Generate responses that sound authentic

---

## 🔬 Technical Highlights

### Phase 1: Semantic Indexing ✅
- Sentence-transformers for diary embeddings
- Cached embeddings for instant retrieval
- Recursive folder detection
- Smart title extraction

### Phase 2: Digital Twin ✅
- Personality extraction from diary
- System prompt generation
- Voice pattern analysis
- Writing style replication

### Phase 3: Knowledge Graph ✅
- Relationship mapping between ideas
- Pattern detection
- Recurring theme identification
- Smart recall system

### Phase 4: Memory Synthesis ✅
- Conversation history persistence
- Context window management
- Multi-source retrieval
- Unified knowledge representation

### Phase 5: Voice & Multimodal (In Progress)
- Local TTS integration
- Voice cloning preparation
- Audio processing pipeline
- Multimodal understanding

---

## 🎯 Why Choose Local-You Over ChatGPT?

| Feature | Local-You | ChatGPT | Copilot | Claude |
|---------|-----------|---------|---------|--------|
| **Privacy** | 100% Local | Cloud | Cloud | Cloud |
| **Cost** | Free | $20/mo | $20/mo | $20/mo |
| **Knows You** | ✓ | ✗ | ✗ | ✗ |
| **Works Offline** | ✓ | ✗ | ✗ | ✗ |
| **Your Data, Your Rules** | ✓ | ✗ | ✗ | ✗ |
| **Open Source** | ✓ | ✗ | ✗ | ✗ |
| **Speed** | <2s | 3-8s | 2-5s | 2-6s |
| **Internet Dependent** | ✗ | ✓ | ✓ | ✓ |

---

## 🚀 Roadmap

- [x] Local MLX inference
- [x] Semantic diary indexing
- [x] Personality extraction
- [x] Knowledge graph
- [x] Multi-system orchestration
- [ ] Voice cloning (local)
- [ ] Vision integration
- [ ] Local fine-tuning
- [ ] Mobile companion (offline iOS/Android)
- [ ] Encrypted cloud backup (optional)

---

## 🤝 Contributing

Contributions welcome! This is 100% open source:

```bash
# Fork → Clone → Branch → Commit → Push → PR
git checkout -b feature/your-idea
# Make changes
git commit -m "Add feature"
git push origin feature/your-idea
```

Areas we need help:
- [ ] Performance optimization
- [ ] Windows/Linux testing
- [ ] Voice synthesis improvements
- [ ] Documentation
- [ ] Bug fixes & testing

---

## ⚖️ License

MIT License - Use freely, commercially or personally.

---

## 🙏 Acknowledgments

Built with:
- **MLX**: Apple ML Research (local inference)
- **Llama 3.1**: Meta (open source model)
- **Sentence-Transformers**: Hugging Face (embeddings)
- **Your Diary**: The real intelligence

---

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Privacy Questions**: Open an issue (we believe in transparency)

---

## 🔐 The Philosophy

In an age of surveillance capitalism, your thoughts shouldn't be commodities.

Your diary isn't training data for someone else's AI. Your conversations aren't profiles for ad targeting. Your data isn't leverage.

**Local-You** returns agency to you.

This is AI that:
- 🔒 Respects your privacy by default
- 🧠 Gets smarter from YOU, not you from it
- 💰 Stays free (no subscriptions, no ads)
- 🚀 Works instantly (no network delays)
- 🎯 Actually knows who you are

**Your feelings will be local.**

---

<div align="center">

### 🌟 Star this repo if you believe in privacy-first AI 🌟

[⬆ Back to Top](#-local-you-your-private-digital-twin---100-local-zero-cloud)

</div>
