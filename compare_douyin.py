#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对照：本次 TikHub 重新抓取（近90天·按热度） vs 看板现有 13 条 TikHub 数据。
- 输出 90 天过滤后的结构化 CSV/JSON（8 字段，中文表头）
- 输出对照报告，核实「TikHub 是否缺粉丝量/点赞数」这一前提
"""
import json, re, csv, os
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "鳜鱼鲈鱼价格看板.html")
NEW = os.path.join(HERE, "douyin_90d_hot.json")

TODAY = datetime(2026, 8, 31)
CUTOFF = TODAY - timedelta(days=90)  # 近 90 天起点


def parse_int(s):
    if isinstance(s, (int, float)):
        return int(s)
    s = (s or "").replace(",", "").strip()
    try:
        return int(s)
    except Exception:
        return 0


# ---------- 1. 载入新抓取 ----------
new_all = json.load(open(NEW, encoding="utf-8"))
for p in new_all:
    try:
        p["_dt"] = datetime.strptime(p["date"], "%Y-%m-%d")
    except Exception:
        p["_dt"] = datetime(1900, 1, 1)
new_90 = [p for p in new_all if p["_dt"] >= CUTOFF]
new_90.sort(key=lambda x: x["_dt"], reverse=True)
print(f"[info] 新抓取总数={len(new_all)}，近90天={len(new_90)}")

# ---------- 2. 解析看板现有 13 条 ----------
html = open(HTML, encoding="utf-8").read()
m = re.search(r"<!-- DOUYIN_LIVE_START -->(.*?)<!-- DOUYIN_LIVE_END -->", html, re.S)
block = m.group(1) if m else ""
chunks = re.split(r'<div class="post">', block)[1:]
old = []
for c in chunks:
    seg = c.split("</div>\n      </div>")[0]
    def g(pat):
        mm = re.search(pat, seg)
        return mm.group(1).strip() if mm else ""
    old.append({
        "title": g(r'class="ptitle">.*?</span>\s*(.*?)</div>'),
        "author": g(r'class="author">([^<]*)<'),
        "fans": g(r'class="fans">粉丝 ([^<]*)<'),
        "date": g(r'class="pdate">📅 ([0-9-]+)'),
        "digg": g(r'👍 <b>([^<]*)</b>'),
        "comment": g(r'💬 <b>([^<]*)</b>'),
        "share": g(r'🔁 <b>([^<]*)</b>'),
        "collect": g(r'⭐ <b>([^<]*)</b>'),
    })
print(f"[info] 看板现有 TikTok 帖子解析出 {len(old)} 条")

# ---------- 3. 对照 ----------
old_titles = {re.sub(r"\s+", "", o["title"]) for o in old}
overlap, fresh = [], []
for p in new_90:
    norm = re.sub(r"\s+", "", p["title"])
    (overlap if norm in old_titles else fresh).append(p)

# 旧数据粉丝量是否缺失
old_fans_missing = sum(1 for o in old if o["fans"] in ("", "—", "-"))
print(f"[info] 旧13条中 粉丝量缺失(空/—) 的条数={old_fans_missing}")

# ---------- 4. 输出 90 天 CSV/JSON（8 字段，中文表头） ----------
fields = [
    ("视频标题", "title"), ("发布账号", "author"), ("粉丝量", "fans"),
    ("发布日期", "date"), ("点赞数", "digg"), ("评论数", "comment"),
    ("分享数", "share"), ("收藏数", "collect"), ("关键词", "keyword"),
    ("链接", "url"),
]
out_rows = []
for p in new_90:
    out_rows.append({
        "视频标题": p["title"], "发布账号": p["author"], "粉丝量": p["fans"],
        "发布日期": p["date"], "点赞数": parse_int(p["digg"]), "评论数": parse_int(p["comment"]),
        "分享数": parse_int(p["share"]), "收藏数": parse_int(p["collect"]),
        "关键词": p["keyword"], "链接": p["url"],
    })

with open(os.path.join(HERE, "douyin_90d.json"), "w", encoding="utf-8") as f:
    json.dump(out_rows, f, ensure_ascii=False, indent=2)
with open(os.path.join(HERE, "douyin_90d.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=[k for k, _ in fields])
    w.writeheader()
    for r in out_rows:
        w.writerow(r)
print(f"[ok] 已写出 douyin_90d.csv / douyin_90d.json（{len(out_rows)} 条近90天）")

# ---------- 5. 对照报告 ----------
lines = []
lines.append("# 抖音数据对照报告（TikHub 重新抓取 vs 看板现有）\n")
lines.append(f"- 抓取时间：2026-08-31｜窗口：近 90 天（≥ {CUTOFF.date()}）｜排序：按热度（最多点赞）")
lines.append(f"- 新抓取总数 **{len(new_all)}** 条，其中近 90 天 **{len(new_90)}** 条")
lines.append(f"- 看板现有 TikHub 帖子 **{len(old)}** 条（08-31 注入，历史标签为「08-18 快照」）\n")
lines.append("## 关键前提核实：TikHub 是否缺「粉丝量 / 点赞数」？\n")
if old_fans_missing == 0:
    lines.append(f"**结论：TikHub 并不缺这些字段。** 看板现有 13 条里，粉丝量字段全部有值（0 条缺失）。"
                 "本次重新抓取同样返回了 粉丝量/点赞/评论/分享/收藏。因此「补充 TikHub 没有的粉丝量/点赞数」"
                 "这一前提不成立——数据字段本身已完整，本次重跑的价值在于**刷新时间窗（收紧到近90天）与按热度重排**，而非补字段。\n")
else:
    lines.append(f"**注意：** 看板现有 13 条中有 **{old_fans_missing}** 条粉丝量为空/「—」，而本次新抓取已补全粉丝量——这正是对旧数据的有效补充。\n")
lines.append("## 近 90 天新数据 vs 看板现有：重叠与新发现\n")
lines.append(f"- 与看板现有帖子**重叠（标题相同）**：**{len(overlap)}** 条")
lines.append(f"- 看板**没有的新帖（近90天）**：**{len(fresh)}** 条\n")
if fresh:
    lines.append("### 看板没有、本次新出现的近90天帖子\n")
    lines.append("| 视频标题 | 账号 | 粉丝量 | 日期 | 点赞 | 评论 | 分享 | 收藏 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for p in fresh:
        lines.append(f"| {p['title'][:40]} | {p['author']} | {p['fans']} | {p['date']} | {parse_int(p['digg']):,} | {parse_int(p['comment']):,} | {parse_int(p['share']):,} | {parse_int(p['collect']):,} |")
lines.append("\n## 近 90 天完整清单（已导出 CSV/JSON）\n")
lines.append("| # | 视频标题 | 账号 | 粉丝量 | 日期 | 点赞 | 评论 | 分享 | 收藏 |")
lines.append("|---|---|---|---|---|---|---|---|---|")
for i, p in enumerate(new_90, 1):
    lines.append(f"| {i} | {p['title'][:38]} | {p['author']} | {p['fans']} | {p['date']} | {parse_int(p['digg']):,} | {parse_int(p['comment']):,} | {parse_int(p['share']):,} | {parse_int(p['collect']):,} |")
open(os.path.join(HERE, "douyin_compare.md"), "w", encoding="utf-8").write("\n".join(lines))
print("[ok] 已写出 douyin_compare.md")
print("OVERLAP", len(overlap), "FRESH", len(fresh), "OLD_FANS_MISSING", old_fans_missing)
