#!/usr/bin/env python3
"""Normalize common Douyin downloader outputs into the skill JSONL schema."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def first_value(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = data.get(key)
        if value not in (None, "", [], {}):
            return value
    return None


def nested(data: dict[str, Any], *path: str) -> Any:
    value: Any = data
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        return value if isinstance(value, dict) else {}
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}


def transcript_for(metadata: Path) -> tuple[str | None, Path | None]:
    candidates = list(metadata.parent.glob("*.transcript.txt")) + list(metadata.parent.glob("*transcript*.txt"))
    for path in sorted(set(candidates)):
        try:
            text = path.read_text(encoding="utf-8-sig").strip()
        except (OSError, UnicodeError):
            continue
        if text:
            return text, path
    return None, None


def video_for(folder: Path) -> Path | None:
    for pattern in ("*.mp4", "*.mov", "*.webm", "*.mkv"):
        match = next(folder.glob(pattern), None)
        if match:
            return match
    return None


def normalize(path: Path, data: dict[str, Any]) -> dict[str, Any] | None:
    aweme_id = first_value(data, "aweme_id", "id", "item_id")
    url = first_value(data, "url", "share_url", "video_url")
    if not url and aweme_id:
        url = f"https://www.douyin.com/video/{aweme_id}"
    if not url:
        return None
    author = first_value(data, "author_name", "nickname") or nested(data, "author", "nickname")
    title = first_value(data, "title", "desc", "caption")
    transcript, transcript_path = transcript_for(path)
    media = video_for(path.parent)
    evidence = [{"type": "metadata", "source": "collector", "path": str(path.resolve())}]
    if title:
        evidence.append({"type": "caption", "source": "collector", "path": str(path.resolve())})
    if transcript_path:
        evidence.append({"type": "transcript", "source": "local_asr", "path": str(transcript_path.resolve())})
    return {
        "aweme_id": str(aweme_id) if aweme_id else None,
        "url": str(url),
        "title": str(title) if title else None,
        "author": str(author) if author else None,
        "author_url": first_value(data, "author_url", "author_sec_uid"),
        "caption": str(title) if title else None,
        "transcript": transcript,
        "text_source": "mixed" if transcript and title else ("local_asr" if transcript else "visible"),
        "local_media_path": str(media.resolve()) if media else None,
        "evidence": evidence,
        "collected_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "favorite_time": None,
        "source": "douyin_favorites",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Import Douyin downloader metadata and transcripts")
    parser.add_argument("download_root", type=Path)
    parser.add_argument("--output", type=Path, default=Path("data/favorites.jsonl"))
    args = parser.parse_args()
    if not args.download_root.is_dir():
        parser.error(f"download root not found: {args.download_root}")
    existing: dict[str, dict[str, Any]] = {}
    if args.output.exists():
        for line in args.output.read_text(encoding="utf-8-sig").splitlines():
            if line.strip():
                item = json.loads(line)
                key = str(item.get("aweme_id") or item.get("url"))
                existing[key] = item
    added = 0
    for path in args.download_root.rglob("*.json"):
        if "transcript" in path.name.lower():
            continue
        record = normalize(path, load_json(path))
        if not record:
            continue
        key = str(record.get("aweme_id") or record["url"])
        if key not in existing:
            existing[key] = record
            added += 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) for item in existing.values())
    args.output.write_text(text + ("\n" if text else ""), encoding="utf-8")
    print(f"Imported: {added}; total: {len(existing)}; output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
