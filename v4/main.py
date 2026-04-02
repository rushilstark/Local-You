#!/usr/bin/env python3
"""
⚡ EXTREME LOCAL GPT v4 — Main Entry Point

Automatically initializes:
  • Your Digital Twin (from diary)
  • Honest Feedback Engine
  • Voice Enhancement (8 agents)
  • 100% local, no APIs

Just run: python3 v4/main.py
"""

import sys
import os
from pathlib import Path

# 💥 CRITICAL APPLE SILICON FIX 💥
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"

# Allow running from either gpt-from-scratch/ or v4/
if os.path.basename(os.getcwd()) == "v4":
    sys.path.insert(0, os.getcwd())
else:
    sys.path.insert(0, os.path.join(os.getcwd(), "v4"))
    # Add parent dir for digital_twin imports
    sys.path.insert(0, os.getcwd())

from core.config import load_config, Color
from core.engine import Engine

# Initialize Digital Twin (reads diary automatically)
try:
    from jarvis_digital_twin import initialize_digital_twin
    digital_twin = initialize_digital_twin(
        diary_folder=Path("data/diary"),
        data_folder=Path("data")
    )
    print(f"{Color.DEBUG}✓ Digital Twin initialized from diary{Color.RESET}")
except Exception as e:
    print(f"{Color.WARNING}⚠ Digital Twin skipped (no diary yet): {e}{Color.RESET}")
    digital_twin = None


def main():
    print(f"\n{Color.BOLD}{Color.SYNTHESIS}⚡ EXTREME LOCAL GPT v4{Color.RESET}")
    print(f"{Color.DIM}Unfiltered • Debate • Memory • Personalization • Digital Twin{Color.RESET}\n")

    # Load config
    config = load_config()

    # Initialize engine (loads model + all subsystems)
    print(f"{Color.DEBUG}Initializing...{Color.RESET}")
    engine = Engine(config)
    
    # Add digital twin system prompt to engine if available
    if digital_twin and digital_twin.get_system_prompt():
        # Inject digital twin prompt into engine's system context
        pass  # Engine will use its own system prompt, but digital twin is ready

    print(f"\n{Color.CHAT}{Color.BOLD}💬 Ready!{Color.RESET}")
    print(f"{Color.DEBUG}Type 'help' for commands or just start chatting.{Color.RESET}\n")

    # Interactive loop
    while True:
        try:
            user_input = input(f"{Color.BOLD}You: {Color.RESET}")

            lower = user_input.strip().lower()
            if lower in ("quit", "exit"):
                print(f"{Color.DEBUG}Goodbye.{Color.RESET}")
                break

            # Process through engine
            result = engine.process_input(user_input)

            if result is None:
                continue

            if result:
                # Apply digital twin processing if available
                if digital_twin:
                    processed = digital_twin.process_response(user_input, result)
                    response = result
                    
                    # Show honest feedback if there are concerns
                    if processed.get("honest_feedback"):
                        print(f"\n{Color.WARNING}⚠ Honest Take: {processed['honest_feedback']}{Color.RESET}")
                    
                    digital_twin.remember_conversation(user_input, result)
                else:
                    response = result
                
                print(f"\n{Color.CHAT}{Color.BOLD}GPT:{Color.RESET} {response}\n")

        except KeyboardInterrupt:
            print(f"\n{Color.DEBUG}Interrupted. Type 'quit' to exit.{Color.RESET}")
        except EOFError:
            break


if __name__ == "__main__":
    main()
