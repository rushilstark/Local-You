#!/usr/bin/env python3
"""
⚡ EXTREME LOCAL GPT v4 — Qwen Omni Voice Pipeline
End-to-End Multimodal Audio Language Model support.

Uses mlx-vlm to run Qwen3-Omni (Audio-in -> Text-out).
This replaces the Whisper STT + Llama Text pipeline for voice mode,
allowing the AI to understand tone, pitch, and emotion natively.
"""

import time
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict

from core.config import AppConfig, Color

try:
    import mlx_vlm
    from mlx_vlm.utils import load_audio
    HAS_MLX_VLM = True
except ImportError:
    HAS_MLX_VLM = False

try:
    import sounddevice as sd
    import soundfile as sf
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False

# Fallback STT for voice loops
try:
    import mlx_whisper
    HAS_STT = True
except ImportError:
    HAS_STT = False


class QwenOmniPipeline:
    """
    Handles inference for Qwen Omni multimodal models via mlx-vlm.
    Takes raw audio as input and generates text output.
    """

    def __init__(self, config: AppConfig):
        self.config = config
        self.model = None
        self.processor = None
        self.model_name = config.voice.omni_model
        
        self._load_model()

    def _load_model(self):
        """Load the Omni model via mlx-vlm."""
        if not HAS_MLX_VLM:
            print(f"{Color.ERROR}❌ mlx-vlm not found for Omni mode{Color.RESET}")
            print(f"   Install: pip install mlx-vlm")
            return

        try:
            from mlx_vlm import load
            print(f"{Color.DEBUG}Loading Omni model: {self.model_name}...{Color.RESET}")
            self.model, self.processor = load(self.model_name)
            print(f"{Color.DEBUG}✓ Loaded Omni model{Color.RESET}")
        except Exception as e:
            print(f"{Color.ERROR}❌ Failed to load Omni model: {e}{Color.RESET}")
            self.model = None

    def process_audio(self, audio_filepath: str, prompt: str = "") -> Optional[str]:
        """
        Transcribe and understand audio using the Omni model.
        """
        if not self.model or not HAS_MLX_VLM:
            return None

        from mlx_vlm import generate
        from mlx_vlm.utils import load_audio

        try:
            print(f"{Color.DEBUG}Omni thinking...{Color.RESET}", end="", flush=True)
            
            # Load audio for mlx-vlm
            audio_data = load_audio(audio_filepath)
            
            # Default prompt for pure transcription + response
            if not prompt:
                prompt = "<|audio|> Listen to this audio and respond appropriately."

            start_time = time.time()
            
            # Generate response
            response = generate(
                self.model,
                self.processor,
                audio=audio_data,
                prompt=prompt,
                max_tokens=self.config.model.max_tokens["chat"],
                verbose=False
            )
            
            elapsed = time.time() - start_time
            print(f" done. ({elapsed:.1f}s)")
            
            return response.strip()

        except Exception as e:
            print(f"\n{Color.ERROR}Omni inference error: {e}{Color.RESET}")
            return None

# ── Qwen3-TTS subprocess script ──
QWEN_TTS_SCRIPT = '''
import sys
import json
import os
import io

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

try:
    import torch
    import sounddevice as sd
    from qwen_tts import Qwen3TTSModel
    HAS_QWEN = True
except ImportError:
    HAS_QWEN = False

def main():
    request = json.loads(sys.stdin.readline())
    text = request["text"]
    instruct = request.get("instruct", "A gentle female voice with a high pitch, speaking happily and expressing emotion naturally.")
    
    if not HAS_QWEN:
        print(json.dumps({"status": "error", "message": "Qwen3-TTS is not installed. Run: pip install -U qwen-tts"}))
        return

    try:
        # Determine Apple Silicon compatibility
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        
        # Load the Voice Design model. This is a 1.7B param model.
        print(f"Loading Qwen3-TTS-12Hz-1.7B-VoiceDesign...", file=sys.stderr, flush=True)
        model = Qwen3TTSModel.from_pretrained(
            "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", 
            device_map=device, 
            dtype=torch.float16,
        )
        print(f"Model loaded successfully.", file=sys.stderr, flush=True)
        
        # Generate audio based on a text prompt and an implicit voice description
        wavs, sr = model.generate_voice_design(
            text=text,
            instruct=instruct,
            language="Auto"
        )
        
        audio_data = wavs[0]
        
        sd.play(audio_data, sr)
        sd.wait()
        
        print(json.dumps({"status": "ok", "samples": len(audio_data)}))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()
'''

