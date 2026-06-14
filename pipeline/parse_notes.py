import json
import re
from pathlib import Path

def parse_notes(filepath: str) -> list[dict]:
    text = Path(filepath).read_text(encoding="utf-8")
    raw_notes = [block.strip() for block in text.split("---") if block.strip()]

    notes = []
    for i, block in enumerate(raw_notes):
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            continue

        label = lines[0]
        details = []
        for line in lines[1:]:
            clean = re.sub(r"^[-*•]\s*", "", line)
            if clean:
                details.append(clean)

        notes.append({
            "id": i,
            "label": label,
            "details": details
        })

    return notes


if __name__ == "__main__":
    notes_path = Path(__file__).parent.parent / "data" / "notes.txt"
    output_path = Path(__file__).parent.parent / "data" / "notes.json"

    notes = parse_notes(str(notes_path))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)

    print(f"Parsed {len(notes)} notes")
    for n in notes:
        print(f"  [{n['id']}] {n['label'][:60]}{'...' if len(n['label'])>60 else ''}")
        print(f"       {len(n['details'])} detail points")