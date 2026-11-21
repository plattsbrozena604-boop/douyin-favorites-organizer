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
  "transcript": "optional platform, local-ASR, or user-provided transcript",
  "text_source": "visible|platform_caption|local_asr|user_provided|ocr|mixed|none",
  "local_media_path": "optional local path; never send the media itself to DeepSeek",
  "evidence": [
    {"type": "metadata|caption|transcript|ocr|frame", "source": "collector|platform|local_asr|user", "path": null}
  ],
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
    "content_type": "study|entertainment|mixed",
    "primary_category": "知识学习/编程技术",
    "suggested_folder": "学习·编程技术",
    "categories": ["一级分类", "二级分类"],
    "tags": ["标签"],
    "action_items": ["可执行事项"],
    "confidence": 0.85,
    "quality": "full|limited",
    "reason": "why information is limited, or an empty string"
  }
}
```

`quality` should be `limited` when the source has only a URL, very little visible text, or the decision depends on unseen visual content. Suggested folders should begin with `学习·`, `娱乐·`, or `混合·` so the two main uses remain distinguishable.
