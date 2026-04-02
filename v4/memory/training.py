#!/usr/bin/env python3
"""
⚡ EXTREME LOCAL GPT v4 — Training Data Collector
Automatically saves high-quality debates and chats for future MLX fine-tuning (LoRA).
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from core.config import AppConfig, Color

@dataclass
class TrainingSample:
    """Format matching MLX fine-tuning JSONL requirements."""
    text: str
    timestamp: str
    source: str
    quality: int

class TrainingCollector:
    """
    Captures your best interactions to build a personalized dataset.
    """
    def __init__(self, config: AppConfig):
        self.config = config
        self.data_dir = Path(self.config.memory.data_dir).expanduser() / "training_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.dataset_file = self.data_dir / "mlx_dataset.jsonl"
        self.samples_collected = 0
        self._count_existing()

    def _count_existing(self):
        if self.dataset_file.exists():
            with open(self.dataset_file, "r") as f:
                self.samples_collected = sum(1 for _ in f)

    def capture_debate(self, dilemma: str, synthesis: str, is_nsfw: bool = False, rating: int = 5):
        """
        Record a debate interaction as an instruction-tuned sample.
        rating > 3 means good.
        """
        if rating < 4:
            return # Only keep high quality

        # Construct MLX-compatible single-turn or multi-turn prompt
        # Standard format: <s>[INST] instruction [/INST] response </s>
        text_payload = f"<s>[INST] You are an AI analyzing complex dilemmas. Provide a brutally honest synthesis for the following:\n\n{dilemma} [/INST] {synthesis} </s>"

        sample = TrainingSample(
            text=text_payload,
            timestamp=datetime.now().isoformat(),
            source="debate",
            quality=rating
        )

        self._save_sample(sample)

    def capture_chat(self, user_msg: str, assistant_msg: str, rating: int = 5):
        """Record standard chat interaction"""
        if rating < 4:
            return

        text_payload = f"<s>[INST] {user_msg} [/INST] {assistant_msg} </s>"
        sample = TrainingSample(
            text=text_payload,
            timestamp=datetime.now().isoformat(),
            source="chat",
            quality=rating
        )
        self._save_sample(sample)

    def _save_sample(self, sample: TrainingSample):
        with open(self.dataset_file, "a") as f:
            f.write(json.dumps(asdict(sample)) + "\n")
        self.samples_collected += 1

    def get_stats(self) -> Dict:
        return {
            "total_samples": self.samples_collected,
            "dataset_path": str(self.dataset_file)
        }