class MacSayVoiceEngine:
    """
    Zero-install voice engine using macOS built-in `say` command.
    Works instantly. Samantha voice at rate 175 sounds natural.
    Upgrade to Qwen3-TTS later if desired.
    """
    # Best built-in macOS voice options (run `say -v '?' | grep en_` to list)
    VOICES = {
        "samantha": "Samantha",   # Default — best natural female
        "karen":    "Karen",      # Australian female
        "daniel":   "Daniel",     # British male
        "alex":     "Alex",       # US male
        "victoria": "Victoria",   # US female
    }

    def __init__(self, config: AppConfig):
        self.config = config
        self._playing = False
        self._proc = None
        self._voice = "Samantha"
        self._rate = 175          # words per minute (default 175, range 80-300)
        print(f"{Color.DEBUG}  ✓ Voice TTS: macOS say ({self._voice}, {self._rate} wpm){Color.RESET}")

    def speak(self, text: str, voice: str = None, block: bool = False):
        import re, threading
        # Strip all action tags: *smiles*, [sighs], (laughs)
        clean = re.sub(r'[\*\(\[].*?[\*\)\]]', '', text)
        # Strip other weird markdown characters
        clean = re.sub(r'[_#`~]', '', clean)
        # Fix spacing
        clean = re.sub(r'\s+', ' ', clean).strip()
        # Remove empty or whitespace-only punctuation leftovers
        clean = re.sub(r'^[\s.,!?]+$', '', clean)
        
        if not clean:
            return
        v = voice or self._voice
        cmd = ["say", "-v", v, "-r", str(self._rate), clean]
        if block:
            self._run(cmd)
        else:
            threading.Thread(target=self._run, args=(cmd,), daemon=True).start()

    def _run(self, cmd):
        self._playing = True
        try:
            self._proc = subprocess.Popen(cmd)
            self._proc.wait()
        except Exception as e:
            print(f"{Color.ERROR}TTS error: {e}{Color.RESET}")
        finally:
            self._playing = False
            self._proc = None

    def speak_streaming(self, text: str, voice: str = None):
        self.speak(text, voice, block=True)

    def stop(self):
        if self._proc:
            try:
                self._proc.terminate()
            except Exception:
                pass
        self._playing = False

    def set_voice(self, name: str) -> bool:
        v = self.VOICES.get(name.lower())
        if v:
            self._voice = v
            return True
        return False

    def list_voices(self) -> str:
        lines = [f"\n{Color.BOLD}🎙️ Available macOS Voices:{Color.RESET}"]
        for k, v in self.VOICES.items():
            mark = " ◀ active" if v == self._voice else ""
            lines.append(f"  {k:<12} → {v}{mark}")
        lines.append(f"\nSpeed: {self._rate} wpm  (type 'voice fast' or 'voice slow' to adjust)")
        return "\n".join(lines)

    def status(self) -> str:
        return (f"\n{Color.BOLD}🎙️ MACOS SAY ENGINE{Color.RESET}\n"
                f"  Voice: {self._voice}  |  Rate: {self._rate} wpm\n"
                f"  Status: {'🔊 Playing' if self._playing else '⏹ Idle'}")

    def listen(self, *a, **kw):
        return None

    def record_audio(self, *a, **kw):
        return None

    @property
    def is_playing(self):
        return self._playing


# Keep old class name as alias so engine.py import still works
QwenVoiceEngine = MacSayVoiceEngine

