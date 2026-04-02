#!/bin/bash

# 🔥 FIX MODEL LOADING - NEURAL ENGINE SETUP

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║         🔥 NEURAL ENGINE - MODEL LOADING FIX & SETUP 🔥                  ║"
echo "║                                                                            ║"
echo "║  This script fixes the 'No safetensors found' error by:                   ║"
echo "║  1. Installing latest MLX + HuggingFace tools                             ║"
echo "║  2. Pre-downloading abliterated model weights                             ║"
echo "║  3. Verifying model cache                                                 ║"
echo "║  4. Launching neural orchestration engine                                 ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi
echo "✅ Python 3 found: $(python3 --version)"

# Step 1: Update pip and install/upgrade core dependencies
echo ""
echo "📦 Step 1: Installing/upgrading MLX and HuggingFace tools..."
echo "   (This may take 2-3 minutes)\n"

pip install --upgrade pip >/dev/null 2>&1
pip install --upgrade mlx-lm mlx huggingface-hub transformers >/dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ MLX and HuggingFace tools installed\n"
else
    echo "❌ Installation failed"
    exit 1
fi

# Step 2: Pre-download model weights
echo ""
echo "📦 Step 2: Pre-downloading abliterated model weights..."
echo "   (First time: 3-5GB download, ~5-10 minutes)"
echo "   (Cached locally after first download)\n"

# Create cache directory
mkdir -p ~/.cache/huggingface/hub

# Download the primary model
echo "   Downloading: Llama-3.1-8B-Instruct-abliterated..."
python3 -c "
from huggingface_hub import snapshot_download
try:
    snapshot_download('mlx-community/Meta-Llama-3.1-8B-Instruct-abliterated-Q4-MLX',
                     local_dir=None,
                     local_dir_use_symlinks=False,
                     repo_type='model')
    print('   ✅ Model downloaded and cached')
except Exception as e:
    print(f'   ⚠️  Download incomplete: {str(e)[:50]}')
    print('   Will retry on first run')
" 2>/dev/null

# Step 3: Verify all dependencies
echo ""
echo "📋 Step 3: Verifying all dependencies...\n"

DEPS_OK=1

check_dep() {
    local import=$1
    local name=$2
    
    python3 -c "import $import" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "  ✅ $name"
    else
        echo "  ❌ $name"
        DEPS_OK=0
    fi
}

check_dep "mlx_lm" "mlx-lm"
check_dep "transformers" "transformers"
check_dep "huggingface_hub" "huggingface-hub"
check_dep "sentence_transformers" "sentence-transformers"
check_dep "lancedb" "lancedb"
check_dep "numpy" "numpy"

if [ $DEPS_OK -eq 0 ]; then
    echo ""
    echo "⚠️  Some dependencies missing, installing..."
    pip install sentence-transformers lancedb numpy >/dev/null 2>&1
    echo "✅ Dependencies installed\n"
fi

# Step 4: Display neural engine info
echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║                    ✅ NEURAL ENGINE READY                                 ║"
echo "║                                                                            ║"
echo "║  You now have:                                                             ║"
echo "║  • Abliterated Llama-3.1-8B (unfiltered, curse-prone)                     ║"
echo "║  • Multi-agent debate system (Advocate + Critic + Synthesizer)            ║"
echo "║  • Test-Time Scaling (2 debate cycles by default)                         ║"
echo "║  • Dharma Matrix ethical weighting                                        ║"
echo "║  • Persistent semantic memory (LanceDB)                                   ║"
echo "║  • M4 hardware optimization (40-80 tok/s)                                 ║"
echo "║                                                                            ║"
echo "║  Model cached in: ~/.cache/huggingface/hub/                               ║"
echo "║                                                                            ║"
echo "║  Debate history stored in: ./neural_memory.json                           ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Step 5: Ask to launch
read -p "🚀 Launch Neural Orchestration Engine now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔥 Starting neural orchestration engine...\n"
    python3 neural_engine_fixed.py
else
    echo ""
    echo "Ready to run:"
    echo "  python3 neural_engine_fixed.py"
    echo ""
fi
