# 定时推送底座 · 内置 China Daily 英语精读

> 一个跑在 **GitHub Actions** 上的**通用定时推送框架**：按日 / 周自动执行脚本，把抓取或生成的内容整理成文档，推送到你的邮箱。
> **电脑关机也能跑，不需要服务器**。
>
> 仓库里已经内置一个**完整可用的示例任务**：每天抓一篇 China Daily 文章，用大模型生成「生词 + 语法 + 长难句」精读 Word。
> 想推别的内容（每周科技要闻、每日天气、网站更新提醒、周报…）→ 按同样的方式再加一个任务即可。

---

## 📁 目录结构

```
main.py                          # 任务一：China Daily 英语精读（同时提供公用函数）
tasks/
  └─ weekly_example.py           # 任务二示例：每周文化版速览（可删可改）
.github/workflows/
  ├─ cet4-daily.yml              # 任务一的工作流（默认手动触发）
  └─ weekly-example.yml          # 任务二的工作流（默认手动触发）
README.md
LICENSE
.gitignore
```

> 一个任务 = **一个脚本 + 一个 workflow**。多个任务共用一个仓库、共用一套 Secrets，互不干扰。

---

## ✨ 内置任务一：China Daily 英语精读

| | |
| --- | --- |
| **自动选题** | 按优先级加权：科技 > 文化 > 体育健康 > 生态 > 社会 > 教育；**近 3 天滚动候选**，当天稿少也不会空转 |
| **正文可靠** | 多容器抽取 + "像不像散文"判定 + 标题/meta 摘要一致性校验 → **防乱码、防"内容与原文不符"** |
| **词汇注释** | 30 词：音标 / 词性 / 级别 / 释义 / 原文例句 / 固定搭配 / 词形变化，**每个词字段分行**；标〔拓展〕者超出四级考纲 |
| **语法讲解** | 6 处重点语法与长难句，原文中加粗 + 下划线 + 句末【n】，并注明「第几段第几句」 |
| **生成即审核** | 16 项自动检查（序号齐全/按序/不重复、下划线数、乱码、成品无 Markdown 记号…）；不合格自动重生成，**硬伤直接拒发** |
| **零依赖** | 纯 Python 标准库，不需要 `pip install` |

**生成的文档**（五部分）：文章信息（含客观配图说明）→ 原文（双重标注）→ 核心词汇与拓展词 → 重点语法与长难句 → 学习建议。

---

## 🚀 快速开始（约 10 分钟）

### 第 1 步：建一个仓库

新建一个 **Private** 仓库，把本目录下所有文件放进去（保持目录结构）。

### 第 2 步：准备两样东西

