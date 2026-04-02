#!/usr/bin/env python3
"""
PHASE 1: SEMANTIC INDEXING FOR DIARY RAG
Intelligent context with semantic search + smart caching
Uses sentence-transformers for embedding, with disk cache for persistence
"""

import json
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np
from dataclasses import dataclass


@dataclass
class EmbeddedPassage:
    """A diary passage with its semantic embedding"""
    text: str
    embedding: np.ndarray
    metadata: Dict  # {source_file, char_index, word_count, timestamp}
    relevance_score: float = 0.0


class SemanticDiaryIndex:
    """
    Index diary passages semantically using sentence-transformers.
    - One-time embedding (~30 sec for 179 passages)
    - Cache embeddings to disk
    - Smart retrieval with relevance weighting
    """

    def __init__(self, diary_folder: Path = None, cache_dir: Path = None):
        self.diary_folder = Path(diary_folder) if diary_folder else Path("data/diary")
        self.cache_dir = Path(cache_dir) if cache_dir else Path(".cache/semantic_embeddings")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache file locations
        self.embeddings_cache = self.cache_dir / "diary_embeddings.pkl"
        self.metadata_cache = self.cache_dir / "diary_metadata.json"
        self.index_cache = self.cache_dir / "diary_index.pkl"
        
        # Runtime state
        self.passages: List[EmbeddedPassage] = []
        self.model = None
        self.indexed = False
        self.recency_weights = {}  # passage_idx -> recency_score (0-1)
        
        # Initialize
        self._init_model()
        self._load_or_build_index()

    def _init_model(self):
        """Load sentence-transformer model (lazy load if not used)"""
        try:
            from sentence_transformers import SentenceTransformer
            print("  🔄 Loading semantic model (one-time, ~5 sec)...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')  # 384-dim, fast
            print("  ✓ Semantic model loaded")
        except ImportError:
            print("  ⚠ sentence-transformers not installed. Install: pip install sentence-transformers")
            self.model = None

    def _load_or_build_index(self):
        """Load cached embeddings or build new index"""
        if self.embeddings_cache.exists() and self.metadata_cache.exists():
            print("  🔄 Loading cached semantic embeddings...")
            self._load_from_cache()
            self.indexed = True
            print(f"  ✓ Loaded {len(self.passages)} embedded passages from cache")
        else:
            print("  🔄 Building semantic index (first run ~30 sec)...")
            self._build_index()
            self._save_to_cache()
            self.indexed = True
            print(f"  ✓ Indexed {len(self.passages)} diary passages")

    def _build_index(self):
        """Build semantic index from diary files"""
        if not self.model or not self.diary_folder.exists():
            return

        all_passages = []
        
        # Load all diary entries
        for txt_file in sorted(self.diary_folder.glob("*.txt")):
            try:
                with open(txt_file, "r") as f:
                    content = f.read()
                    # Chunk into meaningful passages
                    chunks = self._chunk_text(content, str(txt_file))
                    all_passages.extend(chunks)
            except Exception as e:
                print(f"  ⚠ Error reading {txt_file}: {e}")

        # Embed passages
        if all_passages:
            texts = [p["text"] for p in all_passages]
            print(f"  🔄 Embedding {len(texts)} passages...")
            embeddings = self.model.encode(texts, show_progress_bar=True)
            
            # Create embedded passages
            for passage, embedding in zip(all_passages, embeddings):
                embedded = EmbeddedPassage(
                    text=passage["text"],
                    embedding=embedding,
                    metadata=passage["metadata"]
                )
                self.passages.append(embedded)

    def _chunk_text(self, text: str, source_file: str) -> List[Dict]:
        """Split text into meaningful chunks - but KEEP LONG ESSAYS WHOLE"""
        chunks = []
        
        # First, split by titled sections (all caps, short lines)
        sections = []
        current_section = []
        section_title = ""
        
        for line in text.split('\n'):
            # Detect section headers (all caps, < 50 chars)
            if line.strip().isupper() and len(line.strip()) < 50 and line.strip():
                # Save previous section if exists
                if current_section:
                    section_content = '\n'.join(current_section).strip()
                    if section_content:
                        sections.append({
                            "title": section_title,
                            "content": section_content
                        })
                section_title = line.strip()
                current_section = []
            else:
                current_section.append(line)
        
        # Don't forget last section
        if current_section:
            section_content = '\n'.join(current_section).strip()
            if section_content:
                sections.append({
                    "title": section_title,
                    "content": section_content
                })
        
        # Now process each section: LONG essays stay WHOLE, short pieces get chunked
        char_offset = 0
        for section in sections:
            content = section["content"]
            
            if not content or len(content) < 20:
                continue
            
            # If section is LONG (essay-length: > 1500 chars), keep it WHOLE
            if len(content) > 1500:
                chunks.append({
                    "text": content,
                    "metadata": {
                        "source": Path(source_file).name,
                        "section": section["title"],
                        "char_index": char_offset,
                        "word_count": len(content.split()),
                        "length": len(content),
                        "type": "essay"  # Mark as full essay
                    }
                })
            else:
                # SHORT content: chunk by paragraphs
                paragraphs = content.split('\n\n')
                
                for para in paragraphs:
                    cleaned = para.strip()
                    
                    # Keep everything > 10 chars (short poems, thoughts, lines)
                    if cleaned and len(cleaned) > 10:
                        chunks.append({
                            "text": cleaned,
                            "metadata": {
                                "source": Path(source_file).name,
                                "section": section["title"],
                                "char_index": char_offset,
                                "word_count": len(cleaned.split()),
                                "length": len(cleaned),
                                "type": "paragraph"
                            }
                        })
                    
                    char_offset += len(para) + 2
            
            char_offset += len(content) + 2

        return chunks

    def _save_to_cache(self):
        """Save embeddings and metadata to disk"""
        try:
            # Save embeddings as numpy arrays
            embeddings = np.array([p.embedding for p in self.passages])
            with open(self.embeddings_cache, "wb") as f:
                pickle.dump(embeddings, f)
            
            # Save metadata and text
            metadata = {
                "texts": [p.text for p in self.passages],
                "metadata_list": [p.metadata for p in self.passages]
            }
            with open(self.metadata_cache, "w") as f:
                json.dump(metadata, f, indent=2)
            
            print(f"  ✓ Cached {len(self.passages)} embeddings")
        except Exception as e:
            print(f"  ⚠ Error caching: {e}")

    def _load_from_cache(self):
        """Load embeddings and metadata from disk"""
        try:
            # Load embeddings
            with open(self.embeddings_cache, "rb") as f:
                embeddings = pickle.load(f)
            
            # Load metadata
            with open(self.metadata_cache, "r") as f:
                metadata = json.load(f)
            
            # Reconstruct passages
            for text, emb, meta in zip(
                metadata["texts"],
                embeddings,
                metadata["metadata_list"]
            ):
                self.passages.append(EmbeddedPassage(
                    text=text,
                    embedding=emb,
                    metadata=meta
                ))
        except Exception as e:
            print(f"  ⚠ Error loading cache: {e}")
            self.passages = []

    def retrieve(self, query: str, top_k: int = 3, use_keywords: bool = True) -> List[str]:
        """
        Retrieve relevant passages using semantic + keyword hybrid search
        
        Args:
            query: User's message/question
            top_k: Number of passages to return
            use_keywords: Also use keyword matching for robustness
        
        Returns:
            List of most relevant passage texts
        """
        if not self.indexed or not self.passages:
            return []

        if not self.model:
            # Fallback to keyword matching if model not available
            return self._keyword_retrieve(query, top_k)

        # Semantic search: embed query and find similar passages
        query_embedding = self.model.encode(query)
        
        scored = []
        for idx, passage in enumerate(self.passages):
            # Cosine similarity
            similarity = float(np.dot(query_embedding, passage.embedding) / 
                             (np.linalg.norm(query_embedding) * np.linalg.norm(passage.embedding) + 1e-8))
            
            # Apply keyword boost (if keywords match, boost score)
            if use_keywords:
                keyword_boost = self._keyword_boost(query, passage.text)
                similarity = similarity * (1 + keyword_boost)
            
            # Apply recency weight (newer passages slightly preferred)
            if idx in self.recency_weights:
                similarity *= (1 + self.recency_weights[idx] * 0.1)
            
            scored.append({
                "text": passage.text,
                "score": similarity,
                "metadata": passage.metadata
            })

        # Return top passages
        top = sorted(scored, key=lambda x: x["score"], reverse=True)[:top_k]
        return [p["text"] for p in top]

    def _keyword_retrieve(self, query: str, top_k: int) -> List[str]:
        """Fallback keyword-based retrieval"""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored = []
        for passage in self.passages:
            text_lower = passage.text.lower()
            
            # Count matches
            matches = sum(1 for word in query_words if word in text_lower)
            
            # Bonus for exact phrases
            if query_lower in text_lower:
                matches += 5
            
            if matches > 0:
                scored.append({
                    "text": passage.text,
                    "score": matches
                })
        
        top = sorted(scored, key=lambda x: x["score"], reverse=True)[:top_k]
        return [p["text"] for p in top]

    def _keyword_boost(self, query: str, text: str) -> float:
        """Calculate keyword boost factor (0-1)"""
        query_lower = query.lower()
        text_lower = text.lower()
        
        boost = 0.0
        query_words = set(query_lower.split())
        
        # Count keyword matches
        matches = sum(1 for word in query_words if word in text_lower)
        boost = min(1.0, matches / len(query_words)) if query_words else 0.0
        
        # Extra boost for exact phrase match
        if query_lower in text_lower:
            boost += 0.5
        
        return min(1.0, boost)

    def get_context(self, user_message: str, num_passages: int = 3) -> str:
        """
        Get formatted diary context to include in LLM prompt
        IMPORTANT: Shows actual quotes to encourage real engagement
        """
        passages = self.retrieve(user_message, top_k=num_passages)
        
        if not passages:
            return ""
        
        context = "\n[📖 RELEVANT DIARY QUOTES - Engage with these specifically]\n"
        for i, passage in enumerate(passages, 1):
            # Show more of the passage (min 150 chars to see real meaning)
            if len(passage) <= 300:
                display_text = passage
            else:
                # Show start + middle for long passages
                display_text = passage[:200] + "\n...[middle excerpt]...\n" + passage[-100:]
            
            context += f"\n{i}. \"{display_text}\"\n"
        
        context += "\n[INSTRUCTION: Quote from these passages in your response. Engage with specific lines, not vague summaries.]\n"
        
        return context

    def set_recency_weight(self, passage_idx: int, weight: float):
        """Boost specific passages as 'recent' (weight 0-1)"""
        self.recency_weights[passage_idx] = max(0.0, min(1.0, weight))

    def search_with_cross_references(self, query: str, top_k: int = 3) -> List[Tuple[str, List[str]]]:
        """
        Advanced search that also finds cross-references
        Returns list of (main_passage, related_passages)
        """
        main_passages = self.retrieve(query, top_k=top_k)
        
        results = []
        for main in main_passages:
            # Find related passages
            related = self.retrieve(main[:100], top_k=2)  # Use first 100 chars as query
            # Remove duplicates
            related = [r for r in related if r != main][:2]
            results.append((main, related))
        
        return results


# Test/demo
if __name__ == "__main__":
    print("\n🎯 SEMANTIC DIARY INDEX TEST\n")
    
    index = SemanticDiaryIndex()
    
    print(f"\n✓ Index ready with {len(index.passages)} passages\n")
    
    # Test queries
    test_queries = [
        "procrastination and anxiety",
        "fear of people",
        "weed addiction recovery",
        "sister support",
        "authenticity and honesty"
    ]
    
    print("🔍 SEMANTIC SEARCH RESULTS:\n")
    for query in test_queries:
        print(f"Query: '{query}'")
        results = index.retrieve(query, top_k=3)
        for i, result in enumerate(results, 1):
            preview = result[:100] + "..." if len(result) > 100 else result
            print(f"  {i}. {preview}\n")
        print("-" * 80)
    
    print("\n✨ Cross-reference search:\n")
    results = index.search_with_cross_references("procrastination", top_k=2)
    for main, related in results:
        print(f"Main: {main[:80]}...")
        for rel in related:
            print(f"  → Related: {rel[:70]}...")
        print()
