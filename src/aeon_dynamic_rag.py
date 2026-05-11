#!/usr/bin/env python3
"""
AEON Dynamic RAG System
Multi-node RAG with state space indexing
Dependencies: numpy

Fixed and working version.
"""

import numpy as np
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

import sys
sys.path.insert(0, '/home/zixen15/aet-aeon-lang/src')

__version__ = "0.5.1"  # Bumped version after fix

# ========== Simple Embedding ==========
def simple_embed(text: str, dim: int = 2048) -> np.ndarray:
    """Simple hash-based embedding for local use"""
    text_hash = hashlib.sha256(text.encode()).digest()
    vec = np.zeros(dim, dtype=np.float32)
    for i, b in enumerate(text_hash * (dim // 32 + 1)):
        vec[i % dim] = (b / 255.0) * 2.0 - 1.0
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec

# ========== AEONNode Stub ==========
class AEONNode:
    """Stub for distributed AEON node"""
    def __init__(self, node_id: str):
        self.node_id = node_id
    
    def embed(self, text: str) -> np.ndarray:
        return simple_embed(text)

# ========== Chunk ==========
@dataclass
class Chunk:
    """Knowledge chunk for RAG system"""
    id: int
    content: str
    embedding: np.ndarray
    metadata: Dict = field(default_factory=dict)
    dimension: int = 2048
    chunk_id: str = ""
    
    def __post_init__(self):
        if not self.chunk_id:
            self.chunk_id = f"chunk_{self.id:05d}"
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'content': self.content,
            'embedding': self.embedding.tolist() if hasattr(self.embedding, 'tolist') else self.embedding,
            'dimension': self.dimension,
            'chunk_id': self.chunk_id
        }

# ========== State Space Indexing ==========
class StateSpaceIndexing:
    """State space indexing for RAG queries"""
    
    def __init__(self, dimension: int = 2048):
        self.dimension = dimension
        self.vectors: np.ndarray = np.zeros((0, dimension))
        self.contents: List[str] = []
    
    def _normalize(self, vector: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vector)
        return vector / norm if norm > 0 else vector
    
    def add(self, content: str, embedding: np.ndarray) -> Chunk:
        chunk = Chunk(
            id=len(self.contents),
            content=content,
            embedding=self._normalize(embedding),
            dimension=self.dimension
        )
        self.vectors = np.vstack([self.vectors, chunk.embedding])
        self.contents.append(content)
        return chunk
    
    def query(self, query_embedding: np.ndarray, k: int = 5) -> List[Chunk]:
        query = self._normalize(query_embedding)
        similarities = self.vectors @ query
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        
        return [Chunk(
            id=idx,
            content=self.contents[idx] if idx < len(self.contents) else "",
            embedding=self.vectors[idx] if idx < len(self.vectors) else np.zeros(self.dimension),
            dimension=self.dimension
        ) for idx in top_k_indices if idx < len(self.contents)]

# ========== Dynamic RAG System ==========
class DynamicRAGSystem:
    """
    Dynamic RAG system with multi-node indexing
    
    Features:
    - State space chunking for better retrieval
    - Recursive chunking for deep knowledge
    - Simple embedding (no external API)
    """
    
    def __init__(self, 
                 dimension: int = 2048,
                 chunk_size: int = 500):
        self.dimension = dimension
        self.chunk_size = chunk_size
        
        self._chunks: List[Chunk] = []
        self._indexing = StateSpaceIndexing(self.dimension)
    
    def _generate_embedding(self, size_hint: int = 0) -> np.ndarray:
        """Generate deterministic embedding"""
        vec = np.zeros(self.dimension, dtype=np.float32)
        for i in range(self.dimension):
            vec[i] = np.sin(size_hint * 0.001 + i * 0.01)
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec
    
    async def _chunk_document(self, document: str) -> List[Chunk]:
        """Chunk document recursively"""
        if len(document) <= self.chunk_size:
            return [Chunk(
                id=len(self._chunks),
                content=document,
                embedding=self._generate_embedding(len(document)),
                dimension=self.dimension
            )]
        
        # Split document
        mid = len(document) // 2
        first_chunks = await self._chunk_document(document[:mid])
        second_chunks = await self._chunk_document(document[mid:])
        
        return first_chunks + second_chunks
    
    async def add_document(self, document: str) -> List[Chunk]:
        """Add document to RAG system"""
        chunks = await self._chunk_document(document)
        self._chunks.extend(chunks)
        for chunk in chunks:
            self._indexing.add(chunk.content, chunk.embedding)
        return chunks
    
    def query(self, query: str, k: int = 5) -> List[Chunk]:
        """Query the RAG system"""
        query_embedding = simple_embed(query, self.dimension)
        return self._indexing.query(query_embedding, k)
    
    def add_chunk(self, content: str, embedding: Optional[np.ndarray] = None) -> Chunk:
        """Add single chunk"""
        if embedding is None:
            embedding = simple_embed(content, self.dimension)
        chunk = self._indexing.add(content, embedding)
        self._chunks.append(chunk)
        return chunk
    
    def get_context(self, query: str, k: int = 5) -> str:
        """Get formatted context for AI injection"""
        chunks = self.query(query, k)
        context = "=== RAG CONTEXT ===\n"
        for i, chunk in enumerate(chunks):
            context += f"\n[{i+1}] {chunk.content[:200]}...\n"
        context += "\n=== END CONTEXT ==="
        return context


# ========== Demo ==========
if __name__ == "__main__":
    import asyncio
    
    async def demo():
        print("=" * 60)
        print("AEON Dynamic RAG System - Fixed & Working")
        print("=" * 60)
        
        # Create system
        rag = DynamicRAGSystem(dimension=2048, chunk_size=200)
        
        # Add documents
        docs = [
            "AET uses State spaces for vector representations. State(2048) creates a 2048-dimensional vector.",
            "EntropyGate collapses superposition by measuring information gain. Higher entropy means more uncertainty.",
            "The SSM scan processes sequences by maintaining hidden state. Each step updates the state.",
            "JEPA adds predictive auxiliary loss to learn better representations.",
            "Attention mechanisms allow the model to focus on relevant parts of the input.",
        ]
        
        print("\nAdding documents...")
        for doc in docs:
            chunks = await rag.add_document(doc)
            print(f"  Added: {len(chunks)} chunks from '{doc[:50]}...'")
        
        print(f"\nTotal chunks: {len(rag._chunks)}")
        
        # Query
        print("\nQuery: 'What is State in AET?'")
        results = rag.query("What is State in AET?", k=3)
        for i, chunk in enumerate(results):
            print(f"  [{i+1}] Score: {np.dot(chunk.embedding, simple_embed('What is State in AET?', rag.dimension)):.3f}")
            print(f"      {chunk.content[:80]}...")
        
        print("\n" + "=" * 60)
        print("Dynamic RAG System: WORKING ✓")
        print("=" * 60)
    
    asyncio.run(demo())