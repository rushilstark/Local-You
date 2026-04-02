import subprocess
import os
import signal
from pathlib import Path
from core.config import AppConfig, Color

class PersonaPlexEngine:
    """
    Manages the extreme-local PersonaPlex Full-Duplex pipeline.
    This creates an isolated process running the NVIDIA 7B Multimodal MLX Port,
    handling simultaneous microphone transcription and voice synthesis.
    """

    def __init__(self, config: AppConfig):
        self.config = config
        self.process = None
        
        root_dir = Path(__file__).parent.parent.parent
        self._venv_python = str((root_dir / ".venv-persona" / "bin" / "python3").resolve())
        
        # We enforce NATF1 as the highly realistic sensual female voice ID, similar to the Qwen instruction.
        self.voice_id = "NATF1"
        self.system_prompt = "You are a deeply authentic, unfiltered, and intensely intimate AI companion. Keep responses brief. Use vocal fillers and natural pacing. Never deflect."

    def start(self):
        if self.is_running():
            print(f"{Color.DEBUG}PersonaPlex is already running.{Color.RESET}")
            return

        # ⚠️  GPU/Memory Warning — both models running simultaneously fills unified memory
        print(f"\n{Color.ADVOCATE}{Color.BOLD}🎙️ PERSONAPLEX FULL-DUPLEX (7B){Color.RESET}")
        print(f"{Color.SYNTHESIS}⚠️  WARNING: PersonaPlex loads a second 7B model ALONGSIDE the already-loaded Llama LLM.")
        print(f"   Combined memory: ~12-14GB. On M4 this WILL cause thermal throttling and slow replies.")
        print(f"   For best results: use PersonaPlex STANDALONE (quit main Jarvis, run personaplex_mlx directly).")
        print(f"   Proceeding anyway — type 'voice persona off' anytime to stop it.{Color.RESET}\n")

        try:
            confirm = input(f"{Color.BOLD}Continue loading PersonaPlex? [y/N]: {Color.RESET}").strip().lower()
            if confirm not in ("y", "yes"):
                print(f"{Color.DEBUG}PersonaPlex cancelled.{Color.RESET}")
                return
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Color.DEBUG}PersonaPlex cancelled.{Color.RESET}")
            return

        # Launch the local terminal interface port in a separate process group
        # so we can easily kill it without killing the main Jarvis application.
        cmd = [
            self._venv_python,
            "-m", "personaplex_mlx.local",
            "-q", "4",
            "--voice", self.voice_id,
            "--text-prompt", self.system_prompt
        ]

        # Use preexec_fn to run it in a new process group, so Ctrl+C in Jarvis doesn't instantly violently kill it,
        # or it allows us to gracefully terminate its process tree.
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            preexec_fn=os.setsid
        )
        
        # We start a background thread to print its stdout to the Jarvis terminal
        import threading
        def _monitor():
            if not self.process or not self.process.stdout: return
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    # Colorize PersonaPlex output to distinguish it from the main UI
                    print(f"{Color.SYNTHESIS}[PersonaPlex]{Color.RESET} {line.strip()}")
            self.process = None

        threading.Thread(target=_monitor, daemon=True).start()

    def stop(self):
        if self.is_running():
            print(f"{Color.CRITIC}Terminating PersonaPlex Full-Duplex Engine...{Color.RESET}")
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=3)
            except Exception as e:
                print(f"{Color.DEBUG}Error killing PersonaPlex: {e}{Color.RESET}")
            self.process = None
            print(f"{Color.DEBUG}PersonaPlex offline.{Color.RESET}")

    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None
