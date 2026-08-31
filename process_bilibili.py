#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把八爪鱼(B站)采集、经人工筛选的价格行情视频，注入「鳜鱼鲈鱼价格看板.html」的
CROSSPLATFORM_LIVE_START / CROSSPLATFORM_LIVE_END 锚点区块。

用法：
  python3 process_bilibili.py            # 读取 bilibili_price_videos.json 并注入
  python3 process_bilibili.py --reset    # 还原为占位说明
"""
import json, html, re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, "bilibili_price_videos.json")
HTML_PATH = os.path.join(HERE, "鳜鱼鲈鱼价格看板.html")
START = "<!-- CROSSPLATFORM_LIVE_START -->"
END = "<!-- CROSSPLATFORM_LIVE_END -->"

PLACEHOLDER = '''      <div class="card" style="margin-bottom:18px;border-left:4px solid #7c3aed;background:#faf5ff">
        <h3>📡 跨平台社媒补充（快手 / 视频号 / B站）— 待八爪鱼采集</h3>
        <div class="csub">本区块将补充抖音之外的平台鳜鱼·鲈鱼价格讨论。待采集后注入。</div>
      </div>'''


def fmt(n):
    try:
        return f"{int(n):,}"
    except Exception:
        return str(n)


def build_html(data):
    meta = data.get("meta", {})
    videos = data.get("videos", [])
    crawled = meta.get("crawled_at", "")
    raw = meta.get("raw_rows", 0)
    sel = meta.get("selected_rows", len(videos))

    rows = []
    price_signals = []
    for v in videos:
        kw = v.get("keyword", "")
        tag_cls = "tag-gui" if "鳜" in kw else "tag-lu"
        kw_label = "鳜鱼" if "鳜" in kw else "鲈鱼"
        title = v.get("title", "")
        url = v.get("url", "#")
        author = v.get("author", "")
        play = fmt(v.get("play", 0))
        like = fmt(v.get("like", 0))
        comment = fmt(v.get("comment", 0))
        date = v.get("date", "")
        # 含具体价格数字(元/斤/块/钱)的，高亮为行情信号
        hl = ""
        if re.search(r"(\d+(\.\d+)?\s*(元|块)|元/斤|/斤|\d+\s*块|\d+\s*元)", title):
            hl = ' style="background:#fff7ed"'
            price_signals.append(f"《{title}》— {author}（{date}）")
        rows.append(
            f'          <tr{hl}>\n'
            f'            <td><span class="tag {tag_cls}">{kw_label}</span></td>\n'
            f'            <td><a href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(title)}</a></td>\n'
            f'            <td>{html.escape(author)}</td>\n'
            f'            <td>{play}</td>\n'
            f'            <td>{like}</td>\n'
            f'            <td>{comment}</td>\n'
            f'            <td>{html.escape(date)}</td>\n'
            f'          </tr>'
        )
    rows_html = "\n".join(rows)

    signals_html = ""
    if price_signals:
        items = "\n".join(f"              <li>{html.escape(s)}</li>" for s in price_signals[:8])
        signals_html = (
            '      <div class="callout" style="margin-top:12px">\n'
            '        <b>💡 视频中透出的价格信号（含具体报价）：</b>\n'
            '        <ul style="margin:6px 0 0;padding-left:20px;line-height:1.9">\n'
            f'{items}\n'
            '        </ul>\n'
            '      </div>'
        )

    return f'''      <div class="card" style="margin-bottom:18px;border-left:4px solid #7c3aed;background:#faf5ff">
        <h3>📡 跨平台社媒补充（B站）— 鳜鱼·鲈鱼价格相关视频</h3>
        <div class="csub">来源：八爪鱼云采集 <code>templateId=2886</code>（B站关键词搜索视频采集）。采集时间 <b>{html.escape(crawled)}</b>；关键词「鳜鱼价格」「鲈鱼价格」；原始 {raw} 条结果中筛出 <b>{sel} 条</b>与价格行情强相关（剔除纯路亚装备/做菜/魔方/手机等无关话题）。播放/点赞/评论为采集时点快照。<b>抖音侧</b>精确互动数据见上方「实时抓取数据」（TikHub）。</div>
        <table class="price-compare" style="margin-top:12px">
          <thead><tr><th>品种</th><th>视频标题</th><th>UP主</th><th>播放</th><th>点赞</th><th>评论</th><th>发布时间</th></tr></thead>
          <tbody>
{rows_html}
          </tbody>
        </table>{signals_html}
      </div>'''


def inject():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    frag = build_html(data)
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_text = f.read()
    if START not in html_text or END not in html_text:
        raise SystemExit("未找到 CROSSPLATFORM 锚点，注入中止")
    pat = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    new_text = pat.sub(START + "\n" + frag + "\n      " + END, html_text)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(new_text)
    print(f"[ok] 已注入 {len(data.get('videos', []))} 条 B站 价格行情视频")


def reset():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_text = f.read()
    pat = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    new_text = pat.sub(START + "\n" + PLACEHOLDER + "\n      " + END, html_text)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(new_text)
    print("[ok] 已还原为占位说明")


if __name__ == "__main__":
    if "--reset" in sys.argv:
        reset()
    else:
        inject()
