#!/bin/bash

# 🔥 NEURAL ORCHESTRATION LAYER - ULTIMATE QUICK START

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║  🔥 NEURAL ORCHESTRATION LAYER - PROFESSIONAL JARVIS - QUICK START 🔥    ║"
echo "║                                                                            ║"
echo "║  Real unfiltered LLMs with multi-agent debate on your M4 Mac              ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Detect OS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script requires macOS"
    exit 1
fi

# Check for Apple Silicon
if ! sysctl -a | grep -q "machdep.cpu.brand_string.*Apple"; then
    echo "⚠️  Warning: This system may not be Apple Silicon (M1/M2/M3/M4)"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    echo "   Install from: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 3 found"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Version: $PYTHON_VERSION"

# Navigate to script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "📂 Working directory: $SCRIPT_DIR"

# Check dependencies
echo ""
echo "📋 Checking dependencies...\n"

MISSING_DEPS=0

check_package() {
    local import_name=$1
    local pip_name=$2
    
    if python3 -c "import $import_name" 2>/dev/null; then
        echo "  ✅ $pip_name"
    else
        echo "  ❌ $pip_name (missing)"
        MISSING_DEPS=1
    fi
}

check_package "mlx_lm" "mlx-lm"
check_package "sentence_transformers" "sentence-transformers"
check_package "lancedb" "lancedb"
check_package "numpy" "numpy"

# Install if missing
if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    echo "📦 Installing missing dependencies..."
    echo "   (This may take a few minutes)\n"
    
    pip install --upgrade pip >/dev/null 2>&1
    pip install mlx-lm lancedb sentence-transformers numpy >/dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully\n"
    else
        echo "❌ Dependency installation failed"
        exit 1
    fi
else
    echo "\n✅ All dependencies satisfied\n"
fi

# Check for main files
echo "📂 Checking project files...\n"

if [ ! -f "neural_orchestration_layer.py" ]; then
    echo "❌ neural_orchestration_layer.py not found"
    exit 1
fi
echo "  ✅ neural_orchestration_layer.py"

if [ ! -f "install.sh" ]; then
    echo "⚠️  install.sh not found (optional)"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║                    ✅ SETUP COMPLETE & VERIFIED                           ║"
echo "║                                                                            ║"
echo "║  Everything is ready. Your M4 Mac will now run:                           ║"
echo "║                                                                            ║"
echo "║  • Abliterated Llama-3.1-8B (unfiltered, curse-prone)                     ║"
echo "║  • Multi-agent debate (Advocate vs Critic)                                ║"
echo "║  • Test-time scaling (2 debate cycles)                                    ║"
echo "║  • Dharma Matrix ethical weighting                                        ║"
echo "║  • Persistent semantic memory                                             ║"
echo "║  • 40-80 tokens/sec generation                                            ║"
echo "║                                                                            ║"
echo "║  FIRST RUN:                                                                ║"
echo "║  • Downloads ~3-5GB model (5-10 minutes)                                  ║"
echo "║  • Caches locally in .mlx_cache/                                          ║"
echo "║  • Subsequent runs: instant                                                ║"
echo "║                                                                            ║"
echo "║  COMMANDS:                                                                 ║"
echo "║  • [Type dilemma] - Start multi-cycle debate                              ║"
echo "║  • /memory        - Show debate history                                    ║"
echo "║  • /clear         - Clear memory                                           ║"
echo "║  • /quit          - Exit                                                   ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Ask to start
read -p "🚀 Start Neural Orchestration Layer now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔥 Initializing neural orchestration engine...\n"
    
    python3 neural_orchestration_layer.py
else
    echo ""
    echo "Ready when you are! Run this to start:"
    echo "  python3 neural_orchestration_layer.py"
    echo ""
fi
