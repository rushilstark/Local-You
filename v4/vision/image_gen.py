#!/usr/bin/env python3
"""
⚡ EXTREME LOCAL GPT v4 — Vision Engine
Image generation using FLUX.1 Schnell.
"""

import os
import json
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from datetime import datetime

from core.config import AppConfig, Color

try:
    import torch
    from diffusers import FluxPipeline
    import safetensors
    HAS_DIFFUSERS = True
except ImportError:
    HAS_DIFFUSERS = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class ImageGenerator:
    """FLUX.1 Schnell image generation engine"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.model_id = "black-forest-labs/FLUX.1-schnell"
        self.device = self._select_device()
        self.pipe = None
        self.loaded = False

        self.output_dir = Path(self.config.memory.data_dir).expanduser() / "images"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.image_index = {}
        self._load_image_index()

        self._load_model()

    def _select_device(self) -> str:
        """Select appropriate device (GPU preferred, CPU fallback)"""
        if torch.backends.mps.is_available():
            return "mps"
        elif torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def _load_model(self):
        """Load FLUX.1 Schnell model from HuggingFace."""
        if not HAS_DIFFUSERS:
            print(f"{Color.ERROR}❌ Image generation requires diffusers, torch, safetensors{Color.RESET}")
            return

        try:
            print(f"{Color.DEBUG}Loading Image Gen model: {self.model_id}...{Color.RESET}")
            self.pipe = FluxPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.bfloat16 if self.device != "cpu" else torch.float32
            )
            self.pipe = self.pipe.to(self.device)

            # Enable memory optimizations
            try:
                self.pipe.enable_model_cpu_offload()
            except Exception:
                pass

            self.loaded = True
            print(f"{Color.DEBUG}✓ Loaded FLUX.1 (Device: {self.device}){Color.RESET}")
        except Exception as e:
            print(f"{Color.ERROR}❌ Failed to load image model: {e}{Color.RESET}")
            if "gated" in str(e).lower() or "403" in str(e):
                print(f"{Color.ERROR}   Requires HF Login: huggingface-cli login{Color.RESET}")
            self.loaded = False

    def _load_image_index(self):
        index_file = self.output_dir / "index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    self.image_index = json.load(f)
            except Exception:
                self.image_index = {}

    def _save_image_index(self):
        index_file = self.output_dir / "index.json"
        with open(index_file, 'w') as f:
            json.dump(self.image_index, f, indent=2)

    def generate(self, prompt: str, seed: Optional[int] = None) -> Tuple[Optional['Image.Image'], Dict[str, Any]]:
        """
        Generate image from text prompt using FLUX.1 Schnell
        """
        if not self.loaded:
            return None, {"error": "Model not loaded"}

        try:
            import time
            start_time = time.time()
            print(f"{Color.MEMORY}🎨 Generating image ({self.device})...{Color.RESET}", end="", flush=True)

            # Truncate prompt for Schnell max
            prompt_tokens = prompt.split()[:60]
            prompt_str = " ".join(prompt_tokens)

            if seed is not None:
                generator = torch.Generator(self.device).manual_seed(seed)
            else:
                generator = torch.Generator(self.device)

            with torch.no_grad():
                result = self.pipe(
                    prompt=prompt_str,
                    height=768,
                    width=768,
                    num_inference_steps=4,
                    guidance_scale=0.0,
                    num_images_per_prompt=1,
                    generator=generator,
                    max_sequence_length=256
                )

            images = result.images
            image = images[0] if isinstance(images, list) else images

            generation_time = time.time() - start_time
            print(f" done. ({generation_time:.1f}s)")

            metadata = {
                "prompt": prompt_str,
                "height": 768,
                "width": 768,
                "num_inference_steps": 4,
                "guidance_scale": 0.0,
                "seed": seed,
                "generation_time": generation_time,
                "device": self.device,
                "timestamp": datetime.now().isoformat()
            }

            return image, metadata

        except Exception as e:
            print(f"\n{Color.ERROR}Generation error: {e}{Color.RESET}")
            return None, {"error": str(e)}

    def generate_and_save(self, prompt: str, prefix: str = "img") -> Optional[str]:
        """Convenience method to generate and save immediately."""
        image, metadata = self.generate(prompt)
        if not image or not HAS_PIL:
            return None

        filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename

        try:
            image.save(filepath)
            meta_path = str(filepath).replace('.png', '_metadata.json')
            with open(meta_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            self.image_index[filename] = metadata
            self._save_image_index()

            print(f"{Color.ADVOCATE}🖼️  Saved to: {filepath}{Color.RESET}")
            return str(filepath)
        except Exception as e:
            print(f"{Color.ERROR}Save error: {e}{Color.RESET}")
            return None

    def _extract_visual_prompt(self, text: str) -> str:
        """Extract visual theme from debate synthesis for auto-generation."""
        visual_keywords = {
            "conflict": "clash, battle, opposing forces",
            "growth": "expansion, reaching upward, blooming",
            "confusion": "maze, tangled, overlapping",
            "clarity": "light, clear path, sharp focus",
            "journey": "road, path, landscape",
            "choice": "crossroads, multiple paths, decision",
            "support": "foundation, connection, bridge",
            "success": "peak, gold, achievement",
            "failure": "broken, fallen, darkness",
            "balance": "equilibrium, symmetry, harmony"
        }
        
        text_lower = text.lower()
        matches = [theme for key, theme in visual_keywords.items() if key in text_lower]
        
        if matches:
            combined = ", ".join(matches[:3])
            return f"Abstract, ethereal visualization of: {combined}. Artistic, conceptual, flowing design. High quality, detailed. Color palette of deep blues and golden highlights."
        else:
            first_words = " ".join(text.split()[:10])
            return f"Artistic, abstract visualization of the concept: {first_words}. Ethereal, conceptual, flowing. High quality digital art."

    def generate_from_synthesis(self, synthesis_text: str, debate_id: str = None) -> Optional[str]:
        """Auto-generate an image from a debate synthesis."""
        if not synthesis_text or len(synthesis_text.strip()) < 20:
            return None
        
        prompt = self._extract_visual_prompt(synthesis_text)
        seed = hash(synthesis_text) % (2**32) if debate_id is None else int(debate_id[-6:], 16) % (2**32)
        
        print(f"{Color.DEBUG}Generating image from debate theme...{Color.RESET}")
        return self.generate_and_save(prompt, prefix="debate")
