import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

def embed_notes(notes: list[dict]) -> list[dict]:
    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    labels = [n["label"] for n in notes]
    print(f"Embedding {len(labels)} notes...")
    embeddings = model.encode(labels, show_progress_bar=True, normalize_embeddings=True)

    for note, emb in zip(notes, embeddings):
        note["embedding"] = emb.tolist()

    return notes, embeddings


if __name__ == "__main__":
    data_dir = Path(__file__).parent.parent / "data"
    notes_path = data_dir / "notes.json"
    output_path = data_dir / "notes_embedded.json"
    embeddings_path = data_dir / "embeddings.npy"

    with open(notes_path, encoding="utf-8") as f:
        notes = json.load(f)

    notes, embeddings = embed_notes(notes)

    np.save(str(embeddings_path), embeddings)
    print(f"Saved embeddings matrix: {embeddings.shape} → {embeddings_path.name}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(notes)} embedded notes → {output_path.name}")