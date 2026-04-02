#!/usr/bin/env python3
"""Test the TTS subprocess directly"""
import os
import sys
import json
import subprocess
import tempfile

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# Write a simple test script inline
test_script = '''
import sys
import json
import os
import numpy as np

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["KOKORO_VOICE"] = "af_heart"

def main():
    request_line = sys.stdin.readline()
    if not request_line:
        sys.exit(1)
    request = json.loads(request_line)
    
    text = request.get("text", "")
    voice = request.get("voice", "af_heart")
    output_path = request.get("output_path")
    
    if not text:
        sys.exit(1)

    try:
        import kokoro
        
        # Initialize pipeline
        try:
            pipeline = kokoro.KPipeline(lang_code="a")
        except:
            pipeline = kokoro.KPipeline()
        
        # Generate audio
        try:
            audio = pipeline(text, voice=voice)
        except TypeError:
            audio = pipeline(text)
        except:
            audio = pipeline(text, voice="af_heart")
        
        # Handle generator - iterate through Result objects
        if hasattr(audio, '__iter__') and not isinstance(audio, (np.ndarray, str, bytes)):
            try:
                audio_chunks = []
                sr = 24000
                for result in audio:
                    # Result is a KPipeline.Result object
                    if hasattr(result, 'audio'):
                        chunk = result.audio
                        if hasattr(result, 'sample_rate'):
                            sr = result.sample_rate
                    elif isinstance(result, (tuple, list)) and len(result) >= 1:
                        chunk = result[0]
                        if len(result) > 1:
                            sr = result[1]
                    else:
                        chunk = result
                    
                    if isinstance(chunk, np.ndarray):
                        audio_chunks.append(chunk)
                    elif chunk is not None:
                        audio_chunks.append(np.asarray(chunk, dtype=np.float32))
                
                if audio_chunks:
                    audio = np.concatenate(audio_chunks)
                else:
                    raise ValueError("No audio chunks generated")
            except Exception as gen_err:
                audio = pipeline(text)
        
        # Ensure audio is numpy array
        if not isinstance(audio, np.ndarray):
            audio = np.asarray(audio, dtype=np.float32)
        
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

# Write test script to temp file
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(test_script)
    script_path = f.name

try:
    # Create a request
    request = json.dumps({
        "text": "Hello, testing the Kokoro voice engine.",
        "voice": "af_heart",
    })
    
    print(f"Testing TTS subprocess with: {request}")
    print()
    
    # Run subprocess
    result = subprocess.run(
        [sys.executable, script_path],
        input=request + "\n",
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    print(f"Return code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    if result.stderr:
        print(f"Stderr: {result.stderr[:200]}")
    
    if result.returncode == 0:
        print("\n✅ TTS subprocess works!")
    else:
        print("\n❌ TTS subprocess failed")

finally:
    # Clean up
    os.unlink(script_path)
