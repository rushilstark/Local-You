#!/bin/bash
# 🧹 CLEANUP SCRIPT - Remove old files, keep only the hybrid system
# Run: bash cleanup_workspace.sh

echo "🧹 CLEANING WORKSPACE..."

# Files to KEEP (new hybrid system)
KEEP_FILES=(
    "rushil_hybrid_system.py"
    "train.jsonl"
    "data.txt"
    "adapters"
    "rushil_memory_db"
    "conversation_log.json"
    "rushil_profile.json"
)

# OLD SYSTEMS TO REMOVE
OLD_DEBATE_SYSTEM=(
    "v3_system.py"
    "v3_debate_engine.py"
    "v3_inference_simple.py"
    "v3_prompts.py"
    "v3_personalization.py"
    "v3_style_adaptation.py"
    "v3_nsfw_direct_mode.py"
    "v3_inference.py"
)

OLD_DIGITAL_TWIN=(
    "digital_twin_orchestrator.py"
    "digital_twin_system_prompt.py"
    "privacy_data_sanitizer.py"
    "phase1_advanced_data_synthesizer.py"
)

# DOCS TO REMOVE (keep only essential)
OLD_DOCS=(
    "MASTER_SUMMARY.md"
    "FIX_SUMMARY.md"
    "CURRENT_STATUS.md"
    "PHASE1_COMPLETE.md"
    "PHASE2_COMPLETE.md"
    "PHASE1_2_INTEGRATION.md"
    "STATUS.md"
    "ARCHITECTURE.md"
    "PHASE3_COMPLETE_INTEGRATION.md"
    "SYSTEM_DIAGNOSIS_REPORT.md"
    "FIX_PLAN_DIGITAL_TWIN.md"
)

echo ""
echo "Removing old debate system files..."
for file in "${OLD_DEBATE_SYSTEM[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "  ✗ Removed $file"
    fi
done

echo ""
echo "Removing old digital twin files..."
for file in "${OLD_DIGITAL_TWIN[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "  ✗ Removed $file"
    fi
done

echo ""
echo "Removing old documentation..."
for file in "${OLD_DOCS[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "  ✗ Removed $file"
    fi
done

# Remove other unnecessary files
echo ""
echo "Removing other unnecessary files..."
rm -f debates.json 2>/dev/null
rm -f personal_profile.json 2>/dev/null
rm -f user_preferences.json 2>/dev/null
rm -f jarvis_feedback.json 2>/dev/null
rm -f jarvis_preferences.json 2>/dev/null
rm -f system_prompt_personalized.txt 2>/dev/null
echo "  ✗ Removed old data files"

echo ""
echo "✅ CLEANUP COMPLETE"
echo ""
echo "Remaining files:"
ls -lh *.py *.md 2>/dev/null | awk '{print "  " $9}'
echo ""
echo "🚀 To run the new system:"
echo "   python rushil_hybrid_system.py"
