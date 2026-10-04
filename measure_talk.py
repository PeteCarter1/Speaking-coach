"""
measure_talk.py — local delivery metrics for a recorded practice talk.

Audio never leaves your machine. Outputs words/min, fillers/min,
longest pause, and a verbatim transcript you can paste to the coach.

Setup (once, in PyCharm terminal):
    pip install faster-whisper

Usage:
    python measure_talk.py my_talk.m4a
    python measure_talk.py my_talk.m4a --model small --pause 1.0

Caveat: Whisper models tend to delete "um"/"uh". The initial prompt below
nudges the model to keep them, but the count is still a LOWER BOUND.
Check it once against a hand count of the same recording.
"""

import argparse
import re
import sys
from collections import Counter

from faster_whisper import WhisperModel

FILLERS_SINGLE = {"um", "uh", "eh", "er", "erm", "hmm", "so", "actually",
                  "basically", "like", "well"}
FILLERS_MULTI = ["you know", "i mean", "kind of", "sort of"]

# Disfluent example text makes Whisper more likely to transcribe fillers.
VERBATIM_PROMPT = "Um, so, uh, I mean, like, we, we actually... eh, you know."


def clean(word: str) -> str:
    return re.sub(r"[^\w']", "", word.lower())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("audio", help="path to audio file (m4a, mp3, wav)")
    ap.add_argument("--model", default="small",
                    help="tiny | base | small | medium (bigger = slower, better)")
    ap.add_argument("--pause", type=float, default=1.0,
                    help="gap in seconds counted as a long pause")
    args = ap.parse_args()

    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        args.audio,
        language="en",
        word_timestamps=True,
        vad_filter=False,               # VAD would hide pauses we want to measure
        initial_prompt=VERBATIM_PROMPT,
        condition_on_previous_text=False,
    )

    words = []
    for seg in segments:
        for w in seg.words or []:
            words.append((w.start, w.end, w.word.strip()))

    if not words:
        sys.exit("No speech detected.")

    tokens = [clean(w[2]) for w in words]
    speaking_span = words[-1][1] - words[0][0]
    minutes = speaking_span / 60

    # Fillers
    counts = Counter(t for t in tokens if t in FILLERS_SINGLE)
    joined = " ".join(tokens)
    for phrase in FILLERS_MULTI:
        n = len(re.findall(rf"\b{phrase}\b", joined))
        if n:
            counts[phrase] = n
    total_fillers = sum(counts.values())

    # Pauses (gaps between consecutive words)
    gaps = [(words[i + 1][0] - words[i][1], words[i][1])
            for i in range(len(words) - 1)]
    long_pauses = [g for g in gaps if g[0] >= args.pause]
    longest = max(gaps, default=(0.0, 0.0))

    transcript = " ".join(w[2] for w in words)

    print("\n=== DELIVERY METRICS ===")
    print(f"Duration (speech span): {speaking_span:.0f} s")
    print(f"Words: {len(words)}")
    print(f"Words per minute: {len(words) / minutes:.0f}   (clear talk: ~130-160)")
    print(f"Fillers: {total_fillers}  ->  {total_fillers / minutes:.1f} per minute  (lower bound)")
    for f, n in counts.most_common():
        print(f"   {f}: {n}")
    print(f"Pauses >= {args.pause:.1f} s: {len(long_pauses)}")
    print(f"Longest pause: {longest[0]:.1f} s at {longest[1]:.0f} s")
    print("\nLOG line for progress-log.md (Measured baseline table):")
    print(f"| <date> | {len(words) / minutes:.0f} | {total_fillers / minutes:.1f} | "
          f"{longest[0]:.1f} s | faster-whisper {args.model} |")
    print("\n=== TRANSCRIPT (paste to the coach for content feedback) ===")
    print(transcript)


if __name__ == "__main__":
    main()
