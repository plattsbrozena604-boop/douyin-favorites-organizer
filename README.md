# Douyin Favorites Organizer Skill

一个用于整理个人抖音收藏的 Codex Skill：通过已登录的抖音网页会话采集可见元数据，再调用 DeepSeek 进行中文摘要、分类、标签和行动项提取。

## 功能

- 通过桌面浏览器整理用户自己的抖音收藏
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
