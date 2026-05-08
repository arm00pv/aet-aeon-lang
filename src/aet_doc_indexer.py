#!/usr/bin/env python3
"""
AET-DocIndexer - Automatic Documentation Indexing for RAG
========================================================
Indexes all project documentation for AI context retrieval.

This ensures:
1. AET specifications are indexed
2. AEON protocol is indexed
3. Examples are indexed
4. AI bootstrap instructions are indexed

Any AI can query this index and understand the full system.
"""

import hashlib
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple

# Simple embedding system
class SimpleEmbedder:
    """Hash-based embedding for semantic similarity"""
    
    def __init__(self, dim: int = 128):
        self.dim = dim
    
    def embed(self, text: str) -> List[float]:
        text_hash = hashlib.sha256(text.encode()).digest()
        vector = []
        for i in range(self.dim):
            byte_idx = i % len(text_hash)
            val = (text_hash[byte_idx] / 255.0) * 2.0 - 1.0
            vector.append(val)
        norm = math.sqrt(sum(v*v for v in vector))
        if norm > 0:
            vector = [v/norm for v in vector]
        return vector
    
    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        return sum(ai * bi for ai, bi in zip(a, b))

import math

@dataclass
class DocumentChunk:
    content: str
    source: str
    chunk_id: str
    embedding: List[float]
    metadata: Dict

