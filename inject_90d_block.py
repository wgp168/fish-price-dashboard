#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将 douyin_90d.json（近90天+按热度）注入看板一个新区块。
插入位置：在 <!-- DOUYIN_LIVE_END --> 之后、<!-- CROSSPLATFORM_LIVE_START --> 之前。
不触碰 08-18 快照、不触碰现有 08-31 13条实时区块。
可重复执行：若已存在 <!-- DOUYIN_90D_START --> 区块则先移除再注入。
"""
import json, os, re
from dashboard_version import DASHBOARD_VERSION, DASHBOARD_VERSION_DATE

WS = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(WS, "鳜鱼鲈鱼价格看板.html")
JSON = os.path.join(WS, "douyin_90d.json")

A_START = "<!-- DOUYIN_90D_START -->"
A_END = "<!-- DOUYIN_90D_END -->"
LIVE_END = "<!-- DOUYIN_LIVE_END -->"
XP_START = "<!-- CROSSPLATFORM_LIVE_START -->"

# CLI 提示：版本号需要手动 bump，本脚本不自动升版本
# python dashboard_version.py --reason "注入抖音近90天热帖新增8条" --level patch


def fmt(n):
    try:
        return f"{int(n):,}"
    except Exception:
        return str(n)


def build_post(p):
    kw = p.get("关键词", "")
    is_gui = "鳜鱼" in kw
    tagcls = "tag-gui" if is_gui else "tag-lu"
    tagtxt = "鳜鱼" if is_gui else "鲈鱼"
    title = p["视频标题"].replace("\n", " ").replace("\r", " ").strip()
    return f'''      <div class="post">
        <div class="ptop">
          <div class="avatar">{p['发布账号'][0]}</div>
          <div><div class="author">{p['发布账号']}</div><div class="fans">粉丝 {p['粉丝量']}</div></div>
          <span class="platform">抖音</span>
        </div>
        <div class="ptitle"><span class="tag {tagcls}">{tagtxt}</span> {title}</div>
        <div class="pdate">📅 {p['发布日期']} <span class="pill">近90天</span></div>
        <div class="stats">
          <span class="stat">👍 <b>{fmt(p['点赞数'])}</b></span><span class="stat">💬 <b>{fmt(p['评论数'])}</b></span><span class="stat">🔁 <b>{fmt(p['分享数'])}</b></span><span class="stat">⭐ <b>{fmt(p['收藏数'])}</b></span>
        </div>
        <a class="plink" href="{p['链接']}" target="_blank">🔗 {p['链接']}</a>
      </div>'''


def build_block(data):
    posts = "\n".join(build_post(p) for p in data)
    return f'''      {A_START}
      <div class="card" style="margin:18px 0;border-left:4px solid #0ea5e9;background:#f0f9ff">
        <h3>🔥 抖音近90天热帖（2026-08-31 二次抓取 · 按热度排序）</h3>
        <div class="csub">数据源：TikHub(抖音搜索) · 关键词「鳜鱼价格」「鲈鱼价格」· 时间窗 近90天（≥2026-06-02）· 按点赞量排序 · 共 <b>{len(data)}</b> 条。本区块为第二次专项重抓，<b>独立于</b>上方 08-31 的 13 条实时数据，亦不替换 08-18 历史快照，仅作近90天热度视角补充。互动数据为抓取时点快照。</div>
        <div class="posts">
{posts}
        </div>
      </div>
      {A_END}'''


def main():
    data = json.load(open(JSON, encoding="utf-8"))
    html = open(HTML, encoding="utf-8").read()

    if A_START in html:
        html = re.sub(re.escape(A_START) + r".*?" + re.escape(A_END) + r"\n?", "", html, flags=re.S)

    block = build_block(data)

    if LIVE_END not in html or XP_START not in html:
        raise SystemExit("ERROR: 关键锚点 DOUYIN_LIVE_END / CROSSPLATFORM_LIVE_START 缺失，中止以免破坏结构")

    idx_end = html.index(LIVE_END) + len(LIVE_END)
    html = html[:idx_end] + "\n" + block + "\n\n" + html[idx_end:]

    open(HTML, "w", encoding="utf-8").write(html)

    # 校验
    assert LIVE_END in html and XP_START in html
    print(f"注入完成：{len(data)} 条 · 锚点 DOUYIN_90D_START/END 已写入")
    print("08-18 快照标签存在:", "08-18" in html)
    print("原 13 条实时区块存在:", "共 13 条" in html)

    # 刷新 Hero 区「看板更新」时间戳
    try:
        from dashboard_version import stamp_updated_at
        print(f"[OK] 看板更新时间戳已刷新：{stamp_updated_at()}")
    except Exception as e:
        print(f"[WARN] 看板更新时间戳刷新失败（不影响看板）：{e}")


if __name__ == "__main__":
    main()
