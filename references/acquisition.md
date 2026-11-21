# Acquisition and parsing

Use upstream projects as replaceable adapters; this skill owns the normalized dataset and classification output.

## Preferred collectors

- `JoeanAmier/TikTokDownloader` (`https://github.com/JoeanAmier/TikTokDownloader`): preferred high-adoption collector for Douyin favorites and collections. Record the exact commit used.
- `Evil0ctal/Douyin_TikTok_Download_API` (`https://github.com/Evil0ctal/Douyin_TikTok_Download_API`): preferred parsing/MCP service when an API workflow or offline speech-to-text is useful. Record the exact commit used.
- Local `faster-whisper`: preferred private/offline transcript fallback. Start with `base`; use a larger model only when accuracy requires it and resources permit.

Do not assume upstream compatibility. Inspect the current README, license, release activity, configuration, and output format before use. Never commit cookies, downloaded media, or account exports.

## Evidence priority

1. Collector metadata: canonical URL, item id, title, author, caption.
2. Platform captions or transcript supplied with the download.
3. Local speech-to-text transcript.
4. Representative frames and OCR when visual context changes the meaning.

Keep evidence provenance in `evidence[]`. A transcript does not prove visual claims, and a few sampled frames do not prove the full video was watched.

## Write-back boundary

Acquisition and local analysis do not authorize changes to the user's Douyin account. First generate a folder plan. After the user confirms that plan, create missing folders and move items through the logged-in UI with conservative pacing. Stop for verification, CAPTCHA, ambiguous duplicate titles, or unavailable items.
