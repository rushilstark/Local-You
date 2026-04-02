#!/usr/bin/env python3
"""
⚡ EXTREME LOCAL GPT v4 — Config Loader
Loads config.yaml and provides typed access to all settings.
"""

import os
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ModelConfig:
    primary: str = "mlx-community/Meta-Llama-3.1-8B-Instruct-abliterated-Q4-MLX"
    fallbacks: List[str] = field(default_factory=lambda: [
        "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
        "mlx-community/Qwen2.5-7B-Instruct-4bit",
    ])
    max_tokens: Dict[str, int] = field(default_factory=lambda: {
        "chat": 300,
        "debate_cycle": 500,
        "synthesis": 600,
        "final_answer": 600,
    })
    temperature: float = 0.8
    top_p: float = 0.95


@dataclass
class DebateConfig:
    cycles: int = 2
    stream: bool = True
    quick_mode_cycles: int = 1


@dataclass
class MemoryConfig:
    data_dir: str = "~/.local/share/extremegpt"
    conversations_db: str = "conversations.db"
    debates_file: str = "debates.json"
    patterns_file: str = "patterns.json"
    wisdom_file: str = "wisdom.json"
    max_context_messages: int = 10

    @property
    def resolved_data_dir(self) -> Path:
        return Path(self.data_dir).expanduser()

    @property
    def conversations_db_path(self) -> Path:
        return self.resolved_data_dir / self.conversations_db

    @property
    def debates_file_path(self) -> Path:
        return self.resolved_data_dir / self.debates_file

    @property
    def patterns_file_path(self) -> Path:
        return self.resolved_data_dir / self.patterns_file

    @property
    def wisdom_file_path(self) -> Path:
        return self.resolved_data_dir / self.wisdom_file


@dataclass
class PersonaConfig:
    min_debates_for_profile: int = 5
    min_debates_for_patterns: int = 10
    confidence_threshold: float = 60.0


@dataclass
class VoiceConfig:
    omni_mode: bool = False
    persona_auto: bool = False


@dataclass
class FeaturesConfig:
    nsfw_mode: bool = True
    semantic_memory: bool = True
    wisdom_library: bool = True
    pattern_analysis: bool = True
    image_generation: bool = False
    voice_output: bool = False
    streaming: bool = True


class Color:
    """ANSI color codes for terminal output."""
    ADVOCATE = '\033[92m'
    CRITIC = '\033[91m'
    SYNTHESIS = '\033[93m'
    DEBUG = '\033[36m'
    ERROR = '\033[95m'
    MEMORY = '\033[94m'
    CHAT = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


@dataclass
class AppConfig:
    """Root configuration — everything the system needs."""
    model: ModelConfig = field(default_factory=ModelConfig)
    debate: DebateConfig = field(default_factory=DebateConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    persona: PersonaConfig = field(default_factory=PersonaConfig)
    features: FeaturesConfig = field(default_factory=FeaturesConfig)
    voice: VoiceConfig = field(default_factory=VoiceConfig)

    def ensure_data_dir(self):
        """Create data directory if it doesn't exist."""
        self.memory.resolved_data_dir.mkdir(parents=True, exist_ok=True)


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """
    Load config from YAML file. Falls back to defaults if file not found.

    Args:
        config_path: Path to config.yaml. If None, looks in the v4 directory.

    Returns:
        AppConfig with all settings loaded.
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')

    config = AppConfig()

    try:
        with open(config_path, 'r') as f:
            raw = yaml.safe_load(f)

        if raw is None:
            return config

        # Load model config
        if 'model' in raw:
            m = raw['model']
            if 'primary' in m:
                config.model.primary = m['primary']
            if 'fallbacks' in m:
                config.model.fallbacks = m['fallbacks']
            if 'max_tokens' in m:
                config.model.max_tokens.update(m['max_tokens'])
            if 'temperature' in m:
                config.model.temperature = float(m['temperature'])
            if 'top_p' in m:
                config.model.top_p = float(m['top_p'])

        # Load debate config
        if 'debate' in raw:
            d = raw['debate']
            if 'cycles' in d:
                config.debate.cycles = int(d['cycles'])
            if 'stream' in d:
                config.debate.stream = bool(d['stream'])
            if 'quick_mode_cycles' in d:
                config.debate.quick_mode_cycles = int(d['quick_mode_cycles'])

        # Load memory config
        if 'memory' in raw:
            mem = raw['memory']
            if 'data_dir' in mem:
                config.memory.data_dir = mem['data_dir']
            if 'conversations_db' in mem:
                config.memory.conversations_db = mem['conversations_db']
            if 'debates_file' in mem:
                config.memory.debates_file = mem['debates_file']
            if 'max_context_messages' in mem:
                config.memory.max_context_messages = int(mem['max_context_messages'])

        # Load persona config
        if 'persona' in raw:
            p = raw['persona']
            if 'min_debates_for_profile' in p:
                config.persona.min_debates_for_profile = int(p['min_debates_for_profile'])
            if 'min_debates_for_patterns' in p:
                config.persona.min_debates_for_patterns = int(p['min_debates_for_patterns'])

        # Load features config
        if 'features' in raw:
            feat = raw['features']
            for key in ['nsfw_mode', 'semantic_memory', 'wisdom_library',
                        'pattern_analysis', 'image_generation', 'voice_output', 'streaming']:
                if key in feat:
                    setattr(config.features, key, bool(feat[key]))

        # Load voice config
        if 'voice' in raw:
            v_conf = raw['voice']
            if 'omni_mode' in v_conf:
                config.voice.omni_mode = bool(v_conf['omni_mode'])
            if 'omni_model' in v_conf:
                config.voice.omni_model = str(v_conf['omni_model'])
            if 'persona_auto' in v_conf:
                config.voice.persona_auto = bool(v_conf['persona_auto'])

    except FileNotFoundError:
        print(f"{Color.DEBUG}Config file not found at {config_path}, using defaults{Color.RESET}")
    except Exception as e:
        print(f"{Color.ERROR}Error loading config: {e}, using defaults{Color.RESET}")

    config.ensure_data_dir()
    return config
