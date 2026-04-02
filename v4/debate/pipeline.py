#!/usr/bin/env python3
"""
⚡ EXTREME LOCAL GPT v4 — Debate Pipeline
3-cycle debate: Advocate ↔ Critic ↔ Synthesis

Same core logic as v3's debate engine + truth synthesizer, cleaned up.
"""

import time
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict

from core.config import AppConfig, Color
from core.inference import InferenceEngine
from debate.prompts import PromptLibrary


@dataclass
class CycleResult:
    """Result of one debate cycle."""
    perspective: str  # "advocate" or "critic"
    cycle: int
    text: str
    tokens: int
    time_taken: float

    @property
    def speed(self) -> float:
        return self.tokens / self.time_taken if self.time_taken > 0 else 0


@dataclass
class DebateResult:
    """Complete debate result."""
    dilemma: str
    cycles: List[CycleResult] = field(default_factory=list)
    synthesis_text: str = ""
    synthesis_tokens: int = 0
    synthesis_time: float = 0

    @property
    def total_tokens(self) -> int:
        return sum(c.tokens for c in self.cycles) + self.synthesis_tokens

    @property
    def total_time(self) -> float:
        return sum(c.time_taken for c in self.cycles) + self.synthesis_time

    @property
    def advocate_text(self) -> str:
        """Last advocate response."""
        for c in reversed(self.cycles):
            if c.perspective == "advocate":
                return c.text
        return ""

    @property
    def critic_text(self) -> str:
        """Last critic response."""
        for c in reversed(self.cycles):
            if c.perspective == "critic":
                return c.text
        return ""

    def all_responses(self) -> List[Tuple[str, str]]:
        """All responses as (label, text) pairs."""
        results = []
        for c in self.cycles:
            results.append((f"{c.perspective.upper()} C{c.cycle}", c.text))
        results.append(("SYNTHESIS", self.synthesis_text))
        return results


