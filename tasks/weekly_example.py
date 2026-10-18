# -*- coding: utf-8 -*-
"""示例任务 ②：每周一早上，把 China Daily 文化频道的最新 5 条标题发到邮箱。

这个文件的作用是**演示"如何新增一个推送任务"**：
  · 复用 main.py 里的公用函数（抓网页 / 建 Word / 发邮件）
  · 复制本文件 → 改 fetch() 里的抓取逻辑 → 就是你的新任务
  · 再复制 .github/workflows/weekly-example.yml → 改 cron 与脚本路径

本地试跑（不会发信时可先把 send_mail 注释掉）：
    $env:MAIL_TO="you@example.com"
    $env:RESEND_API_KEY="re_..."
    python tasks/weekly_example.py
"""
import os
import re
import sys
from html import unescape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))       # 让 `import main` 能找到仓库根目录

import main as bot                              # 复用：http_get / build_docx / send_mail / now_bj

PAGE = "https://www.chinadaily.com.cn/culture"
LINK = re.compile(
    r'<a\b[^>]*?href="((?:https?:)?//[^"]*?/a/(\d{6})/(\d{2})/(WS[0-9a-f]+)\.html)"[^>]*>(.*?)</a>',
    re.S | re.I)


def fetch():
    """抓取页面 → 返回 [(日期, 标题, 链接), ...]，最多 5 条。"""
    html = bot.http_get(PAGE)
    items, seen = [], set()
    for m in LINK.finditer(html):
        url = m.group(1)
        if url.startswith("//"):
            url = "https:" + url
        if url in seen:
            continue
        title = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", m.group(5)))).strip()
        if len(title) < 8:
            continue
        seen.add(url)
        items.append((m.group(2) + m.group(3), title, url))
    items.sort(reverse=True)                    # 日期倒序，取最新的
    return items[:5]


def build():
    """生成 Markdown 与 .docx（复用 main.py 的 Word 渲染器）。"""
    items = fetch()
    if not items:
        raise RuntimeError("没有抓到文章，可能是页面结构变了")

    lines = ["# China Daily 文化版 · 本周速览", "",
             "> 生成时间：%s" % bot.now_bj().strftime("%Y-%m-%d %H:%M"), ""]
    for i, (d, t, u) in enumerate(items, 1):
        lines.append("%d. **%s**" % (i, t))
        lines.append("   - 发布日期：%s-%s-%s" % (d[:4], d[4:6], d[6:]))
        lines.append("   - 链接：%s" % u)
        lines.append("")
    md = "\n".join(lines)
    return md, bot.build_docx(md)


def main_handler(event=None, context=None):
    try:
        md, docx = build()
        today = bot.now_bj().strftime("%Y-%m-%d")
        fname = "ChinaDaily_Culture_Weekly_%s.docx" % today
        subject = "China Daily 文化版 · 本周速览（%s）" % today
        body = "本周文化版 %d 条要闻见附件（Word）。" % 5
        bot.send_mail(docx, fname, subject, body)
        return {"ok": True, "file": fname}
    except Exception as e:
        import traceback
        return {"ok": False, "error": repr(e),
                "trace": traceback.format_exc()[-1200:]}


if __name__ == "__main__":
    import json
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _res = main_handler()
    print(json.dumps(_res, ensure_ascii=False))
    sys.exit(0 if _res.get("ok") else 1)
