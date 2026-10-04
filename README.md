# Speaking Coach

Personal tool for speaking clearly and convincingly in English at meetings,
conference talks and public lectures.

Principle: **measure first**. Delivery metrics come from local audio analysis,
not from an LLM's opinion. An LLM coach gives content feedback on top.

## What's here

| File | Purpose |
|------|---------|
| `measure_talk.py` | Local delivery metrics: words/min, fillers/min, pauses, verbatim transcript |

## Privacy

- Recordings stay on this machine. They are excluded by `.gitignore`
  (`recordings/`, `transcripts/`, all audio formats).
- Transcripts may be sent to a cloud LLM for content feedback; remove
  confidential project details first.

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

1. Record a 5-minute practice talk on your phone; save it into `recordings/`.
2. Run:

```bash
python measure_talk.py recordings/talk.m4a
python measure_talk.py recordings/talk.m4a --model medium --pause 1.0
```

The first run downloads the Whisper model (~500 MB for `small`).

Output: words per minute, fillers per minute (with breakdown), long pauses,
the longest pause, a log line for the progress table, and the transcript.

## Known limitation

Whisper models tend to delete "um"/"uh". The script nudges the model to keep
them, but the filler count is a **lower bound**. Validate once by counting
fillers by hand in one recording and comparing.

## Roadmap (only after 30 days of daily practice)

1. Validate filler counts against a hand count
2. Pitch and volume variation (Praat / parselmouth)
3. Rubric scoring of transcripts via an LLM (key message, structure, example, ask, delivery)
4. Compare rubric scores with real listeners' ratings
