# auto-push-hub · 定时推送底座

> **到点自动干活，把结果送到你邮箱。**
> 不用买服务器、不用一直开着电脑 —— 任务跑在 GitHub Actions 上，每天 / 每周按你设定的时间执行脚本：抓网页、调 API、整理成 Word 或邮件正文，然后发出去。

这个仓库本身只提供**底座**：抓取、重试、排版、发信、定时、日志都已写好。
你往里塞的"推什么"，可以是新闻摘要、行情日报、论文更新、RSS 聚合、网站改版监控、账单到期提醒……**只要是"定期看一次、想知道变化"的事，都能变成一个任务。**

仓库里预置了 3 个可以直接跑的例子（其中一个稍微复杂：用大模型生成英语精读讲义），用来演示这套东西能写到多细。

---

## 一、能推什么

| 场景 | 数据从哪来 | 推送形态 |
| --- | --- | --- |
| 每日新闻 / 行业要闻摘要 | 任意新闻站首页、频道页 | Word 附件 + 摘要正文 |
| RSS 聚合（博客、播客、期刊） | RSS / Atom 的 XML | 列表 + 链接 |
| 股票 / 基金 / 加密货币行情 | 行情 API（如腾讯、新浪、CoinGecko） | 表格 Word 或 HTML 邮件 |
| 汇率、油价、金价变化 | 公开 API | 单行文字 + 阈值告警 |
| 新论文 / 新专利 / 新招标 | arXiv、PubMed、招标网 | 列表 + 关键词过滤 |
| 招聘岗位更新 | 招聘网站搜索页 | 新增岗位列表 |
| 网站 / 商品页变更监控 | 目标页面 HTML 对比上次快照 | "变了什么"的 diff |
| 微博 / 公众号 / 知乎热榜 | 公开榜单页 | 前 20 条 |
| 每日天气、空气质量、限行 | 天气 API | 短文本 |
| 日程 / 生日 / 保险 / 证书到期 | 自己维护的 JSON / CSV | 提前 N 天提醒 |
| 周报、月报汇总 | 多个来源拼装 | Word 报告 |
| 学习打卡、读书进度、健身记录 | 自己的表格 | 进度 + 连续天数 |
| 大模型生成的定制内容 | LLM API | 任意（本仓库例 ①） |

同时也可以用 Cron 做**定时提醒**：不需要抓任何东西，到点发一封"该交房租了"也算一个任务。

对应的 workflow：`daily-reading.yml` / `weekly-example.yml` / `daily-note-example.yml`（都在 `.github/workflows/` 下）。

> 这些任务**大部分不需要 AI**，纯抓取 + 排版就够；需要总结、翻译、出题、讲解时才调大模型。

---

## 二、预置的 3 个例子

| 文件 | 任务 | 默认频率 | 说明 |
| --- | --- | --- | --- |
| `main.py` | **例 ①：每日英语精读** | 每天 07:00 | 抓 China Daily 一篇文章 → 大模型出「生词表 + 语法点」→ 代码把加粗/下划线/序号写回原文 → 30 项检查不过就重生成 → 出 Word 发信。**最完整的参考实现** |
| `tasks/weekly_example.py` | **例 ②：频道速览** | 每周一 09:00 | 抓一个频道页最新 5 条，生成 Word。**最简模板，20 行就能改出自己的任务** |
| `tasks/daily_note_example.py` | **例 ③：纯文本提醒** | 每天 08:00 | 不抓网页、不带附件，只发一封 HTML 邮件。演示"无附件 / 富文本"用法 |

三个任务的 workflow 都在 `.github/workflows/` 下，默认**只允许手动触发**（`schedule` 被注释），配好 Secrets 并手动跑通后再开启定时，避免刚建仓库就天天报红。

---

## 三、它是怎么跑起来的

```
GitHub 定时触发 (cron)
   └─ 启动 ubuntu 容器，装 Python 3.11
        └─ 运行你的脚本
             ├─ 抓数据      http_get / http_post_json
             ├─ 加工        （你的逻辑，可选调 LLM）
             ├─ 排版        build_docx(md) 或直接拼 HTML
             └─ 发信        send_mail(...)
                  ├─ 已配 Resend → 走 HTTPS API（推荐）
                  └─ 否则       → 走 SMTP（部分邮箱会拦海外 IP）
```

一次运行约 20–60 秒，公开仓库的 Actions 免费额度足够每天跑几十次。

---

## 四、快速开始（约 10 分钟）

### 1. 拿到这个仓库

- 想自己改：**Fork** 或 **Use this template**（建议设成 Private）；
- 只想要一份自己的：Download ZIP，解压后新建仓库上传。

> 目录结构必须保持：

