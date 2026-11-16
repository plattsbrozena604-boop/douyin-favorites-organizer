---
name: douyin-favorites-organizer
description: Collect a user's own Douyin favorites through the logged-in desktop web interface, normalize the metadata, and use DeepSeek to classify, summarize, deduplicate, and export a personal knowledge base. Use for organizing Douyin favorites, not for bulk scraping public accounts or bypassing access controls.
---

# Douyin Favorites Organizer

Turn the user's own, visible Douyin favorites into a resumable local dataset and an organized knowledge base.

## Guardrails

- Operate only on content the user can access in their logged-in session. Do not bypass login, CAPTCHAs, rate limits, privacy controls, or anti-automation measures.
- Treat likes, favorites, viewing history, usernames, and captions as personal data. Keep raw exports local unless the user explicitly chooses another destination.
- Never place cookies, session tokens, browser profiles, or `DEEPSEEK_API_KEY` in generated files, logs, prompts, commits, or screenshots.
- Use conservative pacing. Stop and hand control to the user if Douyin requests verification or shows a CAPTCHA.
- Do not download videos unless the user specifically asks and has the right to do so. Prefer metadata, visible captions, links, and user-provided transcripts.

## Workflow

1. Confirm the desired scope: all visible favorites or a bounded subset, and the preferred export (`Markdown`, `CSV`, or `JSONL`). If unspecified, collect up to 50 new items and produce Markdown plus JSONL.
2. Create or reuse `data/favorites.jsonl`. Read [references/data-schema.md](references/data-schema.md) before collecting or importing data.
3. Open Douyin in the user's existing browser session. Prefer `agent-desktop` when available and follow its desktop/platform rules. Observe the page before acting and verify each navigation or collection action.
4. Ask the user to complete login or verification themselves when needed. Never request their password, cookie, or one-time code in chat.
5. Visit the user's favorites page. For each visible item, record only fields observable in the UI. Use the canonical share URL when available. Append one valid JSON object per line as soon as an item is collected.
6. Deduplicate by `aweme_id` when present, otherwise by normalized `url`. Keep the earliest `collected_at` and fill missing fields from the newer record.
7. Run `python scripts/organize_favorites.py data/favorites.jsonl --output-dir output`. The script reads `DEEPSEEK_API_KEY` from the environment and resumes from `output/organized.jsonl`.
8. Review `output/failures.jsonl`. Do not silently discard failures.
9. Report the number collected, organized, skipped, and failed; link the generated files. Mention any fields that could not be observed rather than inventing them.

## Collection Notes

- Scroll incrementally and stop after two consecutive scrolls yield no new unique items.
- Do not infer `favorite_time`; Douyin may not expose it. Leave unavailable values as `null`.
- If captions or transcripts require opening a video, open one item at a time and return to the favorites list after capture.
- Prefer visible text. OCR is a fallback and OCR-derived text should set `text_source` to `ocr`.
- If only URLs were exported by the user, the organizer can still classify them, but summaries may be limited unless the user supplies text.

## DeepSeek Processing

The helper sends one record per request so failures are isolated and progress is durable. It requests JSON output containing a concise Chinese summary, categories, tags, actionable notes, and a quality flag. Use `--dry-run` to validate input without making API calls.

For custom schemas or downstream imports, preserve the raw record and add derived fields under `analysis` instead of overwriting source data.
