#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把看板从 2026-07-30 更新到 2026-08-13：
- 新塘头价：水产前沿《特水鱼周报 2026 第28期》2026-08-11
- 新批发价：moa_fish_crawler.py 2026-08-13 当日快照
- 同步更新 KPI、图表数据、来源说明、footer
"""
import os

HTML = os.path.join(os.path.dirname(__file__), "鳜鱼鲈鱼价格看板.html")
html = open(HTML, encoding="utf-8").read()


def rep(old, new, label):
    global html
    assert old in html, f"未找到替换锚点：{label}"
    html = html.replace(old, new, 1)
    print(f"✅ {label}")


# 1) 标题
rep(
    "<title>江浙沪皖 鳜鱼·鲈鱼 出塘价与批发价数据看板（2026-07-30 更新）</title>",
    "<title>江浙沪皖 鳜鱼·鲈鱼 出塘价与批发价数据看板（2026-08-13 更新）</title>",
    "标题",
)

# 2) 周期与芯片
rep(
    '<span class="chip">📅 统计周期：2026-06-27 ~ 2026-07-30</span>',
    '<span class="chip">📅 统计周期：2026-07-13 ~ 2026-08-13</span>',
    "周期芯片",
)
rep(
    '<span class="chip">🤖 批发价：农业农村部接口爬虫（2026-07-30）+ 公开价源爬虫 + 科学养鱼OCR（07-27）</span>',
    '<span class="chip">🤖 批发价：农业农村部接口爬虫（2026-08-13）+ 公开价源爬虫 + 科学养鱼OCR（07-27）</span>',
    "批发价芯片",
)

# 3) KPI：鳜鱼批发价 96→86，安徽标鳜 39→41-42，其他不变
rep(
    """    <div class="kpi">
      <div class="lbl"><span class="dot" style="background:var(--gui)"></span>江苏 鳜鱼 批发价（爬虫 7/30）</div>
      <div class="val">96 <small>元/公斤</small></div>
      <div class="trend t-up">▲ 较7/27的78大涨18</div>
    </div>""",
    """    <div class="kpi">
      <div class="lbl"><span class="dot" style="background:var(--gui)"></span>江苏 鳜鱼 批发价（爬虫 8/13）</div>
      <div class="val">86 <small>元/公斤</small></div>
      <div class="trend t-down">▼ 较7/30的96回落10</div>
    </div>""",
    "KPI-鳜鱼批发价",
)
rep(
    """    <div class="kpi">
      <div class="lbl"><span class="dot" style="background:var(--gui)"></span>安徽 标鳜 塘头价（500g+）</div>
      <div class="val">39 <small>元/斤</small></div>
      <div class="trend t-up">▲ 走强</div>
    </div>""",
    """    <div class="kpi">
      <div class="lbl"><span class="dot" style="background:var(--gui)"></span>安徽 标鳜 塘头价（500g+）</div>
      <div class="val">41–42 <small>元/斤</small></div>
      <div class="trend t-up">▲ 较7/20涨2–3</div>
    </div>""",
    "KPI-安徽标鳜",
)
rep(
    """      <div class="trend t-up">▲ 月内涨约 2–4 元/斤</div>""",
    """      <div class="trend t-flat">■ 高位持平</div>""",
    "KPI-江苏标鳜趋势",
)

# 4) 鳜鱼出塘价板块
rep(
    """      <div class="card">
        <h3><span class="tag tag-gui">鳜鱼</span> 出塘价（塘头价）分规格</h3>
        <div class="csub">来源：水产前沿《特水鱼周报 2026 第25期》· 2026-07-20 + 第28期 · 2026-07-23（鳜鱼全线上涨）；腾氏水产播报㉘ 2026-07-17</div>
        <table>
          <thead><tr><th>产区</th><th>规格</th><th>塘头价</th><th>较上周</th></tr></thead>
          <tbody>
            <tr><td>江苏</td><td><span class="spec spec-l">标鳜 / 500g+</span></td><td class="price">36</td><td><span class="badge b-flat">■ 持平</span></td></tr>
            <tr><td>江苏</td><td><span class="spec spec-s">小鳜 / 500g内</span></td><td class="price">33–34 <small>参考</small></td><td><span class="badge b-flat">■ 稳</span></td></tr>
            <tr><td>安徽</td><td><span class="spec spec-l">标鳜 / 500g+</span></td><td class="price">39</td><td><span class="badge b-flat">■ 持平</span></td></tr>
            <tr><td>湖北</td><td><span class="spec spec-l">标鳜 / 500g+</span></td><td class="price">38–39</td><td><span class="badge b-up">▲ 涨 1</span></td></tr>
            <tr><td>湖南</td><td><span class="spec spec-l">标鳜 / 500g+</span></td><td class="price">36</td><td><span class="badge b-flat">■ 持平</span></td></tr>
            <tr><td>广东</td><td><span class="spec spec-l">大鳜 / 500g+</span></td><td class="price">36–37</td><td><span class="badge b-up">▲ 涨 0.5–1</span></td></tr>
          </tbody>
        </table>
        <div class="csub" style="margin-top:12px">※ 据水产前沿《特水鱼周报 2026 第28期》（7/23）：<b>鳜鱼全线上涨，40 元/斤大关指日可待</b>——广东佛山各规格周环比涨 1 元/斤，安徽、湖北涨 1–2 元/斤，江苏标鳜持稳 36。产区存塘见底、暴雨洪水扰动流通，支撑价格。这与农业农村部爬虫 7/30 凌家塘活鳜鱼批发价跳涨至 96 元/公斤相互印证。</div>
      </div>""",
    """      <div class="card">
        <h3><span class="tag tag-gui">鳜鱼</span> 出塘价（塘头价）分规格</h3>
        <div class="csub">来源：水产前沿《特水鱼周报 2026 第28期》· 2026-08-11（7.30→8.11 环比）</div>
        <table>
          <thead><tr><th>产区</th><th>规格</th><th>塘头价</th><th>较上周</th></tr></thead>
          <tbody>
            <tr><td>广东 佛山</td><td><span class="spec spec-l">1成中鳜+1成小鳜</span></td><td class="price">42–43</td><td><span class="badge b-flat">■ 持平</span></td></tr>
            <tr><td>广东 佛山</td><td><span class="spec spec-l">2成中鳜</span></td><td class="price">40</td><td><span class="badge b-flat">■ 持平</span></td></tr>
            <tr><td>广东 佛山</td><td><span class="spec spec-s">2成小鳜</span></td><td class="price">41</td><td><span class="badge b-flat">■ 持平</span></td></tr>
            <tr><td>广东 佛山</td><td><span class="spec spec-s">3成小鳜</span></td><td class="price">40</td><td><span class="badge b-flat">■ 持平</span></td></tr>
            <tr><td>江苏</td><td><span class="spec spec-l">标鳜 / 500g+</span></td><td class="price">39</td><td><span class="badge b-flat">■ 持平</span></td></tr>
            <tr><td>安徽</td><td><span class="spec spec-l">标鳜 / 500g+</span></td><td class="price">41–42</td><td><span class="badge b-up">▲ 涨 2–3</span></td></tr>
            <tr><td>湖北</td><td><span class="spec spec-l">标鳜 / 500g+</span></td><td class="price">40–41</td><td><span class="badge b-flat">■ 持平</span></td></tr>
            <tr><td>湖南</td><td><span class="spec spec-l">标鳜 / 500g+</span></td><td class="price">37</td><td><span class="badge b-down">▼ 跌 3</span></td></tr>
            <tr><td>江西</td><td><span class="spec spec-l">标鳜 / 500g+</span></td><td class="price">37–38</td><td><span class="badge b-flat">■ 持平</span></td></tr>
            <tr><td>广西</td><td><span class="spec spec-l">标鳜 / 500g+</span></td><td class="price">40</td><td><span class="badge b-up">▲ 涨 4</span></td></tr>
          </tbody>
        </table>
        <div class="csub" style="margin-top:12px">※ 据水产前沿《特水鱼周报 2026 第28期》（8/11）：新鱼上市增加，鳜鱼暴涨势头被遏制，局地跌 3 元/斤。广东佛山各规格周环比<b>持平</b>（3成中鳜 39、2成中鳜 40、1成中鳜/小鳜 42–43、2成小鳜 41、3成小鳜 40）；江苏标鳜 39 持平；安徽标鳜 41–42 继续走强；湖南标鳜 37 较上周跌 3 元；广西标鳜 40 涨 4 元。与农业农村部爬虫 8/13 凌家塘活鳜鱼批发价 86 元/公斤（较 7/30 的 96 回落）相互印证。</div>
      </div>""",
    "鳜鱼出塘价板块",
)

# 5) 鳜鱼批发价板块
rep(
    """      <div class="card">
        <h3><span class="tag tag-gui">鳜鱼</span> 批发价（农业农村部接口爬虫 · 2026-07-30）</h3>
        <div class="csub">来源：moa_fish_crawler.py 实时抓取 农业农村部 ncpscxx.moa.gov.cn 全国批发价接口（AES 解密）</div>
        <table>
          <thead><tr><th>市场 / 区域</th><th>规格</th><th>批发价</th><th>折合元/斤</th></tr></thead>
          <tbody>
            <tr><td>江苏 凌家塘市场</td><td><span class="spec spec-l">活鳜鱼 统货</span></td><td class="price">96 <small>元/公斤</small></td><td>≈ 48</td></tr>
            <tr><td>江西 九江琵琶湖</td><td><span class="spec">活鳜鱼</span></td><td class="price">56 <small>元/公斤</small></td><td>≈ 28</td></tr>
            <tr><td>乌鲁木齐 北园春</td><td><span class="spec">活鳜鱼</span></td><td class="price">120 <small>元/公斤</small></td><td>≈ 60</td></tr>
          </tbody>
        </table>
        <div class="callout" style="margin-top:14px"><b>数据说明：</b>本表由爬虫直连农业农村部官方批发价接口（品种码 <b>AM01013003</b>）解密所得，<b>抓取日期 2026-07-30</b>。江苏凌家塘活鳜鱼 <b>96 元/公斤</b>，较 7/27 的 78、7/22 的 84 明显跳涨（约 +18），与水产前沿 7/23 周报「鳜鱼全线上涨、40 元/斤大关指日可待」趋势吻合；流通加价约 24 元/公斤（塘头价 36 元/斤≈72 元/公斤）。另见「补充·科学养鱼」板块 07-27 南环桥分规格鳜鱼（250–500g 72.5 / 500–750g 85.5 元/千克）及「补充·公开价源爬虫」板块 武汉白沙洲/九江分规格鳜鱼可作交叉参考。</div>
      </div>""",
    """      <div class="card">
        <h3><span class="tag tag-gui">鳜鱼</span> 批发价（农业农村部接口爬虫 · 2026-08-13）</h3>
        <div class="csub">来源：moa_fish_crawler.py 实时抓取 农业农村部 ncpscxx.moa.gov.cn 全国批发价接口（AES 解密）</div>
        <table>
          <thead><tr><th>市场 / 区域</th><th>规格</th><th>批发价</th><th>折合元/斤</th></tr></thead>
          <tbody>
            <tr><td>江苏 凌家塘市场</td><td><span class="spec spec-l">活鳜鱼 统货</span></td><td class="price">86 <small>元/公斤</small></td><td>≈ 43</td></tr>
            <tr><td>江西 九江琵琶湖</td><td><span class="spec">活鳜鱼</span></td><td class="price">60 <small>元/公斤</small></td><td>≈ 30</td></tr>
            <tr><td>乌鲁木齐 北园春</td><td><span class="spec">活鳜鱼</span></td><td class="price">120 <small>元/公斤</small></td><td>≈ 60</td></tr>
          </tbody>
        </table>
        <div class="callout" style="margin-top:14px"><b>数据说明：</b>本表由爬虫直连农业农村部官方批发价接口（品种码 <b>AM01013003</b>）解密所得，<b>抓取日期 2026-08-13</b>。江苏凌家塘活鳜鱼 <b>86 元/公斤</b>，较 7/30 的 96 回落 10、较 7/27 的 78 仍高 8，与水产前沿 8/11 周报「新鱼上市、暴涨势头被遏制」趋势吻合；流通加价约 14–22 元/公斤（塘头价 39–43 元/斤≈78–86 元/公斤）。另见「补充·科学养鱼」板块 07-27 南环桥分规格鳜鱼及「补充·公开价源爬虫」板块 武汉白沙洲/九江分规格鳜鱼可作交叉参考。</div>
      </div>""",
    "鳜鱼批发价板块",
)

# 6) 鲈鱼出塘价板块
rep(
    """      <div class="card">
        <h3><span class="tag tag-lu">鲈鱼</span> 出塘价（塘头价）分规格</h3>
        <div class="csub">来源：水产前沿《特水鱼周报 2026 第25期》· 2026-07-20（7.13→7.20 环比）</div>
        <table>
          <thead><tr><th>产区</th><th>规格</th><th>塘头价</th><th>较上周</th></tr></thead>
          <tbody>
            <tr><td>江苏</td><td><span class="spec spec-s">9两上 / ≈450g</span></td><td class="price">9.5–10</td><td><span class="badge b-flat">■ 持平</span></td></tr>
            <tr><td>江苏</td><td><span class="spec spec-l">1斤上 / 500g+</span></td><td class="price">10.5–11 <small>参考周边</small></td><td><span class="badge b-flat">■ 稳</span></td></tr>
            <tr><td>浙江</td><td><span class="spec spec-l">8成统货 / 500g+</span></td><td class="price">11.5–12</td><td><span class="badge b-flat">■ 持平</span></td></tr>
            <tr><td>广东</td><td><span class="spec spec-l">1斤上 / 500g+</span></td><td class="price">10.5–11</td><td><span class="badge b-flat">■ 持平</span></td></tr>
            <tr><td>四川</td><td><span class="spec spec-l">1斤上 / 500g+</span></td><td class="price">15.5</td><td><span class="badge b-down">▼ 跌 0.5</span></td></tr>
            <tr><td>湖南</td><td><span class="spec spec-l">9两上 / 500g+</span></td><td class="price">12</td><td><span class="badge b-down">▼ 跌 0.5</span></td></tr>
          </tbody>
        </table>
        <div class="csub" style="margin-top:12px">※ 全国加州鲈整体走弱：华东、华南、西南普遍下滑 0.2–0.5 元/斤；四川仍为价格高地（15.5）。江苏本地存塘相对充裕但养户出鱼积极性不高，供应偏紧、价格低位持稳。</div>
      </div>""",
    """      <div class="card">
        <h3><span class="tag tag-lu">鲈鱼</span> 出塘价（塘头价）分规格</h3>
        <div class="csub">来源：水产前沿《特水鱼周报 2026 第28期》· 2026-08-11（8.3→8.11 环比）</div>
        <table>
          <thead><tr><th>产区</th><th>规格</th><th>塘头价</th><th>较上周</th></tr></thead>
          <tbody>
            <tr><td>广东</td><td><span class="spec spec-s">9两上</span></td><td class="price">8.8–9.3</td><td><span class="badge b-up">▲ 涨 0.5</span></td></tr>
            <tr><td>广东</td><td><span class="spec spec-l">1斤上</span></td><td class="price">9–9.5</td><td><span class="badge b-up">▲ 涨 0.5</span></td></tr>
            <tr><td>广东</td><td><span class="spec">统货</span></td><td class="price">9.2</td><td><span class="badge b-flat">■ 开价</span></td></tr>
            <tr><td>浙江</td><td><span class="spec spec-l">8成统货</span></td><td class="price">11–11.5</td><td><span class="badge b-flat">■ 持平</span></td></tr>
            <tr><td>江苏</td><td><span class="spec spec-s">9两上</span></td><td class="price">9.5–10</td><td><span class="badge b-flat">■ 持平</span></td></tr>
            <tr><td>四川</td><td><span class="spec spec-s">9两上</span></td><td class="price">15</td><td><span class="badge b-flat">■ 持平</span></td></tr>
            <tr><td>四川</td><td><span class="spec spec-l">1斤上</span></td><td class="price">15.5</td><td><span class="badge b-flat">■ 持平</span></td></tr>
            <tr><td>湖南</td><td><span class="spec spec-s">9两上</span></td><td class="price">10.5–11</td><td><span class="badge b-down">▼ 跌 0.5</span></td></tr>
            <tr><td>湖北</td><td><span class="spec spec-s">8.5两上</span></td><td class="price">10.5–11</td><td><span class="badge b-down">▼ 跌 0.5</span></td></tr>
            <tr><td>河南</td><td><span class="spec spec-l">1斤上</span></td><td class="price">10.5–11</td><td><span class="badge b-down">▼ 跌 0.5–1</span></td></tr>
          </tbody>
        </table>
        <div class="csub" style="margin-top:12px">※ 据水产前沿 8/11 周报：加州鲈缺大鱼，广东 9两上/1斤上均涨 0.5 元/斤，统货开价 9.2 元/斤；外省产区稳中有跌，湖北、湖南、河南跌 0.5–1 元/斤。四川仍为价格高地（15–15.5）。江苏 9两上 9.5–10 元/斤低位持稳，与农业农村部 8/13 海水鲈鱼凌家塘 27 元/公斤（≈13.5 元/斤）的批发价口径差异明显，反映流通加价。</div>
      </div>""",
    "鲈鱼出塘价板块",
)

# 7) 鲈鱼批发价板块
rep(
    """      <div class="card">
        <h3><span class="tag tag-lu">鲈鱼</span> 批发价（农业农村部接口爬虫 · 2026-07-30）</h3>
        <div class="csub">来源：moa_fish_crawler.py 抓取（淡水鲈鱼 AM01009 / 海水鲈鱼 AM02005）</div>
        <table>
          <thead><tr><th>市场 / 区域</th><th>品种</th><th>批发价</th><th>折合元/斤</th></tr></thead>
          <tbody>
            <tr><td>江苏 凌家塘市场</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">27 <small>元/公斤</small></td><td>≈ 13.5</td></tr>
            <tr><td>江苏 苏州南环桥</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">23.5 <small>元/公斤</small></td><td>≈ 11.75</td></tr>
            <tr><td>安徽 合肥周谷堆</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">22.5 <small>元/公斤</small></td><td>≈ 11.25</td></tr>
            <tr><td>马鞍山 安民农贸</td><td><span class="spec spec-s">淡水鲈鱼</span></td><td class="price">22 <small>元/公斤</small></td><td>≈ 11</td></tr>
            <tr><td>云南 华潮水产</td><td><span class="spec spec-s">淡水鲈鱼</span></td><td class="price">35 <small>元/公斤</small></td><td>≈ 17.5</td></tr>
            <tr><td>长治 紫坊农贸</td><td><span class="spec spec-s">淡水鲈鱼</span></td><td class="price">33 <small>元/公斤</small></td><td>≈ 16.5</td></tr>
            <tr><td>青岛 城阳水产</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">50 <small>元/公斤</small></td><td>≈ 25</td></tr>
            <tr><td>山东威海水产品</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">40 <small>元/公斤</small></td><td>≈ 20</td></tr>
            <tr><td>河南万邦国际</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">31 <small>元/公斤</small></td><td>≈ 15.5</td></tr>
            <tr><td>重庆西三街农副</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">45 <small>元/公斤</small></td><td>≈ 22.5</td></tr>
            <tr><td>北京 大洋路市场</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">30.5 <small>元/公斤</small></td><td>≈ 15.25</td></tr>
            <tr><td>山东滨州 鲁北蔬菜</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">26 <small>元/公斤</small></td><td>≈ 13</td></tr>
          </tbody>
        </table>
        <div class="csub" style="margin-top:14px">※ 2026-07-30 爬虫实测：海水鲈鱼凌家塘 27 / 南环桥 23.5 / 合肥周谷堆 22.5（与 7/22、7/27、7/28 持平），淡水鲈鱼马鞍山安民 22、云南华潮 35、长治紫坊 33 元/公斤（均为统货、不分规格）。接口区分「淡水鲈鱼」与「海水鲈鱼」两个品种码。鲈鱼整体低位运行，符合水产前沿 7/23 周报「加州鲈多地跌 0.5–1 元」走弱趋势。</div>
      </div>""",
    """      <div class="card">
        <h3><span class="tag tag-lu">鲈鱼</span> 批发价（农业农村部接口爬虫 · 2026-08-13）</h3>
        <div class="csub">来源：moa_fish_crawler.py 抓取（淡水鲈鱼 AM01009 / 海水鲈鱼 AM02005）</div>
        <table>
          <thead><tr><th>市场 / 区域</th><th>品种</th><th>批发价</th><th>折合元/斤</th></tr></thead>
          <tbody>
            <tr><td>江苏 凌家塘市场</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">27 <small>元/公斤</small></td><td>≈ 13.5</td></tr>
            <tr><td>江苏 苏州南环桥</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">23.5 <small>元/公斤</small></td><td>≈ 11.75</td></tr>
            <tr><td>安徽 合肥周谷堆</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">22.5 <small>元/公斤</small></td><td>≈ 11.25</td></tr>
            <tr><td>马鞍山 安民农贸</td><td><span class="spec spec-s">淡水鲈鱼</span></td><td class="price">22 <small>元/公斤</small></td><td>≈ 11</td></tr>
            <tr><td>云南 华潮水产</td><td><span class="spec spec-s">淡水鲈鱼</span></td><td class="price">33 <small>元/公斤</small></td><td>≈ 16.5</td></tr>
            <tr><td>长治 紫坊农贸</td><td><span class="spec spec-s">淡水鲈鱼</span></td><td class="price">33 <small>元/公斤</small></td><td>≈ 16.5</td></tr>
            <tr><td>青岛 城阳水产</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">44 <small>元/公斤</small></td><td>≈ 22</td></tr>
            <tr><td>山东威海水产品</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">40 <small>元/公斤</small></td><td>≈ 20</td></tr>
            <tr><td>河南万邦国际</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">29 <small>元/公斤</small></td><td>≈ 14.5</td></tr>
            <tr><td>重庆西三街农副</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">40 <small>元/公斤</small></td><td>≈ 20</td></tr>
            <tr><td>北京 大洋路市场</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">32 <small>元/公斤</small></td><td>≈ 16</td></tr>
            <tr><td>山东滨州 鲁北蔬菜</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">25 <small>元/公斤</small></td><td>≈ 12.5</td></tr>
            <tr><td>宁夏 四季鲜</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">38 <small>元/公斤</small></td><td>≈ 19</td></tr>
            <tr><td>甘肃酒泉 春光市场</td><td><span class="spec spec-l">海水鲈鱼</span></td><td class="price">59 <small>元/公斤</small></td><td>≈ 29.5</td></tr>
          </tbody>
        </table>
        <div class="csub" style="margin-top:14px">※ 2026-08-13 爬虫实测：海水鲈鱼凌家塘 27 / 南环桥 23.5 / 合肥周谷堆 22.5（与 7 月持平），淡水鲈鱼马鞍山安民 22、云南华潮 33、长治紫坊 33 元/公斤；海水鲈鱼新增甘肃酒泉 59、宁夏四季鲜 38、重庆西三街 40、北京大洋路 32 等市场（均为统货、不分规格）。接口区分「淡水鲈鱼」与「海水鲈鱼」两个品种码。鲈鱼整体低位运行，与水产前沿 8/11 周报「外省产区稳中有跌」一致。</div>
      </div>""",
    "鲈鱼批发价板块",
)

# 8) 图表数据：鳜鱼 & 鲈鱼
rep(
    """// 鳜鱼塘头价（元/斤）按产区，分规格
