# Douyin Favorites Organizer Skill

一个采用“成熟采集器 + 视频解析/转写 + DeepSeek 分类 + 确认后回写”架构的 Codex Skill。它会读取用户自己的抖音收藏，根据元数据、字幕、语音转写及可用画面证据区分学习与娱乐，先生成可审核的收藏夹方案，再进行任何账号修改。

推荐使用 [JoeanAmier/TikTokDownloader](https://github.com/JoeanAmier/TikTokDownloader) 采集收藏，使用 [Evil0ctal/Douyin_TikTok_Download_API](https://github.com/Evil0ctal/Douyin_TikTok_Download_API) 或本地 `faster-whisper` 解析和转写。仓库不内置这些依赖；使用前应检查并固定具体版本。

## 功能

- 兼容下载器元数据与转写结果，统一导入 JSONL
- 明确区分学习、娱乐和混合内容，并建议二级收藏夹
- 先输出收藏夹预览方案，确认后才允许回写
- JSONL 增量保存，可中断后继续
- DeepSeek JSON 输出，逐条处理并记录失败项
- 导出结构化 JSONL 和 Markdown 知识库
- 不保存抖音 Cookie、登录凭据或 DeepSeek API Key

## 安装

把整个仓库复制到 Codex skills 目录，目录名保持为 `douyin-favorites-organizer`：

```powershell
git clone <repository-url> "$env:USERPROFILE\.codex\skills\douyin-favorites-organizer"
```

然后在 Codex 中使用：

```text
$douyin-favorites-organizer 帮我整理最近 50 条抖音收藏，导出 Markdown 和 JSONL。
```

## 单独运行整理脚本

准备符合 [`references/data-schema.md`](references/data-schema.md) 的 `favorites.jsonl`：

```powershell
$env:DEEPSEEK_API_KEY = "你的 API Key"
python scripts/organize_favorites.py data/favorites.jsonl --output-dir output
```

先验证数据且不调用 API：

```powershell
python scripts/organize_favorites.py data/favorites.jsonl --dry-run
```

DeepSeek API 用法以[官方文档](https://api-docs.deepseek.com/api/create-chat-completion/)为准。

## 隐私与合规

本项目仅用于整理用户本人在已登录会话中可访问的收藏内容，不绕过验证码、访问控制、反自动化机制或平台限制。请遵守抖音服务条款和适用法律。

## License

MIT