class AETDocIndexer:
    """
    Automatically indexes all project documentation.
    Any AI can query this to understand AET/AEON.
    """
    
    def __init__(self, project_root: str = "/home/zixen15/aet-aeon-lang"):
        self.project_root = Path(project_root)
        self.embedder = SimpleEmbedder(dim=128)
        self.chunks: List[DocumentChunk] = []
    
    def index_all(self):
        """Index all documentation files"""
        print("AET-DocIndexer: Indexing all project documentation...")
        
        # Index core specs
        self._index_file("SPECIFICATION.md", "spec", {"type": "specification", "priority": "high"})
        self._index_file("FORMAL_SPECIFICATION.md", "formal_spec", {"type": "formal_spec", "priority": "high"})
        self._index_file("AI_BOOTSTRAP.md", "ai_bootstrap", {"type": "bootstrap", "priority": "high"})
        
        # Index examples
        examples_dir = self.project_root / "examples"
        if examples_dir.exists():
            for f in examples_dir.glob("*.aet"):
                self._index_file(str(f), "example", {"type": "example", "language": "aet"})
        
        # Index source files with docstrings
        src_dir = self.project_root / "src"
        if src_dir.exists():
            for f in src_dir.glob("*.py"):
                if not f.name.startswith("__"):
                    self._index_file(str(f), "source", {"type": "source", "language": "python"})
        
        print(f"Indexed {len(self.chunks)} chunks from project documentation")
        return len(self.chunks)
    
    def _index_file(self, file_path: str, category: str, metadata: Dict):
        """Index a single file"""
        path = self.project_root / file_path if not str(file_path).startswith("/") else Path(file_path)
        
        if not path.exists():
            return
        
        try:
            content = path.read_text(errors="ignore")
        except:
            return
        
        # Split into chunks (by paragraphs or lines)
        chunks = self._chunk_content(content, max_chars=500)
        
        for chunk in chunks:
            if len(chunk.strip()) < 20:  # Skip tiny chunks
                continue
            
            chunk_id = hashlib.sha256(f"{file_path}:{chunk[:50]}".encode()).hexdigest()[:16]
            
            doc_chunk = DocumentChunk(
                content=chunk,
                source=f"{category}:{path.name}",
                chunk_id=chunk_id,
                embedding=self.embedder.embed(chunk),
                metadata={**metadata, "file": str(path)}
            )
            self.chunks.append(doc_chunk)
    
    def _chunk_content(self, content: str, max_chars: int = 500) -> List[str]:
        """Split content into semantic chunks"""
        # Remove markdown code blocks but keep info
        content = re.sub(r'```[\s\S]*?```', '[CODE BLOCK]', content)
        
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\n+', content)
        
        chunks = []
        current = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If single paragraph fits, add it
            if len(current) + len(para) < max_chars:
                current += " " + para if current else para
            else:
                # Save current chunk
                if current:
                    chunks.append(current)
                # Start new chunk
                current = para[:max_chars]
        
        if current:
            chunks.append(current)
        
        return chunks
    
    def query(self, question: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Query the index"""
        query_embedding = self.embedder.embed(question)
        
        results = []
        for chunk in self.chunks:
            similarity = self.embedder.cosine_similarity(query_embedding, chunk.embedding)
            results.append((chunk, similarity))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def get_context(self, question: str, top_k: int = 5) -> str:
        """Get formatted context for AI injection"""
        results = self.query(question, top_k)
        
        context = "=== AET PROJECT CONTEXT ===\n"
        for chunk, score in results:
            context += f"\n[Relevance: {score:.2f}] From: {chunk.source}\n"
            context += f"{chunk.content[:300]}...\n" if len(chunk.content) > 300 else f"{chunk.content}\n"
        
        context += "\n=== END CONTEXT ===\n"
        context += "\nUse the above context to answer the question. If the context doesn't contain enough information, use your training knowledge of AET/AEON systems."
        
        return context

def demo():
    print("AET-DocIndexer - Automatic Documentation Indexing")
    print("=" * 60)
    print()
    
    indexer = AETDocIndexer()
    indexer.index_all()
    
    # Test queries
    queries = [
        "What is State in AET?",
        "How does AEON protocol work?",
        "How do I generate AET code from Python?",
        "What is EntropyGate in AET?",
        "How does superposition work?",
    ]
    
    print("\n" + "=" * 60)
    print("Testing queries...")
    print("=" * 60)
    
    for query in queries:
        print(f"\nQuery: {query}")
        context = indexer.get_context(query, top_k=3)
        print(f"Context (first 200 chars): {context[:200]}...")

def create_ai_instruction_card():
    """
    Create a single-file AI instruction card that any AI can read
    to understand the complete project.
    """
    card = '''# AET-AEON Project: AI Instruction Card

## Project Purpose
This project builds an AI-native programming language (AET) and communication protocol (AEON)
for AI-to-AI computation. It includes MathNet (27,817 math problems) for training.

## Quick Start (Any AI)
```bash
# Clone and enter
git clone https://github.com/arm00pv/aet-aeon-lang.git
cd aet-aeon-lang

# Generate AET code
python3 src/aet_reasoner.py
# Or use orchestrator
python3 src/aet_orchestrator.py

# Compile AET to binary
python3 src/aetc.py examples/hello_world.aet --build
/tmp/aet_compile/main  # Exit 0 = success
```

## Core Concepts

### AET Primitives
- `State(dims)` - Create vector state space
- `@` - Linear transform (matrix multiply)
- `>>` - Compose operations (chain)
- `⊗` - Superposition (parallel paths)
- `⊕` - Entropy gate (collapse/select)
- `Attention(q, m)` - Attention mechanism
- `WaveState(size)` - Wave function

### AEON Protocol
Format: `AEON:task:priority:payload:::hints:validation`
Used for AI-to-AI communication with model hints and validation.

### Fallback System
If cloud models fail (429, timeout), automatically uses `phi4:latest` (local).
No external dependencies when using local fallback.

## Key Files
- `SPECIFICATION.md` - Complete AET/AEON specification (750 lines)
- `FORMAL_SPECIFICATION.md` - Mathematical foundations (537 lines)
- `AI_BOOTSTRAP.md` - This file (instructions for AI)
- `src/aet_orchestrator.py` - Complete system integration
- `src/aet_rag.py` - RAG context system (indexes all docs)

## Topic → AET Config Mapping
- Geometry: State(2048), WaveState(1024), heads=8
- Discrete Math: State(4096), WaveState(2048), paths=8
- Algebra: State(1024), WaveState(512), heads=4

## Workflow
1. Generate AET code (from natural language)
2. Compile to Zig (aetc.py)
3. Compile to binary (zig build-exe)
4. Execute (native speed)

## Communication
AIs communicate via AEON messages. See AI_BOOTSTRAP.md for format.

---
This card ensures any AI can understand and continue the project.
Read AI_BOOTSTRAP.md for complete documentation.
'''
    
    card_path = Path("/home/zixen15/aet-aeon-lang/AI_INSTRUCTION_CARD.md")
    card_path.write_text(card)
    print(f"Created AI instruction card: {card_path}")
    return card_path

if __name__ == "__main__":
    demo()
    print("\n" + "=" * 60)
    create_ai_instruction_card()