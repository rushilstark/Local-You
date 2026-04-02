#!/usr/bin/env python3
"""
PHASE 4: KNOWLEDGE GRAPH FOR MEMORY CONNECTIONS
Link diary entries, concepts, people, places, and insights into a semantic graph.
Enables pattern detection and smart recall.

Graph structure:
  Nodes: people, places, problems, solutions, learnings, emotions
  Edges: "relates to", "caused by", "solved by", "learned from", "supports", "conflicts"
"""

import json
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import re


@dataclass
class Node:
    """A semantic node in the knowledge graph"""
    id: str
    label: str
    node_type: str  # "person", "place", "problem", "solution", "learning", "emotion", "event"
    description: str = ""
    frequency: int = 1  # How many times mentioned
    first_mentioned: str = ""  # Date/location in diary
    attributes: Dict = None  # Extra metadata


@dataclass
class Edge:
    """Connection between two nodes"""
    source_id: str
    target_id: str
    relation_type: str  # "relates to", "caused by", "solved by", "learned from", etc.
    strength: float = 1.0  # 0-1, importance of connection
    evidence: str = ""  # Quote supporting this edge


class DiaryKnowledgeGraph:
    """
    Build semantic knowledge graph from diary entries.
    Discovers relationships and patterns automatically.
    """

    def __init__(self, diary_folder: Path = None, cache_file: Path = None):
        self.diary_folder = Path(diary_folder) if diary_folder else Path("data/diary")
        self.cache_file = Path(cache_file) if cache_file else Path(".cache/knowledge_graph.json")
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Graph structure
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.adjacency: Dict[str, List[Tuple[str, str, float]]] = defaultdict(list)  # node_id -> [(target_id, relation, strength)]
        
        # Entity detection patterns
        self.entity_patterns = {
            "person": r"\b(sister|brother|mom|dad|mother|father|friend|boss|girlfriend|boyfriend|wife|husband|rushil|mom|parents?|people|they?|you|i)\b",
            "place": r"\b(andaman|beach|home|house|office|delhi|india|room|place|city|street|there|here)\b",
            "problem": r"\b(procrastin|anxious|scared|fear|addicted?|weed|pain|struggle|weak|fail|doubt|perfectionism|victim)\b",
            "solution": r"\b(exercise|talk|honest|authentic|admit|face|act|do|start|begin|change|learn|grow|meditation|therapy)\b",
            "emotion": r"\b(angry|sad|happy|excited|calm|stressed|nervous|worried|confident|ashamed|proud|grateful)\b",
        }
        
        # Relationship patterns
        self.relation_patterns = {
            "causes": r"(cause|lead to|trigger|because of|due to|result in)",
            "caused_by": r"(caused by|because|result of|come from)",
            "solved_by": r"(solved by|fixed by|helped by|work through|overcome with)",
            "relates_to": r"(relates to|connected to|similar to|like|same as)",
            "learned_from": r"(learned from|learned that|realized that|understood that)",
            "supports": r"(supports|help|encourages|believe in|stands by)",
            "conflicts": r"(conflicts with|opposite of|contradicts|vs|against)",
        }
        
        # Load or build graph
        self._load_or_build_graph()

    def _load_or_build_graph(self):
        """Load cached graph or build fresh"""
        if self.cache_file.exists():
            print("  🔄 Loading cached knowledge graph...")
            self._load_from_cache()
            print(f"  ✓ Loaded graph: {len(self.nodes)} nodes, {len(self.edges)} edges")
        else:
            print("  🔄 Building knowledge graph from diary...")
            self._build_graph()
            self._save_to_cache()
            print(f"  ✓ Built graph: {len(self.nodes)} nodes, {len(self.edges)} edges")

    def _build_graph(self):
        """Build knowledge graph by analyzing diary entries"""
        if not self.diary_folder.exists():
            return

        all_text = ""
        
        # Load all diary entries
        for txt_file in sorted(self.diary_folder.glob("*.txt")):
            try:
                with open(txt_file, "r") as f:
                    all_text += f.read() + "\n\n"
            except Exception as e:
                print(f"  ⚠ Error reading {txt_file}: {e}")

        if not all_text:
            return

        # Extract entities
        self._extract_entities(all_text)
        
        # Extract relationships
        self._extract_relationships(all_text)
        
        # Build adjacency list
        self._build_adjacency()

    def _extract_entities(self, text: str):
        """Detect entities (people, places, problems, etc.) from text"""
        text_lower = text.lower()
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            
            for match in matches:
                entity = match.group(1).strip().lower()
                
                # Skip generic words
                if len(entity) < 2 or entity in ['a', 'i', 'to', 'is', 'the', 'and']:
                    continue
                
                entity_id = f"{entity_type}_{entity.replace(' ', '_')}"
                
                # Create or update node
                if entity_id not in self.nodes:
                    self.nodes[entity_id] = Node(
                        id=entity_id,
                        label=entity.capitalize(),
                        node_type=entity_type,
                        first_mentioned="diary"
                    )
                else:
                    self.nodes[entity_id].frequency += 1

    def _extract_relationships(self, text: str):
        """Detect relationships between entities"""
        # Split into sentences for relationship extraction
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            if len(sentence.strip()) < 20:
                continue
            
            sentence_lower = sentence.lower()
            
            # Find entities in this sentence
            entities_in_sentence = self._find_entities_in_sentence(sentence_lower)
            
            if len(entities_in_sentence) < 2:
                continue
            
            # Find relationships between entities
            for relation_type, pattern in self.relation_patterns.items():
                if re.search(pattern, sentence_lower):
                    # Create edges between all entity pairs
                    for i, entity1_id in enumerate(entities_in_sentence):
                        for entity2_id in entities_in_sentence[i+1:]:
                            strength = self._calculate_edge_strength(sentence_lower, relation_type)
                            
                            edge = Edge(
                                source_id=entity1_id,
                                target_id=entity2_id,
                                relation_type=relation_type,
                                strength=strength,
                                evidence=sentence.strip()[:100]
                            )
                            
                            # Avoid duplicates
                            if not self._edge_exists(edge):
                                self.edges.append(edge)

    def _find_entities_in_sentence(self, sentence: str) -> List[str]:
        """Find all entities in a sentence"""
        entities = []
        
        for entity_id in self.nodes:
            label = self.nodes[entity_id].label.lower()
            if label in sentence:
                entities.append(entity_id)
        
        return entities

    def _calculate_edge_strength(self, sentence: str, relation_type: str) -> float:
        """Calculate edge strength (0-1) based on context"""
        # Base strength
        strength = 0.7
        
        # Increase if relation appears multiple times in sentence
        pattern = self.relation_patterns.get(relation_type, "")
        if re.search(pattern, sentence):
            strength += 0.2
        
        # Increase if sentence is long (more context)
        if len(sentence) > 100:
            strength += 0.1
        
        return min(1.0, strength)

    def _build_adjacency(self):
        """Build adjacency list for fast lookups"""
        for edge in self.edges:
            self.adjacency[edge.source_id].append(
                (edge.target_id, edge.relation_type, edge.strength)
            )

    def _edge_exists(self, edge: Edge) -> bool:
        """Check if edge already exists"""
        for e in self.edges:
            if (e.source_id == edge.source_id and 
                e.target_id == edge.target_id and 
                e.relation_type == edge.relation_type):
                return True
        return False

    def get_related_nodes(self, node_id: str, max_depth: int = 2) -> Dict[str, any]:
        """
        Get all nodes related to given node (with depth limit)
        Returns: {related_node_id: relationship_path}
        """
        if node_id not in self.nodes:
            return {}
        
        related = {node_id: {"depth": 0}}
        visited = {node_id}
        queue = [(node_id, 0)]
        
        while queue:
            current_id, depth = queue.pop(0)
            
            if depth >= max_depth:
                continue
            
            # Find all connected nodes
            if current_id in self.adjacency:
                for target_id, relation, strength in self.adjacency[current_id]:
                    if target_id not in visited:
                        visited.add(target_id)
                        related[target_id] = {
                            "depth": depth + 1,
                            "relation": relation,
                            "strength": strength
                        }
                        queue.append((target_id, depth + 1))
        
        return related

    def find_pattern_connections(self, problem_node_id: str) -> List[str]:
        """
        Find hidden patterns/connections for a problem.
        Example: "procrastination" connects to "anxiety", "perfectionism", "fear"
        """
        if problem_node_id not in self.nodes:
            return []
        
        connections = []
        related = self.get_related_nodes(problem_node_id, max_depth=3)
        
        for node_id, info in related.items():
            if node_id != problem_node_id and self.nodes[node_id].node_type in ["problem", "emotion"]:
                relation = info.get("relation", "unknown")
                strength = info.get("strength", 0)
                
                if strength > 0.6:  # Only strong connections
                    connections.append({
                        "node": self.nodes[node_id].label,
                        "relation": relation,
                        "strength": strength
                    })
        
        return sorted(connections, key=lambda x: x["strength"], reverse=True)

    def get_solution_path(self, problem_node_id: str) -> List[Dict]:
        """
        Find how you've solved similar problems before.
        Returns path from problem → learned → solution
        """
        if problem_node_id not in self.nodes:
            return []
        
        solutions = []
        related = self.get_related_nodes(problem_node_id, max_depth=3)
        
        for node_id, info in related.items():
            if self.nodes[node_id].node_type == "solution":
                relation_chain = f"{info.get('relation', 'related')} → solved"
                solutions.append({
                    "solution": self.nodes[node_id].label,
                    "evidence": info.get("strength", 0),
                    "path": relation_chain
                })
        
        return solutions

    def get_smart_recall(self, user_message: str) -> str:
        """
        Analyze user's message and provide smart recall.
        "I'm struggling again" → Find past struggles and solutions.
        
        Returns formatted text for including in chat context.
        """
        # Extract potential problem entities from message
        problems_mentioned = []
        for node_id, node in self.nodes.items():
            if node.node_type == "problem" and node.label.lower() in user_message.lower():
                problems_mentioned.append(node_id)
        
        if not problems_mentioned:
            return ""
        
        recall_text = "\n[🧠 PATTERN RECOGNITION]\n"
        
        for problem_id in problems_mentioned:
            problem = self.nodes[problem_id]
            
            # Find connections
            connections = self.find_pattern_connections(problem_id)
            if connections:
                recall_text += f"  • {problem.label}:\n"
                for conn in connections[:3]:
                    recall_text += f"    - Connects to: {conn['node']} ({conn['relation']})\n"
            
            # Find solutions
            solutions = self.get_solution_path(problem_id)
            if solutions:
                recall_text += f"  • Solutions you've used before:\n"
                for sol in solutions[:2]:
                    recall_text += f"    - {sol['solution']}\n"
        
        return recall_text if recall_text != "\n[🧠 PATTERN RECOGNITION]\n" else ""

    def _save_to_cache(self):
        """Save graph to disk"""
        try:
            graph_data = {
                "nodes": {node_id: asdict(node) for node_id, node in self.nodes.items()},
                "edges": [asdict(edge) for edge in self.edges]
            }
            with open(self.cache_file, "w") as f:
                json.dump(graph_data, f, indent=2)
            print(f"  ✓ Cached graph: {len(self.nodes)} nodes, {len(self.edges)} edges")
        except Exception as e:
            print(f"  ⚠ Error saving cache: {e}")

    def _load_from_cache(self):
        """Load graph from disk"""
        try:
            with open(self.cache_file, "r") as f:
                graph_data = json.load(f)
            
            # Reconstruct nodes
            for node_id, node_dict in graph_data.get("nodes", {}).items():
                node = Node(**node_dict)
                self.nodes[node_id] = node
            
            # Reconstruct edges
            for edge_dict in graph_data.get("edges", []):
                edge = Edge(**edge_dict)
                self.edges.append(edge)
            
            self._build_adjacency()
        except Exception as e:
            print(f"  ⚠ Error loading cache: {e}")

    def visualize_summary(self) -> str:
        """Get text summary of graph structure"""
        summary = "\n📊 KNOWLEDGE GRAPH SUMMARY\n"
        summary += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        summary += f"Nodes: {len(self.nodes)}\n"
        summary += f"Edges: {len(self.edges)}\n"
        summary += f"\nNode types:\n"
        
        type_counts = defaultdict(int)
        for node in self.nodes.values():
            type_counts[node.node_type] += 1
        
        for node_type, count in sorted(type_counts.items()):
            summary += f"  • {node_type}: {count}\n"
        
        summary += f"\nTop entities:\n"
        top_nodes = sorted(self.nodes.values(), key=lambda n: n.frequency, reverse=True)[:5]
        for node in top_nodes:
            summary += f"  • {node.label} ({node.node_type}): {node.frequency} mentions\n"
        
        return summary


# Test/demo
if __name__ == "__main__":
    print("\n🧠 KNOWLEDGE GRAPH TEST\n")
    
    graph = DiaryKnowledgeGraph()
    
    print(graph.visualize_summary())
    
    # Test pattern detection
    print("\n🔍 PATTERN DETECTION:\n")
    
    for node_id, node in list(graph.nodes.items())[:5]:
        if node.node_type == "problem":
            print(f"Problem: {node.label}")
            connections = graph.find_pattern_connections(node_id)
            for conn in connections[:3]:
                print(f"  → {conn['node']} ({conn['relation']})")
            print()
    
    # Test smart recall
    print("\n💭 SMART RECALL:\n")
    
    test_messages = [
        "I'm struggling with procrastination again",
        "I'm scared of people",
        "I can't stop smoking weed"
    ]
    
    for msg in test_messages:
        recall = graph.get_smart_recall(msg)
        print(f"Message: '{msg}'")
        print(recall)
        print()
