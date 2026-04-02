#!/bin/bash

# Delete redundant files (functionality merged into v3_system_complete.py)
FILES_TO_DELETE=(
    "v3_debate_engine.py"
    "v3_inference_simple.py"
    "v3_personalization.py"
    "v3_style_adaptation.py"
    "v3_nsfw_direct_mode.py"
    "v3_memory.py"
    "v3_patterns.py"
    "v3_voice.py"
    "v3_user_profile.py"
    "v3_personalization_loader.py"
    "v3_context_injection.py"
    "v3_wisdom.py"
    "v3_outcome_tracker.py"
    "v3_training_data_collector.py"
    "v3_finetuning.py"
    "v3_phase6_hybrid.py"
    "v3_prompts.py"
    "build_memory_rag.py"
    "virtual_rushil_rag.py"
    "virtual_rushil.py"
    "adaptive_trainer.py"
    "jarvis.py"
    "jarvis_unified.py"
    "jarvis_architecture.py"
    "jarvis_ollama_bridge.py"
    "phase6_text_engine.py"
    "rushil_main.py"
    "v3_inference_complete.py"
)

echo "🗑️  Deleting redundant files..."
deleted_count=0

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "  ✓ Deleted: $file"
        ((deleted_count++))
    fi
done

echo ""
echo "✅ Cleanup complete: Deleted $deleted_count redundant files"
echo ""
echo "📁 Remaining Python files:"
ls -lah *.py 2>/dev/null | grep -v "total"
echo ""
echo "🎯 Main entry point: v3_system_complete.py"
echo ""
echo "Usage:"
echo "  python3 v3_system_complete.py"
