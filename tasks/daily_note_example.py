# -*- coding: utf-8 -*-
"""示例任务 ③：每天一封纯邮件（不带附件）。

演示两件事：
  1. send_mail() 的 docx_bytes 传 None → 只发文本 + HTML，不做 Word 附件；
  2. 不联网也能当一个"定时提醒"任务用（到点发信）。

改法：把 REMINDERS 换成你自己的清单（生日、账单、体检、证书到期…），
     或把 get_items() 换成读你的 CSV / 调你的 API。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import main as bot

# 日程：日期 → 事项列表（留空就发一条"今日无安排"）
REMINDERS = {
    "10-20": ["周三 14:00 项目评审", "提交报销单"],
    "10-25": ["信用卡还款日"],
    "11-01": ["房租 / 水电"],
}


def get_items():
    today = bot.now_bj()
    key = today.strftime("%m-%d")
    return today, REMINDERS.get(key, [])


def build_text(today, items):
    head = "【%s】今日提醒" % today.strftime("%Y-%m-%d")
    if not items:
        return head, "今天没有安排。"
    return head, "\n".join("· " + x for x in items)


def build_html(today, items):
    rows = "".join("<li>%s</li>" % x for x in items) or "<li>今天没有安排。</li>"
    return (
        "<div style=\"font-family:-apple-system,'Microsoft YaHei',sans-serif;"
        "font-size:15px;line-height:1.7;color:#222\">"
        "<h2 style=\"margin:0 0 12px\">%s</h2>"
        "<ul style=\"padding-left:20px;margin:0\">%s</ul>"
        "<p style=\"color:#888;font-size:12px;margin-top:18px\">由 auto-push-hub 自动发送</p>"
        "</div>" % (today.strftime("%Y-%m-%d"), rows)
    )


def main_handler(event=None, context=None):
    try:
        today, items = get_items()
        subject, text = build_text(today, items)
        bot.send_mail(subject=subject, body_text=text, body_html=build_html(today, items))
        return {"ok": True, "items": len(items)}
    except Exception as e:
        import traceback
        return {"ok": False, "error": repr(e), "trace": traceback.format_exc()[-1200:]}


if __name__ == "__main__":
    import json
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _res = main_handler()
    print(json.dumps(_res, ensure_ascii=False))
    sys.exit(0 if _res.get("ok") else 1)
