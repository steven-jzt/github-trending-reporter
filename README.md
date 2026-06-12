# GitHub Trending Reporter

每日/每周自动抓取 GitHub Trending，通过 AI 生成深度趋势分析报告，推送到邮件/微信/QQ 等渠道。

## 功能

- 抓取 GitHub Trending（每日 / 每周）
- AI 深度分析：趋势总览、方向解读、新星挖掘、生态变化
- 同时附带完整项目列表（AI 摘要 + 原始列表双输出）
- 多渠道推送：邮件（QQ 邮箱）、微信（Server 酱）、QQ（Qmsg 酱）、通用 Webhook
- 支持 Claude / OpenAI / DeepSeek 等兼容 API
- 支持 Windows 定时任务本地运行
- 支持 GitHub Actions 云端自动运行

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

复制 `.env.example` 为 `.env`，填入你的配置：

```env
# AI 摘要（至少选一个）
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.deepseek.com   # DeepSeek 或其他兼容 API
AI_MODEL=deepseek-chat

# 推送通道（选填）
EMAIL_USER=your@qq.com
EMAIL_PASS=授权码
EMAIL_TO=receive@example.com
```

### 3. 运行

```bash
python main.py daily     # 每日报告
python main.py weekly    # 每周报告
```

## 推送通道

| 通道 | 配置项 | 获取方式 |
|------|--------|---------|
| QQ 邮箱 | `EMAIL_USER` `EMAIL_PASS` | QQ 邮箱 → 设置 → 账户 → 开启 SMTP → 获取授权码 |
| 微信 | `SCT_KEY` | [Server 酱](https://sct.ftqq.com) |
| QQ | `QMSG_KEY` | [Qmsg 酱](https://qmsg.zendee.cn) |
| 企业微信 / Discord / Slack | `WEBHOOK_URL` | 对应平台的 Webhook 地址 |

## 定时运行

### Windows 定时任务（推荐国内用户）

运行 `register_tasks.py`，自动创建每天早上 9:00 的定时任务。

```bash
python register_tasks.py
```

**前提条件：电脑开机 + GitHub 加速器开启。** 关机则不会执行。适合日常使用电脑的用户。

### GitHub Actions（云端兜底）

推送到 GitHub 后自动运行。**不依赖电脑状态**，服务器 24 小时执行。

但 GitHub Actions 服务器在海外，DeepSeek 等国内 API 无法直连，AI 摘要会降级为纯项目列表格式。如需恢复 AI 摘要，可部署 `proxy.py` 作为 API 中转（见下方说明）。

需在仓库 Settings → Secrets 中配置 API key 和推送通道信息。

### AI 摘要可用性

| 运行方式 | DeepSeek (国内) | OpenAI / Claude (海外) |
|---------|:--:|:--:|
| 本地 / Windows 定时任务 | AI 摘要 + 列表 | AI 摘要 + 列表 |
| GitHub Actions | 仅列表 | AI 摘要 + 列表 |
| GitHub Actions + proxy.py 部署 | AI 摘要 + 列表 | — |

> `proxy.py` 可作为 DeepSeek API 中转服务器部署到云函数，使 GitHub Actions 也能使用 AI 摘要。目前已写好，待部署。

## 项目结构

```
├── main.py              # 主程序入口
├── config.py            # 配置读取
├── trending/            # GitHub Trending 抓取
│   ├── fetcher.py       # 网页爬虫
│   └── models.py        # 数据模型
├── summarizer/          # AI 摘要
│   ├── claude.py        # Claude API
│   ├── openai.py        # OpenAI / 兼容 API
│   └── utils.py         # Prompt 模板
├── notifier/            # 推送通道
│   ├── email.py         # 邮件
│   ├── serverchan.py    # Server 酱（微信）
│   ├── qmsg.py          # Qmsg 酱（QQ）
│   └── webhook.py       # 通用 Webhook
├── proxy.py             # DeepSeek API 中转服务器
├── worker.js            # Cloudflare Worker 中转（备选）
└── .github/workflows/   # GitHub Actions 配置
```

## License

MIT
