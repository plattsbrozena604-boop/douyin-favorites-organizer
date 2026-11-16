#!/usr/bin/env python3
"""Organize Douyin favorite records with DeepSeek using only the stdlib."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable


API_URL = "https://api.deepseek.com/chat/completions"
SYSTEM_PROMPT = """你是个人知识库整理助手。请根据用户提供的抖音收藏记录输出一个 JSON 对象，不要输出 Markdown。字段必须为：summary（简洁中文摘要字符串）、categories（1到3个中文分类字符串数组）、tags（2到8个中文标签字符串数组）、action_items（可执行事项字符串数组，没有则为空数组）、quality（full 或 limited）、reason（信息不足原因，否则为空字符串）。不要声称看过未提供的视频内容；只有链接或文本过少时必须设为 limited。"""


def read_jsonl(path: Path) -> Iterable[tuple[int, dict[str, Any]]]:
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: each line must be a JSON object")
            yield line_number, value


def record_key(record: dict[str, Any]) -> str:
    aweme_id = str(record.get("aweme_id") or "").strip()
    url = str(record.get("url") or "").strip().rstrip("/")
    if aweme_id:
        return f"id:{aweme_id}"
    if url:
        return f"url:{url}"
    raise ValueError("record must contain a non-empty url or aweme_id")


def validate(record: dict[str, Any]) -> None:
    if not str(record.get("url") or "").strip():
        raise ValueError("missing url")
    if record.get("source") != "douyin_favorites":
        raise ValueError("source must be douyin_favorites")
    if not str(record.get("collected_at") or "").strip():
        raise ValueError("missing collected_at")


def append_jsonl(path: Path, value: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def completed_keys(path: Path) -> set[str]:
    if not path.exists():
        return set()
    keys: set[str] = set()
    for _, record in read_jsonl(path):
        try:
            keys.add(record_key(record))
        except ValueError:
            continue
    return keys


def call_deepseek(record: dict[str, Any], api_key: str, model: str, timeout: int) -> dict[str, Any]:
    source = {k: v for k, v in record.items() if k != "analysis"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "请整理这条记录并返回 JSON：\n" + json.dumps(source, ensure_ascii=False)},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
        "max_tokens": 1200,
        "stream": False,
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
    content = body["choices"][0]["message"]["content"]
    if not isinstance(content, str) or not content.strip():
        raise ValueError("DeepSeek returned empty content")
    analysis = json.loads(content)
    required = {"summary", "categories", "tags", "action_items", "quality", "reason"}
    if not isinstance(analysis, dict) or not required.issubset(analysis):
        raise ValueError("DeepSeek response does not match the expected schema")
    if analysis["quality"] not in {"full", "limited"}:
        raise ValueError("DeepSeek response has invalid quality")
    return analysis


def write_markdown(path: Path, records: list[dict[str, Any]]) -> None:
    lines = ["# 抖音收藏知识库", ""]
    for record in records:
        analysis = record.get("analysis", {})
        title = record.get("title") or analysis.get("summary") or record.get("url")
        lines.extend([
            f"## {title}", "",
            f"- 链接：{record.get('url', '')}",
            f"- 作者：{record.get('author') or '未知'}",
            f"- 分类：{', '.join(analysis.get('categories', []))}",
            f"- 标签：{', '.join(analysis.get('tags', []))}",
            f"- 摘要：{analysis.get('summary', '')}",
        ])
        actions = analysis.get("action_items", [])
        if actions:
            lines.append("- 行动：" + "；".join(actions))
        if analysis.get("quality") == "limited":
            lines.append("- 信息质量：有限（" + str(analysis.get("reason") or "源文本不足") + "）")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Organize Douyin favorites with DeepSeek")
    parser.add_argument("input", type=Path, help="UTF-8 JSONL input")
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--model", default="deepseek-chat")
    parser.add_argument("--delay", type=float, default=0.8, help="seconds between API calls")
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input.is_file():
        print(f"Input not found: {args.input}", file=sys.stderr)
        return 2
    args.output_dir.mkdir(parents=True, exist_ok=True)
    organized_path = args.output_dir / "organized.jsonl"
    failures_path = args.output_dir / "failures.jsonl"
    done = completed_keys(organized_path)

    try:
        records = list(read_jsonl(args.input))
        for _, record in records:
            validate(record)
            record_key(record)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.dry_run:
        unique = len({record_key(record) for _, record in records})
        print(f"Valid records: {len(records)}; unique: {unique}; already organized: {len(done)}")
        return 0

    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        print("DEEPSEEK_API_KEY is not set", file=sys.stderr)
        return 2

    succeeded = skipped = failed = 0
    seen: set[str] = set()
    for line_number, record in records:
        key = record_key(record)
        if key in seen or key in done:
            skipped += 1
            continue
        seen.add(key)
        try:
            analysis = call_deepseek(record, api_key, args.model, args.timeout)
            output = dict(record)
            output["analysis"] = analysis
            append_jsonl(organized_path, output)
            done.add(key)
            succeeded += 1
        except (ValueError, KeyError, json.JSONDecodeError, urllib.error.URLError) as exc:
            append_jsonl(failures_path, {"line": line_number, "key": key, "error": str(exc)})
            failed += 1
        time.sleep(max(0.0, args.delay))

    organized = [record for _, record in read_jsonl(organized_path)] if organized_path.exists() else []
    write_markdown(args.output_dir / "knowledge-base.md", organized)
    print(f"Organized: {succeeded}; skipped: {skipped}; failed: {failed}; total output: {len(organized)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
