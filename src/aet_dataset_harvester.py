#!/usr/bin/env python3
"""
AET Dataset Harvester (Phase 17)
================================
Autonomous data ingestion for Omni-Brain training.
"""

import os
import json
from pathlib import Path
from typing import List, Dict

class DatasetHarvester:
    def __init__(self, storage_dir: str = "/home/zixen15/aet_data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.categories = ["math", "physics", "science", "programming", "architecture"]

    def harvest_local(self, file_path: str, category: str):
        """Ingest a local file into the training corpus"""
        if category not in self.categories:
            print(f"Error: Unknown category {category}")
            return
            
        src = Path(file_path)
        if not src.exists():
            print(f"Error: Source file {file_path} not found.")
            return
            
        print(f"Harvester: Ingesting {src.name} into '{category}' corpus...")
        # Simulate tokenization and storage
        dest = self.storage_dir / f"{category}_training.jsonl"
        with open(dest, "a") as f:
            f.write(json.dumps({
                "source": str(src),
                "category": category,
                "content_preview": src.read_text()[:200],
                "ingested_at": 1778263925 # Simulated timestamp
            }) + "\n")
        print(f"✅ Harvest successful. Dest: {dest}")

    def scan_workspace(self):
        """Autonomously find useful code/docs in the current project"""
        print("Harvester: Scanning workspace for AI-native logic...")
        # Target Zig and Python files as 'programming' data
        for root, _, files in os.walk("/home/zixen15/aet-aeon-lang/src"):
            for file in files:
                if file.endswith((".py", ".zig")):
                    self.harvest_local(os.path.join(root, file), "programming")

if __name__ == "__main__":
    harvester = DatasetHarvester()
    harvester.scan_workspace()
