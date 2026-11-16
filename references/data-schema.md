# Data schema

Store one UTF-8 JSON object per line in `favorites.jsonl`. Unknown values are `null`; never guess them.

## Raw record

```json
{
  "aweme_id": "optional stable Douyin item id",
  "url": "https://www.douyin.com/video/...",
  "title": "visible title or first caption line",
  "author": "visible display name",
  "author_url": "optional visible profile URL",
  "caption": "visible caption",
  "transcript": "optional visible or user-provided transcript",
  "text_source": "visible|user_provided|ocr|none",
  "collected_at": "2026-11-16T20:00:00+08:00",
  "favorite_time": null,
  "source": "douyin_favorites"
}
```

Required fields are `url`, `collected_at`, and `source`. `source` must be `douyin_favorites`. Extra source fields may be retained.

## Organized record

The helper preserves the raw record and adds:

```json
{
  "analysis": {
    "summary": "one concise Chinese summary",
    "categories": ["一级分类"],
    "tags": ["标签"],
    "action_items": ["可执行事项"],
    "quality": "full|limited",
    "reason": "why information is limited, or an empty string"
  }
}
```

`quality` should be `limited` when the source has only a URL or very little visible text.
