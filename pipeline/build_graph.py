import json
import numpy as np
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

K_NEIGHBORS = 4
N_CLUSTERS = 6

def build_graph(notes: list[dict], embeddings: np.ndarray) -> tuple[list, list]:
    n = len(notes)
    sim = cosine_similarity(embeddings)

    # k-means clustering
    n_clusters = min(N_CLUSTERS, n)
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    labels = km.fit_predict(embeddings)
    for note, cluster in zip(notes, labels):
        note["cluster"] = int(cluster)

    # k-NN edges (skip self, avoid duplicates)
    edges = []
    seen = set()
    for i in range(n):
        sims = sim[i].copy()
        sims[i] = -1
        top_k = np.argsort(sims)[::-1][:K_NEIGHBORS]
        for j in top_k:
            key = tuple(sorted([i, int(j)]))
            if key not in seen:
                seen.add(key)
                edges.append({
                    "source": i,
                    "target": int(j),
                    "weight": float(sim[i][j])
                })

    return notes, edges


if __name__ == "__main__":
    data_dir = Path(__file__).parent.parent / "data"

    with open(data_dir / "notes_embedded.json", encoding="utf-8") as f:
        notes = json.load(f)

    embeddings = np.load(str(data_dir / "embeddings.npy"))
    notes, edges = build_graph(notes, embeddings)

    nodes_out = []
    for n in notes:
        nodes_out.append({
            "id": n["id"],
            "label": n["label"],
            "details": n["details"],
            "cluster": n["cluster"]
        })

    with open(data_dir / "nodes.json", "w", encoding="utf-8") as f:
        json.dump(nodes_out, f, indent=2, ensure_ascii=False)

    with open(data_dir / "edges.json", "w", encoding="utf-8") as f:
        json.dump(edges, f, indent=2, ensure_ascii=False)

    print(f"Built graph: {len(nodes_out)} nodes, {len(edges)} edges")
    print(f"Clusters: {N_CLUSTERS}  |  k-neighbors: {K_NEIGHBORS}")
    for node in nodes_out:
        print(f"  [{node['id']}] cluster={node['cluster']}  {node['label'][:55]}")