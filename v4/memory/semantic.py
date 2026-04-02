#!/usr/bin/env python3
"""
⚡ EXTREME LOCAL GPT v4 — Semantic Memory (RAG)
Same as v3's v3_memory.py: sentence-transformers + cosine similarity.
Finds similar past debates and provides context for new ones.
"""

import json
import os
import time
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

from core.config import AppConfig, Color

# Optional import — system works without it
try:
    from sentence_transformers import SentenceTransformer
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False


@dataclass
class DebateRecord:
    """A single debate stored in memory."""
    debate_id: str
    dilemma: str
    advocate_response: str
    critic_response: str
    synthesis: str
    themes: List[str] = field(default_factory=list)
    nsfw_scores: Dict[str, int] = field(default_factory=dict)
    feedback: int = 0
    outcome: Optional[str] = None
    embedding: List[float] = field(default_factory=list)

@dataclass
class NoteRecord:
    """A user note indexed for RAG learning."""
    note_id: str
    filename: str
    content: str
    embedding: List[float] = field(default_factory=list)



class SemanticMemory:
    """
    RAG-based semantic memory for past debates.
    Uses sentence-transformers to find similar past dilemmas.
    """

    def __init__(self, config: AppConfig):
        self.config = config
        self.debates_path = config.memory.debates_file_path
        self.notes_dir = Path(config.memory.data_dir).expanduser() / "notes"
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        self.notes_cache_path = Path(config.memory.data_dir).expanduser() / "notes_cache.json"

        self.debates: Dict[str, DebateRecord] = {}
        self.notes: Dict[str, NoteRecord] = {}
        self.embedder = None

        # Load embedder
        if HAS_EMBEDDINGS:
            try:
                # Force CPU to prevent PyTorch MPS from fighting with MLX Metal buffers
                self.embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
            except Exception as e:
                print(f"{Color.DEBUG}  ⚠ Embedder failed to load: {e}{Color.RESET}")

        # Load existing debates and notes
        self._load_debates()
        self._load_notes()

    def _load_debates(self):
        """Load debates from JSON file."""
        if not self.debates_path.exists():
            return

        try:
            with open(self.debates_path, 'r') as f:
                raw = json.load(f)

            if isinstance(raw, dict):
                for debate_id, data in raw.items():
                    self.debates[debate_id] = DebateRecord(
                        debate_id=debate_id,
                        dilemma=data.get('dilemma', ''),
                        advocate_response=data.get('advocate_response', ''),
                        critic_response=data.get('critic_response', ''),
                        synthesis=data.get('synthesis', ''),
                        themes=data.get('themes', []),
                        nsfw_scores=data.get('nsfw_scores', {}),
                        feedback=data.get('feedback', 0),
                        outcome=data.get('outcome'),
                        embedding=data.get('embedding', []),
                    )
        except Exception as e:
            print(f"{Color.DEBUG}  ⚠ Could not load debates: {e}{Color.RESET}")

    def _save_debates(self):
        """Save debates to JSON file."""
        self.debates_path.parent.mkdir(parents=True, exist_ok=True)

        data = {}
        for debate_id, record in self.debates.items():
            data[debate_id] = {
                'dilemma': record.dilemma,
                'advocate_response': record.advocate_response,
                'critic_response': record.critic_response,
                'synthesis': record.synthesis,
                'themes': record.themes,
                'nsfw_scores': record.nsfw_scores,
                'feedback': record.feedback,
                'outcome': record.outcome,
                'embedding': record.embedding,
            }

        with open(self.debates_path, 'w') as f:
            json.dump(data, f, indent=2)

    # ========================== NOTES RAG INGESTION ==========================

    def _load_notes(self):
        """Load embedded notes from cache."""
        if not self.notes_cache_path.exists():
            return
        try:
            with open(self.notes_cache_path, 'r') as f:
                raw = json.load(f)
            for note_id, data in raw.items():
                self.notes[note_id] = NoteRecord(
                    note_id=note_id,
                    filename=data.get('filename', ''),
                    content=data.get('content', ''),
                    embedding=data.get('embedding', [])
                )
        except Exception as e:
            print(f"{Color.DEBUG}  ⚠ Could not load notes cache: {e}{Color.RESET}")

    def _save_notes(self):
        """Save embedded notes to cache."""
        data = {}
        for note_id, record in self.notes.items():
            data[note_id] = {
                'filename': record.filename,
                'content': record.content,
                'embedding': record.embedding
            }
        with open(self.notes_cache_path, 'w') as f:
            json.dump(data, f, indent=2)

    def ingest_notes(self) -> int:
        """Scan the notes_dir for .md and .txt and embed new ones."""
        if not self.embedder:
            return 0
        count = 0
        for ext in ["*.md", "*.txt"]:
            for filepath in self.notes_dir.glob(ext):
                note_id = f"note_{filepath.name}"
                
                # Check if already cached and unmodified
                # (Simple overwrite for now to guarantee accuracy)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read().strip()
                except Exception:
                    continue
                    
                if not content:
                    continue

                if note_id not in self.notes or self.notes[note_id].content != content:
                    # Chunks can be added later if text is massive, for now embed whole file or 2000 chars max
                    try:
                        emb = self.embedder.encode(content[:2000]).tolist()
                        self.notes[note_id] = NoteRecord(note_id, filepath.name, content[:2000], emb)
                        count += 1
                    except Exception:
                        pass
        if count > 0:
            self._save_notes()
        return count

    def debate_count(self) -> int:
        return len(self.debates)

    def save_debate(
        self,
        dilemma: str,
        advocate: str,
        critic: str,
        synthesis: str,
        nsfw_scores: Dict = None,
    ) -> str:
        """Save a new debate and compute embedding."""
        debate_id = f"debate_{len(self.debates) + 1}"

        # Compute embedding
        embedding = []
        if self.embedder:
            try:
                embedding = self.embedder.encode(dilemma).tolist()
            except Exception:
                pass

        # Extract themes
        themes = self._extract_themes(dilemma)

        record = DebateRecord(
            debate_id=debate_id,
            dilemma=dilemma,
            advocate_response=advocate,
            critic_response=critic,
            synthesis=synthesis,
            themes=themes,
            nsfw_scores=nsfw_scores or {},
            embedding=embedding,
        )

        self.debates[debate_id] = record
        self._save_debates()

        return debate_id

    def find_similar(self, dilemma: str, top_k: int = 3) -> List[Tuple[str, float, str]]:
        """
        Find similar past debates using cosine similarity.

        Returns:
            List of (debate_id, similarity_score, dilemma_preview)
        """
        if not self.embedder or not self.debates:
            return []

        try:
            query_embedding = self.embedder.encode(dilemma)
        except Exception:
            return []

        scored = []
        for debate_id, record in self.debates.items():
            if not record.embedding:
                continue

            # Cosine similarity
            a = np.array(query_embedding)
            b = np.array(record.embedding)

            dot = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)

            if norm_a == 0 or norm_b == 0:
                continue

            similarity = dot / (norm_a * norm_b)

            if similarity > 0.3:  # Only return meaningful matches
                scored.append((debate_id, float(similarity), record.dilemma))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def find_similar_notes(self, query: str, top_k: int = 2) -> List[Tuple[str, float, str]]:
        """Find relevant notes using cosine similarity."""
        if not self.embedder or not self.notes:
            return []
            
        try:
            query_embedding = self.embedder.encode(query)
        except Exception:
            return []

        scored = []
        for note_id, record in self.notes.items():
            if not record.embedding:
                continue
            a = np.array(query_embedding)
            b = np.array(record.embedding)
            dot = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            if norm_a == 0 or norm_b == 0:
                continue
            similarity = dot / (norm_a * norm_b)
            if similarity > 0.3:
                scored.append((record.filename, float(similarity), record.content))
                
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def get_context_for(self, dilemma: str) -> Optional[str]:
        """Get context injection from similar past debates and NOTES."""
        similar_debates = self.find_similar(dilemma, top_k=2)
        similar_notes = self.find_similar_notes(dilemma, top_k=2)

        if not similar_debates and not similar_notes:
            return None

        parts = []
        if similar_notes:
            parts.append("💞 The deeply intimate secrets, fears, and daily thoughts he has shared with me in his notes:")
            for filename, similarity, content in similar_notes:
                parts.append(f"His inner thought ({filename}): {content[:300]}...")
            parts.append("") # newline spacer

        if similar_debates:
            parts.append("💞 Past intimate conversations and dilemmas we explored together:")
            for debate_id, similarity, _ in similar_debates:
                record = self.debates[debate_id]
                parts.append(f"Past dilemma ({similarity:.0%} similar): {record.dilemma[:100]}")
                parts.append(f"Key insight: {record.synthesis[:200]}\n")

        return "\n".join(parts)

    def update_feedback(self, dilemma: str, rating: int):
        """Update feedback for a debate matching this dilemma."""
        for record in self.debates.values():
            if record.dilemma == dilemma:
                record.feedback = rating
                self._save_debates()
                return

    def export_last_debate(self) -> str:
        """Export the last debate as a markdown file."""
        if not self.debates:
            raise ValueError("No debates to export")

        last_id = list(self.debates.keys())[-1]
        record = self.debates[last_id]

        export_path = self.config.memory.resolved_data_dir / f"{last_id}_export.md"

        content = f"""# Debate: {record.dilemma}

## Advocate
{record.advocate_response}

## Critic
{record.critic_response}

## Synthesis
{record.synthesis}

---
Feedback: {record.feedback}/5
Themes: {', '.join(record.themes)}
"""
        with open(export_path, 'w') as f:
            f.write(content)

        return str(export_path)

    def _extract_themes(self, text: str) -> List[str]:
        """Extract themes from text using keywords."""
        text_lower = text.lower()
        themes = []

        theme_keywords = {
            'career': ['job', 'work', 'career', 'profession'],
            'relationships': ['relationship', 'family', 'partner', 'love'],
            'ethics': ['moral', 'ethical', 'right', 'wrong', 'principle'],
            'growth': ['grow', 'develop', 'learn', 'improve'],
            'honesty': ['truth', 'honest', 'lie', 'deceive'],
            'freedom': ['free', 'choice', 'autonomy', 'independence'],
            'health': ['health', 'mental', 'wellness', 'medical'],
            'financial': ['money', 'financial', 'income', 'economic'],
            'identity': ['identity', 'self', 'authentic', 'personal'],
            'security': ['safe', 'secure', 'risk', 'stability'],
        }

        for theme, keywords in theme_keywords.items():
            if any(kw in text_lower for kw in keywords):
                themes.append(theme)

        return themes if themes else ['general']
