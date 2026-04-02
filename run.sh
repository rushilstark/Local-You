#!/bin/bash
# 🚀 STARTUP SCRIPT FOR EXTREME LOCAL GPT v3
# Makes sure we use the right Python with mlx-lm installed

set -e  # Exit on any error

echo "🚀 EXTREME LOCAL GPT v3 - STARTUP"
echo "=================================="
echo ""

# Determine which Python to use
PYTHON_PATH="/Users/rushilreddy/.pyenv/versions/3.11.8/bin/python3"

# Verify Python exists
if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ ERROR: Python not found at $PYTHON_PATH"
    echo "   Using system python3 instead..."
    PYTHON_PATH="python3"
fi

# Check if mlx_lm is available
echo "📦 Checking dependencies..."
if $PYTHON_PATH -c "import mlx_lm" 2>/dev/null; then
    echo "   ✅ mlx_lm: OK"
else
    echo "   ❌ mlx_lm: NOT FOUND"
    echo ""
    echo "📥 INSTALLING DEPENDENCIES..."
    $PYTHON_PATH -m pip install -q mlx-lm
    echo "   ✅ mlx-lm installed"
fi

# Check if v3_system_complete.py exists
if [ ! -f "v3_system_complete.py" ]; then
    echo "❌ ERROR: v3_system_complete.py not found"
    echo "   Make sure you're in the gpt-from-scratch directory"
    exit 1
fi

echo ""
echo "🎯 STARTING SYSTEM..."
echo "   Python: $PYTHON_PATH"
echo "   Command: python3 v3_system_complete.py"
echo ""
echo "════════════════════════════════════════════════════"
echo ""

# Run the system
$PYTHON_PATH v3_system_complete.py

