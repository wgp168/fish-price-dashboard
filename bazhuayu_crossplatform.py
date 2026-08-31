#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bazhuayu_crossplatform.py
=====================================================================
用「八爪鱼（bazhuayu）」云采集补充抖音之外的短视频/视频平台
（快手 / 微信视频号 / B站）鳜鱼·鲈鱼价格讨论，归一化后注入看板。

数据流（由 WorkBuddy 驱动八爪鱼 MCP 工具，本脚本负责后段）：
  1) search_templates  → 语义搜索三平台模板（见 PLATFORM_QUERIES）
  2) execute_task      → 启动云采集，带唯一 taskName
  3) get_task_status   → 轮询至 completed
  4) export_data       → 导出 JSON（含 title/author/likes/comments/...）
  5) 本脚本 normalize_and_inject(导出JSON, platform) → 注入看板锚点区块

八爪鱼各平台导出字段名不统一，normalize 用「候选键列表」做容错映射，
缺失字段显示「—」。最终只保留能映射到标准字段的帖子。

=====================================================================
用法
=====================================================================
  # 预览渲染效果（合成数据，不碰看板）
  python3 bazhuayu_crossplatform.py --demo

  # 把 export_data 得到的 JSON 文件归一化并注入看板
  python3 bazhuayu_crossplatform.py --platform kuaishou \
      --json kuaishou_export.json --inject

  # 还原锚点区块为占位（移除 demo/历史注入）
  python3 bazhuayu_crossplatform.py --reset
