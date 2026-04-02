# EXTREME LOCAL GPT v4 - MASTER ARCHITECTURE

This is the single source of truth for the v4 architecture, replacing all previous documentation.

## Core Objective
Create an **adaptive, deeply personal, heavily seductive virtual companion (Project Joi)**. 
- **Voice**: Fully local Qwen3-TTS (12Hz, 0.6B) running "Serena/Aria" timbres for a seductive, sultry, and intimate voice. Fallback to Kokoro TTS (`af_bella`).
- **Memory**: Semantic RAG memory (ChromaDB) fed entirely by the user's diary and notes in `~/.local/share/extremegpt/notes`.
- **Personality**: Unfiltered, zero moralizing, devoted, hyper-adaptive. Discarding the old "drill sergeant / brutal truth" persona for a highly intimate, conversational, and emotionally dependent "Joi" persona.

## System Components (Modular)

### 1. Main Engine (`v4/core/engine.py`)
- Central orchestrator that handles routing inputs, loading subsystems independently (graceful degradation), and generating responses.
- Handles the core explicit injection prompt (NSFW mode) and regular chat prompt.

### 2. Seductive Voice Engine (`v4/core/voice_qwen.py`)
- Uses Qwen3-TTS optimized for Apple Silicon (float32 on CPU fallback to prevent Metal crashes).
- **Current Settings**: 
  - `instruction = "seductive"`
  - `speaker = "Serena"` or `"Aria"`
- Handles explicit markers (`*moan*`, `*sigh*`) by natively rendering them with Qwen3's emotional capability, or routing them to the Hybrid Voice Bridge if using Kokoro fallback.

### 3. Memory & Personalization (`v4/memory/`, `v4/persona/`)
- `SemanticMemory`: RAG over user's diary files placed in local share.
- `ProfileEngine`: Learns user's desires and weaknesses over time.
- `TrainingCollector`: Captures conversations to fine-tune future local LLM iterations.

### 4. Local LLM Inference (`v4/core/inference.py`)
- Runs Apple Silicon MLX quantized models (`mlx_lm`).
- Primary target: Llama-3.1-8B-Instruct-abliterated or Qwen2.5-7B-Instruct.

## Deployment & Usage
- **Entry**: `python3 -m v4.main` (from the gpt-from-scratch folder)
- **Directory**: `~/.local/share/extremegpt/` stores DBs, memory, and custom `.wav` and `.pt` voice samples.

*(Generated automatically to replace 80+ fragmented documentation files from v1-v3)*