| 需要什么 | 怎么拿 |
| --- | --- |
| **大模型 API Key** | 推荐 [DeepSeek](https://platform.deepseek.com)（便宜）；也可用任意兼容 OpenAI 接口的模型（智谱 / 通义等） |
| **发信通道** | 推荐 [Resend](https://resend.com)（免费 100 封/天，走 HTTPS，不受云服务器 IP 风控）；也可用邮箱 SMTP |

> ⚠️ **Resend 免费版**：`from` 只能是 `onboarding@resend.dev`，且**只能发到注册 Resend 用的那个邮箱**。
> 所以请**用你要收信的那个邮箱去注册 Resend**。

### 第 3 步：配置 Secrets

仓库 → **Settings → Secrets and variables → Actions → New repository secret**

| Name | 必填 | 说明 |
| --- | --- | --- |
| `LLM_API_KEY` | ✅（任务一） | 大模型 Key |
| `MAIL_TO` | ✅ | 收件邮箱（代码里**不内置**任何地址） |
| `RESEND_API_KEY` | 二选一 | 用 Resend 发信时填 |
| `RESEND_FROM` | 可选 | 已验证域名时才需要（默认 `onboarding@resend.dev`） |
| `SMTP_USER` / `SMTP_PASS` | 二选一 | 用邮箱 SMTP 发信时填（`SMTP_PASS` 是**授权码**，不是登录密码） |
| `SMTP_HOST` / `SMTP_PORT` | 可选 | 默认 `smtp.qq.com` / `465` |
| `LLM_BASE_URL` / `LLM_MODEL` | 可选 | 默认 `https://api.deepseek.com/v1` / `deepseek-chat` |
| `MAIL_FROM_NAME` | 可选 | 发件人显示名，默认「CET-4 助教」 |

### 第 4 步：手动跑一次

仓库 → **Actions** → 左侧 **CET-4 每日精读** → 右侧 **Run workflow**

绿色的 ✓ 就表示成功，去邮箱查收（**先看垃圾邮件**）。

### 第 5 步：开启每天自动运行

手动跑通后，打开 `.github/workflows/cet4-daily.yml`，把这两行的 `#` 去掉：

```yaml
  # schedule:
  #   - cron: '0 23 * * *'      # 北京时间每天 07:00 = UTC 23:00
```

改完提交即可，之后每天早上 **07:00（北京）** 自动运行。

> 为什么默认关着？刚 fork / 刚建的仓库还没配 Secret，直接开着定时会每天报一次红。

---

## 🧩 新增一个推送任务（三步）

### ① 写脚本

复制 `tasks/weekly_example.py` 改成你的逻辑，或者新建 `tasks/你的任务.py`。
**直接 `import main` 就能复用**这些公用函数：

| 函数 | 作用 |
| --- | --- |
| `http_get(url)` | 抓网页，自动处理编码与浏览器 UA |
| `http_post_json(url, payload, headers)` | 调 API（已带浏览器 UA，兼容 Resend / 各类 LLM） |
| `build_docx(md)` | 把 Markdown 转成 `.docx`（支持标题 / 列表 / 表格 / 加粗 / 下划线） |
| `send_mail(docx_bytes, 文件名, 主题, 正文)` | 发信：配了 `RESEND_API_KEY` 走 Resend，否则走 SMTP |
| `now_bj()` | 北京时间（不受运行环境时区影响） |

最小骨架：

```python
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main as bot

def main_handler():
    text = bot.http_get("https://example.com")          # ① 抓数据
    md = "# 今日简报\n\n" + text[:500]                   # ② 整理成 Markdown
    bot.send_mail(bot.build_docx(md), "digest.docx",    # ③ 生成 Word + 发信
                  "今日简报", "见附件")
    return {"ok": True}
```

### ② 加 workflow

复制 `.github/workflows/weekly-example.yml` → 只改三处：

```yaml
name: 你的任务名
on:
  workflow_dispatch:
  # schedule:
  #   - cron: '0 1 * * 1'        # ① 时间（UTC = 北京时间 − 8 小时）
...
        run: python tasks/你的任务.py    # ② 脚本路径
```

常用 cron 对照（北京时间 → cron）：

| 时间 | cron |
| --- | --- |
| 每天 07:00 | `0 23 * * *` |
| 每周一 09:00 | `0 1 * * 1` |
| 每月 1 日 08:00 | `0 0 1 * *` |
| 每天 08:00 与 20:00 | `0 0,12 * * *` |

### ③ 提交

推到仓库即可。Secrets 共用，不用重配。第一次先 **Run workflow** 手动验证，再取消 `schedule` 的注释。

---

## 🎨 自定义任务一（CET-4 精读）

| 想改什么 | 改哪里 |
| --- | --- |
| **运行时间** | `.github/workflows/cet4-daily.yml` 的 `schedule`（默认被注释，取消注释即开启）；`cron` 用 **UTC**，**UTC = 北京时间 − 8 小时**（北京 07:00 → `0 23 * * *`） |
| **选题偏好** | `main.py` 的 `PREFER_KEYWORDS`（词 → 权重，数字越大越优先）、`EXCLUDE_KEYWORDS`（命中即淘汰） |
| **候选时间窗** | `rank_candidates(..., window=3)` |
| **词汇数量** | `CIRCLED`（带圈序号串的长度）＋ `WORD_PROMPT` 里的数量说明 |
| **语法条数** | `GRAMMAR_PROMPT` 里要求的条数（程序会取能在原文定位到的前 6 条） |
| **难度** | `WORD_PROMPT` / `GRAMMAR_PROMPT` 里「四级高分 / 六级」「偏难考点」等描述 |
| **文档语言** | `build_markdown()` 里的中文标题与字段名 |

---

## 🧯 常见问题

**① 报 `SMTPServerDisconnected` / `535 Authentication failed`**
GitHub 的服务器在海外，QQ / 163 邮箱的 SMTP 常直接掐断连接。**改用 `RESEND_API_KEY`** 即可绕开（配了就优先走 Resend）。

**② Resend 报 403（Cloudflare 1010）**
Resend 前置 Cloudflare，请求**必须带浏览器 User-Agent**——`http_post_json()` 已统一处理。

**③ 报红 `exit code 1`，日志里有 `[选文] 无合格文章`**
说明近 3 天确实没有达到门槛的文章（正文 ≥1200 字 / 与标题摘要吻合）。日志会**逐条打印淘汰原因**。周末、节假日更容易遇到。
放宽办法：调 `pick_best_article()` 里的 `minlen`，或 `rank_candidates()` 的 `window`。

**④ 早上 7:00 没准时收到**
GitHub 的定时任务在整点高峰期可能延迟几分钟到几十分钟，7:00–7:40 之间到都属正常。

**⑤ 想本地试跑**
```powershell
$env:LLM_API_KEY="sk-..."; $env:MAIL_TO="you@example.com"; $env:RESEND_API_KEY="re_..."
python main.py                    # 任务一
python tasks/weekly_example.py    # 任务二示例
```

---

## 🔐 安全提示

- **密钥只放 GitHub Secrets**，永远不要写进代码或提交历史；Secrets 在网页上只显示名字，日志里会自动打码。
- 若某个 Key 曾经被提交过，**改私有并不能撤销**——请立刻到服务商后台**吊销并重建**。
- 仓库建议设为 **Private**；想分享给别人用，分享这个模板（或让对方 fork），**不要**分享你的 Secrets。

## ⚠️ 免责声明

本项目仅用于**个人学习**。抓取的文章版权归 **China Daily** 所有，请勿将生成内容用于商业用途或二次分发。

## 📄 License

[MIT](LICENSE)