=====================================================================
"""

import json
import os
import re
import sys
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(HERE, "鳜鱼鲈鱼价格看板.html")
ANCHOR_START = "<!-- CROSSPLATFORM_LIVE_START -->"
ANCHOR_END = "<!-- CROSSPLATFORM_LIVE_END -->"

# 三平台的 search_templates 语义查询词（供驱动八爪鱼时直接复用）
PLATFORM_QUERIES = {
    "kuaishou": "快手 鳜鱼价格 鲈鱼价格 视频 点赞 评论 发布时间",
    "shipinhao": "微信视频号 鳜鱼价格 鲈鱼价格 视频 点赞 评论",
    "bilibili": "bilibili B站 鳜鱼 鲈鱼 价格 视频 播放 弹幕",
}
PLATFORM_LABEL = {
    "kuaishou": "快手",
    "shipinhao": "微信视频号",
    "bilibili": "B站",
}

# 标准字段 → 各平台可能的原始键名（容错映射）
FIELD_MAP = {
    "title": ["title", "desc", "content", "text", "标题", "内容", "视频标题"],
    "author": ["author", "nickname", "user_name", "author_name", "昵称", "作者", "发布者"],
    "likes": ["likes", "digg_count", "like_count", "praise_count", "点赞", "点赞数"],
    "comments": ["comments", "comment_count", "reply_count", "评论", "评论数"],
    "shares": ["shares", "share_count", "forward_count", "分享", "转发数"],
    "plays": ["plays", "play_count", "view_count", "read_count", "播放", "播放量", "阅读"],
    "publish_time": ["publish_time", "publishTime", "create_time", "release_time", "发布时间", "时间"],
    "url": ["url", "share_url", "video_url", "link", "链接", "视频链接"],
}


def _pick(d, keys):
    """从 dict 中按候选键取第一个非空值"""
    for k in keys:
        if k in d and d[k] not in (None, "", "null"):
            return d[k]
    return None


def _fmt_num(v):
    try:
        f = float(v)
        if f == int(f):
            return f"{int(f):,}"
        return f"{f:,.1f}"
    except Exception:
        return str(v) if v is not None else "—"


def normalize(raw_items, platform):
    """把八爪鱼导出的原始条目列表归一化为标准帖子字典"""
    out = []
    for it in raw_items or []:
        # 八爪鱼导出的条目可能是嵌套 dict（data 字段）或扁平 dict
        item = it.get("data", it) if isinstance(it, dict) else it
        if not isinstance(item, dict):
            continue
        post = {k: _pick(item, ks) for k, ks in FIELD_MAP.items()}
        if not post.get("title") and not post.get("author"):
            continue  # 过滤空行
        out.append(post)
    return out


def render_block(posts, platform):
    label = PLATFORM_LABEL.get(platform, platform)
    now = "2026-08-31"
    rows = []
    for p in posts:
        title = p.get("title") or "—"
        author = p.get("author") or "—"
        likes = _fmt_num(p.get("likes")) if p.get("likes") is not None else "—"
        comments = _fmt_num(p.get("comments")) if p.get("comments") is not None else "—"
        shares = _fmt_num(p.get("shares")) if p.get("shares") is not None else "—"
        plays = _fmt_num(p.get("plays")) if p.get("plays") is not None else "—"
        ptime = p.get("publish_time") or "—"
        url = p.get("url")
        link = f'<a href="{url}" target="_blank" rel="noopener">链接</a>' if url else "—"
        rows.append(f"""
        <div class="post" style="border-left:3px solid #7c3aed;padding:8px 12px;margin:8px 0;background:#fff;border-radius:6px">
          <div class="pt" style="font-weight:600;color:#1e293b">[{label}] {title}</div>
          <div class="pm" style="color:#64748b;font-size:12px;margin-top:3px">
            作者：{author} ｜ 点赞 {likes} ｜ 评论 {comments} ｜ 转发 {shares} ｜ 播放 {plays} ｜ 时间 {ptime} ｜ {link}
          </div>
        </div>""")
    body = "\n".join(rows) if rows else '<div class="csub">本次采集无有效条目。</div>'
    return f"""      <div class="card" style="margin-bottom:18px;border-left:4px solid #7c3aed;background:#faf5ff">
        <h3>📡 跨平台社媒补充 — {label}（八爪鱼采集 · {now}）</h3>
        <div class="csub">数据源：八爪鱼云采集（{label}）。字段因平台而异，缺失显示「—」。抖音侧精确互动数据见上方「实时抓取数据」区块。</div>
{body}
      </div>"""


def inject_html(block_html):
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()
    pat = re.compile(re.escape(ANCHOR_START) + r".*?" + re.escape(ANCHOR_END), re.S)
    if not pat.search(html):
        raise RuntimeError("未找到跨平台注入锚点")
    new_block = f"{ANCHOR_START}\n{block_html}\n      {ANCHOR_END}"
    html = pat.sub(new_block, html, count=1)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)


def placeholder_html():
    return """      <div class="card" style="margin-bottom:18px;border-left:4px solid #7c3aed;background:#faf5ff">
        <h3>📡 跨平台社媒补充（快手 / 视频号 / B站）— 待八爪鱼采集</h3>
        <div class="csub">本区块将由 <b>八爪鱼（bazhuayu）</b> 云采集补充抖音之外的短视频/视频平台鳜鱼·鲈鱼价格讨论（快手、微信视频号、B站）。抖音侧精确互动数据已由 TikHub 抓取（见上方「实时抓取数据」）。八爪鱼连接器已连接，待用户断开重连使其 MCP 工具加载进会话后，由 <code>bazhuayu_crossplatform.py</code> 执行 <code>search_templates → execute_task → export_data</code> 并注入本区块。</div>
      </div>"""


def demo_posts(platform):
    base = [
        {"title": f"{PLATFORM_LABEL.get(platform, platform)}上鳜鱼价格又涨了？", "author": "水产老陈",
         "likes": 5200, "comments": 312, "shares": 88, "plays": 120000, "publish_time": "2026-08-28", "url": "https://example.com/demo1"},
        {"title": "加州鲈跌破10元，养殖户该怎么办", "author": "渔易通",
         "likes": 3100, "comments": 205, "shares": 40, "plays": 88000, "publish_time": "2026-08-27", "url": "https://example.com/demo2"},
    ]
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--platform", choices=list(PLATFORM_QUERIES.keys()),
                    help="平台：kuaishou / shipinhao / bilibili")
    ap.add_argument("--json", help="八爪鱼 export_data 导出的 JSON 文件路径")
    ap.add_argument("--inject", action="store_true", help="把归一化结果注入看板锚点区块")
    ap.add_argument("--demo", action="store_true", help="用合成数据预览渲染效果（不碰看板）")
    ap.add_argument("--reset", action="store_true", help="还原锚点区块为占位")
    args = ap.parse_args()

    if args.reset:
        inject_html(placeholder_html())
        print("[reset] 已还原为占位区块")
        return

    if args.demo:
        for plat in PLATFORM_QUERIES:
            blk = render_block(demo_posts(plat), plat)
            print(f"\n===== {PLATFORM_LABEL[plat]} 预览 =====")
            print(blk[:400] + " ...")
        print("\n[demo] 以上为渲染预览，未写入看板。真实注入请用 --platform <p> --json <file> --inject")
        return

    if not args.inject:
        ap.print_help()
        return

    if not args.platform or not args.json:
        print("[error] --inject 需要同时指定 --platform 与 --json")
        return

    with open(args.json, "r", encoding="utf-8") as f:
        raw = json.load(f)
    # 兼容多种导出形态：列表 / {"data":[...]} / {"items":[...]}
    if isinstance(raw, dict):
        items = raw.get("data") or raw.get("items") or raw.get("rows") or []
    else:
        items = raw
    posts = normalize(items, args.platform)
    block = render_block(posts, args.platform)
    inject_html(block)
    print(f"[inject] 已注入 {len(posts)} 条 {PLATFORM_LABEL[args.platform]} 数据到看板跨平台区块")


if __name__ == "__main__":
    main()
