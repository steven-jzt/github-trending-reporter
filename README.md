# GitHub Trending Reporter

每日/每周/月度自动抓取 GitHub Trending，通过 AI 生成深度趋势分析报告，推送到邮件/微信/QQ 等渠道。

## 一键部署

**方式 A：Use this template（推荐给新手）**

点击仓库首页的绿色 **"Use this template"** 按钮 → Create new repository → 然后：

```bash
git clone <你的仓库地址>
cd github-trending-reporter
pip install -r requirements.txt
python setup.py        # 交互式配置向导，2 分钟
python main.py daily   # 立即测试
```

**方式 B：直接 clone**

```bash
git clone https://github.com/steven-jzt/github-trending-reporter.git
cd github-trending-reporter
pip install -r requirements.txt
python setup.py
python main.py daily
```

向导依次引导配置：AI API → 邮件推送 → 其他推送通道 → 定时方式（Windows 定时任务 / GitHub Actions / 两者）。配置写入 `.env`，不需要手动编辑。

> 如果选了 GitHub Actions，向导会打印 Secrets 清单，去仓库 Settings → Secrets → Actions 填入即可。

## 功能

- 抓取 GitHub Trending（每日 / 每周 / 月度）
- AI 深度分析：趋势总览、方向解读、新星挖掘、生态变化
- 同时附带完整项目列表（AI 摘要 + 原始列表双输出）
- 多渠道推送：邮件（QQ 邮箱）、微信（Server 酱）、QQ（Qmsg 酱）、通用 Webhook
- 支持 Claude / OpenAI / DeepSeek 等兼容 API
- 启动前自动预检：API 连通性、SMTP 认证、配置完整性
- 结构化日志：同时输出控制台和日志文件，定时任务出错可追溯
- 支持 Windows 定时任务本地运行
- 支持 GitHub Actions 云端自动运行

## 手动配置（不用向导）

如果你不想用 `python setup.py`，手动复制 `.env.example` 为 `.env`：

```env
# AI 摘要（至少选一个）
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.deepseek.com
AI_MODEL=deepseek-chat

# 邮件推送
EMAIL_USER=your@qq.com
EMAIL_PASS=授权码
EMAIL_TO=a@qq.com,b@qq.com  # 逗号分隔多个收件人
```

启动时自动预检 API 连通性、SMTP 认证、配置完整性，问题一次性报告。

```bash
python main.py daily     # 每日报告
python main.py weekly    # 每周报告
python main.py monthly   # 月度报告
```

控制台输出同时写入 `logs/` 目录，按日期保存。

## 推送通道

| 通道 | 配置项 | 获取方式 |
|------|--------|---------|
| QQ 邮箱 | `EMAIL_USER` `EMAIL_PASS` `EMAIL_TO` | QQ 邮箱 → 设置 → 账户 → 开启 SMTP → 获取授权码。<br>`EMAIL_TO` 支持逗号分隔多个收件人。 |
| 微信 | `SCT_KEY` | [Server 酱](https://sct.ftqq.com) |
| QQ | `QMSG_KEY` | [Qmsg 酱](https://qmsg.zendee.cn) |
| 企业微信 / Discord / Slack | `WEBHOOK_URL` | 对应平台的 Webhook 地址 |

## 定时运行

### Windows 定时任务（推荐国内用户）

**方式 A：双击 `schedule.bat`**（最简单）

直接双击项目目录下的 `schedule.bat`，自动创建三个定时任务：

| 任务名 | 频率 | 时间 |
|--------|------|------|
| `GitHubTrendingDaily` | 每天 | 09:00 |
| `GitHubTrendingWeekly` | 每周一 | 09:00 |
| `GitHubTrendingMonthly` | 每月 1 号 | 09:00 |

**方式 B：命令行**

```bash
python register_tasks.py   # 同上，创建全部三个定时任务
```

可通过 `taskschd.msc`（任务计划程序）查看或删除任务。

**前提条件：电脑开机 + GitHub 可访问。** 关机则不会执行。适合日常使用电脑的用户。

### 新增收件人补发

在 `.env` 的 `EMAIL_TO` 中添加新地址后，运行补发脚本将当天的报告发送给所有收件人：

```bash
python resend_today.py
```

### GitHub Actions（云端兜底）

推送到 GitHub 后自动运行。**不依赖电脑状态**，服务器 24 小时执行。

运行前自动预检 API 连通性，失败时会打印明确原因。运行日志作为 Artifact 保留（Actions → 具体 run → Artifacts），方便排查问题。

但 GitHub Actions 服务器在海外，DeepSeek 等国内 API 无法直连，预检会提示 DNS 解析失败，AI 摘要会降级为纯项目列表格式。如需恢复 AI 摘要，有两种方式（见下文）：

需在仓库 Settings → Secrets 中配置 API key 和推送通道信息。

### AI 摘要可用性

| 运行方式 | DeepSeek (国内) | OpenAI / Claude (海外) |
|---------|:--:|:--:|
| 本地 / Windows 定时任务 | AI 摘要 + 列表 | AI 摘要 + 列表 |
| GitHub Actions | 仅列表 | AI 摘要 + 列表 |
| GitHub Actions + proxy.py 部署 | AI 摘要 + 列表 | — |

### 如何让 GitHub Actions 也有 AI 摘要

GitHub Actions 服务器在海外，访问国内 API（DeepSeek 等）会 DNS 失败。两种解决方式：

**方式 A：换海外 API（推荐，零部署）**

注册 [OpenAI](https://platform.openai.com) 或 [Anthropic](https://console.anthropic.com) 获取 API key：

```env
# OpenAI
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o

# 或 Claude
ANTHROPIC_API_KEY=sk-ant-xxx
AI_MODEL=claude-sonnet-4-6
```

本地和 Actions 可以各用各的：本地 `.env` 用 DeepSeek，GitHub Secrets 用 OpenAI，互不影响。

**方式 B：部署 API 中转（继续用 DeepSeek，需云服务）**

注册 [阿里云函数计算 FC](https://fc.console.aliyun.com)（免费额度 100 万次/月），将 `proxy.py` 部署上去，获取公网 URL：

```env
OPENAI_BASE_URL=https://xxx.cn-hangzhou.fc.aliyuncs.com
```

> `proxy.py` 代码已写好，支持直接运行和 WSGI 云函数两种模式，无需修改代码即可部署。

## 项目结构

```
├── main.py              # 主程序入口
├── setup.py             # 交互式一键部署向导
├── config.py            # 配置读取
├── validate.py          # 启动前配置预检 + 连通性测试
├── log.py               # 结构化日志（控制台 + 文件）
├── register_tasks.py    # Windows 定时任务注册
├── schedule.bat         # 一键注册定时任务（双击即可）
├── run_daily.bat        # 每日任务脚本
├── run_weekly.bat       # 每周任务脚本
├── run_monthly.bat      # 月度任务脚本
├── resend_today.py      # 补发当天报告给新增收件人
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