class DebatePipeline:
    """
    Orchestrates multi-cycle debates.

    Flow per cycle:
      1. Advocate argues FOR a position
      2. Critic attacks the Advocate's argument
    After all cycles:
      3. Synthesis merges both into a verdict
    """

    def __init__(self, inference: InferenceEngine, config: AppConfig):
        self.inference = inference
        self.config = config
        self.prompts = PromptLibrary()

    def run(
        self,
        dilemma: str,
        cycles: int = 2,
        is_nsfw: bool = False,
        stream: bool = True,
        context_injections: Optional[str] = None,
        wisdom_context: Optional[str] = None,
        persona_context: Optional[str] = None,
    ) -> DebateResult:
        """
        Run a complete debate.

        Args:
            dilemma: The topic/question to debate
            cycles: Number of Advocate↔Critic cycles
            is_nsfw: Whether to use explicit prompts
            stream: Whether to stream output token-by-token
            context_injections: Past debate context from RAG
            wisdom_context: Historical wisdom parallels
            persona_context: Personalization context
        """
        result = DebateResult(dilemma=dilemma)

        advocate_history = []
        critic_history = []

        for cycle_num in range(1, cycles + 1):
            print(f"\n{Color.BOLD}{'═' * 60}")
            print(f"  CYCLE {cycle_num}/{cycles}")
            print(f"{'═' * 60}{Color.RESET}")

            # ── ADVOCATE ──
            advocate_result = self._run_advocate(
                dilemma=dilemma,
                cycle=cycle_num,
                is_nsfw=is_nsfw,
                previous_critic=critic_history[-1] if critic_history else None,
                context_injections=context_injections,
                wisdom_context=wisdom_context if cycle_num == 1 else None,
                persona_context=persona_context,
                stream=stream,
            )
            result.cycles.append(advocate_result)
            advocate_history.append(advocate_result.text)

            # ── CRITIC ──
            critic_result = self._run_critic(
                dilemma=dilemma,
                cycle=cycle_num,
                is_nsfw=is_nsfw,
                advocate_text=advocate_result.text,
                previous_advocate=advocate_history[-2] if len(advocate_history) > 1 else None,
                persona_context=persona_context,
                stream=stream,
            )
            result.cycles.append(critic_result)
            critic_history.append(critic_result.text)

        # ── SYNTHESIS ──
        synthesis_text, synthesis_tokens, synthesis_time = self._run_synthesis(
            dilemma=dilemma,
            advocate_text=advocate_history[-1],
            critic_text=critic_history[-1],
            is_nsfw=is_nsfw,
            wisdom_context=wisdom_context,
            persona_context=persona_context,
            stream=stream,
        )
        result.synthesis_text = synthesis_text
        result.synthesis_tokens = synthesis_tokens
        result.synthesis_time = synthesis_time

        return result

    def _run_advocate(
        self, dilemma, cycle, is_nsfw, previous_critic,
        context_injections, wisdom_context, persona_context, stream
    ) -> CycleResult:
        """Run Advocate cycle."""
        print(f"\n{Color.ADVOCATE}💚 ADVOCATE (Cycle {cycle})...{Color.RESET}")

        system_prompt = self.prompts.advocate_system(
            is_nsfw=is_nsfw, cycle=cycle, persona_context=persona_context
        )
        user_prompt = self.prompts.advocate_user(
            dilemma=dilemma,
            cycle=cycle,
            previous_critic=previous_critic,
            context_injections=context_injections,
            wisdom_context=wisdom_context,
        )

        start = time.time()
        response, metadata = self.inference.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=self.config.model.max_tokens["debate_cycle"],
        )
        elapsed = time.time() - start

        if stream:
            print(f"{Color.ADVOCATE}{response}{Color.RESET}")

        print(f"{Color.DEBUG}✓ {metadata['tokens']} tokens in {elapsed:.1f}s ({metadata['speed']:.0f} tok/s){Color.RESET}")

        return CycleResult(
            perspective="advocate",
            cycle=cycle,
            text=response,
            tokens=metadata["tokens"],
            time_taken=elapsed,
        )

    def _run_critic(
        self, dilemma, cycle, is_nsfw, advocate_text,
        previous_advocate, persona_context, stream
    ) -> CycleResult:
        """Run Critic cycle."""
        print(f"\n{Color.CRITIC}🔴 CRITIC (Cycle {cycle})...{Color.RESET}")

        system_prompt = self.prompts.critic_system(
            is_nsfw=is_nsfw, cycle=cycle, persona_context=persona_context
        )
        user_prompt = self.prompts.critic_user(
            dilemma=dilemma,
            cycle=cycle,
            advocate_text=advocate_text,
            previous_advocate=previous_advocate,
        )

        start = time.time()
        response, metadata = self.inference.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=self.config.model.max_tokens["debate_cycle"],
        )
        elapsed = time.time() - start

        if stream:
            print(f"{Color.CRITIC}{response}{Color.RESET}")

        print(f"{Color.DEBUG}✓ {metadata['tokens']} tokens in {elapsed:.1f}s ({metadata['speed']:.0f} tok/s){Color.RESET}")

        return CycleResult(
            perspective="critic",
            cycle=cycle,
            text=response,
            tokens=metadata["tokens"],
            time_taken=elapsed,
        )

    def _run_synthesis(
        self, dilemma, advocate_text, critic_text, is_nsfw,
        wisdom_context, persona_context, stream
    ) -> Tuple[str, int, float]:
        """Run Synthesis (final verdict)."""
        print(f"\n{Color.SYNTHESIS}⚡ SYNTHESIS...{Color.RESET}")

        system_prompt = self.prompts.synthesis_system(
            is_nsfw=is_nsfw, persona_context=persona_context
        )
        user_prompt = self.prompts.synthesis_user(
            dilemma=dilemma,
            advocate_text=advocate_text,
            critic_text=critic_text,
            wisdom_context=wisdom_context,
        )

        start = time.time()
        response, metadata = self.inference.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=self.config.model.max_tokens["synthesis"],
        )
        elapsed = time.time() - start

        if stream:
            print(f"{Color.SYNTHESIS}{response}{Color.RESET}")

        print(f"{Color.DEBUG}✓ {metadata['tokens']} tokens in {elapsed:.1f}s ({metadata['speed']:.0f} tok/s){Color.RESET}")

        return response, metadata["tokens"], elapsed
