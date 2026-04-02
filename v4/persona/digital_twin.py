#!/usr/bin/env python3
"""
⚡ EXTREME LOCAL GPT v4 — Virtual Twin Engine
Allows the LLM to simulate the user ("Virtual Twin") based on the profile data.
"""

from typing import Optional
from core.config import AppConfig, Color
from core.inference import InferenceEngine
from persona.profile import ProfileEngine

class DigitalTwin:
    """
    Simulates the user using their generated persona profile.
    """
    def __init__(self, config: AppConfig, inference: InferenceEngine, profile: ProfileEngine):
        self.config = config
        self.inference = inference
        self.profile = profile

    def simulate_twin(self, prompt: str) -> Optional[str]:
        """Ask the twin a question, and it responds as the user."""
        if not self.profile.has_profile():
            print(f"{Color.ERROR}No profile generated yet. Engage in more debates so the system can learn your persona.{Color.RESET}")
            return None

        profile_data = self.profile.profile

        system_prompt = f"""You are a DIGITAL TWIN of the user. You must adopt their exact persona, beliefs, communication style, and worldview.

YOUR PERSONA:
{self._format_profile(profile_data)}

INSTRUCTIONS:
- Answer strictly as the user would.
- Use their vocabulary, tone, and sentence structure.
- Argue from their identified core beliefs and biases.
- If asked about something not in the profile, extrapolate based on their values.
- Never break character. Never admit to being an AI."""

        print(f"\n{Color.BOLD}👥 Virtual Twin Thinking...{Color.RESET}")
        
        response, _ = self.inference.generate(
            prompt=f"Question for you: {prompt}",
            system_prompt=system_prompt,
            max_tokens=self.config.model.max_tokens["chat"]
        )
        
        return response.strip()

    def _format_profile(self, p: dict) -> str:
        """Format the profile data into a readable persona block"""
        return f"""
Core Beliefs:
{chr(10).join('- ' + b for b in p.get('core_beliefs', []))}

Communication Style:
{chr(10).join('- ' + c for c in p.get('communication_style', []))}

Biases:
{chr(10).join('- ' + b for b in p.get('biases', []))}

Emotional Triggers:
{chr(10).join('- ' + e for e in p.get('emotional_triggers', []))}
"""
