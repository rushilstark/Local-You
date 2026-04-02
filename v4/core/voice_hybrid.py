#!/usr/bin/env python3
"""
⚡ EXTREME LOCAL GPT v4 — Hybrid Voice with Manual Sound Markers

CORRECTED APPROACH:
1. AI response contains markers: "I love you *moan* so much"
2. EXTRACT markers FIRST (before voice.py processes them)
3. Build segments: speech chunks + sound markers
4. For each speech chunk: use voice.py to speak (clean text, no markers)
5. For each marker: play the sound file directly from memory
6. Result: seamless speech + sounds, NO duplicates, NO speed issues
"""

import os
import sys
import re
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Tuple, List

from core.config import AppConfig, Color

# Try to import sounddevice for direct audio playback
try:
    import sounddevice as sd
    import soundfile as sf
    HAS_SOUNDDEVICE = True
except ImportError:
    HAS_SOUNDDEVICE = False


class HybridVoiceEngine:
    """Seamless voice with manual sound effect markers."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.data_dir = config.memory.resolved_data_dir / "voice"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Sound files loaded into memory
        self.sounds = {}
        self.manual_sounds_dir = None
        self._playing = False
        self._play_thread = None
        self._tts_engine = None  # Lazy-loaded
        
        # Check if we can use Kokoro TTS
        self._has_tts = self._check_tts()
        
        if self._has_tts:
            print(f"{Color.DEBUG}  ✓ Hybrid Voice: Kokoro TTS + manual sound markers (seamless){Color.RESET}")
        else:
            print(f"{Color.DEBUG}  ⚠ Hybrid Voice: TTS not available{Color.RESET}")

    def _check_tts(self) -> bool:
        """Check if Kokoro is available."""
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import kokoro; print('ok')"],
                capture_output=True, text=True, timeout=10
            )
            return result.stdout.strip() == "ok"
        except:
            return False

    def set_manual_sounds_dir(self, directory: str) -> bool:
        """Load all sound files from directory (store as file paths for afplay)."""
        path = Path(directory).expanduser()
        if not path.exists():
            print(f"{Color.ERROR}Sound directory not found: {directory}{Color.RESET}")
            return False
        
        self.manual_sounds_dir = path
        self.sounds = {}
        
        # Load all audio files
        audio_files = list(path.glob("*.wav")) + list(path.glob("*.mp3")) + list(path.glob("*.m4a"))
        
        if not audio_files:
            print(f"{Color.DEBUG}  No audio files found in {directory}{Color.RESET}")
            return False
        
        print(f"{Color.DEBUG}  Loading sounds from {path.name}/{Color.RESET}")
        
        for audio_file in audio_files:
            filename = audio_file.stem.lower()
            sound_type = self._categorize_sound(filename)
            
            try:
                # Store as file path (will use afplay for playback, no PortAudio issues)
                self.sounds[sound_type] = str(audio_file)
                
                # Get duration for display
                try:
                    if HAS_SOUNDDEVICE:
                        data, sr = sf.read(str(audio_file))
                        duration = len(data) / sr
                    else:
                        duration = 0
                except:
                    duration = 0
                
                if duration > 0:
                    print(f"{Color.MEMORY}    ✓ {sound_type}: {audio_file.name} ({duration:.2f}s){Color.RESET}")
                else:
                    print(f"{Color.MEMORY}    ✓ {sound_type}: {audio_file.name}{Color.RESET}")
            except Exception as e:
                print(f"{Color.ERROR}    ✗ Failed to load {audio_file.name}: {e}{Color.RESET}")
        
        if self.sounds:
            print(f"{Color.MEMORY}  ✓ Loaded {len(self.sounds)} sound types{Color.RESET}")
            return True
        return False

    def _categorize_sound(self, filename: str) -> str:
        """Determine sound type from filename."""
        if "moan" in filename:
            return "moan"
        elif "gasp" in filename or "ah" in filename or "oh" in filename:
            return "gasp"
        elif "laugh" in filename or "giggle" in filename:
            return "laugh"
        elif "breath" in filename:
            return "breath"
        elif "whimper" in filename:
            return "whimper"
        elif "sigh" in filename:
            return "sigh"
        else:
            return filename.split("_")[0] if "_" in filename else "other"

    def _play_sound(self, sound_type: str):
        """Play a sound file directly (blocking until done).
        
        Strongly prefers afplay (native macOS) to avoid PortAudio issues.
        sounddevice can cause delays due to CoreAudio unit initialization errors.
        """
        if not self.sounds or sound_type not in self.sounds:
            return
        
        sound_data = self.sounds[sound_type]
        
        # If sound is stored as a file path, use afplay directly (fast, native)
        if isinstance(sound_data, str):
            try:
                subprocess.run(["afplay", sound_data], check=False, timeout=30)
                return
            except:
                pass
        
        # For in-memory audio, save to temp file and use afplay
        # This avoids PortAudio/sounddevice delays entirely
        if isinstance(sound_data, tuple):
            import tempfile
            data, sr = sound_data
            try:
                # Create temp file with minimal overhead
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                    tmp_path = tmp.name
                
                # Write audio to temp file
                sf.write(tmp_path, data, sr)
                
                # Play using native afplay (fastest on macOS)
                subprocess.run(["afplay", tmp_path], check=False, timeout=30)
                
                # Clean up
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                return
            except Exception as e:
                pass

    def speak_with_bridge(self, response: str, insert_moans: bool = False, sound_type: str = "moan", block: bool = True, voice: str = "default"):
        """Speak response with sound markers.
        
        CORRECTED APPROACH:
        1. Extract markers FIRST using regex
        2. Split text into [speech, marker, speech, marker, ...] segments
        3. For speech segments: pass to voice.py WITHOUT markers (so voice.py doesn't interfere)
        4. For marker segments: play the sound file directly
        
        Args:
            response: Text to speak (may contain markers like *moan*)
            insert_moans: Deprecated, ignored
            sound_type: Default sound type if not using markers
            block: If True, wait for playback to finish before returning
            voice: Voice name to use
        """
        try:
            if not self._tts_engine:
                from core.voice import VoiceEngine
                self._tts_engine = VoiceEngine(self.config)
            
            clean = response.strip()
            if not clean:
                return
            
            # EXTRACT markers BEFORE voice.py processes them
            segments = self._parse_markers_first(clean)
            
            if block:
                # Blocking: play all segments and wait for completion
                self._play_segments_blocking(segments, voice)
            else:
                # Non-blocking: play in background thread
                self._play_segments_nonblocking(segments, voice)
                
        except Exception as e:
            print(f"{Color.DEBUG}[Voice bridge error: {e}]{Color.RESET}")

    def _parse_markers_first(self, text: str) -> List[Dict]:
        """
        Extract markers FIRST, before voice.py processes them.
        
        Pattern: *keyword* where keyword is alphanumeric/underscore
        Example: "I love you *moan* so much" 
        Result: [
            {"type": "speech", "text": "I love you"},
            {"type": "sound", "name": "moan"},
            {"type": "speech", "text": "so much"}
        ]
        """
        # Match markers like *moan*, *gasp*, etc (case-insensitive)
        parts = re.split(r'(\*[a-zA-Z_]+\*)', text)
        
        segments = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Check if this is a marker
            if part.startswith('*') and part.endswith('*'):
                marker_name = part[1:-1].lower()
                segments.append({"type": "sound", "name": marker_name})
            else:
                # Regular speech
                segments.append({"type": "speech", "text": part})
        
        return segments

    def _play_segments_blocking(self, segments: List[Dict], voice_name: str = "default"):
        """
        Play speech and sounds interspersed for natural conversation.
        
        OPTIMAL APPROACH:
        1. Combine ALL speech into one text
        2. Build a timing map: where each sound should play (char position in text)
        3. Start speech in background thread (non-blocking)
        4. Calculate delays for each sound based on speaking speed
        5. Play sounds at calculated times (overlaps with speech)
        6. Wait for both speech and sounds to finish
        
        Speaking speed: Kokoro speaks at ~2.5-3 chars/sec (150 wpm = ~900 chars/min)
        This gives us accurate timing for sound placement.
        
        Result: Sounds play DURING speech at natural moments, seamless conversation
        """
        self._playing = True
        speech_thread = None
        sound_thread = None
        
        try:
            # Collect speech and build timing map for sounds
            speech_text = ""
            char_position = 0
            sound_timings = []  # List of (char_offset, sound_name)
            
            for seg in segments:
                if seg["type"] == "speech":
                    if speech_text:
                        speech_text += " "
                        char_position += 1
                    speech_text += seg["text"]
                    char_position += len(seg["text"])
                else:  # sound
                    # Record where this sound should play (at current position in text)
                    sound_timings.append((char_position, seg["name"]))
            
            if not speech_text:
                # No speech, just play sounds sequentially
                for _, sound_name in sound_timings:
                    self._play_sound(sound_name)
                return
            
            # Estimate total speaking duration for timeout
            estimated_duration = len(speech_text) / 2.8  # ~2.8 chars/sec
            
            def play_speech():
                """Run TTS in background thread."""
                try:
                    self._tts_engine.speak(speech_text, voice=voice_name, block=True, no_sound_interleaving=True)
                except Exception as e:
                    pass
            
            def play_sounds_interspersed():
                """Play sounds at calculated times during speech playback."""
                try:
                    # Add 0.3s startup delay (let Kokoro subprocess start)
                    time.sleep(0.3)
                    
                    for char_offset, sound_name in sound_timings:
                        # Calculate when to play this sound based on text position
                        # At ~2.8 chars/sec speaking speed
                        delay = char_offset / 2.8
                        
                        # Sleep until it's time to play this sound
                        time.sleep(delay)
                        self._play_sound(sound_name)
                except Exception as e:
                    pass
            
            # Start both speech and sounds in background threads
            speech_thread = threading.Thread(target=play_speech, daemon=False)
            speech_thread.start()
            
            if sound_timings:
                sound_thread = threading.Thread(target=play_sounds_interspersed, daemon=False)
                sound_thread.start()
            
            # Wait for both to finish
            timeout = max(15, estimated_duration + 5)
            
            if speech_thread:
                speech_thread.join(timeout=timeout)
            if sound_thread:
                sound_thread.join(timeout=timeout)
                    
        finally:
            self._playing = False

    def _play_segments_nonblocking(self, segments: List[Dict], voice_name: str = "default"):
        """Play segments in background thread (non-blocking to caller)."""
        def _run():
            try:
                self._play_segments_blocking(segments, voice_name)
            except Exception as e:
                pass
        
        # Stop any currently playing audio before starting new playback
        if self._play_thread and self._play_thread.is_alive():
            try:
                self._play_thread.join(timeout=1.0)  # Wait up to 1 second
            except:
                pass
        
        # Use non-daemon thread so it completes before process exits
        self._play_thread = threading.Thread(target=_run, daemon=False)
        self._play_thread.start()

    def speak(self, text: str, block: bool = True, voice: str = "default"):
        """Simple speak without sound markers.
        
        Args:
            text: Text to speak (pure speech, no markers)
            block: If True (default), wait for playback to finish
            voice: Voice name to use
        """
        try:
            if not self._tts_engine:
                from core.voice import VoiceEngine
                self._tts_engine = VoiceEngine(self.config)
            
            # Pass to voice.py with sound interleaving disabled
            self._tts_engine.speak(text, voice=voice, block=block, no_sound_interleaving=True)
        except Exception as e:
            print(f"{Color.DEBUG}[Voice error: {e}]{Color.RESET}")

    def stop(self):
        """Stop any currently playing audio."""
        self._playing = False
        if self._play_thread and self._play_thread.is_alive():
            self._play_thread.join(timeout=0.5)
        try:
            subprocess.run(["killall", "afplay"], check=False, timeout=1)
        except:
            pass

    def status(self) -> str:
        """Return status string."""
        lines = []
        lines.append(f"\n{Color.ADVOCATE}🎙️ HYBRID VOICE STATUS{Color.RESET}")
        lines.append(f"  TTS: {'✓ Kokoro' if self._has_tts else '✗ Not available'}")
        
        if self.manual_sounds_dir:
            lines.append(f"  Sounds: ✓ Loaded ({len(self.sounds)} types)")
            for sound_type in sorted(self.sounds.keys()):
                lines.append(f"    - {sound_type}")
        else:
            lines.append(f"  Sounds: ✗ Not loaded (use: voice sounds /path/to/dir)")
        
        lines.append(f"  Status: {'🔊 Playing' if self._playing else '⏹ Idle'}")
        
        return "\n".join(lines)
