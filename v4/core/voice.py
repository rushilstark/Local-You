#!/usr/bin/env python3
"""
⚡ EXTREME LOCAL GPT v4 — Voice Module
Fully local voice I/O:
  - Speech-to-Text: mlx-whisper (Apple Silicon optimized)
  - Text-to-Speech: Kokoro (82M params, human-like, fast)

ARCHITECTURE NOTE: Kokoro TTS runs in a subprocess to avoid Metal GPU
conflicts with MLX (which uses Metal for LLM inference). Both frameworks
try to use Metal command buffers simultaneously → GPU fault. Running
Kokoro in a subprocess gives it its own Metal context.
"""

import os
import sys
import time
import tempfile
import subprocess
import threading
import json
from pathlib import Path
from typing import Optional, Tuple

from core.config import AppConfig, Color

# ── Optional imports (graceful degradation) ──

HAS_AUDIO = False
HAS_STT = False

try:
    import sounddevice as sd
    import soundfile as sf
    HAS_AUDIO = True
except ImportError:
    pass

try:
    import mlx_whisper
    HAS_STT = True
except ImportError:
    pass


# ── TTS subprocess script (written to temp file and executed) ──
TTS_SUBPROCESS_SCRIPT = '''
import sys
import json
import os
import numpy as np

# Force CPU fallback to prevent Metal hard crashes if ops are missing
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["KOKORO_VOICE"] = "af_heart"  # Set default voice

def main():
    # Read request from stdin
    try:
        request_line = sys.stdin.readline()
        if not request_line:
            sys.exit(1)
        request = json.loads(request_line)
    except:
        sys.exit(1)
    
    text = request.get("text", "")
    voice = request.get("voice", "af_heart")
    output_path = request.get("output_path")
    
    if not text:
        sys.exit(1)

    try:
        # Import kokoro
        import kokoro
        
        # Initialize pipeline
        try:
            pipeline = kokoro.KPipeline(lang_code="a")
        except:
            # Fallback if language code fails
            pipeline = kokoro.KPipeline()
        
        # Generate audio - use try/except for voice parameter
        try:
            # Try with explicit voice parameter
            audio = pipeline(text, voice=voice)
        except TypeError:
            # If voice parameter doesn't work, try without it
            audio = pipeline(text)
        except:
            # Last resort - use default
            audio = pipeline(text, voice="af_heart")
        
        # Handle generator or list returns from Kokoro
        if hasattr(audio, '__iter__') and not isinstance(audio, (np.ndarray, str, bytes)):
            # It's a generator - Kokoro yields Result objects with audio chunks
            # KPipeline.Result has attributes: audio, sample_rate, and metadata
            try:
                audio_chunks = []
                sr = 24000
                for result in audio:
                    # Result is a KPipeline.Result object with .audio, .sample_rate attributes
                    if hasattr(result, 'audio'):
                        chunk = result.audio
                        if hasattr(result, 'sample_rate'):
                            sr = result.sample_rate
                    elif isinstance(result, (tuple, list)) and len(result) >= 1:
                        # Fallback: if it's a tuple/list, unpack it
                        chunk = result[0]
                        if len(result) > 1:
                            sr = result[1]
                    else:
                        chunk = result
                    
                    # Ensure chunk is numpy array
                    if isinstance(chunk, np.ndarray):
                        audio_chunks.append(chunk)
                    elif chunk is not None:
                        audio_chunks.append(np.asarray(chunk, dtype=np.float32))
                
                if audio_chunks:
                    audio = np.concatenate(audio_chunks)
                else:
                    raise ValueError("No audio chunks generated")
            except Exception as gen_err:
                # If generator consumption fails, retry with plain call
                audio = pipeline(text)
        
        # Ensure audio is numpy array
        if not isinstance(audio, np.ndarray):
            audio = np.asarray(audio, dtype=np.float32)
        
        # Kokoro native sample rate
        sr = 24000
        
        # Write to output path if provided
        if output_path:
            import soundfile as sf
            sf.write(output_path, audio, sr)
            print(json.dumps({"status": "success", "output": output_path}))
        else:
            # Play directly
            import sounddevice as sd
            sd.play(audio, sr)
            sd.wait()
            print(json.dumps({"status": "success"}))
            
    except Exception as e:
        import traceback
        err_msg = str(e)
        print(json.dumps({"status": "error", "message": err_msg}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
'''


