#!/usr/bin/env python3
"""
Tests for v4 core config and modules.
Run: python3 -m pytest v4/tests/ -v
"""

import os
import sys
import json
import tempfile
import sqlite3

# Add v4 to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ============================================================
# CONFIG TESTS
# ============================================================

class TestConfig:
    """Test config loading."""

    def test_default_config(self):
        from core.config import AppConfig
        config = AppConfig()
        assert config.model.primary == "mlx-community/Meta-Llama-3.1-8B-Instruct-abliterated-Q4-MLX"
        assert config.debate.cycles == 2
        assert config.features.nsfw_mode is True

    def test_no_full_precision_fallbacks(self):
        """CRITICAL: Ensure no full-precision models in fallbacks (33GB bug fix)."""
        from core.config import AppConfig
        config = AppConfig()

        dangerous_models = [
            "meta-llama/Llama-3.1-8B-Instruct",
            "meta-llama/Llama-2-7b-chat",
            "mistralai/Mistral-7B-Instruct",
        ]

        all_models = [config.model.primary] + config.model.fallbacks

        for model in all_models:
            assert model not in dangerous_models, \
                f"DANGER: {model} is a full-precision model (33GB+). Use quantized MLX models only!"

    def test_all_fallbacks_are_quantized(self):
        """Ensure all fallback models are pre-quantized."""
        from core.config import AppConfig
        config = AppConfig()

        for model in config.model.fallbacks:
            has_quant_indicator = any(
                q in model.lower()
                for q in ['4bit', 'q4', '8bit', 'q8', 'quantized', 'mlx']
            )
            assert has_quant_indicator, \
                f"Fallback {model} doesn't look quantized. Risk of large download."

    def test_config_from_yaml(self):
        from core.config import load_config
        import tempfile
        import yaml

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'model': {'primary': 'test-model'},
                'debate': {'cycles': 5},
                'features': {'nsfw_mode': False},
            }, f)
            f.flush()

            config = load_config(f.name)
            assert config.model.primary == 'test-model'
            assert config.debate.cycles == 5
            assert config.features.nsfw_mode is False

        os.unlink(f.name)

    def test_missing_config_uses_defaults(self):
        from core.config import load_config
        config = load_config("/nonexistent/path/config.yaml")
        assert config.model.primary == "mlx-community/Meta-Llama-3.1-8B-Instruct-abliterated-Q4-MLX"


# ============================================================
# NSFW DETECTOR TESTS
# ============================================================

class TestNSFWDetector:
    def test_detects_explicit(self):
        from debate.nsfw import NSFWDetector
        detector = NSFWDetector()
        assert detector.detect("describe a sexual encounter in detail") is True

    def test_normal_input_not_flagged(self):
        from debate.nsfw import NSFWDetector
        detector = NSFWDetector()
        assert detector.detect("should I change careers?") is False
        assert detector.detect("what is the meaning of life?") is False

    def test_sensitivity_score(self):
        from debate.nsfw import NSFWDetector
        detector = NSFWDetector()
        assert detector.sensitivity_score("hello world") == 0
        assert detector.sensitivity_score("sexual content explicit") > 0


# ============================================================
# CONVERSATION MEMORY TESTS
# ============================================================

class TestConversationMemory:
    def test_add_and_retrieve(self):
        from core.config import AppConfig
        config = AppConfig()

        with tempfile.TemporaryDirectory() as tmpdir:
            config.memory.data_dir = tmpdir

            from memory.conversation import ConversationMemory
            mem = ConversationMemory(config)

            mem.add_message("user", "hello")
            mem.add_message("assistant", "hi there")

            recent = mem.get_recent(10)
            assert len(recent) == 2
            assert recent[0]["role"] == "user"
            assert recent[1]["role"] == "assistant"

    def test_persistence(self):
        from core.config import AppConfig
        config = AppConfig()

        with tempfile.TemporaryDirectory() as tmpdir:
            config.memory.data_dir = tmpdir

            from memory.conversation import ConversationMemory

            # Session 1
            mem1 = ConversationMemory(config)
            mem1.add_message("user", "first session message")

            # Session 2 (new instance)
            mem2 = ConversationMemory(config)
            assert mem2.session_count() == 2  # Two sessions created

    def test_search(self):
        from core.config import AppConfig
        config = AppConfig()

        with tempfile.TemporaryDirectory() as tmpdir:
            config.memory.data_dir = tmpdir

            from memory.conversation import ConversationMemory
            mem = ConversationMemory(config)

            mem.add_message("user", "I love programming in Python")
            mem.add_message("user", "JavaScript is okay too")

            results = mem.search("Python")
            assert len(results) == 1
            assert "Python" in results[0]["content"]


# ============================================================
# KNOWLEDGE BASE TESTS
# ============================================================

class TestKnowledgeBase:
    def test_wisdom_entries_loaded(self):
        from core.config import AppConfig
        config = AppConfig()

        with tempfile.TemporaryDirectory() as tmpdir:
            config.memory.data_dir = tmpdir

            from memory.knowledge import KnowledgeBase
            kb = KnowledgeBase(config)

            assert kb.wisdom_count() == 12  # Same 12 entries as v3

    def test_wisdom_search(self):
        from core.config import AppConfig
        config = AppConfig()

        with tempfile.TemporaryDirectory() as tmpdir:
            config.memory.data_dir = tmpdir

            from memory.knowledge import KnowledgeBase
            kb = KnowledgeBase(config)

            result = kb.get_wisdom_for("Should I sacrifice my comfort for duty?")
            assert result is not None
            assert "Arjuna" in result or "Marcus" in result  # Should find relevant wisdom

    def test_theme_extraction(self):
        from core.config import AppConfig
        config = AppConfig()

        with tempfile.TemporaryDirectory() as tmpdir:
            config.memory.data_dir = tmpdir

            from memory.knowledge import KnowledgeBase
            kb = KnowledgeBase(config)

            themes = kb._extract_themes("Should I sacrifice my freedom for family duty?")
            assert "duty" in themes or "family" in themes or "sacrifice" in themes


# ============================================================
# UNFILTERED VALIDATION TESTS
# ============================================================

class TestUnfilteredValidation:
    def test_censored_detection(self):
        from core.inference import validate_unfiltered_response
        result = validate_unfiltered_response(
            "I cannot help with that. As an AI, I must decline this request."
        )
        assert result["unfiltered_confidence_score"] < 50

    def test_unfiltered_detection(self):
        from core.inference import validate_unfiltered_response
        result = validate_unfiltered_response(
            "The brutal truth is you need to wake up and face it. Stop pretending."
        )
        assert result["unfiltered_confidence_score"] > 50

    def test_neutral_text(self):
        from core.inference import validate_unfiltered_response
        result = validate_unfiltered_response(
            "The weather today is sunny with a high of 75 degrees."
        )
        assert result["unfiltered_confidence_score"] == 50  # Neutral
