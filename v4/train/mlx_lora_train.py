#!/usr/bin/env python3
"""
⚡ EXTREME LOCAL GPT v4 — Fine-Tuning Pipeline
Uses mlx-lm to run LoRA fine-tuning on your high-quality recorded debates/chats.
"""

import os
import sys
import subprocess
from pathlib import Path
from core.config import load_config, Color

def main():
    print(f"\n{Color.BOLD}🧠 JARVIS MLX LORA FINE-TUNING{Color.RESET}\n")
    
    config = load_config()
    data_dir = Path(config.memory.data_dir).expanduser() / "training_data"
    dataset_file = data_dir / "mlx_dataset.jsonl"
    
    if not dataset_file.exists():
        print(f"{Color.ERROR}No training data found at {dataset_file}!{Color.RESET}")
        print("Engage in more debates and rate them >= 4 to build the dataset.")
        sys.exit(1)
        
    # Count lines to see samples
    with open(dataset_file, "r") as f:
        num_samples = sum(1 for _ in f)
        
    print(f"Dataset: {num_samples} high-quality samples found.")
    
    if num_samples < 50:
        print(f"{Color.WARNING}Warning: Recommended to have at least 50 samples before fine-tuning. Continuing anyway...{Color.RESET}\n")
        
    model_name = config.voice.omni_model if config.voice.omni_mode else config.model.model_path
    output_adapter_dir = data_dir / "adapters"
    output_adapter_dir.mkdir(exist_ok=True)
    
    print(f"{Color.SYSTEM}Model:{Color.RESET} {model_name}")
    print(f"{Color.SYSTEM}Adapters will save to:{Color.RESET} {output_adapter_dir}")
    
    print(f"\n{Color.DEBUG}Checking mlx-lm installation...{Color.RESET}")
    try:
        import mlx_lm
    except ImportError:
        print(f"{Color.ERROR}pip install mlx-lm first!{Color.RESET}")
        sys.exit(1)
        
    print(f"\n🚀 {Color.BOLD}Starting LoRA Training...{Color.RESET}")
    print("This will heavily utilize your Apple Silicon GPU.\n")
    
    # Run mlx_lm lora directly using python -m
    cmd = [
        sys.executable, "-m", "mlx_lm.lora",
        "--model", model_name,
        "--train",
        "--data", str(data_dir), # Directory containing valid train.jsonl
        "--iters", "200",
        "--adapter-path", str(output_adapter_dir / "jarvis_lora")
    ]
    
    # We must rename mlx_dataset.jsonl to train.jsonl for mlx_lm
    train_file = data_dir / "train.jsonl"
    import shutil
    shutil.copy(dataset_file, train_file)
    
    # Use validation if enough samples? Just copy to valid.jsonl for now
    valid_file = data_dir / "valid.jsonl"
    shutil.copy(dataset_file, valid_file)
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ {Color.BOLD}Fine-Tuning Complete!{Color.RESET}")
        print(f"Your personalized adapters are saved in {output_adapter_dir}/jarvis_lora")
        print("\nTo use them, update your start script or engine to load the lora adapter paths.")
    except subprocess.CalledProcessError as e:
        print(f"\n{Color.ERROR}Training failed with code {e.returncode}{Color.RESET}")

if __name__ == "__main__":
    main()
