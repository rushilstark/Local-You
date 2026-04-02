#!/usr/bin/env python3
"""
Diary-based RAG (Retrieval Augmented Generation)
During conversation, dynamically retrieve relevant diary passages to include in context
"""

import json
from pathlib import Path
from typing import List, Dict, Optional


class DiaryRAG:
    """Retrieve relevant diary passages based on conversation topic"""
    
    def __init__(self, diary_folder: Path = None):
        self.diary_folder = Path(diary_folder) if diary_folder else Path("data/diary")
        self.passages = []
        self.indexed = False
        self._index_diary()
    
    def _index_diary(self):
        """Load and chunk diary entries into searchable passages"""
        if not self.diary_folder.exists():
            return
        
        # Load all diary entries
        for txt_file in self.diary_folder.glob("*.txt"):
            try:
                with open(txt_file, "r") as f:
                    content = f.read()
                    # Split into meaningful chunks (paragraphs)
                    chunks = self._chunk_text(content)
                    self.passages.extend(chunks)
            except:
                pass
        
        self.indexed = True
    
    def _chunk_text(self, text: str) -> List[Dict]:
        """Split text into chunks with metadata"""
        chunks = []
        
        # Split by multiple newlines (paragraphs)
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            cleaned = para.strip()
            # Keep meaningful paragraphs (at least 50 chars)
            if len(cleaned) > 50:
                chunks.append({
                    "text": cleaned,
                    "length": len(cleaned),
                    "word_count": len(cleaned.split())
                })
        
        return chunks
    
    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """
        Retrieve relevant diary passages based on query using keyword matching
        In production, use sentence-transformers for semantic search
        """
        if not self.indexed or not self.passages:
            return []
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Score passages by keyword overlap
        scored = []
        for passage in self.passages:
            text_lower = passage["text"].lower()
            
            # Count keyword matches
            matches = sum(1 for word in query_words if word in text_lower)
            
            # Bonus for exact phrases
            if query_lower in text_lower:
                matches += 5
            
            if matches > 0:
                scored.append({
                    "text": passage["text"],
                    "score": matches
                })
        
        # Return top passages
        top = sorted(scored, key=lambda x: x["score"], reverse=True)[:top_k]
        return [p["text"] for p in top]
    
    def get_context(self, user_message: str) -> str:
        """Get diary context to add to LLM prompt"""
        passages = self.retrieve(user_message, top_k=2)
        
        if not passages:
            return ""
        
        context = "\n[DIARY CONTEXT]\n"
        for i, passage in enumerate(passages, 1):
            # Truncate long passages
            if len(passage) > 200:
                passage = passage[:197] + "..."
            context += f"  {i}. {passage}\n"
        
        return context


# Test it
if __name__ == "__main__":
    rag = DiaryRAG()
    
    print(f"✓ Indexed {len(rag.passages)} diary passages\n")
    
    # Test queries
    test_queries = [
        "procrastination",
        "scared of people",
        "addiction weed",
        "my sister",
        "project deadline"
    ]
    
    for query in test_queries:
        print(f"Query: '{query}'")
        results = rag.retrieve(query, top_k=2)
        for result in results:
            print(f"  → {result[:100]}...\n")