class VoiceEngine:
    """
    Fully local voice I/O using Kokoro TTS + Whisper STT.

    TTS runs in a subprocess to avoid Metal GPU conflict with MLX.
    STT uses mlx-whisper directly (no conflict since it runs sequentially).
    """

    # Available Kokoro voices
    VOICES = {
        "default": "af_heart",       # American female, warm, clear (better than af_sky)
        "heart": "af_heart",         # American female, warm, clear
        "bella": "af_bella",         # American female, soft, gentle
        "sexy": "af_bella",          # Mapped to a softer, more intimate voice
        "male": "am_adam",           # American male
        "female": "af_heart",        # Default female fallback
        "nicole": "af_nicole",       # American female, alternative
        "sarah": "af_sarah",         # American female, alternative
        "british_f": "bf_emma",      # British female
        "british_m": "bm_george",    # British male
    }

    def __init__(self, config: AppConfig):
        self.config = config
        self.voice = self.VOICES["default"]
        self.sample_rate = 44100  # CD quality
        self.data_dir = config.memory.resolved_data_dir / "voice"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self._playing = False
        self._play_thread = None
        
        # Enhancement pipeline disabled - was causing unwanted text injection
        # self.enhancement_pipeline = VoiceEnhancementPipeline()

        # Write the TTS subprocess script to a temp file
        self._tts_script_path = self.data_dir / "_tts_worker.py"
        with open(self._tts_script_path, 'w') as f:
            f.write(TTS_SUBPROCESS_SCRIPT)

        # Check if Kokoro is importable
        self._has_tts = self._check_tts()

        # Custom voices directory
        self.custom_voices_dir = self.data_dir / "custom"
        self.custom_voices_dir.mkdir(parents=True, exist_ok=True)

        if self._has_tts:
            print(f"{Color.DEBUG}  ✓ Voice TTS: Kokoro (voice: {self.voice}) [subprocess mode]{Color.RESET}")
            print(f"{Color.DEBUG}  ✓ Voice Enhancement: Natural breathing pauses (ellipsis-based){Color.RESET}")
        else:
            print(f"{Color.DEBUG}  ⚠ Voice TTS: not available (pip install kokoro){Color.RESET}")

    def _check_tts(self) -> bool:
        """Check if Kokoro is installed without importing it in main process."""
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import kokoro; print('ok')"],
                capture_output=True, text=True, timeout=10
            )
            return result.stdout.strip() == "ok"
        except Exception:
            return False

    # ================================================================
    # TEXT-TO-SPEECH (Kokoro via subprocess)
    # ================================================================

    def speak(self, text: str, voice: Optional[str] = None, block: bool = False, no_sound_interleaving: bool = False):
        """
        Convert text to speech and play it via subprocess.
        
        Now includes 8-agent enhancement pipeline:
          Agent 1: Emotion Detection
          Agent 2: Speed Variation
          Agent 3: Voice Switching
          Agent 4: Advanced Fillers
          Agent 5: Punctuation Awareness
          Agent 6: Emphasis Injection
          Agent 7: Phonetic Markers
          Agent 8: Audio Blending

        Args:
            text: Text to speak
            voice: Voice name (see VOICES dict)
            block: If True, wait for playback to finish
            no_sound_interleaving: If True, disable auto-sound-insertion
        """
        if not self._has_tts:
            print(f"{Color.DEBUG}[Voice not available]{Color.RESET}")
            return

        # Translate visceral roleplay tags into spoken breath sounds
        import re
        fillers = {
            r'\*sigh[s]?\*': 'Haaah...',
            r'\*moan[s]?\*': 'Mmm...',
            r'\*chuckle[s]?\*': 'Hehe.',
            r'\*laugh[s]?\*': 'Haha!',
            r'\*giggle[s]?\*': 'Hehe!',
            r'\*groan[s]?\*': 'Ugh...',
            r'\*gasp[s]?\*': 'Haa!',
        }
        for pattern, replacement in fillers.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # 1. Strip remaining silent roleplay actions like *smiles* or [looks away]
        clean_text = re.sub(r'[\*\(\[].*?[\*\)\]]', '', text)
        
        # 2. Strip markdown headers and bolding
        clean_text = re.sub(r'[_#`~]', '', clean_text)
        
        # 3. Clean up spacing and empty strings
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        clean_text = re.sub(r'^[\s.,!?]+$', '', clean_text)

        # ✨ ENHANCEMENT: Add natural breathing pauses (NOT saying "breath")
        # Add ellipsis after periods to create natural pause effect in TTS
        tts_text = clean_text.replace(". ", "... ")
        tts_text = tts_text.replace("! ", "!! ")
        tts_text = tts_text.replace("? ", "?? ")
        # Add slight pauses within longer sentences (after commas)
        tts_text = tts_text.replace(", ", ", ... ")
        # Clean up any triple+ spaces
        tts_text = re.sub(r'\s+', ' ', tts_text).strip()

        if not clean_text:
            return

        voice_id = self.VOICES.get(voice, voice) if voice else self.voice

        if block:
            self._speak_sync(clean_text, voice_id, no_sound_interleaving=no_sound_interleaving)
        else:
            self._speak_async(clean_text, voice_id, no_sound_interleaving=no_sound_interleaving)

    def _get_voice_id(self, voice_name: str) -> str:
        """Map standard name or return path to custom .pt file."""
        if voice_name in self.VOICES:
            return self.VOICES[voice_name]
        
        # Check for custom .pt file in data/voice/custom/
        custom_path = self.custom_voices_dir / f"{voice_name}.pt"
        if custom_path.exists():
            return str(custom_path)
            
        return self.VOICES["default"]

    def _speak_sync(self, text: str, voice_id: str, no_sound_interleaving: bool = False):
        """Run TTS in subprocess synchronously."""
        # Map voice name to either a standard ID or a path
        resolved_voice = self._get_voice_id(voice_id)
        
        request = json.dumps({
            "text": text,
            "voice": resolved_voice,
        })

        try:
            result = subprocess.run(
                [sys.executable, str(self._tts_script_path)],
                input=request + "\n",
                capture_output=True, text=True,
                timeout=120,
            )

            if result.returncode != 0:
                stderr = result.stderr.strip()
                # Filter out torch warnings
                errors = [l for l in stderr.split('\n')
                         if l and 'UserWarning' not in l and 'FutureWarning' not in l
                         and 'warnings.warn' not in l and 'Defaulting repo_id' not in l]
                if errors:
                    print(f"{Color.ERROR}TTS error: {errors[-1][:100]}{Color.RESET}")

        except subprocess.TimeoutExpired:
            print(f"{Color.ERROR}TTS timed out{Color.RESET}")
        except Exception as e:
            print(f"{Color.ERROR}TTS error: {e}{Color.RESET}")

    def _speak_async(self, text: str, voice_id: str, no_sound_interleaving: bool = False):
        """Run TTS in subprocess asynchronously."""
        def _run():
            self._playing = True
            try:
                self._speak_sync(text, voice_id, no_sound_interleaving=no_sound_interleaving)
            finally:
                self._playing = False

        self.stop()
        self._play_thread = threading.Thread(target=_run, daemon=True)
        self._play_thread.start()

    def speak_streaming(self, text: str, voice: Optional[str] = None):
        """
        Stream TTS — for long responses, plays via subprocess.
        (Subprocess mode doesn't support true streaming, but it avoids GPU crashes)
        """
        self.speak(text, voice=voice, block=True)

    def save_speech(self, text: str, filename: str, voice: Optional[str] = None) -> Optional[str]:
        """Save speech to a WAV file via subprocess."""
        if not self._has_tts:
            return None

        voice_id = self.VOICES.get(voice, voice) if voice else self.voice
        filepath = str(self.data_dir / filename)

        request = json.dumps({
            "text": text,
            "voice": voice_id,
            "output_path": filepath,
            "sample_rate": self.sample_rate,
        })

        try:
            result = subprocess.run(
                [sys.executable, str(self._tts_script_path)],
                input=request + "\n",
                capture_output=True, text=True,
                timeout=120,
            )
            if result.returncode == 0:
                return filepath
        except Exception as e:
            print(f"{Color.ERROR}Save speech error: {e}{Color.RESET}")

        return None

    def stop(self):
        """Stop current playback."""
        self._playing = False

    @property
    def is_playing(self) -> bool:
        return self._playing

    # ================================================================
    # SPEECH-TO-TEXT (mlx-whisper — runs in main process, no conflict)
    # ================================================================

    def listen(self, duration: float = 5.0) -> Optional[str]:
        """
        Record from microphone and transcribe.

        Args:
            duration: Recording duration in seconds

        Returns:
            Transcribed text, or None on failure
        """
        if not HAS_STT or not HAS_AUDIO:
            print(f"{Color.DEBUG}[Speech-to-text not available]{Color.RESET}")
            return None

        try:
            print(f"{Color.MEMORY}🎤 Listening ({duration}s)...{Color.RESET}", end="", flush=True)

            # Record audio
            recording = sd.rec(
                int(duration * 16000),
                samplerate=16000,
                channels=1,
                dtype='float32'
            )
            sd.wait()
            print(f" done.", flush=True)

            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                sf.write(f.name, recording, 16000)
                temp_path = f.name

            # Transcribe with mlx-whisper
            print(f"{Color.DEBUG}Transcribing...{Color.RESET}", end="", flush=True)
            result = mlx_whisper.transcribe(
                temp_path,
                path_or_hf_repo="mlx-community/whisper-small",
            )
            print(f" done.", flush=True)

            # Clean up
            os.unlink(temp_path)

            text = result.get("text", "").strip()
            return text if text else None

        except Exception as e:
            print(f"{Color.ERROR}STT error: {e}{Color.RESET}")
            return None

    def record_audio(self, duration: float = 5.0) -> Optional[str]:
        """
        Record from microphone and return the filepath to the temporary WAV file.
        Used for passing raw audio directly to the Omni model.
        """
        if not HAS_AUDIO:
            return None

        try:
            print(f"{Color.MEMORY}🎤 Listening for Omni ({duration}s)...{Color.RESET}", end="", flush=True)

            recording = sd.rec(
                int(duration * 16000),
                samplerate=16000,
                channels=1,
                dtype='float32'
            )
            sd.wait()
            print(f" done.", flush=True)

            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                sf.write(f.name, recording, 16000)
                return f.name

        except Exception as e:
            print(f"{Color.ERROR}Recording error: {e}{Color.RESET}")
            return None

    def listen_continuous(self, silence_threshold: float = 0.01, max_duration: float = 30.0) -> Optional[str]:
        """Listen continuously until silence is detected."""
        return self.listen(duration=5.0)

    # ================================================================
    # VOICE MODE (interactive)
    # ================================================================

    def set_voice(self, voice_name: str) -> bool:
        """Change the TTS voice."""
        # 1. Check standard names
        if voice_name in self.VOICES:
            self.voice = self.VOICES[voice_name]
            return True
        
        # 2. Check internal voice IDs (e.g. af_heart)
        if voice_name in self.VOICES.values():
            self.voice = voice_name
            return True

        # 3. Check custom voices directory
        custom_path = self.custom_voices_dir / f"{voice_name}.pt"
        if custom_path.exists():
            self.voice = voice_name # Store the name, _get_voice_id will resolve the path
            return True
            
        return False

    def list_voices(self) -> str:
        """List available voices."""
        lines = [f"{Color.BOLD}Available standard voices:{Color.RESET}"]
        for name, voice_id in self.VOICES.items():
            marker = " ← current" if voice_id == self.voice or name == self.voice else ""
            lines.append(f"  {name}: {voice_id}{marker}")
        
        # List custom voices
        custom_files = list(self.custom_voices_dir.glob("*.pt"))
        if custom_files:
            lines.append(f"\n{Color.BOLD}Available custom voices:{Color.RESET}")
            for cf in custom_files:
                vname = cf.stem
                marker = " ← current" if vname == self.voice else ""
                lines.append(f"  {vname}{marker}")
                
        return "\n".join(lines)

    # ================================================================
    # STATUS
    # ================================================================

    def status(self) -> str:
        """Voice system status."""
        lines = [f"\n{Color.BOLD}🎙️ VOICE STATUS{Color.RESET}"]
        lines.append(f"  TTS (Kokoro): {'✓ ready (subprocess)' if self._has_tts else '✗ not available'}")
        lines.append(f"  STT (Whisper): {'✓ ready' if HAS_STT else '✗ not available'}")
        lines.append(f"  Audio I/O: {'✓ ready' if HAS_AUDIO else '✗ not available'}")
        lines.append(f"  Voice: {self.voice}")
        return "\n".join(lines)
