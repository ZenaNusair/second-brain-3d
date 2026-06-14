# Second Brain

A **3D, hand-controlled map of your notes**. Write notes as plain text, and a local
pipeline embeds them, finds the semantic connections, clusters them by theme, and
renders the result as a glowing force-directed graph you can fly through with your
hands via your webcam — no mouse required.

The notes currently loaded describe **this project itself**, so the visualization
doubles as a living diagram of its own architecture: pinch any node to bloom out
its implementation details.

---

## Features

- **Semantic graph** — notes are auto-linked by embedding similarity and grouped
  into color-coded clusters; no manual linking.
- **Hand control** — point to steer, hover to select, pinch to dive into a node —
  all from your webcam, no mouse required.
- **Pinch to explore** — zooming into a node blooms its detail bullets into a
  constellation of subnodes, with tiny orange dots streaming along the connectors.
- **Focus highlighting** — selecting a node lights up its connections and
  neighbors while the rest of the graph dims away.
- **Living visuals** — neon glow halos, particles flowing along the edges, a
  drifting starfield, a cinematic vignette, proximity-revealed titles, and a slow
  idle orbit.
- **HUD** — live note / link / cluster counts, a color-coded cluster legend, and
  an intro title sequence.
- **Self-documenting** — the loaded notes describe this project, so the graph is a
  diagram of its own architecture.

---

## How it works

```
notes.txt ──▶ parse ──▶ embed ──▶ cluster + link ──▶ nodes.json / edges.json ──▶ web viewer
```

Two halves:

1. **A Python pipeline** turns a flat text file into a graph (`data/nodes.json`,
   `data/edges.json`).
2. **A single-page web viewer** (served by Flask) renders that graph in 3D and
   takes hand input from the webcam.

### The pipeline

| Step | File | What it does |
|------|------|--------------|
| Parse | `pipeline/parse_notes.py` | Splits `data/notes.txt` on `---`; first line → label, `-` lines → details. Writes `notes.json`. |
| Embed | `pipeline/embed_notes.py` | Encodes each note with `sentence-transformers` (`all-MiniLM-L6-v2`, 384-dim). Writes `embeddings.npy` + `notes_embedded.json`. |
| Build graph | `pipeline/build_graph.py` | K-means clusters the embeddings and links each note to its `k` nearest neighbors by cosine similarity. Writes `nodes.json` + `edges.json`. |

`run_pipeline.py` runs all three in order.

### The viewer

`static/index.html` is the entire front-end — a few hundred lines, no build step,
everything loaded from CDNs:

- **[3d-force-graph](https://github.com/vasturiano/3d-force-graph)** (wraps Three.js) for the force-directed 3D layout and the directional particles flowing along edges.
- **Three.js** (a second global build) for the custom objects: glow halos, the wireframe selection box, Orbitron text-sprite labels, the detail subnodes with their orange flow dots, and the starfield.
- **[MediaPipe Hands](https://developers.google.com/mediapipe)** for webcam hand tracking.

The rest — focus highlighting, proximity labels, the HUD, the intro, and the
camera system (idle orbit + pinch-zoom focus) — is plain JS in that one file.

`server.py` is a tiny Flask app that serves the page and exposes the graph at
`/api/graph`.

---

## Setup

Requires Python 3 and a webcam (for the hand-tracking; the graph works without it).

```bash
# from the project root
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Dependencies: `sentence-transformers`, `numpy`, `scikit-learn`, `flask` (plus
`torch` et al., pulled in automatically — the first install is large).

---

## Run

```bash
# 1. build the graph from data/notes.txt
python run_pipeline.py

# 2. serve the viewer
python server.py
```

Then open **http://localhost:5001**.

> **Port note:** the server uses **5001**, not 5000 — on macOS the AirPlay Receiver
> squats on port 5000 and returns 403. Override with `PORT=8080 python server.py`.

The 3D graph works immediately with the mouse. To enable hand control, click
**“▶ enable hand tracking”** (bottom-left) and grant camera access. `localhost`
counts as a secure origin, so no HTTPS is needed.

---

## Controls

**Mouse**
- Drag to orbit · scroll to zoom · click a node for its details.

**Hands** (after enabling the camera)

| Gesture | Action |
|---------|--------|
| ☝ **Point** (extended index) | Steer — fingertip acts as a joystick to rotate the view. |
| ☝ **Hover** a node | Selects it after a short dwell — its connections light up, the rest dim. |
| 🤏 **Pinch** | Zoom into the nearest node; its detail bullets bloom into subnodes. |
| 🤏 **Pinch + move** | Orbit around the focused node. |
| 🤏 **Release** | Ease back out to the full-tree overview. |

When idle, the scene slowly orbits on its own.

---

## Adding / editing notes

Edit `data/notes.txt`. Each note is a block separated by a line containing only `---`:

```
A short title that becomes the node label
- a detail point
- another detail point

---

The next note's title
- its details
```

Then re-run `python run_pipeline.py` and refresh the page. The clusters, colors,
and connections all regenerate from the new text.

---

## Tuning

A few knobs, all near the top of their sections:

- **`pipeline/build_graph.py`** — `K_NEIGHBORS` (edges per note) and `N_CLUSTERS`.
- **`static/index.html`** (gesture/camera constants) — `AUTO_ORBIT` (idle spin
  speed), `FOCUS_RADIUS` (pinch zoom depth), `DWELL_MS` / `SELECT_DIST`
  (hover-select feel), `LABEL_FRAC` (how many titles show at once), and the
  `CLUSTER_ACCENT` color map.

---

## Project structure

```
.
├── data/
│   ├── notes.txt              # source notes (edit this)
│   ├── nodes.json             # graph nodes (label, details, cluster)
│   ├── edges.json             # graph edges (source, target, weight)
│   ├── notes.json             # generated · parsed notes        (gitignored)
│   ├── notes_embedded.json    # generated · parsed + embeddings (gitignored)
│   └── embeddings.npy         # generated · embedding matrix    (gitignored)
├── pipeline/
│   ├── parse_notes.py
│   ├── embed_notes.py
│   └── build_graph.py
├── run_pipeline.py            # runs the three pipeline steps
├── server.py                  # Flask server (port 5001)
├── static/
│   └── index.html             # the 3D viewer + hand tracking
├── requirements.txt
├── .gitignore
└── README.md
```

`nodes.json` and `edges.json` are committed so the viewer runs straight after a
clone; the other `data/*` files are regenerable intermediates and are gitignored.

---

## Notes & caveats

- **Internet on first load:** the CDN libraries and Google fonts (Orbitron, Share
  Tech Mono) are fetched at runtime, not vendored. They cache after the first load.
- **Browser:** hand tracking is most reliable in Chrome; Safari can fail to load
  the MediaPipe WebAssembly.
- **Camera:** if the status chip shows an error, it reports the real cause
  (permission denied, camera in use, etc.) rather than a generic failure.
