#!/bin/bash

# 🚀 RUSHIL - QUICK START SCRIPT

echo "
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║                  🚀 RUSHIL - AI CLONE SETUP                   ║
║                                                                ║
║  One file. Complete system. Your authentic voice.             ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"

# Check Python version
echo "📦 Checking Python..."
python3 --version

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install chromadb sentence-transformers -q
echo "✓ Dependencies installed"

# Verify files exist
echo ""
echo "📋 Checking required files..."

FILES=(
  "rushil_main.py"
  "data.txt"
  "user_profile_extracted.json"
  "system_prompt_personalized.txt"
)

for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "  ✓ $file"
  else
    echo "  ✗ MISSING: $file"
  fi
done

# Build memory brain if needed
echo ""
echo "🧠 Setting up memory brain..."

if [ ! -d "rushil_memory_db" ]; then
  echo "  Building vector database..."
  python3 -c "
from rushil_main import Rushil
r = Rushil()
print('  ✓ Memory brain ready')
" 2>/dev/null || echo "  ⚠ Brain will build on first run"
else
  echo "  ✓ Memory brain exists ($(du -sh rushil_memory_db | cut -f1))"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "✅ SETUP COMPLETE!"
echo ""
echo "Ready to use Rushil. Start with:"
echo ""
echo "   python3 rushil_main.py"
echo ""
echo "Then try these commands:"
echo "   • profile          - See your personality"
echo "   • search: love     - Search your diary"
echo "   • debate: career   - Run a 3-cycle debate"
echo "   • help             - All commands"
echo ""
echo "════════════════════════════════════════════════════════════════"
