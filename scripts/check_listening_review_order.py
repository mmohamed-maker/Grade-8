#!/usr/bin/env python3
"""Verify that each audio clip's serialized answer order matches the on-screen order."""
from pathlib import Path
import json
import re

page = Path("unit2/u2_c9_listening_formative_review.html").read_text(encoding="utf-8")
m = re.search(r"const questions\s*=\s*(\[[\s\S]*?\]);\s*\n\s*let currentIdx", page)
assert m, "Missing question data"
questions = json.loads(m.group(1))
voice_data = json.loads(Path("scripts/listening_review_voice_data.json").read_text(encoding="utf-8"))["questions"]
assert len(questions) == len(voice_data) == 6
assert "const indices = item.displayOrder.slice();" in page
assert "ordered-v2.mp3" in page
for i, (screen, audio) in enumerate(zip(questions, voice_data), 1):
    assert screen["q"] == audio["question"], f"Question {i} text differs"
    assert screen["options"] == audio["options"], f"Question {i} options differ"
    assert screen["displayOrder"] == audio["displayOrder"], f"Question {i} order differs"
    order = screen["displayOrder"]
    assert sorted(order) == [0, 1, 2, 3]
    shown = [screen["options"][index] for index in order]
    spoken = [audio["options"][index] for index in audio["displayOrder"]]
    assert shown == spoken, f"Question {i} audio is not visually ordered"
    assert 0 <= screen["correct"] <= 3
    print(f"Question {i}: visible/spoken indexes {order}; correct visible option {order.index(screen['correct'])+1}")
print("All six questions passed alignment checks.")
