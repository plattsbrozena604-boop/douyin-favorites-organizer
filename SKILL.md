---
name: douyin-favorites-organizer
description: Read and analyze a user's own Douyin favorites, including downloaded metadata, transcripts, and available visual evidence; use DeepSeek to separate study from entertainment, assign folders, summarize, deduplicate, and export a reviewable organization plan. Use for organizing Douyin favorites, not public-account scraping or access-control bypasses.
---

# Douyin Favorites Organizer

Turn the user's own favorites into a resumable local dataset, evidence-based analyses, and a reviewable folder plan.

## Guardrails

- Operate only on content the user can access in their logged-in session. Do not bypass login, CAPTCHAs, rate limits, privacy controls, or anti-automation measures.
- Treat likes, favorites, viewing history, usernames, and captions as personal data. Keep raw exports local unless the user explicitly chooses another destination.
- Never place cookies, session tokens, browser profiles, or `DEEPSEEK_API_KEY` in generated files, logs, prompts, commits, or screenshots.
- Use conservative pacing. Stop and hand control to the user if Douyin requests verification or shows a CAPTCHA.
- Download only the user's own accessible favorites and only when analysis requires it. Never redistribute downloaded media.
- Classification and local export are reversible. Creating folders or moving favorites in Douyin is a separate mutation: show the plan first and obtain the user's confirmation immediately before applying it.

## Workflow

1. Determine whether the task is collection, analysis, planning, or an explicitly confirmed write-back. If scope is unspecified, process all accessible favorites and emit Markdown plus JSONL.
2. Read [references/acquisition.md](references/acquisition.md) before installing or running a collector. Prefer `JoeanAmier/TikTokDownloader` for favorite acquisition and `Evil0ctal/Douyin_TikTok_Download_API` or local `faster-whisper` for speech-to-text. Pin the observed revision in the run report; do not blindly execute unreviewed setup scripts.
3. Ask the user to complete login or verification themselves. Never request or expose passwords, cookies, browser profiles, or one-time codes in chat.
4. Import collector output with `python scripts/import_downloads.py <download-root> --output data/favorites.jsonl`. Read [references/data-schema.md](references/data-schema.md) for the evidence model.
5. For items lacking meaningful text, obtain a transcript. Sample frames/OCR only when audio and metadata are insufficient; record every evidence source. A model may analyze supplied frames, but must not claim to have watched portions it did not inspect.
6. Run `python scripts/organize_favorites.py data/favorites.jsonl --output-dir output`. It reads `DEEPSEEK_API_KEY` from the environment and resumes from `output/organized.jsonl`.
7. Review `output/failures.jsonl`, all `limited` records, and borderline `study`/`entertainment` decisions. Do not silently discard failures.
8. Present `output/folder-plan.md` and counts before any write-back. Apply folder creation/moves only after explicit confirmation, using the logged-in UI and verifying each material action.

## Collection Notes

- Scroll incrementally and stop after two consecutive scrolls yield no new unique items.
- Do not infer `favorite_time`; Douyin may not expose it. Leave unavailable values as `null`.
- If captions or transcripts require opening a video, open one item at a time and return to the favorites list after capture.
- Prefer visible text. OCR is a fallback and OCR-derived text should set `text_source` to `ocr`.
- If only URLs were exported by the user, the organizer can still classify them, but summaries may be limited unless the user supplies text.

## DeepSeek Processing

The helper sends one record per request so failures are isolated and progress is durable. It requires a `content_type` of `study`, `entertainment`, or `mixed`, a stable primary category, a suggested folder, a concise Chinese summary, tags, actionable notes, confidence, and an evidence-based quality flag. Use `--dry-run` to validate input without making API calls.

For custom schemas or downstream imports, preserve the raw record and add derived fields under `analysis` instead of overwriting source data.
