#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把看板从 2026-08-13 更新到 2026-08-18：
- 新批发价：moa_fish_crawler.py 2026-08-18 当日快照
    · 活鳜鱼 凌家塘 78（较 8/13 的 86 回落 8，回到 7/27 水平）
    · 鲈鱼各市场小幅变动（马鞍山20 / 云南华潮35 / 青岛36 / 北京大洋路31 / 山东滨州26 等）
- 同步更新 KPI、批发价表格/说明、来源卡片、数据局限天数、footer、标题与周期芯片
（塘头价仍引 水产前沿 第28期 8/11；公开价源爬虫与科学养鱼 OCR 板块沿用，未变）
"""
import os

HTML = os.path.join(os.path.dirname(__file__), "鳜鱼鲈鱼价格看板.html")
html = open(HTML, encoding="utf-8").read()


def rep(old, new, label):
    global html
    assert old in html, f"未找到替换锚点：{label}\n--- 缺失片段 ---\n{old[:120]}"
    html = html.replace(old, new, 1)
    print(f"✅ {label}")


# 1) 标题
rep(
    "<title>江浙沪皖 鳜鱼·鲈鱼 出塘价与批发价数据看板（2026-08-13 更新）</title>",
    "<title>江浙沪皖 鳜鱼·鲈鱼 出塘价与批发价数据看板（2026-08-18 更新）</title>",
    "标题",
)

# 2) 周期与芯片
rep(
    '<span class="chip">📅 统计周期：2026-07-13 ~ 2026-08-13</span>',
    '<span class="chip">📅 统计周期：2026-07-13 ~ 2026-08-18</span>',
    "周期芯片",
)
rep(
    '<span class="chip">🤖 批发价：农业农村部接口爬虫（2026-08-13）+ 公开价源爬虫 + 科学养鱼OCR（07-27）</span>',
    '<span class="chip">🤖 批发价：农业农村部接口爬虫（2026-08-18）+ 公开价源爬虫 + 科学养鱼OCR（07-27）</span>',
    "批发价芯片",
)

# 3) KPI：鳜鱼批发价 86→78
rep(
    '江苏 鳜鱼 批发价（爬虫 8/13）',
    '江苏 鳜鱼 批发价（爬虫 8/18）',
    "KPI-鳜鱼批发价标签",
)
rep(
    '      <div class="val">86 <small>元/公斤</small></div>\n      <div class="trend t-down">▼ 较7/30的96回落10</div>',
    '      <div class="val">78 <small>元/公斤</small></div>\n      <div class="trend t-down">▼ 较8/13的86回落8</div>',
    "KPI-鳜鱼批发价数值",
)

# 4) 鳜鱼批发价板块（h3 / 凌家塘行 / 九江行 / 说明）
rep(
    '<h3><span class="tag tag-gui">鳜鱼</span> 批发价（农业农村部接口爬虫 · 2026-08-13）</h3>',
    '<h3><span class="tag tag-gui">鳜鱼</span> 批发价（农业农村部接口爬虫 · 2026-08-18）</h3>',
    "鳜鱼批发价-h3",
)
rep(
    '<td>江苏 凌家塘市场</td><td><span class="spec spec-l">活鳜鱼 统货</span></td><td class="price">86 <small>元/公斤</small></td><td>≈ 43</td>',
    '<td>江苏 凌家塘市场</td><td><span class="spec spec-l">活鳜鱼 统货</span></td><td class="price">78 <small>元/公斤</small></td><td>≈ 39</td>',
    "鳜鱼批发价-凌家塘行",
)
rep(
    '<td>江西 九江琵琶湖</td><td><span class="spec">活鳜鱼</span></td><td class="price">60 <small>元/公斤</small></td><td>≈ 30</td>',
    '<td>江西 九江琵琶湖</td><td><span class="spec">活鳜鱼</span></td><td class="price">62 <small>元/公斤</small></td><td>≈ 31</td>',
    "鳜鱼批发价-九江行",
)
rep(
    '<b>抓取日期 2026-08-13</b>。江苏凌家塘活鳜鱼 <b>86 元/公斤</b>，较 7/30 的 96 回落 10、较 7/27 的 78 仍高 8，与水产前沿 8/11 周报「新鱼上市、暴涨势头被遏制」趋势吻合；流通加价约 14–22 元/公斤（塘头价 39–43 元/斤≈78–86 元/公斤）。',
    '<b>抓取日期 2026-08-18</b>。江苏凌家塘活鳜鱼 <b>78 元/公斤</b>，较 8/13 的 86 继续回落 8、回到 7/27 水平，与水产前沿 8/11 周报「新鱼上市、暴涨势头被遏制」趋势延续一致；流通加价约 0–15 元/公斤（塘头价 39–43 元/斤≈78–86 元/公斤）。',
    "鳜鱼批发价-数据说明",
)

# 5) 鲈鱼批发价板块（h3 / 变动行 / 说明）
rep(
    '<h3><span class="tag tag-lu">鲈鱼</span> 批发价（农业农村部接口爬虫 · 2026-08-13）</h3>',
    '<h3><span class="tag tag-lu">鲈鱼</span> 批发价（农业农村部接口爬虫 · 2026-08-18）</h3>',
    "鲈鱼批发价-h3",
)
rep(
    '<td>马鞍山 安民农贸</td><td><span class="spec spec-s">淡水鲈鱼</span></td><td class="price">22 <small>元/公斤</small></td><td>≈ 11</td>',
    '<td>马鞍山 安民农贸</td><td><span class="spec spec-s">淡水鲈鱼</span></td><td class="price">20 <small>元/公斤</small></td><td>≈ 10</td>',
    "鲈鱼批发价-马鞍山行",
)
rep(
    '<td>云南 华潮水产</td><td><span class="spec spec-s">淡水鲈鱼</span></td><td class="price">33 <small>元/公斤</small></td><td>≈ 16.5</td>',
    '<td>云南 华潮水产</td><td><span class="spec spec-s">淡水鲈鱼</span></td><td class="price">35 <small>元/公斤</small></td><td>≈ 17.5</td>',
    "鲈鱼批发价-云南华潮行",
)
rep(
    '<td>青岛 城阳水产</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">44 <small>元/公斤</small></td><td>≈ 22</td>',
    '<td>青岛 城阳水产</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">36 <small>元/公斤</small></td><td>≈ 18</td>',
    "鲈鱼批发价-青岛行",
)
rep(
    '<td>北京 大洋路市场</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">32 <small>元/公斤</small></td><td>≈ 16</td>',
    '<td>北京 大洋路市场</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">31 <small>元/公斤</small></td><td>≈ 15.5</td>',
    "鲈鱼批发价-北京大洋路行",
)
rep(
    '<td>山东滨州 鲁北蔬菜</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">25 <small>元/公斤</small></td><td>≈ 12.5</td>',
    '<td>山东滨州 鲁北蔬菜</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">26 <small>元/公斤</small></td><td>≈ 13</td>',
    "鲈鱼批发价-山东滨州行",
)
rep(
    '2026-08-13 爬虫实测：海水鲈鱼凌家塘 27 / 南环桥 23.5 / 合肥周谷堆 22.5（与 7 月持平），淡水鲈鱼马鞍山安民 22、云南华潮 33、长治紫坊 33 元/公斤；海水鲈鱼新增甘肃酒泉 59、宁夏四季鲜 38、重庆西三街 40、北京大洋路 32 等市场（均为统货、不分规格）。接口区分「淡水鲈鱼」与「海水鲈鱼」两个品种码。鲈鱼整体低位运行，与水产前沿 8/11 周报「外省产区稳中有跌」一致。',
    '2026-08-18 爬虫实测：海水鲈鱼凌家塘 27 / 南环桥 23.5 / 合肥周谷堆 22.5（与 7 月持平），淡水鲈鱼马鞍山安民 20（较 7/27 的 22 回落）、云南华潮 35、长治紫坊 33 元/公斤；海水鲈鱼青岛城阳 36（较 8/13 的 44 回落）、北京大洋路 31、山东滨州 26、甘肃酒泉 59 等市场（均为统货、不分规格）。接口区分「淡水鲈鱼」与「海水鲈鱼」两个品种码。鲈鱼整体低位运行，与水产前沿 8/11 周报「外省产区稳中有跌」一致。',
    "鲈鱼批发价-数据说明",
)

# 6) 来源卡片-MOA
rep(
    '<div class="sd">2026-08-13 · 活鳜鱼凌家塘86元/公斤（较7/30的96回落）；海水鲈鱼凌家塘27/南环桥23.5/合肥周谷堆22.5、淡水鲈鱼马鞍山22/云南华潮33/长治33元/公斤</div>',
    '<div class="sd">2026-08-18 · 活鳜鱼凌家塘78元/公斤（较8/13的86回落）；海水鲈鱼凌家塘27/南环桥23.5/合肥周谷堆22.5、淡水鲈鱼马鞍山20/云南华潮35/长治33元/公斤</div>',
    "来源卡片-MOA",
)

# 7) 来源汇总-MOA
rep(
    '<div class="sd">2026-08-13 · 直连 ncpscxx.moa.gov.cn 批发价接口，AES 解密后取活鳜鱼/淡水鲈鱼/海水鲈鱼各市场当日批发价（凌家塘活鳜鱼86元/公斤等）</div>',
    '<div class="sd">2026-08-18 · 直连 ncpscxx.moa.gov.cn 批发价接口，AES 解密后取活鳜鱼/淡水鲈鱼/海水鲈鱼各市场当日批发价（凌家塘活鳜鱼78元/公斤等）</div>',
    "来源汇总-MOA",
)

# 8) 数据局限 天数 5 → 6
rep(
    '看板「六、历史序列」已开启逐日累积，现已 5 天',
    '看板「六、历史序列」已开启逐日累积，现已 6 天',
    "数据局限-天数",
)

# 9) footer
rep(
    '    统计周期 2026-07-13 ~ 2026-08-13 · 农业农村部爬虫抓取日期 2026-08-13（活鳜鱼凌家塘86元/公斤）· 公开价源爬虫 07-03~07-24 · 科学养鱼 OCR 07-27 · 价格随行就市，仅供参考',
    '    统计周期 2026-07-13 ~ 2026-08-18 · 农业农村部爬虫抓取日期 2026-08-18（活鳜鱼凌家塘78元/公斤）· 公开价源爬虫 07-03~07-24 · 科学养鱼 OCR 07-27 · 价格随行就市，仅供参考',
    "footer",
)

open(HTML, "w", encoding="utf-8").write(html)
print("\n✅ 看板文本更新完成（2026-08-18）")
