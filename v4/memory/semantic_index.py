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
        
        # Load all diary entries (recursively from all subfolders)
        for txt_file in sorted(self.diary_folder.glob("**/*.txt")):
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
        """
        Split text into meaningful chunks.
        
        Since essays are now in individual files, we can use a simpler strategy:
        - Each file is ONE essay
        - Split only on LARGE section breaks (3+ blank lines = new section)
        - This preserves essay integrity while splitting very long essays
        """
        chunks = []
        
        # Extract essay title from filename (most reliable source)
        # Format: "data/diary/We Said Yes.txt" → "We Said Yes"
        import os
        filename_without_ext = os.path.splitext(os.path.basename(source_file))[0]
        # Replace underscores and dashes with spaces for readability
        essay_title_from_filename = filename_without_ext.replace('_', ' ').replace('-', ' ')
        
        # Also try to extract from first line as fallback
        lines = text.split('\n')
        essay_title = essay_title_from_filename  # Use filename as primary
        
        if lines:
            first_line = lines[0].strip()
            # If first line is a proper title (not too short, not obviously content), use it
            if first_line and 10 < len(first_line) < 100 and not first_line.startswith('('):
                # Only override if it's clearly better than filename version
                if first_line != filename_without_ext:
                    essay_title = first_line
                    
        # Sanitize for comparison (remove punctuation, lowercase)
        essay_title_compare = essay_title.lower().replace('!!', '').replace('?', '').replace(',', '').strip()
        
        # For most essay files, just keep as ONE chunk
        # Only split if the essay is VERY long (>500 lines)
        if len(lines) <= 500:
            # Keep entire file as one chunk
            chunk_text = text.strip()
            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "source_file": source_file,
                        "section": essay_title,  # Add essay title as "section"
                        "char_index": 0,
                        "word_count": len(chunk_text.split()),
                        "timestamp": None
                    }
                })
            return chunks
        
        # For very long essays, split on major section breaks (3+ blank lines)
        current_chunk = []
        blank_count = 0
        char_index = 0
        
        for line in lines:
            if not line.strip():
                blank_count += 1
                current_chunk.append(line)
            else:
                blank_count = 0
                current_chunk.append(line)
            
            # Major break detected - flush current chunk
            if blank_count >= 3:
                chunk_text = '\n'.join(current_chunk).strip()
                if chunk_text and len(chunk_text) > 100:  # Only save non-tiny chunks
                    chunks.append({
                        "text": chunk_text,
                        "metadata": {
                            "source_file": source_file,
                            "section": essay_title,
                            "char_index": char_index,
                            "word_count": len(chunk_text.split()),
                            "timestamp": None
                        }
                    })
                    char_index += len(chunk_text)
                
                current_chunk = []
                blank_count = 0
        
        # Don't forget the final chunk
        chunk_text = '\n'.join(current_chunk).strip()
        if chunk_text and len(chunk_text) > 100:
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source_file": source_file,
                    "section": essay_title,
                    "char_index": char_index,
                    "word_count": len(chunk_text.split()),
                    "timestamp": None
                }
            })
        
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
        
        Strategy:
        1. TITLE MATCHING: If query contains essay title words → return that essay's passages
        2. SEMANTIC SEARCH: Find passages most similar to query semantically
        3. KEYWORD BOOST: Amplify scores when keywords match content
        
        Args:
            query: User's message/question
            top_k: Number of passages to return
            use_keywords: Also use keyword matching for robustness
        
        Returns:
            List of most relevant passage texts (no duplicates)
        """
        if not self.indexed or not self.passages:
            return []

        if not self.model:
            # Fallback to keyword matching if model not available
            return self._keyword_retrieve(query, top_k)

        query_lower = query.lower()
        
        # ====================================================================
        # STEP 1: AGGRESSIVE TITLE DETECTION
        # If user asks about specific essay, retrieve ALL passages from it
        # ====================================================================
        essay_passages = {}  # title_normalized -> list of passages
        
        for passage in self.passages:
            section = passage.metadata.get("section", "").lower()
            if section and len(section) > 3:
                # Normalize title for comparison (remove punctuation, extra spaces)
                section_normalized = section.replace('!!', '').replace('?', '').replace(',', '').strip()
                if section_normalized not in essay_passages:
                    essay_passages[section_normalized] = []
                essay_passages[section_normalized].append(passage)
        
        # Check if query contains essay title keywords
        query_words = set(w for w in query_lower.split() if len(w) > 2)
        best_match_title = None
        best_match_score = 0
        
        for title, passages_list in essay_passages.items():
            title_words = set(w for w in title.split() if len(w) > 2)
            if not title_words:
                continue
            
            # Calculate word overlap between query and title
            overlap = len(title_words & query_words)
            
            # If found matching words, this is likely the essay they're asking about
            if overlap > 0:
                if overlap > best_match_score:
                    best_match_score = overlap
                    best_match_title = title
                elif overlap == best_match_score and title and len(title) < len(best_match_title or ""):
                    # If tied, prefer shorter title (more specific)
                    best_match_title = title
        
        # If we found a strong title match, return those passages
        if best_match_title and best_match_score >= 1:
            results = [p.text for p in essay_passages[best_match_title]]
            # Remove duplicates while preserving order
            seen = set()
            unique_results = []
            for r in results[:top_k]:
                r_hash = hash(r[:50])  # Use first 50 chars as proxy
                if r_hash not in seen:
                    unique_results.append(r)
                    seen.add(r_hash)
            return unique_results[:top_k]
        
        # ====================================================================
        # STEP 2: SEMANTIC SEARCH (fallback if no title match)
        # ====================================================================
        query_embedding = self.model.encode(query)
        
        scored = []
        for idx, passage in enumerate(self.passages):
            # Cosine similarity
            similarity = float(np.dot(query_embedding, passage.embedding) / 
                             (np.linalg.norm(query_embedding) * np.linalg.norm(passage.embedding) + 1e-8))
            
            # Apply keyword boost if enabled
            if use_keywords:
                keyword_boost = self._keyword_boost(query, passage.text)
                similarity = similarity * (1 + keyword_boost * 0.5)
            
            # Apply recency weight (newer passages slightly preferred)
            if idx in self.recency_weights:
                similarity *= (1 + self.recency_weights[idx] * 0.1)
            
            scored.append({
                "text": passage.text,
                "score": similarity,
                "metadata": passage.metadata
            })

        # Sort by relevance and return top passages
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
        Format diary context for LLM prompt with intelligent presentation.
        
        Strategy:
        - Single essay (num_passages=1): Show FULL TEXT with clear boundaries
        - Multiple passages: Show with source attribution and smart truncation
        - Always: Include instruction to engage with specific content
        """
        passages = self.retrieve(user_message, top_k=num_passages)
        
        if not passages:
            return ""
        
        if len(passages) == 1 and num_passages == 1:
            # ================================================================
            # SINGLE ESSAY MODE: Complete text with essay title
            # ================================================================
            essay_text = passages[0]
            
            # Extract essay title from first line (most likely to be title)
            lines = essay_text.split('\n')
            essay_title = lines[0].strip() if lines else "Essay"
            
            # Validate it looks like a title (not too short, not content)
            if not (10 < len(essay_title) < 100 and not essay_title.startswith('(')):
                essay_title = "Essay"
            
            # Format with clear visual boundaries
            context = "\n" + "╔" + "═"*78 + "╗\n"
            context += f"║ 📖 ESSAY: {essay_title:<70} ║\n"
            context += "╠" + "═"*78 + "╣\n"
            context += "║                                                                              ║\n"
            context += "╚" + "═"*78 + "╝\n\n"
            context += essay_text
            context += "\n\n" + "╔" + "═"*78 + "╗\n"
            context += "║ ⚠️  READ THE ENTIRE ESSAY ABOVE CAREFULLY                                    ║\n"
            context += "║                                                                              ║\n"
            context += "║ RESPOND TO HIS ACTUAL QUESTION/STATEMENT - Quote specific lines.              ║\n"
            context += "╚" + "═"*78 + "╝\n"
            
        else:
            # ================================================================
            # MULTIPLE PASSAGES MODE: Better formatting with source info
            # ================================================================
            context = "\n" + "┌" + "─"*78 + "┐\n"
            context += "│ � RELEVANT DIARY PASSAGES                                                    │\n"
            context += "└" + "─"*78 + "┘\n"
            
            for i, passage in enumerate(passages, 1):
                # Extract essay/section info if available
                source = "Diary Entry"
                
                # Try to find the source from passage metadata
                for p in self.passages:
                    if p.text == passage:
                        section = p.metadata.get("section", "")
                        if section:
                            source = section
                        break
                
                # Smart truncation for display
                if len(passage) <= 400:
                    display_text = passage
                else:
                    # Show: beginning + indicator + end
                    start_len = 180
                    end_len = 160
                    omitted = len(passage) - start_len - end_len
                    display_text = (
                        passage[:start_len].rstrip() +
                        f"\n\n[... {omitted} characters omitted ...]\n\n" +
                        passage[-end_len:].lstrip()
                    )
                
                context += f"\n┌─ Passage {i}: {source} " + "─"*(65-len(source)) + "┐\n"
                context += display_text
                context += f"\n└─" + "─"*76 + "┘\n"
            
            context += "\n" + "┌" + "─"*78 + "┐\n"
            context += "│ 📌 Quote specific lines from above passages when responding                   │\n"
            context += "└" + "─"*78 + "┘\n"
        
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
