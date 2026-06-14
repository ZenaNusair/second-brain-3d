"""
run_pipeline.py  —  run all three pipeline steps in order
Usage: python run_pipeline.py
"""
import subprocess
import sys
from pathlib import Path

pipeline_dir = Path(__file__).parent / "pipeline"
steps = [
    ("Parsing notes",    pipeline_dir / "parse_notes.py"),
    ("Embedding notes",  pipeline_dir / "embed_notes.py"),
    ("Building graph",   pipeline_dir / "build_graph.py"),
]

for label, script in steps:
    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}")
    result = subprocess.run([sys.executable, str(script)], check=False)
    if result.returncode != 0:
        print(f"\nFailed at: {label}")
        sys.exit(1)

print("\n Pipeline complete!")
print("  data/nodes.json  — nodes with labels, details, cluster")
print("  data/edges.json  — edges with weights")
print("\n  Next: python server.py")