```
main.py                            # 公用函数 + 例 ①
tasks/
  weekly_example.py                # 例 ②
  daily_note_example.py            # 例 ③
.github/workflows/
  daily-reading.yml                # 例 ① 的 workflow
  weekly-example.yml               # 例 ②
  daily-note-example.yml           # 例 ③
README.md  LICENSE  .gitignore
```

> ⚠️ `.github` 和 `.gitignore` 是**隐藏文件**，Windows 上传前要在资源管理器里勾选「查看 → 显示 → 隐藏的项目」，否则会漏传，结果就是 Actions 里一个任务都没有。

### 2. 准备两样东西

| 需要什么 | 怎么拿 | 是否必需 |
| --- | --- | --- |
| **能发信的通道** | 推荐 [Resend](https://resend.com)（免费 100 封/天，走 HTTPS，不受云服务器 IP 风控）；或任意邮箱 SMTP | ✅ 必需 |
| **大模型 API Key** | [DeepSeek](https://platform.deepseek.com)（便宜）或任意兼容 OpenAI 接口的服务 | 仅例 ① / 需要 AI 的任务 |

> ⚠️ Resend 免费版：`from` 只能是 `onboarding@resend.dev`，且**只能发到注册 Resend 用的那个邮箱**。
> 所以请**用你想收信的那个邮箱去注册 Resend**。

### 3. 配 Secrets

仓库 → **Settings → Secrets and variables → Actions → New repository secret**

| Name | 必填 | 说明 |
| --- | --- | --- |
| `MAIL_TO` | ✅ | 收件邮箱（代码里不内置任何地址） |
| `RESEND_API_KEY` | 发信二选一 | 用 Resend 时填（推荐） |
| `SMTP_USER` / `SMTP_PASS` | 发信二选一 | 用 SMTP 时填，`SMTP_PASS` 是**授权码**不是登录密码 |
| `SMTP_HOST` / `SMTP_PORT` | 可选 | 默认 `smtp.qq.com` / `465` |
| `RESEND_FROM` | 可选 | 已验证域名才需要 |
| `LLM_API_KEY` | 例 ① 必填 | 大模型 Key |
| `LLM_BASE_URL` / `LLM_MODEL` | 可选 | 默认 `https://api.deepseek.com/v1` / `deepseek-chat` |
| `MAIL_FROM_NAME` | 可选 | 发件人显示名，默认「自动推送」 |

### 4. 手动跑一次

**Actions** → 左侧选任务 → 右侧 **Run workflow** → 等 1 分钟。

绿灯 ≠ 成功，**一定要看日志最后几行**；脚本内部失败会打印原因并 `exit 1`，那种情况是红灯。

### 5. 开启定时

打开对应 workflow，把 `schedule:` 那两行的 `#` 去掉，提交即可：

```yaml
  # schedule:
  #   - cron: '0 23 * * *'      # 北京时间 07:00（GitHub 用 UTC）
```

**cron 速查（UTC = 北京时间 − 8 小时）**

| 北京时间 | cron |
| --- | --- |
| 每天 07:00 | `0 23 * * *` |
| 每天 08:00 与 20:00 | `0 0,12 * * *` |
| 每周一 09:00 | `0 1 * * 1` |
| 工作日 09:30 | `30 1 * * 1-5` |
| 每月 1 日 08:00 | `0 0 1 * *` |

> 整点高峰会有几分钟到几十分钟延迟，属正常现象。

---

## 五、加一个自己的推送（三步）

### ① 写脚本

复制 `tasks/weekly_example.py` 改名，只改"取数据"和"拼内容"两段。**下面四种是最常见的写法。**

**A. 纯文本 / HTML 提醒（不带附件）**

```python
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main as bot

def main_handler():
    html = "<h2>本周待办</h2><ul><li>周三交报告</li><li>周五体检</li></ul>"
    bot.send_mail(subject="本周待办提醒", body_text="周三交报告 / 周五体检", body_html=html)
    return {"ok": True}
```

**B. RSS / API 摘要（生成 Word）**

```python
import main as bot

FEED = "https://example.com/feed.xml"

def main_handler():
    xml = bot.http_get(FEED)                       # 抓 XML
    titles = [t for t in __import__("re").findall(r"<title>(.*?)</title>", xml, 8)][:10]
    md = "# 今日聚合\n\n" + "\n".join("- %s" % t.strip() for t in titles)
    bot.send_mail(bot.build_docx(md), "digest.docx", "今日聚合", "%d 条更新，见附件" % len(titles))
    return {"ok": True}
```

**C. 调 JSON API（行情 / 天气 / 榜单）**

```python
import main as bot

def main_handler():
    raw = bot.http_get("https://api.example.com/quotes?symbols=600519,000001")
    rows = [["名称", "价格", "涨跌幅"]] + [["贵州茅台", "1680.0", "+1.2%"]]
    md = "# 行情日报\n\n| " + " | ".join(rows[0]) + " |\n| --- | --- | --- |\n"
    md += "\n".join("| " + " | ".join(r) + " |" for r in rows[1:])
    bot.send_mail(bot.build_docx(md), "quotes.docx", "行情日报", "见附件")
    return {"ok": True}
```

**D. 网页变更监控（和上次比）**

```python
import main as bot

def main_handler():
    html = bot.http_get("https://example.com/notice")
    old = bot._read_state("notice.txt") or ""
    if html == old:
        return {"ok": True, "msg": "无变化"}          # 没变就不发信
    bot._write_state("notice.txt", html)
    bot.send_mail(subject="页面有更新", body_text="https://example.com/notice 内容变了")
    return {"ok": True}
```

> `_read_state / _write_state` 读写仓库里的 `.state/` 目录，配合 workflow 里的保活提交，可以跨天记住"上次的样子"。

### ② 加 workflow

复制 `.github/workflows/weekly-example.yml`，只改三处：

```yaml
name: 你的任务名
on:
  workflow_dispatch:
  # schedule:
  #   - cron: '0 1 * * 1'          # ① 时间（UTC）
...
        run: python tasks/你的任务.py  # ② 脚本路径
```

### ③ 提交并验证

推上去 → Actions 手动跑一次 → 收到信 → 再取消 `schedule` 注释。Secrets 是仓库级的，所有任务共用，不用重配。

> 一个任务 = 一个脚本 + 一个 workflow。加第二个、第三个任务就是再复制一遍，互不影响。

---

## 六、可以直接调用的公用函数

`import main as bot` 之后：

| 函数 | 作用 |
| --- | --- |
| `http_get(url, timeout=25)` | GET 一个地址，自动带浏览器 UA、自动处理编码 |
| `http_post_json(url, payload, headers)` | POST JSON，已带浏览器 UA（Resend 这类前置 Cloudflare 的接口必须带） |
| `build_docx(md)` | Markdown → `.docx` 字节流（支持标题 / 列表 / 表格 / **加粗** / <u>下划线</u>） |
| `send_mail(docx_bytes, filename, subject, body_text, body_html=None)` | 发信。`docx_bytes` 传 `None` 就是纯文本/HTML 邮件；配了 Resend 走 API，否则走 SMTP |
| `now_bj()` | 北京时间（不依赖运行环境时区） |
| `_read_state(name)` / `_write_state(name, text)` | 读写 `.state/` 下的状态文件（做"变化对比"用） |

改 `main.py` 里这几个函数，会同时影响所有任务 —— 所以建议**先复制一份再改**，或只在 `tasks/` 里写自己的逻辑。

---

## 七、常见问题

**① `SMTPServerDisconnected` / `535 Authentication failed`**
GitHub 的机器在海外，QQ / 163 的 SMTP 经常直接切断连接。**改用 `RESEND_API_KEY`** 即可绕开（配了就优先走 Resend）。

**② Resend 返回 403（Cloudflare 1010）**
Resend 前置 Cloudflare，请求必须带浏览器 UA —— `http_post_json()` 已统一处理，自己手写 `urllib` 时要记得加。

**③ Resend 报 403 且提示 domain is not verified**
免费版只能用 `onboarding@resend.dev` 发信，且收件人必须是注册 Resend 的邮箱。

**④ 定时没跑**
依次检查：`schedule` 是否取消了注释 → 是否在默认分支上 → **连续 60 天没有提交，GitHub 会自动停用定时**（本仓库的 workflow 里带了保活提交，会自动写 `.state/last-run.txt`）。

**⑤ 想本地试跑**

```powershell
$env:MAIL_TO="you@example.com"; $env:RESEND_API_KEY="re_..."
$env:LLM_API_KEY="sk-..."      # 只有例 ① 需要
python main.py
python tasks/weekly_example.py
```

**⑥ 抓不到内容了**
十有八九是页面改版，正则/选择器失效。日志里会打印抓回的原始长度，先用 `http_get()` 把页面存下来看结构。

---

## 八、安全

- **密钥只放 GitHub Secrets**，不要写进代码、不要提交到仓库；Secrets 在网页上只显示名字，日志里会自动打码。
- Key 一旦进过提交历史，**改私有也不能撤销** —— 立刻去服务商后台吊销重建。
- 别人的仓库里没有你的 Secrets；fork 出去的是代码，不是密钥。
- 抓取请遵守目标站点的 `robots.txt` 与服务条款，别把频率设得比人工还高。

## 九、License

[MIT](LICENSE)
