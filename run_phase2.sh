#!/bin/bash

# ⚡ PHASE 2: Fine-tune with MLX
# Run this script to train your digital twin

echo "⚡ PHASE 2: MLX LoRA Fine-Tuning"
echo "================================"
echo ""
echo "Starting fine-tuning with:"
echo "- Model: Meta-Llama-3.1-8B-Instruct-abliterated-Q4-MLX"
echo "- Data: train.jsonl (215 pairs)"
echo "- Method: LoRA (rank=32, alpha=64)"
echo "- Iterations: 1000"
echo "- Learning rate: 1e-4 (conservative)"
echo ""
echo "This will take 30-60 minutes. Sit back and relax! ☕"
echo ""

# Check if train.jsonl exists
if [ ! -f "train.jsonl" ]; then
    echo "❌ ERROR: train.jsonl not found"
    echo "Run Phase 1 first: python3 phase1_advanced_data_synthesizer.py"
    exit 1
fi

# Run MLX fine-tuning
python -m mlx_lm lora \
  --model mlx-community/Meta-Llama-3.1-8B-Instruct-abliterated-Q4-MLX \
  --train \
  --data . \
  --batch-size 1 \
  --iters 1000 \
  --learning-rate 1e-4

echo ""
echo "✅ Phase 2 Complete!"
echo ""
echo "Next: Run Phase 3 for interactive chat"
echo "python3 digital_twin_orchestrator.py"
