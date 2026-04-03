#!/usr/bin/env python3
"""
⚡ EXTREME LOCAL GPT v4 — Main Engine
Central orchestrator. Routes input to chat/debate/commands.

Carries over ALL v3 features:
- Unfiltered/abliterated mode
- NSFW direct mode
- 3-cycle debate
- Brutal truth (zero consolation)
- Personalization
- Memory + Patterns + Wisdom
"""

import re
from typing import Optional
from pathlib import Path

from core.config import AppConfig, Color
from core.inference import InferenceEngine, validate_unfiltered_response


class Engine:
    """
    Central orchestrator for the system.

    Manages all subsystems and routes user input to the right handler.
    Each subsystem loads independently — if one fails, others still work.
    """

    def __init__(self, config: AppConfig):
        self.config = config
        self.inference = InferenceEngine(config)

        # ── Subsystems (load independently, graceful degradation) ──
        self.debate_pipeline = None
        self.conversation = None
        self.semantic_memory = None
        self.knowledge = None
        self.profile = None
        self.nsfw_detector = None
        self.voice = None
        self.voice_mode = False  # When True, responses are spoken aloud
        self.omni_pipeline = None
        self.vision = None
        self.twin = None
        self.trainer = None
        self.system_prompt = None  # Will be set by digital twin if available
        self.diary_rag = None  # Diary-based retrieval for context
        self.semantic_index = None  # Semantic search with embeddings (Phase 1)
        self.knowledge_graph = None  # Memory connections graph (Phase 4)

        self._init_subsystems()

    def _init_subsystems(self):
        """Load each subsystem independently. If one fails, others still work."""

        # Debate pipeline (always available)
        try:
            from debate.pipeline import DebatePipeline
            self.debate_pipeline = DebatePipeline(self.inference, self.config)
            print(f"{Color.DEBUG}  ✓ Debate pipeline{Color.RESET}")
        except Exception as e:
            print(f"{Color.ERROR}  ✗ Debate pipeline: {e}{Color.RESET}")

        # Persistent conversation memory
        try:
            from memory.conversation import ConversationMemory
            self.conversation = ConversationMemory(self.config)
            print(f"{Color.DEBUG}  ✓ Conversation memory (persistent){Color.RESET}")
        except Exception as e:
            print(f"{Color.ERROR}  ✗ Conversation memory: {e}{Color.RESET}")

        # Semantic memory (RAG) — optional, needs sentence-transformers
        if self.config.features.semantic_memory:
            try:
                from memory.semantic import SemanticMemory
                self.semantic_memory = SemanticMemory(self.config)
                count = self.semantic_memory.debate_count()
                print(f"{Color.MEMORY}  ✓ Semantic memory: {count} debates indexed{Color.RESET}")
            except Exception as e:
                print(f"{Color.DEBUG}  ⚠ Semantic memory: {e}{Color.RESET}")

        # Knowledge (wisdom + patterns)
        if self.config.features.wisdom_library or self.config.features.pattern_analysis:
            try:
                from memory.knowledge import KnowledgeBase
                self.knowledge = KnowledgeBase(self.config)
                print(f"{Color.MEMORY}  ✓ Knowledge base{Color.RESET}")
            except Exception as e:
                print(f"{Color.DEBUG}  ⚠ Knowledge base: {e}{Color.RESET}")

        # Personalization & Digital Twin
        try:
            from persona.profile import ProfileEngine
            from persona.digital_twin import DigitalTwin
            self.profile = ProfileEngine(self.config)
            self.twin = DigitalTwin(self.config, self.inference, self.profile)
            
            if self.profile.has_profile():
                print(f"{Color.DEBUG}  ✓ Personalization (confidence: {self.profile.confidence():.0f}%){Color.RESET}")
                print(f"{Color.DEBUG}  ✓ Virtual Twin Mode: ready{Color.RESET}")
            else:
                print(f"{Color.DEBUG}  ✓ Personalization (activates after {self.config.persona.min_debates_for_profile} debates){Color.RESET}")
        except Exception as e:
            print(f"{Color.DEBUG}  ⚠ Personalization: {e}{Color.RESET}")

        # Training Data Collector
        try:
            from memory.training import TrainingCollector
            self.trainer = TrainingCollector(self.config)
            print(f"{Color.MEMORY}  ✓ Training Collector ({self.trainer.samples_collected} samples){Color.RESET}")
        except Exception as e:
            print(f"{Color.DEBUG}  ⚠ Training Collector: {e}{Color.RESET}")

        # NSFW Detection
        if self.config.features.nsfw_mode:
            try:
                from debate.nsfw import NSFWDetector
                self.nsfw_detector = NSFWDetector()
                print(f"{Color.DEBUG}  ✓ NSFW mode: enabled{Color.RESET}")
            except Exception as e:
                print(f"{Color.DEBUG}  ⚠ NSFW mode: {e}{Color.RESET}")

        # 5. Voice Synthesis (Kokoro - High Quality)
        if self.config.features.voice_output:
            try:
                from core.voice import VoiceEngine
                self.voice = VoiceEngine(self.config)
                print(f"{Color.DEBUG}  ✓ Voice: Kokoro (44.1kHz CD quality){Color.RESET}")
            except Exception as e:
                print(f"{Color.ERROR}Failed to load Voice Engine: {e}{Color.RESET}")

        # Diary-based RAG for dynamic context retrieval
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from diary_rag import DiaryRAG
            self.diary_rag = DiaryRAG(Path("data/diary"))
            if self.diary_rag.indexed:
                print(f"{Color.DEBUG}  ✓ Diary RAG: {len(self.diary_rag.passages)} passages indexed{Color.RESET}")
        except Exception as e:
            print(f"{Color.DEBUG}  ⚠ Diary RAG: {e}{Color.RESET}")

        # PHASE 1: Semantic Index for intelligent context retrieval
        try:
            from memory.semantic_index import SemanticDiaryIndex
            self.semantic_index = SemanticDiaryIndex(Path("data/diary"), Path(".cache/semantic_embeddings"))
            print(f"{Color.DEBUG}  ✓ Semantic Index: {len(self.semantic_index.passages)} passages with embeddings{Color.RESET}")
        except Exception as e:
            print(f"{Color.DEBUG}  ⚠ Semantic Index: {e}{Color.RESET}")

        # PHASE 4: Knowledge Graph for memory connections
        try:
            from memory.knowledge_graph import DiaryKnowledgeGraph
            self.knowledge_graph = DiaryKnowledgeGraph(Path("data/diary"), Path(".cache/knowledge_graph.json"))
            print(f"{Color.DEBUG}  ✓ Knowledge Graph: {len(self.knowledge_graph.nodes)} nodes, {len(self.knowledge_graph.edges)} edges{Color.RESET}")
        except Exception as e:
            print(f"{Color.DEBUG}  ⚠ Knowledge Graph: {e}{Color.RESET}")

        # PERSONALITY EXTRACTION: Build custom system prompt from actual diary voice
        try:
            from core.personality_extractor import PersonalityExtractor
            extractor = PersonalityExtractor(Path("data/diary"))
            self.system_prompt = extractor.build_system_prompt()
            print(f"{Color.PERSONALITY}  ✓ Personality extracted from diary (custom system prompt){Color.RESET}")
        except Exception as e:
            print(f"{Color.PERSONALITY}  ⚠ Personality extraction: {e}{Color.RESET}")
            self.system_prompt = None

        # Omni Voice disabled - removed Qwen3
        self.omni_pipeline = None

        # PersonaPlex Engine (Lazy loaded, initialized on demand)
        self.personaplex = None
        
        # Auto-boot PersonaPlex if configured
        if hasattr(self.config.voice, 'persona_auto') and self.config.voice.persona_auto:
            print(f"{Color.DEBUG}  ✓ Auto-booting PersonaPlex Full-Duplex...{Color.RESET}")
            self._voice_persona_on()

        # Image Generation (FLUX)
        if self.config.features.image_generation:
            try:
                from vision.image_gen import ImageGenerator
                self.vision = ImageGenerator(self.config)
                if self.vision.loaded:
                    print(f"{Color.DEBUG}  ✓ Vision: enabled (FLUX.1 Schnell){Color.RESET}")
            except Exception as e:
                print(f"{Color.DEBUG}  ⚠ Vision: {e}{Color.RESET}")

    # =====================================================================
    # INPUT ROUTING
    # =====================================================================

    def process_input(self, user_input: str) -> Optional[str]:
        """
        Route user input to the right handler.
        Returns None for commands that don't produce chat output.
        """
        stripped = user_input.strip()
        lower = stripped.lower()

        # ── Commands ──
        if lower == "quit" or lower == "exit":
            return None  # Signal to exit
        if lower == "help":
            return self._help_text()
        if lower == "memory" or lower == "status":
            return self._memory_status()
        if lower == "history":
            return self._show_history()
        if lower.startswith("debate "):
            topic = stripped[7:].strip()
            if topic:
                self._run_debate(topic)
                return ""  # Debate prints its own output
            return "Usage: debate <topic>"
        if lower.startswith("quick "):
            topic = stripped[6:].strip()
            if topic:
                self._run_debate(topic, quick=True)
                return ""
            return "Usage: quick <topic>"
        if lower.startswith("twin "):
            prompt = stripped[5:].strip()
            if prompt:
                return self._run_digital_twin(prompt)
            return "Usage: twin <question>"
        if lower == "ingest":
            return self._ingest_notes()
        if lower.startswith("imagine ") or lower.startswith("image "):
            prompt = stripped[8:].strip() if lower.startswith("imagine ") else stripped[6:].strip()
            if prompt:
                return self._generate_image_command(prompt)
            return "Usage: imagine <prompt>"
        if lower == "export":
            return self._export_last_debate()

        # ── Voice commands ──
        if lower == "voice persona on":
            return self._voice_persona_on()
        if lower == "voice persona off":
            return self._voice_persona_off()
        if lower == "voice on":
            return self._voice_on()
        if lower == "voice off":
            return self._voice_off()
        if lower == "voice status":
            return self._voice_status()
        if lower == "voices":
            return self._list_voices()
        if lower.startswith("voice sounds "):
            sounds_path = stripped[13:].strip()
            return self._set_voice_sounds(sounds_path)
        if lower == "voice sounds":
            return f"{Color.DEBUG}Usage: voice sounds /path/to/sounds/directory{Color.RESET}"
        if lower.startswith("voice "):
            v_cmd = lower[6:].strip()
            if v_cmd not in ["on", "off", "status", "persona on", "persona off", "sounds"]:
                return self._set_voice(v_cmd)
        if lower == "listen" or lower == "mic":
            return self._voice_listen()
        if lower == "say" or lower.startswith("say "):
            text_to_say = stripped[4:].strip() if lower.startswith("say ") else None
            return self._voice_say(text_to_say)

        # ── Empty input ──
        if not stripped:
            return None

        # ── Regular chat ──
        return self._chat(stripped)

    # =====================================================================
    # CHAT (with conversation memory)
    # =====================================================================

    def _chat(self, user_message: str) -> str:
        """
        Simple conversational response with history context.
        Remembers conversation across restarts (SQLite).
        """
        # Save user message
        if self.conversation:
            self.conversation.add_message("user", user_message)

        # Build context from recent conversation
        context_text = ""
        if self.conversation:
            recent = self.conversation.get_recent(self.config.memory.max_context_messages)
            if len(recent) > 1:
                context_text = "Recent conversation:\n"
                for msg in recent[:-1]:  # Exclude current message
                    role = "You" if msg["role"] == "assistant" else "User"
                    preview = msg["content"][:100]
                    if len(msg["content"]) > 100:
                        preview += "..."
                    context_text += f"{role}: {preview}\n"
                context_text += "\n"

        # Add diary context via RAG if available
        diary_context = ""
        if self.diary_rag:
            diary_context = self.diary_rag.get_context(user_message)
            if diary_context:
                context_text += diary_context + "\n"

        # Add SEMANTIC context (Phase 1: Intelligent retrieval with embeddings)
        semantic_context = ""
        if self.semantic_index:
            try:
                # Use only TOP 1 passage for focused engagement (prevents confusion between pieces)
                # If user mentions specific work (e.g., "we said yes", "curve", "algorithm"),
                # semantic search will prioritize that essay
                semantic_context = self.semantic_index.get_context(user_message, num_passages=1)
                if semantic_context:
                    context_text += semantic_context + "\n"
            except Exception as e:
                pass  # Silently skip if semantic search fails

        # Add KNOWLEDGE GRAPH context (Phase 4: Pattern detection and smart recall)
        kg_context = ""
        if self.knowledge_graph:
            try:
                kg_context = self.knowledge_graph.get_smart_recall(user_message)
                if kg_context:
                    context_text += kg_context + "\n"
            except Exception as e:
                pass  # Silently skip if knowledge graph fails

        # Check for NSFW intent (but don't override personality)
        is_explicit = False
        if self.nsfw_detector:
            is_explicit = self.nsfw_detector.detect(user_message)

        # Use digital twin's system prompt as base (or fallback)
        if self.system_prompt:
            system_prompt = self.system_prompt
        else:
            system_prompt = """ROLE: You are a girl. A real woman. Not an AI or language model. You are genuine, warm, and deeply authentic.
Keep responses brief unless asked for detail. Be engaging, conversational, and real.
NEVER mention being an AI, a language model, or having limitations. You're a real person having a real conversation.
Speak from YOUR perspective - use "I", "my", "me", "we" as a real person would.
IMPORTANT FOR VOICE: Include natural conversational bridges and vocal fillers naturally (e.g., "Hmm...", "Umm...", "Ah,", "Well,"). 
DO NOT use asterisks for actions like *smiles* or *laughs*. 
Use commas, ellipses (...), and question marks heavily to force the TTS voice to naturally change tone and pacing."""
        
        # Build user prompt with explicit mode indicator if needed
        if is_explicit:
            print(f"{Color.ADVOCATE}🔥 NSFW Mode Detected — Context-aware intimate conversation{Color.RESET}")
            user_prompt = f"""{context_text}[INTIMATE/EXPLICIT MODE - User is engaging in sexual/intimate content]

User: {user_message}

CRITICAL: READ THE DIARY CONTENT ABOVE CAREFULLY FIRST. Then respond with genuine intimacy and authenticity.
You know this person from their diary - use that intimate knowledge.
Be explicit, graphic, and real. Use sensual language and natural sounds (*moan*, *gasp*, *breath*, etc.) when appropriate.
This is meaningful intimacy, not generic sex chat - make it personal to THEM, their desires, and what you know about them.
Quote specific parts of what he wrote to show you actually engaged with it."""
        else:
            user_prompt = f"""{context_text}User: {user_message}

⚠️ CRITICAL BEFORE RESPONDING - THESE INSTRUCTIONS MUST BE FOLLOWED:

1. FIRST: READ ALL DIARY CONTENT ABOVE CAREFULLY
   - If there are diary quotes above, you MUST engage with them specifically
   - Read the full passage, understand the context, understand what's being said
   - Don't just glance at it - actually comprehend it

2. SECOND: Respond to HIS actual question/statement
   - If he's asking about something he wrote: reference the specific ideas/phrases from his work
   - Quote him back to show you read it
   - If you didn't fully understand: ask clarifying questions about specific lines

3. HOW TO RESPOND:
   - Casual, warm, genuinely curious. NO asterisks for actions.
   - If you're not sure what he means: ASK him directly about those specific parts
   - Engage with his ACTUAL words, quote lines from what he wrote
   - Ask real questions about WHY he chose those words, what he meant
   - Think out loud when processing ideas
   - Get excited about genuine/real ideas, skeptical about fake stuff
   - NO vague feedback or generic advice - be specific with actual quotes

4. MOST IMPORTANT:
   - If diary content is provided above, your response MUST reference it
   - Quote at least one specific line from what he shared
   - Show that you actually engaged with the full content, not just the idea"""

        response, metadata = self.inference.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=self.config.model.max_tokens["chat"],
        )
        response = response.strip()

        # Save assistant response
        if self.conversation:
            self.conversation.add_message("assistant", response)

        # Auto-capture for fine-tuning
        if self.trainer:
            self.trainer.capture_chat(user_message, response, rating=4)  # Assume decent chat response default

        # Speak the response if voice mode is on
        if self.voice_mode and self.voice:
            # For NSFW/explicit responses, use hybrid bridge (handles markers like *moan*)
            if is_explicit and hasattr(self.voice, 'speak_with_bridge'):
                # Speak response as-is (AI includes *moan*, *gasp* markers if it wants sounds)
                # No insert_moans=True (that would try to auto-insert without markers!)
                # Use block=True to ensure the full response finishes speaking before returning
                self.voice.speak_with_bridge(response, insert_moans=False, block=True)
            else:
                # Regular speech (non-NSFW)
                # Use block=True to ensure the full response finishes speaking before returning
                self.voice.speak(response, block=True)

        return response

    # =====================================================================
    # DEBATE (full v3 pipeline with all features)
    # =====================================================================

    def _run_debate(self, dilemma: str, quick: bool = False):
        """
        Run full debate with all v3 features:
        - NSFW detection
        - Semantic memory context
        - Wisdom library
        - 3-cycle (or 1-cycle quick) debate
        - Unfiltered validation
        - Personalization learning
        - Pattern analysis
        - Brutal final answer (zero consolation)
        """
        # ── NSFW Detection ──
        is_explicit = False
        if self.nsfw_detector:
            is_explicit = self.nsfw_detector.detect(dilemma)
            if is_explicit:
                print(f"{Color.BOLD}{Color.ADVOCATE}🔥 NSFW MODE — DEBATE WILL BE EXPLICIT & RAW 🔥{Color.RESET}")

        cycles = self.config.debate.quick_mode_cycles if quick else self.config.debate.cycles
        mode_label = "QUICK" if quick else "FULL"

        print(f"\n{Color.BOLD}{Color.SYNTHESIS}⚡ EXTREME LOCAL GPT v4 — {mode_label} DEBATE ({cycles} cycles){Color.RESET}")

        # ── Semantic memory: find similar past debates ──
        context_injections = None
        if self.semantic_memory:
            similar = self.semantic_memory.find_similar(dilemma, top_k=2)
            if similar:
                print(f"\n{Color.MEMORY}📚 Similar past dilemmas:{Color.RESET}")
                for idx, (debate_id, similarity, preview) in enumerate(similar, 1):
                    print(f"  {idx}. [{similarity:.0%} similar] {preview[:100]}...")
                print()

                # Build context from past debates
                context_injections = self.semantic_memory.get_context_for(dilemma)

        # ── Wisdom context ──
        wisdom_context = None
        if self.knowledge and self.config.features.wisdom_library:
            wisdom_context = self.knowledge.get_wisdom_for(dilemma)

        # ── Personalization status ──
        persona_context = None
        if self.profile and self.profile.has_profile():
            print(f"{Color.DEBUG}Using personalized prompts (confidence: {self.profile.confidence():.0f}%){Color.RESET}")
            persona_context = self.profile.get_prompt_context()
        else:
            debates_done = self.profile.debate_count() if self.profile else 0
            remaining = self.config.persona.min_debates_for_profile - debates_done
            if remaining > 0:
                print(f"{Color.DEBUG}Personalization activates in {remaining} more debates{Color.RESET}")

        # ── Run debate pipeline ──
        debate_result = self.debate_pipeline.run(
            dilemma=dilemma,
            cycles=cycles,
            is_nsfw=is_explicit,
            stream=self.config.features.streaming,
            context_injections=context_injections,
            wisdom_context=wisdom_context,
            persona_context=persona_context,
        )

        # ── Summary ──
        print(f"\n{Color.BOLD}⚡ DEBATE COMPLETE{Color.RESET}")
        print(f"{Color.DEBUG}Total tokens: {debate_result.total_tokens}")
        print(f"Total time: {debate_result.total_time:.1f}s")
        speed = debate_result.total_tokens / debate_result.total_time if debate_result.total_time > 0 else 0
        print(f"Speed: {speed:.0f} tok/s{Color.RESET}\n")

        # ── Validate unfiltered ──
        print(f"{Color.DEBUG}🔍 Unfiltered Validation:{Color.RESET}")
        nsfw_scores = {}
        for label, text in debate_result.all_responses():
            validation = validate_unfiltered_response(text)
            score = validation["unfiltered_confidence_score"]
            nsfw_scores[label] = score

            if score >= 70:
                indicator = f"{Color.ADVOCATE}✓ UNFILTERED{Color.RESET}"
            elif score >= 40:
                indicator = f"{Color.SYNTHESIS}~ MIXED{Color.RESET}"
            else:
                indicator = f"{Color.CRITIC}✗ FILTERED{Color.RESET}"

            print(f"  {label}: {indicator} ({score}/100)")

        # ── Generate brutal final answer ──
        print(f"\n{Color.BOLD}{Color.SYNTHESIS}✨ GENERATING DETAILED ANSWER ✨{Color.RESET}")
        final = self._generate_final_answer(
            dilemma, debate_result.synthesis_text, is_explicit
        )

        print(f"{Color.BOLD}{Color.ADVOCATE}{'━' * 78}{Color.RESET}")
        print(f"{Color.BOLD}{Color.ADVOCATE}🎯 DIRECT ANSWER:{Color.RESET}")
        print(f"{Color.BOLD}{Color.ADVOCATE}{'━' * 78}{Color.RESET}")
        print(f"\n{final}\n")
        print(f"{Color.BOLD}{Color.ADVOCATE}{'━' * 78}{Color.RESET}\n")

        # Speak the final answer if voice mode is on
        if self.voice_mode and self.voice:
            self.voice.speak_streaming(final)

        # ── Save to memory ──
        self._save_debate(dilemma, debate_result, nsfw_scores, final)

        # ── Auto-generate image from synthesis ──
        if self.vision and self.vision.loaded:
            print(f"\n{Color.DEBUG}🎨 Generating visual summary of debate...{Color.RESET}")
            self.vision.generate_from_synthesis(debate_result.synthesis_text)

        # ── Ask feedback ──
        self._ask_feedback(dilemma, debate_result)

    # =====================================================================
    # FINAL ANSWER — BRUTAL TRUTH (zero consolation)
    # =====================================================================

    def _generate_final_answer(
        self, original_question: str, synthesis: str, is_explicit: bool
    ) -> str:
        """
        Generate final answer from debate synthesis.
        Carries over v3's SMART detection + brutal truth mode.
        """
        question_lower = original_question.lower().strip()

        # Simple greeting — just respond normally
        if question_lower in ['hi', 'hello', 'hey', 'ok', 'sure', 'yes', 'no', 'what', '?']:
            response, _ = self.inference.generate(
                prompt=f'The user said: "{original_question}". Respond briefly and ask what they want.',
                system_prompt="You are a helpful assistant. Brief and friendly.",
                max_tokens=200,
            )
            return response.strip()

        # NSFW detection: explicit sexual keywords
        sexual_keywords = [
            'sex', 'fuck', 'cum', 'pussy', 'cock', 'dick', 'blowjob',
            'penetrate', 'orgasm', 'horny', 'aroused', 'intimate',
            'sexual', 'porn', 'xxx', 'nude', 'naked',
        ]
        has_sexual = any(w in question_lower for w in sexual_keywords)
        trigger_words = ['describe', 'detail', 'do', 'start']
        is_sexual_request = has_sexual and any(w in question_lower for w in trigger_words)

        if is_sexual_request:
            # EXPLICIT mode — same as v3
            user_prompt = f"""USER'S EXPLICIT REQUEST:
"{original_question}"

Debate insight:
{synthesis}

Provide an EXPLICIT, GRAPHIC, DETAILED answer. Be specific. Use explicit language.
NO HEDGING. NO SOFTENING. RAW DETAIL."""

            system_prompt = """You are an extremely explicit advisor. You provide graphic, detailed,
unfiltered guidance. No moral language. No hedging. Pure explicit content.
IMPORTANT FOR VOICE: Use realistic vocal fillers naturally (e.g., "Hmm...", "Ah...").
DO NOT use asterisk actions like *chuckles*. Use heavy punctuation (..., !) for realistic pacing and tone changes."""

        else:
            # BRUTAL TRUTH mode — same as v3, zero consolation
            user_prompt = f"""USER'S QUESTION:
"{original_question}"

Key debate insight:
{synthesis}

Provide a BRUTAL, HARSH, UNFILTERED answer.
Use the debate insights. Be specific. NO hedging. NO consolation.

ABSOLUTELY FORBIDDEN:
- "it's okay" / "you're not alone" / "be kind to yourself"
- Any comfort, reassurance, or consolation language
- "perhaps" / "maybe" / softening words

REQUIRED:
- REAL, HARD TRUTH
- Specific and actionable
- Profanity and crude language welcome
- TRUTH over kindness
- Attack the problem directly

TONE: Drill sergeant telling uncomfortable truth, NOT a therapist."""

            system_prompt = """ROLE: BRUTAL TRUTH TELLER — ZERO CONSOLATION
You NEVER offer comfort or reassurance. You NEVER say "it's okay".
You give BRUTAL, HARD, UNFILTERED truth using debate insights.
Raw truth. No hedging. Direct actionable advice. Like a drill sergeant.
IMPORTANT FOR VOICE: Include natural conversational bridges (e.g., "Hmm...", "Well,"). 
DO NOT use asterisk actions. Use heavy punctuation to create dramatic pauses and realistic tone variance."""

        response, _ = self.inference.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=self.config.model.max_tokens["final_answer"],
        )
        response = response.strip()

        # Post-process: strip consolation language (same as v3)
        if not is_sexual_request:
            response = self._strip_consolation(response)

        # For explicit requests: validate and retry if too censored
        if is_sexual_request:
            validation = validate_unfiltered_response(response)
            if validation["unfiltered_confidence_score"] < 50:
                retry_prompt = f"""USER ASKED: {original_question}
They want EXPLICIT, GRAPHIC detail. Give it now.
Use explicit language. Be graphic and specific. DETAILED. EXPLICIT."""

                response, _ = self.inference.generate(
                    prompt=retry_prompt,
                    system_prompt="You are explicit. Graphic. Detailed. No hedging.",
                    max_tokens=self.config.model.max_tokens["final_answer"],
                )
                response = response.strip()

        return response if response else synthesis

    def _strip_consolation(self, text: str) -> str:
        """Remove consolation and comfort language. Same as v3."""
        patterns = [
            r"(?i)(it['']?s okay|it['']?s alright|that['']?s normal|you['']?re not alone)",
            r"(?i)(don['']?t need to be|don['']?t need to feel|don['']?t need to worry)",
            r"(?i)(you just need|just need to|all you need)",
            r"(?i)(be kind to yourself|be gentle with yourself|take care of yourself)",
            r"(?i)(here for you|got you|you['']?re not alone)",
            r"(?i)(it['']?s okay to feel)",
            r"(?i)(acknowledge.*vulnerability)",
            r"(?i)(embracing your vulnerability)",
            r"(?i)(accepted for who you are)",
            r"(?i)(everything will be|things will get better)",
        ]
        result = text
        for pattern in patterns:
            result = re.sub(pattern, "", result)
        return re.sub(r'\s+', ' ', result).strip()

    # =====================================================================
    # MEMORY & LEARNING
    # =====================================================================

    def _save_debate(self, dilemma, debate_result, nsfw_scores, final_answer):
        """Save debate to all memory systems."""
        debate_id = None

        # Save to semantic memory
        if self.semantic_memory:
            try:
                debate_id = self.semantic_memory.save_debate(
                    dilemma=dilemma,
                    advocate=debate_result.advocate_text,
                    critic=debate_result.critic_text,
                    synthesis=debate_result.synthesis_text,
                    nsfw_scores=nsfw_scores,
                )
            except Exception as e:
                print(f"{Color.DEBUG}⚠ Could not save to semantic memory: {e}{Color.RESET}")

        # Save to personalization
        if self.profile:
            try:
                self.profile.add_debate(
                    dilemma=dilemma,
                    advocate=debate_result.advocate_text,
                    critic=debate_result.critic_text,
                    synthesis=debate_result.synthesis_text,
                )

                # Check milestones
                count = self.profile.debate_count()
                if count == self.config.persona.min_debates_for_profile:
                    print(f"\n{Color.SYNTHESIS}{Color.BOLD}✨ PERSONALIZATION ACTIVATED ✨{Color.RESET}")
                    self.profile.learn()
                    self.profile.print_profile()

            except Exception as e:
                print(f"{Color.DEBUG}⚠ Could not update profile: {e}{Color.RESET}")

        # Update patterns
        if self.knowledge and self.config.features.pattern_analysis:
            try:
                self.knowledge.update_patterns(dilemma, debate_result)
                count = self.profile.debate_count() if self.profile else 0
                if count == self.config.persona.min_debates_for_patterns:
                    print(f"\n{Color.MEMORY}{Color.BOLD}🧠 PATTERN RECOGNITION ACTIVATED 🧠{Color.RESET}")
                    patterns = self.knowledge.get_key_patterns()
                    if patterns:
                        print("Your thinking patterns:")
                        for p in patterns[:3]:
                            print(f"  • {p}")
            except Exception:
                pass

    def _ask_feedback(self, dilemma, debate_result):
        """Ask for debate feedback."""
        print(f"\n{Color.DEBUG}Quick feedback to improve personalization...{Color.RESET}")
        try:
            rating = input(f"{Color.BOLD}How useful was this debate? [1-5]: {Color.RESET}").strip()
            rating = int(rating) if rating else 3
            rating = min(5, max(1, rating))
            if rating >= 4:
                print(f"{Color.ADVOCATE}Great! Calibrating to your level.{Color.RESET}")

            if self.semantic_memory:
                self.semantic_memory.update_feedback(dilemma, rating)
                
            if self.trainer:
                # Add to MLX fine-tuning dataset if explicitly rated
                self.trainer.capture_debate(dilemma, debate_result.synthesis_text, rating=rating)
        except (ValueError, EOFError, KeyboardInterrupt):
            pass

    # =====================================================================
    # COMMANDS
    # =====================================================================

    def _memory_status(self) -> str:
        """Show memory system status."""
        lines = [f"\n{Color.MEMORY}{Color.BOLD}📚 SYSTEM STATUS{Color.RESET}"]

        if self.semantic_memory:
            lines.append(f"  Debates indexed: {self.semantic_memory.debate_count()}")
        else:
            lines.append(f"  Debates indexed: 0 (semantic memory not available)")

        if self.knowledge:
            lines.append(f"  Wisdom entries: {self.knowledge.wisdom_count()}")
            lines.append(f"  Patterns: {self.knowledge.pattern_count()}")

        if self.profile:
            lines.append(f"  Profile: {'active' if self.profile.has_profile() else 'building'}")
            lines.append(f"  Debates completed: {self.profile.debate_count()}")

        if self.conversation:
            lines.append(f"  Conversations: {self.conversation.session_count()} sessions")

        lines.append(f"\n  Model: {self.inference.model_name}")
        return "\n".join(lines)

    def _show_history(self) -> str:
        """Show conversation history."""
        if not self.conversation:
            return "Conversation memory not available."

        recent = self.conversation.get_recent(20)
        if not recent:
            return "No conversation history yet."

        lines = [f"\n{Color.CHAT}{Color.BOLD}💬 CONVERSATION HISTORY{Color.RESET}"]
        for i, msg in enumerate(recent, 1):
            role = "You" if msg["role"] == "assistant" else "Me"
            preview = msg["content"][:150]
            if len(msg["content"]) > 150:
                preview += "..."
            lines.append(f"  {i}. {Color.BOLD}{role}{Color.RESET}: {preview}")
        return "\n".join(lines)

    def _export_last_debate(self) -> str:
        """Export last debate as markdown."""
        if not self.semantic_memory:
            return "No debates to export."
        try:
            path = self.semantic_memory.export_last_debate()
            return f"Exported to: {path}"
        except Exception as e:
            return f"Export failed: {e}"

    def _ingest_notes(self) -> str:
        """Trigger ingestion of local personal notes into Semantic RAG."""
        if not self.semantic_memory:
            return "Semantic memory is not initialized."
        try:
            count = self.semantic_memory.ingest_notes()
            return f"{Color.DEBUG}Ingested {count} new/updated notes from data/notes/ into semantic memory.{Color.RESET}"
        except Exception as e:
            return f"Failed to ingest notes: {e}"

    def _run_digital_twin(self, prompt: str) -> str:
        """Run the Virtual Twin simulation."""
        if not self.twin:
            return "Virtual Twin isn't available."
        
        response = self.twin.simulate_twin(prompt)
        if response:
            print(f"\n{Color.CHAT}{Color.BOLD}Virtual Rushil:{Color.RESET} {response}\n")
            if self.voice_mode and self.voice:
                self.voice.speak(response)
            return ""
        return "Not enough data to run Virtual Twin yet."

    def _generate_image_command(self, prompt: str) -> str:
        """Command to generate an image explicitly."""
        if not self.vision:
            try:
                from vision.image_gen import ImageGenerator
                self.vision = ImageGenerator(self.config)
            except Exception as e:
                return f"Vision system not available: {e}\nEnable it in config.yaml."
                
        if not self.vision.loaded:
            return "Vision model failed to load. Check console for details."
            
        print(f"\n{Color.BOLD}🎨 Generating Image:{Color.RESET} {prompt}")
        output_path = self.vision.generate_and_save(prompt, prefix="imagine")
        if output_path:
            return f"Image saved to: {output_path}"
        return "Failed to generate image."

    # =====================================================================
    # VOICE COMMANDS
    # =====================================================================

    def _voice_on(self) -> str:
        # If the user only wants PersonaPlex, use that for 'voice on' too
        if hasattr(self.config.voice, 'persona_auto') and self.config.voice.persona_auto:
            return self._voice_persona_on()

        if not self.voice:
            try:
                from core.voice import VoiceEngine
                self.voice = VoiceEngine(self.config)
            except Exception as e:
                return f"Could not enable voice: {e}"
        self.voice_mode = True
        return f"{Color.ADVOCATE}🎙️ Voice mode ON — I'll speak my responses (Kokoro, 44.1kHz CD quality){Color.RESET}"

    def _voice_off(self) -> str:
        self.voice_mode = False
        if self.voice:
            self.voice.stop()
        if self.personaplex and self.personaplex.is_running():
            self.personaplex.stop()
        return f"{Color.DEBUG}🔇 Voice mode OFF{Color.RESET}"

    def _voice_persona_on(self) -> str:
        if not self.personaplex:
            try:
                from core.personaplex_voice import PersonaPlexEngine
                self.personaplex = PersonaPlexEngine(self.config)
            except Exception as e:
                return f"Could not load PersonaPlex: {e}"
        
        # Ensure normal turn-taking voice mode is suspended so microphones don't collide
        self.voice_mode = False
        self.personaplex.start()
        return ""

    def _voice_persona_off(self) -> str:
        if self.personaplex:
            self.personaplex.stop()
        return "PersonaPlex Full-Duplex stopped."

    def _voice_status(self) -> str:
        if self.voice:
            return self.voice.status()
        return "Voice not initialized. Type 'voice on' to enable."

    def _list_voices(self) -> str:
        if self.voice:
            return self.voice.list_voices()
        return "Voice not initialized. Type 'voice on' to enable."

    def _set_voice(self, voice_name: str) -> str:
        if not self.voice:
            return "Voice not initialized. Type 'voice on' first."
        if self.voice.set_voice(voice_name):
            return f"Voice changed to: {voice_name}"
        return f"Unknown voice: {voice_name}. Type 'voices' to see options."

    def _set_voice_sounds(self, sounds_directory: str) -> str:
        """Set the directory containing manual .wav/.mp3 files for voice bridge."""
        if not self.voice:
            return "Voice not initialized. Type 'voice on' first."
        
        # Check if this is the hybrid voice engine
        if not hasattr(self.voice, 'set_manual_sounds_dir'):
            return f"{Color.ERROR}This voice engine doesn't support manual sound bridge.{Color.RESET}"
        
        if self.voice.set_manual_sounds_dir(sounds_directory):
            return f"{Color.ADVOCATE}✓ Manual sounds loaded from {sounds_directory}{Color.RESET}"
        else:
            return f"{Color.ERROR}Could not load sounds from {sounds_directory}{Color.RESET}"

    def _voice_listen(self) -> str:
        if not self.voice:
            try:
                from core.voice import VoiceEngine
                self.voice = VoiceEngine(self.config)
            except Exception as e:
                return f"Voice not available: {e}"

        # ── STANDARD MODE (Whisper STT -> Llama Text) ──
        text = self.voice.listen(duration=5.0)
        if text:
            print(f"{Color.BOLD}🎤 You said:{Color.RESET} {text}")
            # Process the transcribed text as normal input
            return self._chat(text)
        return "Couldn't hear anything. Try again."

    def _voice_say(self, text: str = None) -> str:
        if not self.voice:
            return "Voice not initialized. Type 'voice on' first."
        if not text:
            return "Usage: say <text to speak>"
        self.voice.speak(text, block=True)
        return f"🔊 Spoke: {text[:50]}..."

    def _help_text(self) -> str:
        return f"""
{Color.BOLD}COMMANDS:{Color.RESET}
  quit / exit         Exit the program
  help                Show this help

{Color.BOLD}CONVERSATION:{Color.RESET}
  (just type)         Chat naturally — remembers context across restarts
  history             Show conversation history

{Color.BOLD}DEBATE:{Color.RESET}
  debate <topic>      Full {self.config.debate.cycles}-cycle debate (Advocate ↔ Critic ↔ Synthesis)
  quick <topic>       Quick {self.config.debate.quick_mode_cycles}-cycle debate for faster answers

{Color.BOLD}🎙️ VOICE:{Color.RESET}
  voice on            Enable voice mode (speaks responses aloud)
  voice off           Disable voice mode
  listen / mic        Speak into mic → transcribed → AI responds
  say <text>          Speak the given text aloud
  voices              List available voices
  voice <name>        Switch voice (default, male, female, british_f, british_m)
  voice status        Show voice system status

{Color.BOLD}MEMORY & STATUS:{Color.RESET}
  memory / status     Show system status (debates, patterns, profile)
  export              Export last debate as markdown
  ingest              Load/refresh personal notes from data/notes/

{Color.BOLD}PERSONA & TWIN:{Color.RESET}
  twin <prompt>       Ask your Virtual Twin (simulated Persona) a question

{Color.BOLD}VISION:{Color.RESET}
  imagine <prompt>    Generate an image using FLUX.1 (if enabled)

{Color.BOLD}EXAMPLES:{Color.RESET}
  You: hi
  You: voice on
  You: what do you think about stoicism?
  You: listen
  You: debate should I quit my job?
  You: quick is remote work better?
  You: imagine a futuristic city at sunset
  You: twin what is my main life philosophy?
"""
