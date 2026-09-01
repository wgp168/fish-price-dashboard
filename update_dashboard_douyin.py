# -*- coding: utf-8 -*-
"""用 AgentKey(TikHub) 实时抓取的抖音代表性帖子替换看板占位块。

CLI 提示：版本号需要手动 bump，本脚本不自动升版本：
    python dashboard_version.py --reason "抖音13条实时更新" --level patch
"""
import os
from dashboard_version import DASHBOARD_VERSION, DASHBOARD_VERSION_DATE

HTML = "鳜鱼鲈鱼价格看板.html"

# 8 条真实帖子（关键词「鳜鱼价格」「鲈鱼价格」，按点赞排序，近6个月）
# 字段: aweme_id, date, author, fans, desc(clean), digg, cmt, share, collect, tag
posts = [
    ("7651636236453470436", "2026-06-15", "奇妙大百科", 137750,
     "科普分享26种溪流鱼以及价格，你都吃过哪几种", 17627, 724, 12181, 15169, "gui"),
    ("7626228712442219816", "2026-04-08", "舟小九", 1189282,
     "安徽黄山土菜刺客，巴掌大的小鳜鱼268一斤", 12288, 342, 501, 1152, "gui"),
    ("7672969539180777843", "2026-08-12", "在路上的番茄", 1109880,
     "为什么东北的鳌花鱼，比南方的鳜鱼价格贵了那么多？", 7468, 3556, 1779, 1145, "gui"),
    ("7670096463246202496", "2026-08-04", "刘氏水产", 7159,
     "这两天鳜鱼突然断货，导致鳜鱼一下子卖到50多一斤！", 838, 149, 233, 76, "gui"),
    ("7643800190746496292", "2026-05-25", "一吃一大碗", 164193,
     "鲈鱼生蚝豆腐煲，家常吃法惊艳味蕾！", 90833, 1335, 74996, 87495, "lu"),
    ("7664540823509372179", "2026-07-20", "平凡的菜", 292829,
     "广东家常菜｜紫苏鲈鱼煲！鱼肉紧实鲜嫩", 12811, 221, 12560, 14074, "lu"),
    ("7630707734479998242", "2026-04-20", "大师兄下厨房", 460158,
     "清蒸鲈鱼来喽～手把手教学", 5152, 214, 894, 2674, "lu"),
    ("7654590277932010467", "2026-06-23", "🐟渔你同行🐟", 893,
     "三农·鮰鱼·水产养殖·鳜鱼·罗非鱼", 99, 9, 6, 22, "lu"),
]


def fmt_fans(n):
    if n >= 10000:
        return f"{n/10000:.1f}万"
    return str(n)


def build_posts():
    out = ['    <div class="posts">']
    for aweme_id, date, author, fans, desc, digg, cmt, share, collect, tag in posts:
        av = author[0]
        tagcls = "tag tag-gui" if tag == "gui" else "tag tag-lu"
        tagtxt = "鳜鱼" if tag == "gui" else "鲈鱼"
        out.append(f'''      <div class="post">
        <div class="ptop">
          <div class="avatar">{av}</div>
          <div><div class="author">{author}</div><div class="fans">粉丝 {fmt_fans(fans)}</div></div>
          <span class="platform">抖音</span>
        </div>
        <div class="ptitle"><span class="{tagcls}">{tagtxt}</span> {desc}</div>
        <div class="pdate">📅 {date} <span class="pill">AgentKey实时</span></div>
        <div class="stats">
          <span class="stat">👍 <b>{digg:,}</b></span><span class="stat">💬 <b>{cmt:,}</b></span><span class="stat">🔁 <b>{share:,}</b></span><span class="stat">⭐ <b>{collect:,}</b></span>
        </div>
        <a class="plink" href="https://www.iesdouyin.com/share/video/{aweme_id}" target="_blank">🔗 iesdouyin.com/share/video/{aweme_id}</a>
      </div>''')
    out.append("    </div>")
    return "\n".join(out)


def main():
    with open(HTML, encoding="utf-8") as f:
        s = f.read()

    # 1) note 标记
    old_note = '<span class="note">本轮未用 AgentKey 抓抖音</span>'
    new_note = '<span class="note">2026-08-18 由 AgentKey（TikHub）实时抓取</span>'
    assert old_note in s, "note 标记未找到"
    s = s.replace(old_note, new_note, 1)

    # 2) 占位说明 callout（无嵌套div，找下一个 </div>）
    marker = '<div class="callout" style="margin-bottom:18px"><b>关于抖音帖子的说明：'
    i = s.find(marker)
    assert i != -1, "抖音说明 callout 未找到"
    j = s.find("</div>", i) + len("</div>")
    new_callout = ('<div class="callout" style="margin-bottom:18px"><b>关于抖音帖子的说明：</b>'
                   '本版看板中的抖音代表性帖子（含点赞/评论/分享/收藏等互动数据）由 <b>AgentKey（TikHub）</b> 于 '
                   '<b>2026-08-18</b> 实时抓取。检索关键词为「鳜鱼价格」「鲈鱼价格」，按点赞量排序、覆盖近 6 个月。'
                   '如实反映抖音生态：<b>鳜鱼</b>侧高互动帖子以行情/科普/地方价为主，<b>鲈鱼</b>侧高互动帖子以家常烹饪为主、纯行情类偏少。'
                   '互动数据为抓取时点快照，非实时滚动值。</div>')
    s = s[:i] + new_callout + s[j:]

    # 3) posts 区块：用 div 括号计数定位 .posts 闭合
    pstart = s.find('<div class="posts">')
    assert pstart != -1, "posts 区块未找到"
    # 从 pstart 起数 <div 与 </div>
    k = pstart
    depth = 0
    while k < len(s):
        op = s.find("<div", k)
        cl = s.find("</div>", k)
        if cl == -1:
            break
        if op != -1 and op < cl:
            depth += 1
            k = op + 4
        else:
            depth -= 1
            k = cl + 6
            if depth == 0:
                pend = k
                break
    assert depth == 0, "posts 括号未平衡"
    s = s[:pstart] + build_posts() + s[pend:]

    with open(HTML, "w", encoding="utf-8") as f:
        f.write(s)
    print("OK: 抖音板块已用 AgentKey 实时数据替换，共", len(posts), "条帖子")


if __name__ == "__main__":
    main()