new Chart(document.getElementById('guiChart'),{
  type:'bar',
  data:{
    labels:['江苏','安徽','湖北','湖南','广东'],
    datasets:[
      {label:'500g以内（小鳜，参考）',data:[33.5,null,null,null,33.5],backgroundColor:'#f59e0b',borderRadius:6,maxBarThickness:32},
      {label:'500g以上（标鳜）',data:[36,39,38,36,36.5],backgroundColor:'#7c3aed',borderRadius:6,maxBarThickness:32}
    ]
  },
  options:{
    responsive:true,maintainAspectRatio:false,
    plugins:{legend:{position:'top',labels:{boxWidth:12,font:{size:12}}},
      tooltip:{callbacks:{label:c=>c.dataset.label+'：'+(c.parsed.y==null?'—':c.parsed.y+' 元/斤')}}},
    scales:{y:{suggestedMin:28,suggestedMax:42,title:{display:true,text:'元/斤'},grid:{color:'#eef1f5'}},x:{grid:{display:false}}}
  }
});""",
    """// 鳜鱼塘头价（元/斤）按产区，分规格
new Chart(document.getElementById('guiChart'),{
  type:'bar',
  data:{
    labels:['广东佛山','江苏','安徽','湖北','湖南','江西','广西'],
    datasets:[
      {label:'500g以内（小鳜）',data:[40.5,null,null,null,null,null,null],backgroundColor:'#f59e0b',borderRadius:6,maxBarThickness:28},
      {label:'500g以上（标鳜）',data:[42.5,39,41.5,40.5,37,37.5,40],backgroundColor:'#7c3aed',borderRadius:6,maxBarThickness:28}
    ]
  },
  options:{
    responsive:true,maintainAspectRatio:false,
    plugins:{legend:{position:'top',labels:{boxWidth:12,font:{size:12}}},
      tooltip:{callbacks:{label:c=>c.dataset.label+'：'+(c.parsed.y==null?'—':c.parsed.y+' 元/斤')}}},
    scales:{y:{suggestedMin:30,suggestedMax:46,title:{display:true,text:'元/斤'},grid:{color:'#eef1f5'}},x:{grid:{display:false}}}
  }
});""",
    "图表-鳜鱼",
)

rep(
    """// 鲈鱼 塘头价 vs 批发价（元/斤）
