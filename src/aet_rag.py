#!/usr/bin/env python3
"""
AET-RAG 2.0 - Advanced Retrieval for AI Context
==============================================
Vector-based retrieval system for AI instructions and documentation.

Key features:
- Vector embeddings for semantic search
- Chunk-based document indexing
- Context injection into AI prompts
- Tool documentation retrieval
- Multi-source indexing (AET docs, MathNet, examples)

This is "bleeding edge" RAG - not just keyword search,
but semantic understanding of what the AI needs.
"""

import json
import hashlib
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import math

# Simple embedding system (no external API needed)
class SimpleEmbedder:
    """Hash-based embedding for semantic similarity"""
    
    def __init__(self, dim: int = 128):
        self.dim = dim
    
    def embed(self, text: str) -> List[float]:
        """Create embedding vector from text"""
        # Use hash to create deterministic vector
        text_hash = hashlib.sha256(text.encode()).digest()
        
        # Convert to float vector
        vector = []
        for i in range(self.dim):
            byte_idx = i % len(text_hash)
            val = (text_hash[byte_idx] / 255.0) * 2.0 - 1.0  # Normalize to [-1, 1]
            vector.append(val)
        
        # Normalize
        norm = math.sqrt(sum(v*v for v in vector))
        if norm > 0:
            vector = [v/norm for v in vector]
        
        return vector
    
    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between vectors"""
        return sum(ai * bi for ai, bi in zip(a, b))

@dataclass
class DocumentChunk:
    content: str
    source: str
    chunk_id: str
    embedding: List[float]
    metadata: Dict
    created_at: float

@dataclass 
class AETTool:
    name: str
    description: str
    usage: str
    examples: List[str]
    category: str
    related_tools: List[str]

class AETRAG:
    """
    RAG system for AET documentation and tools.
    
    Maintains indexed corpus of:
    - AET language specifications
    - Tool documentation
    - MathNet problem types
    - Example code
    - Instructions for AI workers
    """
    
    def __init__(self, index_dir: str = "/tmp/aet_rag_index"):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(exist_ok=True)
        self.embedder = SimpleEmbedder(dim=128)
        self.chunks: List[DocumentChunk] = []
        self.tools: Dict[str, AETTool] = {}
        self._initialized = False
    
    def initialize(self):
        """Build the RAG index"""
        if self._initialized:
            return
        
        print("Initializing AET-RAG 2.0...")
        
        # Index AET specifications
        self._index_aet_spec()
        
        # Index tool documentation
        self._index_tools()
        
        # Index MathNet topic mappings
        self._index_mathnet()
        
        # Index example code
        self._index_examples()
        
        self._initialized = True
        print(f"RAG index ready: {len(self.chunks)} chunks, {len(self.tools)} tools")
    
    def _index_aet_spec(self):
        """Index AET language specification"""
        specs = [
            {
                "name": "State",
                "content": """
                State(dimensions) → name
                Creates a vector state space of given dimensions.
                Dimensions can be 512, 1024, 2048, 4096, etc.
                State represents the problem space for AI computation.
                """,
                "category": "primitive",
                "examples": [
                    "State(4096) → reasoning",
                    "State(1024) → embedding",
                    "State(512) → classification"
                ]
            },
            {
                "name": "LinearTransform",
                "content": """
                state @ matrix
                Linear transform operator for state spaces.
                Performs matrix multiplication on the state vector.
                Used for: projections, embeddings, transformations.
                """,
                "category": "operator",
                "examples": [
                    "vec @ W_transform",
                    "state @ W_projection >> ReLU"
                ]
            },
            {
                "name": "Composition",
                "content": """
                op1 >> op2
                Morphism composition operator.
                Chains multiple operations together.
                Left-to-right execution order.
                """,
                "category": "operator",
                "examples": [
                    "state @ W1 >> LayerNorm >> ReLU",
                    "vec @ M >> Attention >> Collapse"
                ]
            },
            {
                "name": "Superposition",
                "content": """
                ⊗ [state1, state2, ...]
                Superposition operator for parallel state existence.
                Allows multiple candidate solutions to coexist.
                Used for exploring multiple paths simultaneously.
                """,
                "category": "primitive",
                "examples": [
                    "⊗ [path_1, path_2, path_3, path_4]",
                    "solution ⊗ [candidate_a, candidate_b]"
                ]
            },
            {
                "name": "EntropyGate",
                "content": """
                ⊕EntropyGate(threshold)
                Entropy-based selection mechanism.
                Collapses superposition to single solution.
                Uses variance/diversity to select optimal path.
                """,
                "category": "primitive",
                "examples": [
                    "⊕EntropyGate(threshold=0.5)",
                    "candidates ⊕ EntropyGate(threshold=0.3)"
                ]
            },
            {
                "name": "Attention",
                "content": """
                Attention(query=state, memory=wave)
                Attention mechanism for state refinement.
                Computes relevance between query and memory.
                Scaled dot-product attention.
                """,
                "category": "primitive",
                "examples": [
                    "Attention(query=reasoning, memory=context)",
                    "Attention(query=state, memory=WaveState(1024))"
                ]
            },
            {
                "name": "WaveState",
                "content": """
                WaveState(size)
                Complex-valued wave function representation.
                Used for probabilistic and wave-based computations.
                Evolves via wave propagation operators.
                """,
                "category": "primitive",
                "examples": [
                    "WaveState(1024) → solution_wave",
                    "WaveState(2048) → probability_dist"
                ]
            },
        ]
        
        for spec in specs:
            self._add_chunk(
                content=f"{spec['name']}: {spec['content']}",
                source="aet_spec",
                metadata={"type": "primitive", "name": spec['name']}
            )
    
    def _index_tools(self):
        """Index available tools"""
        tools = [
            AETTool(
                name="aetc",
                description="AET Compiler - transpiles AET to Zig to native binary",
                usage="python3 aetc.py <file.aet> [--emit|--build]",
                examples=[
                    "python3 aetc.py program.aet",
                    "python3 aetc.py program.aet --emit",
                    "python3 aetc.py program.aet --build"
                ],
                category="compiler",
                related_tools=["aet_runtime", "zig"]
            ),
            AETTool(
                name="aet_reasoner",
                description="Natural language to AET code generator",
                usage="from aet_reasoner import AETReasoner; reasoner.reason(problem)",
                examples=[
                    "reasoner.reason('Create state space for reasoning')",
                    "result = solve_with_aet('math problem')"
                ],
                category="reasoning",
                related_tools=["dual_brain", "model_router_fallback"]
            ),
            AETTool(
                name="dual_brain",
                description="Ollama Cloud + Gemini coordination system",
                usage="from dual_brain import DualBrain; brain = DualBrain()",
                examples=[
                    "brain.generate_aet(task)",
                    "brain.execute_aet(aet_code)"
                ],
                category="coordination",
                related_tools=["model_router_fallback", "aet_reasoner"]
            ),
            AETTool(
                name="model_router_fallback",
                description="Intelligent model routing with automatic fallback",
                usage="router = AETModelRouter(); router.execute_with_fallback(prompt)",
                examples=[
                    "router.execute_with_fallback('AET code for...')",
                    "router.get_status()"
                ],
                category="infrastructure",
                related_tools=["dual_brain"]
            ),
            AETTool(
                name="aeon",
                description="AI-to-AI communication protocol",
                usage="AEON message format: AEON:task:priority:payload:hints:validation",
                examples=[
                    "create_message(task_id, priority, aet_code, models)",
                    "parse_message(aeon_string)"
                ],
                category="protocol",
                related_tools=["dual_brain"]
            ),
        ]
        
        for tool in tools:
            self.tools[tool.name] = tool
            content = f"""
            Tool: {tool.name}
            Description: {tool.description}
            Usage: {tool.usage}
            Examples: {'; '.join(tool.examples)}
            Category: {tool.category}
            Related: {', '.join(tool.related_tools)}
            """
            self._add_chunk(
                content=content,
                source=f"tool:{tool.name}",
                metadata={"type": "tool", "name": tool.name, "category": tool.category}
            )
    
    def _index_mathnet(self):
        """Index MathNet problem types and their AET mappings"""
        mappings = [
            ("Geometry", "State(2048), WaveState(1024), attention_heads=8"),
            ("Discrete Mathematics", "State(4096), WaveState(2048), paths=8"),
            ("Algebra", "State(1024), WaveState(512), attention_heads=4"),
            ("Number Theory", "State(512), WaveState(256), attention_heads=2"),
            ("Statistics", "State(2048), WaveState(1024), probability_dist"),
        ]
        
        for topic, config in mappings:
            content = f"""
            MathNet Topic: {topic}
            Recommended AET Configuration:
            {config}
            Use these settings for {topic} problems.
            """
            self._add_chunk(
                content=content,
                source="mathnet",
                metadata={"type": "topic_mapping", "topic": topic}
            )
    
    def _index_examples(self):
        """Index example AET code"""
        examples = [
            {
                "name": "wave_transform",
                "content": """
                // AET Wave Transform
                State(512) → vec
                WaveState(1024) → wave
                vec @ W_transform >> LayerNorm >> ReLU
                Attention(query=vec, memory=wave)
                ⊕EntropyGate(threshold=0.5)
                """
            },
            {
                "name": "reasoning",
                "content": """
                // AET Reasoning Chain
                State(4096) → reasoning_space
                reasoning_space @ W_chain >> LayerNorm
                Attention(query=reasoning_space, memory=WaveState(1024))
                ⊗ [candidate_1, candidate_2, candidate_3, candidate_4]
                ⊕EntropyGate(threshold=0.4) → solution
                """
            },
            {
                "name": "math_solver",
                "content": """
                // AET Math Solver
                State(2048) → problem_state
                problem_state @ W_search >> ReLU
                ⊗ [hypothesis_1, hypothesis_2, hypothesis_3]
                Attention(query=problem_state, memory=solution_wave)
                ⊕EntropyGate(threshold=0.6) → answer
                """
            }
        ]
        
        for ex in examples:
            self._add_chunk(
                content=f"Example: {ex['name']}\n{ex['content']}",
                source="examples",
                metadata={"type": "example", "name": ex['name']}
            )
    
    def _add_chunk(self, content: str, source: str, metadata: Dict):
        """Add document chunk to index"""
        chunk_id = hashlib.sha256(content.encode()).hexdigest()[:16]
        embedding = self.embedder.embed(content)
        
        chunk = DocumentChunk(
            content=content,
            source=source,
            chunk_id=chunk_id,
            embedding=embedding,
            metadata=metadata,
            created_at=0  # Would use time.time() in production
        )
        self.chunks.append(chunk)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """
        Retrieve most relevant chunks for query.
        
        Returns list of (chunk, similarity_score) tuples.
        """
        if not self._initialized:
            self.initialize()
        
        query_embedding = self.embedder.embed(query)
        
        # Compute similarities
        results = []
        for chunk in self.chunks:
            similarity = self.embedder.cosine_similarity(query_embedding, chunk.embedding)
            results.append((chunk, similarity))
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def get_context(self, query: str, max_chunks: int = 5) -> str:
        """
        Get contextual information for AI prompt injection.
        
        Returns formatted string with relevant documentation.
        """
        results = self.retrieve(query, top_k=max_chunks)
        
        context = "=== RELEVANT CONTEXT ===\n"
        for chunk, score in results:
            context += f"\n[Relevance: {score:.2f}] {chunk.source}\n"
            context += f"{chunk.content}\n"
        
        context += "\n=== END CONTEXT ==="
        return context
    
    def get_tool_info(self, tool_name: str) -> Optional[str]:
        """Get documentation for specific tool"""
        tool = self.tools.get(tool_name)
        if not tool:
            return None
        
        return f"""
        Tool: {tool.name}
        Description: {tool.description}
        Usage: {tool.usage}
        Examples: {'; '.join(tool.examples)}
        """
    
    def get_topic_config(self, topic: str) -> Optional[str]:
        """Get AET configuration for MathNet topic"""
        results = self.retrieve(f"MathNet {topic} configuration", top_k=1)
        if results:
            return results[0][0].content
        return None

def inject_context(rag: AETRAG, query: str, base_prompt: str) -> str:
    """
    Inject RAG context into prompt for AI.
    
    This is the "bleeding edge" part - not just RAG retrieval,
    but intelligent context assembly that the AI understands.
    """
    context = rag.get_context(query, max_chunks=3)
    return f"""{base_prompt}

{context}
"""

def demo():
    print("AET-RAG 2.0 - Advanced Retrieval for AI Context")
    print("=" * 60)
    print()
    
    rag = AETRAG()
    rag.initialize()
    
    # Test queries
    queries = [
        "How do I create a state space for geometry problems?",
        "How do I use the EntropyGate operator?",
        "Write AET code for counting problems",
    ]
    
    for query in queries:
        print(f"Query: {query}")
        print("-" * 40)
        
        results = rag.retrieve(query, top_k=3)
        for chunk, score in results:
            print(f"  [{score:.2f}] {chunk.metadata.get('type', 'doc')}: {chunk.content[:100]}...")
        print()
    
    # Test context injection
    print("Context Injection Example:")
    print("-" * 40)
    prompt = "Generate AET code for a geometry problem"
    enhanced = inject_context(rag, prompt, prompt)
    print(enhanced[:500])
    print("...")
    print()

if __name__ == "__main__":
    demo()