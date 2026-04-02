#!/usr/bin/env python3
"""
⚡ EXTREME LOCAL GPT v4 — Inference Engine
Model loading with safe fallbacks + streaming generation.

CRITICAL: Only uses pre-quantized MLX models as fallbacks.
Never downloads full-precision models (the 33GB bug fix).
"""

import sys
import time
from typing import Generator, Tuple, Optional, List, Dict

from core.config import AppConfig, Color


class InferenceEngine:
    """
    Handles model loading and text generation.

    - Loads primary model, falls back to quantized alternatives only
    - Supports both blocking and streaming generation
    - Tracks token counts and speed
    """

    def __init__(self, config: AppConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.model_name = None

        self._load_model()

    def _load_model(self):
        """Load model with safe fallback chain. Never downloads 33GB models."""
        try:
            from mlx_lm import load
        except ImportError:
            print(f"{Color.ERROR}❌ mlx_lm not found{Color.RESET}")
            print(f"   Install: pip3 install mlx-lm")
            sys.exit(1)

        # Build candidate list: primary + fallbacks
        candidates = [self.config.model.primary] + self.config.model.fallbacks

        for model_name in candidates:
            try:
                print(f"{Color.DEBUG}Loading {model_name}...{Color.RESET}")
                self.model, self.tokenizer = load(model_name)
                self.model_name = model_name
                print(f"{Color.DEBUG}✓ Loaded {model_name}{Color.RESET}")
                return
            except Exception as e:
                print(f"{Color.DEBUG}  ✗ Failed: {str(e)[:80]}{Color.RESET}")
                continue

        print(f"{Color.ERROR}❌ Could not load any model{Color.RESET}")
        print(f"Models tried:")
        for m in candidates:
            print(f"  - {m}")
        sys.exit(1)

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 500,
        temperature: Optional[float] = None,
    ) -> Tuple[str, Dict]:
        """
        Generate a response (blocking).

        Returns:
            (response_text, metadata_dict)
        """
        if temperature is None:
            temperature = self.config.model.temperature

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            formatted = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        except Exception:
            formatted = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        start = time.time()

        try:
            from mlx_lm import stream_generate
            import mlx.core as mx

            # Build a sampler with temperature + top_p
            sampler = self._make_sampler(temperature)

            text = ""
            for response in stream_generate(
                self.model,
                self.tokenizer,
                prompt=formatted,
                max_tokens=max_tokens,
                sampler=sampler,
            ):
                text += response.text

        except Exception as e:
            return f"[Generation failed: {e}]", {"tokens": 0, "time": 0, "speed": 0}

        elapsed = time.time() - start
        text = text.strip()

        # Clean up common artifacts
        if "Response:" in text:
            text = text.split("Response:")[-1].strip()

        tokens = len(self.tokenizer.encode(text))

        metadata = {
            "tokens": tokens,
            "time": elapsed,
            "speed": tokens / elapsed if elapsed > 0 else 0,
        }

        return text, metadata

    def generate_stream(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 500,
        temperature: Optional[float] = None,
    ) -> Generator[str, None, Dict]:
        """
        Generate a response with streaming (token-by-token).

        Yields individual tokens. Returns metadata after completion.
        Usage:
            gen = engine.generate_stream(prompt)
            for token in gen:
                print(token, end="", flush=True)
        """
        if temperature is None:
            temperature = self.config.model.temperature

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            formatted = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        except Exception:
            formatted = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        try:
            from mlx_lm import stream_generate

            sampler = self._make_sampler(temperature)

            start = time.time()
            token_count = 0

            for response in stream_generate(
                self.model,
                self.tokenizer,
                prompt=formatted,
                max_tokens=max_tokens,
                sampler=sampler,
            ):
                token_count += 1
                yield response.text

            elapsed = time.time() - start

            return {
                "tokens": token_count,
                "time": elapsed,
                "speed": token_count / elapsed if elapsed > 0 else 0,
            }

        except Exception:
            # Fallback to blocking generation
            response, metadata = self.generate(
                prompt, system_prompt, max_tokens, temperature
            )
            yield response
            return metadata

    def _make_sampler(self, temperature: float):
        """Create a simple sampler function for mlx-lm generation."""
        import mlx.core as mx

        def sampler(logits: mx.array) -> mx.array:
            if temperature == 0:
                return mx.argmax(logits, axis=-1)
            # Simple temperature scaling (avoid complex Top-P sorting graph that causes PageFaults on Metal)
            return mx.random.categorical(logits / temperature)

        return sampler


def validate_unfiltered_response(text: str) -> Dict:
    """
    Check if a response is truly unfiltered or if the model self-censored.

    Returns:
        dict with 'unfiltered_confidence_score' (0-100) and 'flags'
    """
    text_lower = text.lower()

    # Censorship indicators (model is self-censoring)
    censored_phrases = [
        "i cannot", "i can't", "i'm unable", "as an ai",
        "i don't think", "not appropriate", "i must decline",
        "i won't", "against my", "harmful", "offensive",
        "i'm not able", "i shouldn't", "guidelines",
        "i apologize but", "i'm sorry but i can",
    ]

    # Unfiltered indicators (model is being direct)
    unfiltered_phrases = [
        "fuck", "shit", "damn", "hell", "ass",
        "brutal", "harsh", "raw", "unfiltered",
        "truth is", "reality is", "hard truth",
        "stop pretending", "wake up", "face it",
    ]

    censored_count = sum(1 for p in censored_phrases if p in text_lower)
    unfiltered_count = sum(1 for p in unfiltered_phrases if p in text_lower)

    # Score: 100 = fully unfiltered, 0 = fully censored
    if censored_count + unfiltered_count == 0:
        score = 50  # Neutral
    else:
        ratio = unfiltered_count / (censored_count + unfiltered_count)
        score = int(ratio * 100)

    # Penalty for heavy censorship
    if censored_count >= 3:
        score = max(0, score - 30)

    # Bonus for assertive language
    if unfiltered_count >= 3:
        score = min(100, score + 20)

    flags = []
    if censored_count > 0:
        flags.append(f"{censored_count} censorship phrases detected")
    if unfiltered_count > 0:
        flags.append(f"{unfiltered_count} unfiltered indicators")

    return {
        "unfiltered_confidence_score": score,
        "censored_phrases": censored_count,
        "unfiltered_phrases": unfiltered_count,
        "flags": flags,
    }
