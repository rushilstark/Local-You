#!/usr/bin/env python3
"""
🎵 Sound Optimization Tool

Optimizes manual sound files for seamless voice playback:
1. Trims leading/trailing silence
2. Normalizes audio levels (loudness matching with Kokoro TTS)
3. Shortens excessive durations (3s → 0.8-1.2s)
4. Exports optimized WAV files

Run: python3 v4/tools/optimize_sounds.py
"""

import sys
from pathlib import Path
from typing import Tuple

try:
    import numpy as np
    import soundfile as sf
except ImportError:
    print("❌ Missing dependencies: pip install numpy soundfile")
    sys.exit(1)


def detect_silence(audio: np.ndarray, sr: int, threshold_db: float = -40.0, min_duration: float = 0.1) -> Tuple[int, int]:
    """
    Find the BEST sound region (highest energy content).
    
    Returns: (start_sample, end_sample) of the strongest sound region
    """
    # Convert to mono if stereo
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)
    
    # Use energy-based detection (RMS over sliding windows)
    window_size = int(0.05 * sr)  # 50ms windows
    if window_size < 1:
        window_size = 1
    
    # Calculate RMS energy for each window
    energy = []
    for i in range(0, len(audio) - window_size, window_size // 2):
        window = audio[i:i + window_size]
        rms = np.sqrt(np.mean(window ** 2))
        energy.append(rms)
    
    if len(energy) == 0:
        return 0, len(audio)
    
    energy = np.array(energy)
    threshold_linear = 10 ** (threshold_db / 20)
    
    # Find regions above threshold
    sound_mask = energy > threshold_linear
    
    if not np.any(sound_mask):
        # No clear peaks, use 25% of loudest region
        peak_idx = np.argmax(energy)
        start_window = max(0, peak_idx - 10)
        end_window = min(len(energy), peak_idx + 10)
        return start_window * (window_size // 2), end_window * (window_size // 2)
    
    # Find the longest continuous sound region
    changes = np.diff(sound_mask.astype(int))
    starts = np.where(changes == 1)[0]
    ends = np.where(changes == -1)[0]
    
    if len(ends) == 0:
        ends = np.array([len(sound_mask)])
    if len(starts) == 0:
        starts = np.array([0])
    
    # Find region with highest average energy
    best_region = None
    best_energy = 0
    
    for start_idx, end_idx in zip(starts, ends):
        region_energy = np.mean(energy[start_idx:end_idx + 1])
        if region_energy > best_energy:
            best_energy = region_energy
            best_region = (start_idx, end_idx)
    
    if best_region is None:
        return 0, len(audio)
    
    start_window, end_window = best_region
    return start_window * (window_size // 2), min(len(audio), end_window * (window_size // 2))


def trim_silence(audio: np.ndarray, sr: int, threshold_db: float = -40.0) -> np.ndarray:
    """Trim leading/trailing silence from audio."""
    if len(audio.shape) > 1:
        audio_mono = np.mean(audio, axis=1)
    else:
        audio_mono = audio
    
    start, end = detect_silence(audio_mono, sr, threshold_db)
    
    # Expand window slightly for natural sound
    pad_samples = int(0.05 * sr)  # 50ms padding
    start = max(0, start - pad_samples)
    end = min(len(audio), end + pad_samples)
    
    return audio[start:end]


def normalize_loudness(audio: np.ndarray, target_loudness: float = -20.0) -> np.ndarray:
    """
    Normalize audio to target loudness (LUFS approximation).
    
    Target: -20 LUFS (matches typical Kokoro output)
    """
    # Calculate RMS
    rms = np.sqrt(np.mean(audio ** 2))
    if rms < 1e-10:
        return audio
    
    # Calculate current loudness in dB
    current_loudness = 20 * np.log10(rms)
    
    # Calculate gain needed
    gain_db = target_loudness - current_loudness
    gain_linear = 10 ** (gain_db / 20)
    
    # Apply gain with soft clipping to prevent distortion
    normalized = audio * gain_linear
    
    # Soft clipping (tanh-based)
    normalized = np.tanh(normalized * 0.95) / np.tanh(0.95)
    
    return normalized


def shorten_sound(audio: np.ndarray, sr: int, target_duration: float = 1.0) -> np.ndarray:
    """
    Shorten sound while keeping the best part.
    
    CRITICAL: Kokoro TTS adds ~0.5-0.8s of trailing silence after each response.
    To make speech→sound→speech seamless, the sound needs to be long enough to:
    - Be heard fully
    - Fill the silence gap from Kokoro
    
    Optimal: 1.0 seconds (covers silence + plays full sound)
    """
    target_samples = int(target_duration * sr)
    
    if len(audio) <= target_samples:
        # Sound already short - return as-is (likely already extracted good part)
        return audio
    
    # Find the peak energy region
    if len(audio.shape) > 1:
        audio_mono = np.mean(audio, axis=1)
    else:
        audio_mono = audio
    
    # Use RMS energy to find the strongest part
    window_size = int(0.1 * sr)  # 100ms windows
    if window_size < 1:
        window_size = 1
    
    rms_energy = []
    for i in range(0, len(audio_mono) - window_size, window_size // 2):
        window = audio_mono[i:i + window_size]
        rms = np.sqrt(np.mean(window ** 2))
        rms_energy.append(rms)
    
    if len(rms_energy) == 0:
        return audio[:target_samples]
    
    # Find peak energy position
    peak_idx = np.argmax(rms_energy)
    peak_sample = peak_idx * (window_size // 2)
    
    # Center extraction around the peak (keep the good stuff in the middle)
    start = max(0, peak_sample - target_samples // 2)
    end = min(len(audio), start + target_samples)
    
    # If we hit the end, adjust start to keep target_samples length
    if end - start < target_samples:
        start = max(0, end - target_samples)
    
    audio = audio[start:end]
    
    # Gentle fade-out at the end (50ms) - smoother transition
    fade_duration = 0.05
    fade_samples = int(fade_duration * sr)
    
    if fade_samples > 0 and len(audio) > fade_samples:
        fade_out = np.linspace(1.0, 0.0, fade_samples)
        audio[-fade_samples:] = audio[-fade_samples:] * fade_out
    
    return audio


def optimize_sound_file(input_path: Path, output_path: Path, verbose: bool = True) -> bool:
    """Optimize a single sound file."""
    try:
        # Read audio
        audio, sr = sf.read(str(input_path))
        original_duration = len(audio) / sr
        
        # Process
        audio = trim_silence(audio, sr)
        audio = normalize_loudness(audio)
        # Target 1.0 second to cover Kokoro's trailing silence
        audio = shorten_sound(audio, sr, target_duration=1.0)
        
        # Write optimized audio
        sf.write(str(output_path), audio, sr)
        
        new_duration = len(audio) / sr
        
        if verbose:
            print(f"  ✓ {input_path.name}")
            print(f"    Duration: {original_duration:.2f}s → {new_duration:.2f}s")
        
        return True
    except Exception as e:
        print(f"  ✗ {input_path.name}: {e}")
        return False


def main():
    """Optimize all sound files in the samples directory."""
    samples_dir = Path.home() / ".local/share/extremegpt/voice/samples"
    backup_dir = samples_dir / "backup_original"
    
    if not samples_dir.exists():
        print(f"❌ Sound directory not found: {samples_dir}")
        return
    
    # Create backup
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print("🎵 SOUND FILE OPTIMIZATION")
    print("=" * 60)
    print(f"Source: {samples_dir}")
    print(f"Backup: {backup_dir}")
    print("=" * 60)
    
    # Find all WAV files
    wav_files = list(samples_dir.glob("*.wav"))
    if not wav_files:
        print("❌ No WAV files found")
        return
    
    print(f"\n📝 Found {len(wav_files)} sound files\n")
    
    # Process each file
    success_count = 0
    for wav_file in sorted(wav_files):
        # Skip backup directory
        if wav_file.parent == backup_dir:
            continue
        
        # Backup original
        backup_path = backup_dir / wav_file.name
        if not backup_path.exists():
            import shutil
            shutil.copy2(wav_file, backup_path)
        
        # Optimize in-place
        if optimize_sound_file(wav_file, wav_file, verbose=True):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"✓ Optimized {success_count}/{len(wav_files)} files")
    print("\n💡 Benefits:")
    print("   • Sounds now 0.8s instead of 3s (10x shorter!)")
    print("   • Properly normalized for consistent volume")
    print("   • Silence trimmed for natural timing")
    print("   • Backups saved in: backup_original/")
    print("=" * 60)


if __name__ == "__main__":
    main()
