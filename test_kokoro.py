#!/usr/bin/env python3
import os
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

import kokoro
import numpy as np

print("Testing Kokoro API...")

try:
    # Initialize pipeline
    pipeline = kokoro.KPipeline(lang_code="a")
    print(f"✅ Pipeline initialized: {type(pipeline)}")
    
    # Test basic call
    text = "Hello, how are you today?"
    print(f"\n🔧 Calling pipeline with: '{text}'")
    
    result = pipeline(text, voice="af_heart")
    print(f"✅ Result type: {type(result)}")
    print(f"✅ Result repr: {repr(result)[:100]}")
    
    # Check if it's a generator
    if hasattr(result, '__iter__') and not isinstance(result, (np.ndarray, list, tuple, str, bytes)):
        print("⚠️  Result is iterable (likely generator)")
        try:
            # Try to get first item
            first_item = next(iter(result))
            print(f"   First item type: {type(first_item)}")
            print(f"   First item shape/len: {first_item.shape if hasattr(first_item, 'shape') else len(first_item)}")
        except StopIteration:
            print("   Generator is empty!")
    
    # Try different signatures
    print("\n🔧 Trying different signatures...")
    
    print("   1. pipeline(text, voice) - already tried")
    
    # Try without voice
    try:
        result2 = pipeline(text)
        print(f"   2. pipeline(text) works: {type(result2)}")
    except Exception as e:
        print(f"   2. pipeline(text) failed: {e}")
    
    # Try with different parameters
    try:
        result3 = pipeline(text, speaker="af_heart")
        print(f"   3. pipeline(text, speaker=...) works: {type(result3)}")
    except Exception as e:
        print(f"   3. pipeline(text, speaker=...) failed: {e}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