new Chart(document.getElementById('luChart'),{
  type:'bar',
  data:{
    labels:['江苏','合肥','浙江','广东'],
    datasets:[
      {label:'塘头价（元/斤）',data:[9.75,null,11.75,10.75],backgroundColor:'#0284c7',borderRadius:6,maxBarThickness:32},
      {label:'批发价（折元/斤）',data:[13.5,11.75,null,null],backgroundColor:'#0ea5a4',borderRadius:6,maxBarThickness:32}
    ]
  },
  options:{
    responsive:true,maintainAspectRatio:false,
    plugins:{legend:{position:'top',labels:{boxWidth:12,font:{size:12}}},
      tooltip:{callbacks:{label:c=>c.dataset.label+'：'+(c.parsed.y==null?'—':c.parsed.y+' 元/斤')}}},
    scales:{y:{beginAtZero:true,suggestedMax:16,title:{display:true,text:'元/斤'},grid:{color:'#eef1f5'}},x:{grid:{display:false}}}
  }
});""",
    """// 鲈鱼 塘头价 vs 批发价（元/斤）
new Chart(document.getElementById('luChart'),{
  type:'bar',
  data:{
    labels:['广东','浙江','江苏','四川','湖南','湖北','河南'],
    datasets:[
      {label:'塘头价（元/斤）',data:[9.2,11.5,9.75,15.5,10.75,10.75,10.75],backgroundColor:'#0284c7',borderRadius:6,maxBarThickness:28},
      {label:'批发价（折元/斤）',data:[null,null,13.5,11.25,null,null,null],backgroundColor:'#0ea5a4',borderRadius:6,maxBarThickness:28}
    ]
  },
  options:{
    responsive:true,maintainAspectRatio:false,
    plugins:{legend:{position:'top',labels:{boxWidth:12,font:{size:12}}},
      tooltip:{callbacks:{label:c=>c.dataset.label+'：'+(c.parsed.y==null?'—':c.parsed.y+' 元/斤')}}},
    scales:{y:{beginAtZero:true,suggestedMax:18,title:{display:true,text:'元/斤'},grid:{color:'#eef1f5'}},x:{grid:{display:false}}}
  }
});""",
    "图表-鲈鱼",
)

# 9) 来源卡片
rep(
    """        <div class="src">
          <div class="st">农业农村部批发价接口（moa_fish_crawler.py 爬虫）</div>
          <div class="sd">2026-07-30 · 活鳜鱼凌家塘96元/公斤（较7/27的78大涨）；海水鲈鱼凌家塘27/南环桥23.5/合肥周谷堆22.5、淡水鲈鱼马鞍山22/云南华潮35/长治33元/公斤</div>
        </div>""",
    """        <div class="src">
          <div class="st">农业农村部批发价接口（moa_fish_crawler.py 爬虫）</div>
          <div class="sd">2026-08-13 · 活鳜鱼凌家塘86元/公斤（较7/30的96回落）；海水鲈鱼凌家塘27/南环桥23.5/合肥周谷堆22.5、淡水鲈鱼马鞍山22/云南华潮33/长治33元/公斤</div>
        </div>""",
    "来源卡片-MOA",
)
rep(
    """        <div class="src">
          <div class="st">腾氏水产商务网 海南卓越联合播报㉘</div>
          <div class="sd">2026-07-17 · 江苏标鳜36元/斤（涨1）、湖北38、广东大鳜36-37</div>
        </div>""",
    """        <div class="src">
          <div class="st">水产前沿《特水鱼周报 2026 第28期》</div>
          <div class="sd">2026-08-11 · 鳜鱼新鱼上市暴涨势头被遏制，局地跌3元/斤；加州鲈广东涨0.5元、外省稳中有跌</div>
        </div>""",
    "来源卡片-水产前沿",
)

# 10) 来源汇总
rep(
    """      <div class="src">
        <div class="st">🤖 moa_fish_crawler.py 农业农村部接口爬虫</div>
        <div class="sd">2026-07-30 · 直连 ncpscxx.moa.gov.cn 批发价接口，AES 解密后取活鳜鱼/淡水鲈鱼/海水鲈鱼各市场当日批发价（凌家塘活鳜鱼96元/公斤等）</div>
      </div>""",
    """      <div class="src">
        <div class="st">🤖 moa_fish_crawler.py 农业农村部接口爬虫</div>
        <div class="sd">2026-08-13 · 直连 ncpscxx.moa.gov.cn 批发价接口，AES 解密后取活鳜鱼/淡水鲈鱼/海水鲈鱼各市场当日批发价（凌家塘活鳜鱼86元/公斤等）</div>
      </div>""",
    "来源汇总-MOA",
)
rep(
    """      <div class="src">
        <div class="st">📰 水产前沿《特水鱼周报 2026》第22–25期</div>
        <div class="sd">2026-06-22 ~ 07-20 · 分产区分规格塘头价（鳜鱼/加州鲈），核心数据来源</div>
      </div>""",
    """      <div class="src">
        <div class="st">📰 水产前沿《特水鱼周报 2026》第22–28期</div>
        <div class="sd">2026-06-22 ~ 08-11 · 分产区分规格塘头价（鳜鱼/加州鲈），核心数据来源；第28期（8/11）为最新</div>
      </div>""",
    "来源汇总-水产前沿",
)
rep(
    """      <b>数据局限说明：</b>① 塘头价（出塘价）全部来自水产前沿周报，分规格清晰、来源权威；② <b>批发价板块已升级为双爬虫直采</b>：moa_fish_crawler.py 逆向农业农村部批发价异步接口（品种码 活鳜鱼 AM01013003 / 淡水鲈鱼 AM01009 / 海水鲈鱼 AM02005），AES 解密后得 2026-07-30 当日各市场真实报价（凌家塘活鳜鱼 96 元/公斤）；另以 public_price_crawler.py 抓取武汉白沙洲/九江/云南华潮政府官网<b>分规格</b>批发价，补足农业农村部统货价缺口；③ 该接口<b>仅返回「当日」最新快照，无历史日期参数</b>，故无法自动回溯近 30 天序列，「近 30 天」维度暂以周报塘头价 + 爬虫当日批发价组合呈现（看板「六、历史序列」已开启逐日累积，现已 4 天）；④ 农业农村部接口报价为<b>统货价、不分 500g 内/外规格</b>，分规格需求以水产前沿周报塘头价 + 公开价源爬虫（武汉白沙洲/九江分规格）为准；⑤ <b>「科学养鱼」公众号价格已通过 OCR 纳入</b>：其价格以图片发布、纯文本爬虫取不到数字，由用户提供截图 + OCR 提取，将 2026-07-27 鳜鱼/青鱼/鲫鱼/鲤鱼/鲢鱼/鳊鱼（元/千克，分规格）补入「补充」板块，与农业农村部爬虫互为交叉参考；⑥ 抖音社媒互动数据因需 AgentKey 未重新抓取，保留 7 月上旬快照仅作连续性参考；⑦ 价格随行就市，仅供参考。""",
    """      <b>数据局限说明：</b>① 塘头价（出塘价）全部来自水产前沿周报，分规格清晰、来源权威，最新为第28期（2026-08-11）；② <b>批发价板块已升级为双爬虫直采</b>：moa_fish_crawler.py 逆向农业农村部批发价异步接口（品种码 活鳜鱼 AM01013003 / 淡水鲈鱼 AM01009 / 海水鲈鱼 AM02005），AES 解密后得 2026-08-13 当日各市场真实报价（凌家塘活鳜鱼 86 元/公斤）；另以 public_price_crawler.py 抓取武汉白沙洲/九江/云南华潮政府官网<b>分规格</b>批发价，补足农业农村部统货价缺口；③ 该接口<b>仅返回「当日」最新快照，无历史日期参数</b>，故无法自动回溯近 30 天序列，「近 30 天」维度暂以周报塘头价 + 爬虫当日批发价组合呈现（看板「六、历史序列」已开启逐日累积，现已 5 天）；④ 农业农村部接口报价为<b>统货价、不分 500g 内/外规格</b>，分规格需求以水产前沿周报塘头价 + 公开价源爬虫（武汉白沙洲/九江分规格）为准；⑤ <b>「科学养鱼」「a渔业行情」等公众号价格无法直接爬取</b>：搜狗微信未索引/反爬，纯文本爬虫拿不到文章；目前靠用户提供截图 + OCR 提取（科学养鱼 2026-07-27 已纳入）；⑥ 抖音社媒互动数据因需 AgentKey 未重新抓取，保留 7 月上旬快照仅作连续性参考；⑦ 价格随行就市，仅供参考。""",
    "数据局限说明",
)

# 11) footer
rep(
    """  <footer>
    数据整理：WorkBuddy · 塘头价源自水产前沿/腾氏水产周报；批发价 = moa_fish_crawler.py（农业农村部官方接口 AES 解密）+ public_price_crawler.py（武汉白沙洲/九江/云南华潮分规格）+ 科学养鱼公众号 OCR（用户截图）<br>
    统计周期 2026-06-27 ~ 2026-07-30 · 农业农村部爬虫抓取日期 2026-07-30（活鳜鱼凌家塘96元/公斤）· 公开价源爬虫 07-03~07-24 · 科学养鱼 OCR 07-27 · 价格随行就市，仅供参考
  </footer>""",
    """  <footer>
    数据整理：WorkBuddy · 塘头价源自水产前沿/腾氏水产周报；批发价 = moa_fish_crawler.py（农业农村部官方接口 AES 解密）+ public_price_crawler.py（武汉白沙洲/九江/云南华潮分规格）+ 科学养鱼公众号 OCR（用户截图）<br>
    统计周期 2026-07-13 ~ 2026-08-13 · 农业农村部爬虫抓取日期 2026-08-13（活鳜鱼凌家塘86元/公斤）· 公开价源爬虫 07-03~07-24 · 科学养鱼 OCR 07-27 · 价格随行就市，仅供参考
  </footer>""",
    "footer",
)

# 12) 关于公众号爬取的说明
rep(
    """    <div class="callout" style="margin-bottom:18px"><b>关于「科学养鱼」公众号价格：</b>经搜狗微信检索确认该号确实发布鳜鱼/鲈鱼等淡水鱼批发价专栏（如《各地乌鳢、加州鲈、黄颡鱼、鳜鱼批发价格｜今日鱼价》）。其价格以<b>图片</b>形式发布，正文仅含省份标题，纯文本爬虫取不到数字；搜狗索引到的多为 2018–2020 年历史文章、2026 年近期未公开索引。本轮由<b>用户提供截图 + OCR 提取</b>，已将 2026-07-27 鳜鱼/青鱼/鲫鱼/鲤鱼/鲢鱼/鳊鱼（元/千克，分规格）结构化补入「补充·科学养鱼公众号批发价」板块，详见该节。</div>""",
    """    <div class="callout" style="margin-bottom:18px"><b>关于微信公众号行情爬取：</b>用户要求尝试爬取「a渔业行情」与「科学养鱼」两个公众号。经搜狗微信检索实测：① <b>「a渔业行情」</b>虽发布《2026年8月11日全国水产塘口价》等行情文章，但<b>搜狗微信未索引到该号文章</b>，且微信文章需登录/反爬，纯文本爬虫无法直接获取正文；② <b>「科学养鱼」</b>与之前结论一致，价格以<b>图片</b>形式发布，搜狗微信也未索引到 2026 年近期文章。因此两个公众号目前<b>均无法通过公开网络爬虫自动抓取</b>，仍需用户提供文章截图进行 OCR 提取，或提供具体微信文章链接（若有临时访问权限）。本轮由搜狐转载的水产前沿 8/11 周报获得等效塘头价数据，已补入「一、二」板块。</div>""",
    "公众号爬取说明",
)

# 13) 可视化图表小标题日期
rep(
    """        <h3>各产区 鳜鱼 塘头价对比（元/斤）</h3>
        <div class="csub">按规格分组，截至 2026-07-20</div>""",
    """        <h3>各产区 鳜鱼 塘头价对比（元/斤）</h3>
        <div class="csub">按规格分组，截至 2026-08-11</div>""",
    "图表副标题-鳜鱼",
)

open(HTML, "w", encoding="utf-8").write(html)
print("\n✅ 看板已更新到 2026-08-13，请运行 inline_assets.py 重新内联历史数据。")
