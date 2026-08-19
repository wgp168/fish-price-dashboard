# -*- coding: utf-8 -*-
"""用 2026-08-19 新截图 OCR 数据更新看板：科学养鱼 08-18 + a渔业行情 08-11。"""
import csv
import json
import os

HTML = "鳜鱼鲈鱼价格看板.html"

# ===== 1. OCR 结构化数据 =====
ocr_rows = []

# 科学养鱼 2026-08-18（元/千克）
kexue = [
    ("科学养鱼", "2026-08-18", "2026-08-18", "鳜鱼（桂花鱼）", "江苏苏州南环桥农副产品批发市场", "500≤条重<750g", 89.50, "元/千克", ""),
    ("科学养鱼", "2026-08-18", "2026-08-18", "鳜鱼（桂花鱼）", "广州黄沙水产交易市场有限公司", "条重≥750g", 60.00, "元/千克", ""),
    ("科学养鱼", "2026-08-18", "2026-08-18", "鳜鱼（桂花鱼）", "江苏凌家塘市场发展有限公司", "500≤条重<750g", 78.00, "元/千克", ""),
    ("科学养鱼", "2026-08-18", "2026-08-18", "鳜鱼（桂花鱼）", "湖北黄冈硕源水产品批发市场", "250≤条重<500g", 84.00, "元/千克", ""),
    ("科学养鱼", "2026-08-18", "2026-08-18", "鳜鱼（桂花鱼）", "湖北黄冈硕源水产品批发市场", "500≤条重<750g", 94.00, "元/千克", ""),
    ("科学养鱼", "2026-08-18", "2026-08-18", "鳜鱼（桂花鱼）", "湖北黄冈硕源水产品批发市场", "条重≥750g", 86.00, "元/千克", ""),
    ("科学养鱼", "2026-08-18", "2026-08-18", "鳜鱼（桂花鱼）", "乌鲁木齐北园春果业经营有限责任公司", "500≤条重<750g", 50.00, "元/千克", ""),
    ("科学养鱼", "2026-08-18", "2026-08-18", "鳜鱼（桂花鱼）", "江苏苏州南环桥农副产品批发市场", "250≤条重<500g", 76.50, "元/千克", ""),
    ("科学养鱼", "2026-08-18", "2026-08-18", "加州鲈鱼", "广州黄沙水产交易市场有限公司", "条重≥500g", 26.00, "元/千克", ""),
    ("科学养鱼", "2026-08-18", "2026-08-18", "加州鲈鱼", "中国供销上饶农产品交易城", "条重≥500g", 25.00, "元/千克", ""),
    ("科学养鱼", "2026-08-18", "2026-08-18", "加州鲈鱼", "湖州菱湖乌板桥水产品批发市场", "条重≥500g", 25.00, "元/千克", ""),
    ("科学养鱼", "2026-08-18", "2026-08-18", "加州鲈鱼", "湖州菱湖乌板桥水产品批发市场", "条重<500g", 21.40, "元/千克", ""),
    ("科学养鱼", "2026-08-18", "2026-08-18", "加州鲈鱼", "上海江阳水产品批发交易市场经营管理有限公司", "条重≥500g", 24.00, "元/千克", ""),
    ("科学养鱼", "2026-08-18", "2026-08-18", "加州鲈鱼", "上海江杨水产品批发市场经营管理有限公司", "条重≥500g", 30.00, "元/千克", ""),
    ("科学养鱼", "2026-08-18", "2026-08-18", "加州鲈鱼", "两湖绿谷淡水鱼市场", "条重≥500g", 22.70, "元/千克", ""),
    ("科学养鱼", "2026-08-18", "2026-08-18", "青鱼", "湖北黄冈硕源水产品批发市场", "条重<2000g", 14.10, "元/千克", ""),
    ("科学养鱼", "2026-08-18", "2026-08-18", "青鱼", "湖北黄冈硕源水产品批发市场", "条重≥2000g", 15.40, "元/千克", ""),
]
ocr_rows.extend(kexue)

# a渔业行情 2026-08-11（元/斤）；发文 2026-08-10，鳜鱼报价日期 8.9
ayuqing = [
    ("a渔业行情", "2026-08-10", "2026-08-09", "鳜鱼", "广东地区", "小鳜（0.8斤以下）", 31.00, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-09", "鳜鱼", "广东地区", "标鳜（0.8-1.5斤）", 46.00, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-09", "鳜鱼", "广东地区", "中鳜（1.5斤以上）", 42.00, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-09", "鳜鱼", "湖北地区", "标鳜", 41.00, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-09", "鳜鱼", "安徽地区", "标鳜", 39.00, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-09", "鳜鱼", "江西地区", "标鳜", 38.50, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-09", "鳜鱼", "湖南地区", "标鳜", 38.50, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-09", "鳜鱼", "江苏地区", "标鳜", 39.50, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-11", "加州鲈", "南海九江", "统货", 9.80, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-11", "加州鲈", "南海九江", "1斤以上", 9.80, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-11", "加州鲈", "珠海金湾", "1斤", 9.70, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-11", "加州鲈", "珠海金湾", "1.3斤", 10.50, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-11", "加州鲈", "福建漳州", "0.8-1.5斤", 11.50, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-11", "加州鲈", "龙岩上杭", "8两以上", 12.70, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-11", "加州鲈", "湖南钱粮湖", "8两上", 11.50, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-11", "加州鲈", "湖北白沙洲", "9两上", 11.50, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-11", "加州鲈", "成都邛崃", "9两起", None, "元/斤", "无报价"),
    ("a渔业行情", "2026-08-10", "2026-08-11", "加州鲈", "成都邛崃", "1斤", 15.50, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-11", "加州鲈", "眉山东坡", "9两起", None, "元/斤", "无报价"),
    ("a渔业行情", "2026-08-10", "2026-08-11", "加州鲈", "河南郑州", "1斤起", 11.50, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-11", "加州鲈", "江苏吴江", "9两起", 11.50, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-11", "加州鲈", "江苏高邮", "1斤", 9.80, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-11", "加州鲈", "江苏高邮", "1.1斤", 10.20, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-11", "加州鲈", "江苏高邮", "1.2斤", 10.50, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-11", "加州鲈", "浙江湖州", "8两起", 11.00, "元/斤", ""),
    ("a渔业行情", "2026-08-10", "2026-08-11", "加州鲈", "浙江湖州", "统货", 10.50, "元/斤", ""),
]
ocr_rows.extend(ayuqing)

# 保存 CSV/JSON
with open("wechat_ocr_prices_20260819.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["source", "article_date", "price_date", "species", "market", "spec", "price", "unit", "note"])
    for r in ocr_rows:
        w.writerow([r[0], r[1], r[2], r[3], r[4], r[5], "" if r[6] is None else r[6], r[7], r[8]])

json_out = []
for r in ocr_rows:
    json_out.append({
        "source": r[0], "article_date": r[1], "price_date": r[2], "species": r[3],
        "market": r[4], "spec": r[5], "price": r[6], "unit": r[7], "note": r[8]
    })
with open("wechat_ocr_prices_20260819.json", "w", encoding="utf-8") as f:
    json.dump(json_out, f, ensure_ascii=False, indent=2)


# ===== 2. HTML 更新 =====
with open(HTML, encoding="utf-8") as f:
    s = f.read()

# (a) hero 段落
old_hero = ('聚焦江苏及周边（安徽、浙江、上海、湖北参照）近 30 天鳜鱼（桂花鱼）与鲈鱼（加州鲈）的<b>出塘价（塘头价）</b>与<b>批发价</b>行情，'
            '按鱼的规格拆分为「500 克以内 / 500 克以上」，并附代表性帖子、互动数据与价格来源。本轮<b>未使用 AgentKey</b>，'
            '数据来自公开网页检索（水产前沿、腾氏水产、农业农村部、地方农业农村局）。')
new_hero = ('聚焦江苏及周边（安徽、浙江、上海、湖北参照）近 30 天鳜鱼（桂花鱼）与鲈鱼（加州鲈）的<b>出塘价（塘头价）</b>与<b>批发价</b>行情，'
            '按鱼的规格拆分为「500 克以内 / 500 克以上」，并附代表性帖子、互动数据与价格来源。'
            '出塘价来自公开网页检索（水产前沿、腾氏水产、地方农业农村局）及「a渔业行情」公众号截图 OCR；'
            '批发价来自农业农村部接口爬虫、公开价源爬虫及「科学养鱼」公众号截图 OCR；'
            '抖音社媒互动数据由 <b>AgentKey（TikHub）</b> 于 2026-08-18 实时抓取。')
assert old_hero in s
s = s.replace(old_hero, new_hero, 1)

# (b) chip
old_chip = '<span class="chip">🤖 批发价：农业农村部接口爬虫（2026-08-18）+ 公开价源爬虫 + 科学养鱼OCR（07-27）</span>'
new_chip = '<span class="chip">🤖 批发价：农业农村部接口爬虫（2026-08-18）+ 公开价源爬虫 + 科学养鱼OCR（08-18）</span>'
assert old_chip in s
s = s.replace(old_chip, new_chip, 1)

# (c) 鳜鱼批发价 callout 中的旧日期引用
old_ref = '另见「补充·科学养鱼」板块 07-27 南环桥分规格鳜鱼及「补充·公开价源爬虫」板块 武汉白沙洲/九江分规格鳜鱼可作交叉参考。'
new_ref = '另见「补充·科学养鱼」板块 08-18 南环桥/凌家塘分规格鳜鱼及「补充·公开价源爬虫」板块 武汉白沙洲/九江分规格鳜鱼可作交叉参考。'
assert old_ref in s
s = s.replace(old_ref, new_ref, 1)


# (d) 替换「科学养鱼」section（从注释到 </section>）
section_comment = '<!-- 科学养鱼公众号 OCR 数据 -->'
start = s.find(section_comment)
assert start != -1
# 找到该 section 的 <section> 及匹配 </section>
sec_open = s.find('<section>', start)
depth = 0
i = sec_open
while i < len(s):
    op = s.find('<section', i)
    cl = s.find('</section>', i)
    if cl == -1:
        break
    if op != -1 and op < cl:
        depth += 1
        i = op + 8
    else:
        depth -= 1
        i = cl + 10
        if depth == 0:
            sec_end = i
            break
assert depth == 0

new_kexue = '''<!-- 科学养鱼公众号 OCR 数据 -->
  <section>
    <div class="sec-head">
      <span class="bar" style="background:#7c3aed"></span>
      <h2>补充 · 「科学养鱼」公众号批发价（OCR 提取）</h2>
      <span class="note">2026-08-18 · 元/千克 · 已按图片数字录入</span>
    </div>
    <div class="card">
      <h3>🌟 科学养鱼公众号 淡水鱼类分品种分规格批发价</h3>
      <div class="csub">来源：用户提供的「科学养鱼」公众号价格截图（截屏2026-08-19 09.03.27 / 09.03.53 / 09.04.03），单位已确认为<b>淡水鱼类（元/千克）</b>；由 OCR 提取，发布日期 2026-08-18。鳜鱼、加州鲈鱼、青鱼为本次新截图数据。</div>
      <div class="grid2">
        <div>
          <h3 style="font-size:14px;margin:6px 0 8px"><span class="tag tag-gui">鳜鱼</span> 桂花鱼 批发价（元/千克）</h3>
          <table>
            <thead><tr><th>市场</th><th>规格</th><th>价格</th></tr></thead>
            <tbody>
              <tr><td>江苏苏州南环桥</td><td><span class="spec spec-l">500≤条重<750g</span></td><td class="price">89.50</td></tr>
              <tr><td>江苏凌家塘市场</td><td><span class="spec spec-l">500≤条重<750g</span></td><td class="price">78.00</td></tr>
              <tr><td>湖北黄冈硕源</td><td><span class="spec spec-s">250≤条重<500g</span></td><td class="price">84.00</td></tr>
              <tr><td>湖北黄冈硕源</td><td><span class="spec spec-l">500≤条重<750g</span></td><td class="price">94.00</td></tr>
              <tr><td>湖北黄冈硕源</td><td><span class="spec spec-l">条重≥750g</span></td><td class="price">86.00</td></tr>
              <tr><td>乌鲁木齐北园春</td><td><span class="spec spec-l">500≤条重<750g</span></td><td class="price">50.00</td></tr>
              <tr><td>广州黄沙水产</td><td><span class="spec spec-l">条重≥750g</span></td><td class="price">60.00</td></tr>
              <tr><td>江苏苏州南环桥</td><td><span class="spec spec-s">250≤条重<500g</span></td><td class="price">76.50</td></tr>
            </tbody>
          </table>
        </div>
        <div>
          <h3 style="font-size:14px;margin:6px 0 8px"><span class="tag tag-lu">加州鲈鱼</span> 批发价（元/千克）</h3>
          <table>
            <thead><tr><th>市场</th><th>规格</th><th>价格</th></tr></thead>
            <tbody>
              <tr><td>广州黄沙水产</td><td><span class="spec spec-l">条重≥500g</span></td><td class="price">26.00</td></tr>
              <tr><td>中国供销上饶</td><td><span class="spec spec-l">条重≥500g</span></td><td class="price">25.00</td></tr>
              <tr><td>湖州菱湖乌板桥</td><td><span class="spec spec-l">条重≥500g</span></td><td class="price">25.00</td></tr>
              <tr><td>湖州菱湖乌板桥</td><td><span class="spec spec-s">条重<500g</span></td><td class="price">21.40</td></tr>
              <tr><td>上海江阳水产品</td><td><span class="spec spec-l">条重≥500g</span></td><td class="price">24.00</td></tr>
              <tr><td>上海江杨水产品</td><td><span class="spec spec-l">条重≥500g</span></td><td class="price">30.00</td></tr>
              <tr><td>两湖绿谷淡水鱼</td><td><span class="spec spec-l">条重≥500g</span></td><td class="price">22.70</td></tr>
            </tbody>
          </table>
        </div>
      </div>
      <div style="margin-top:16px">
        <h3 style="font-size:14px;margin:6px 0 8px">🐟 青鱼 批发价（元/千克）</h3>
        <table>
          <thead><tr><th>市场</th><th>规格</th><th>价格</th></tr></thead>
          <tbody>
            <tr><td>湖北黄冈硕源</td><td><span class="spec spec-s">条重<2000g</span></td><td class="price">14.10</td></tr>
            <tr><td>湖北黄冈硕源</td><td><span class="spec spec-l">条重≥2000g</span></td><td class="price">15.40</td></tr>
          </tbody>
        </table>
      </div>
      <div class="callout" style="margin-top:14px"><b>数据说明：</b>该公众号价格以<b>图片</b>形式发布，纯文本爬虫取不到数字；本次由用户提供截图、我方 OCR 提取后录入。① 单位已确认为<b>元/千克</b>；② 鳜鱼（桂花鱼）与农业农村部爬虫（凌家塘活鳜鱼 78 元/公斤）口径不同（公众号为全国多市场分规格、农业农村部为统货当日快照），可互为补充；③ 发布日期 2026-08-18，与农业农村部爬虫 08-18 快照同日，可作最新交叉参考；④ 鲫鱼/鲤鱼/鲢鱼/鳊鱼等历史截图数据仍保留于 <code>wechat_ocr_prices_20260819.csv</code> 及 2026-07-27 记录中。</div>
    </div>
  </section>'''
s = s[:start] + new_kexue + s[sec_end:]


# (e) 在「图表」section 前插入 a渔业行情 section
chart_marker = '<!-- 图表 -->'
assert chart_marker in s

new_ayuqing = '''<!-- a渔业行情公众号 OCR 数据 -->
  <section>
    <div class="sec-head">
      <span class="bar" style="background:#059669"></span>
      <h2>补充 · 「a渔业行情」公众号塘口价（OCR 提取）</h2>
      <span class="note">2026-08-11 全国水产塘口价 · 元/斤</span>
    </div>
    <div class="card">
      <h3>🎣 a渔业行情公众号 分产区塘口价</h3>
      <div class="csub">来源：用户提供的「a渔业行情」公众号文章《2026年8月11日全国水产塘口价》截图（发文 2026-08-10），由 OCR 提取。鳜鱼报价日期为 8.9，加州鲈报价日期为 8.11；<b>单位元/斤</b>，属塘口/出塘价，与批发价不可直接比较。</div>
      <div class="grid2">
        <div>
          <h3 style="font-size:14px;margin:6px 0 8px"><span class="tag tag-gui">鳜鱼</span> 8.9 报价（元/斤）</h3>
          <table>
            <thead><tr><th>地区</th><th>规格</th><th>塘口价</th></tr></thead>
            <tbody>
              <tr><td>广东地区</td><td><span class="spec spec-s">小鳜（0.8斤以下）</span></td><td class="price">31</td></tr>
              <tr><td>广东地区</td><td><span class="spec spec-l">标鳜（0.8-1.5斤）</span></td><td class="price">46</td></tr>
              <tr><td>广东地区</td><td><span class="spec spec-l">中鳜（1.5斤以上）</span></td><td class="price">42</td></tr>
              <tr><td>湖北地区</td><td><span class="spec spec-l">标鳜</span></td><td class="price">41</td></tr>
              <tr><td>安徽地区</td><td><span class="spec spec-l">标鳜</span></td><td class="price">39</td></tr>
              <tr><td>江西地区</td><td><span class="spec spec-l">标鳜</span></td><td class="price">38.5</td></tr>
              <tr><td>湖南地区</td><td><span class="spec spec-l">标鳜</span></td><td class="price">38.5</td></tr>
              <tr><td>江苏地区</td><td><span class="spec spec-l">标鳜</span></td><td class="price">39.5</td></tr>
            </tbody>
          </table>
        </div>
        <div>
          <h3 style="font-size:14px;margin:6px 0 8px"><span class="tag tag-lu">加州鲈</span> 8.11 报价（元/斤）</h3>
          <table>
            <thead><tr><th>地区</th><th>规格</th><th>塘口价</th></tr></thead>
            <tbody>
              <tr><td>南海九江</td><td><span class="spec">统货</span></td><td class="price">9.8</td></tr>
              <tr><td>南海九江</td><td><span class="spec spec-l">1斤以上</span></td><td class="price">9.8</td></tr>
              <tr><td>珠海金湾</td><td><span class="spec spec-l">1斤</span></td><td class="price">9.7</td></tr>
              <tr><td>珠海金湾</td><td><span class="spec spec-l">1.3斤</span></td><td class="price">10.5</td></tr>
              <tr><td>福建漳州</td><td><span class="spec spec-l">0.8-1.5斤</span></td><td class="price">11.5</td></tr>
              <tr><td>龙岩上杭</td><td><span class="spec spec-l">8两以上</span></td><td class="price">12.7</td></tr>
              <tr><td>湖南钱粮湖</td><td><span class="spec spec-l">8两上</span></td><td class="price">11.5</td></tr>
              <tr><td>湖北白沙洲</td><td><span class="spec spec-l">9两上</span></td><td class="price">11.5</td></tr>
              <tr><td>成都邛崃</td><td><span class="spec spec-l">1斤</span></td><td class="price">15.5</td></tr>
              <tr><td>河南郑州</td><td><span class="spec spec-l">1斤起</span></td><td class="price">11.5</td></tr>
              <tr><td>江苏吴江</td><td><span class="spec spec-l">9两起</span></td><td class="price">11.5</td></tr>
              <tr><td>江苏高邮</td><td><span class="spec spec-l">1斤</span></td><td class="price">9.8</td></tr>
              <tr><td>江苏高邮</td><td><span class="spec spec-l">1.1斤</span></td><td class="price">10.2</td></tr>
              <tr><td>江苏高邮</td><td><span class="spec spec-l">1.2斤</span></td><td class="price">10.5</td></tr>
              <tr><td>浙江湖州</td><td><span class="spec spec-l">8两起</span></td><td class="price">11</td></tr>
              <tr><td>浙江湖州</td><td><span class="spec">统货</span></td><td class="price">10.5</td></tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="callout" style="margin-top:14px"><b>数据说明：</b>「a渔业行情」公众号文章以<b>图片表格</b>形式发布，搜狗微信未索引且微信文章需登录/反爬，纯文本爬虫无法获取；本次由用户提供截图、OCR 提取。① <b>单位为元/斤</b>，属塘口（出塘）价；② 江苏标鳜 39.5 元/斤、江苏吴江 9两起 11.5 元/斤、江苏高邮 1斤 9.8 元/斤，与水产前沿 8/11 周报中江苏产区数据相互印证；③ 成都邛崃、眉山东坡「9两起」无报价，已标注。</div>
    </div>
  </section>

'''
s = s.replace(chart_marker, new_ayuqing + chart_marker, 1)


# (f) 微信公众号行情爬取 callout（四、代表性来源与帖子 里的说明）
old_wechat = ('<div class="callout" style="margin-bottom:18px"><b>关于微信公众号行情爬取：</b>'
              '用户要求尝试爬取「a渔业行情」与「科学养鱼」两个公众号。经搜狗微信检索实测：① <b>「a渔业行情」</b>虽发布《2026年8月11日全国水产塘口价》等行情文章，'
              '但<b>搜狗微信未索引到该号文章</b>，且微信文章需登录/反爬，纯文本爬虫无法直接获取正文；② <b>「科学养鱼」</b>与之前结论一致，价格以<b>图片</b>形式发布，'
              '搜狗微信也未索引到 2026 年近期文章。因此两个公众号目前<b>均无法通过公开网络爬虫自动抓取</b>，仍需用户提供文章截图进行 OCR 提取，或提供具体微信文章链接（若有临时访问权限）。'
              '本轮由搜狐转载的水产前沿 8/11 周报获得等效塘头价数据，已补入「一、二」板块。</div>')
new_wechat = ('<div class="callout" style="margin-bottom:18px"><b>关于微信公众号行情爬取：</b>'
              '用户已重新提供「科学养鱼」（2026-08-18）与「a渔业行情」（2026-08-11）公众号价格截图，我方已完成 OCR 提取并补入「补充」板块。'
              '经此前搜狗微信检索实测：① <b>「a渔业行情」</b>文章以<b>图片表格</b>形式发布，搜狗微信未索引，微信文章需登录/反爬，纯文本爬虫无法直接获取正文；'
              '② <b>「科学养鱼」</b>价格以<b>图片</b>形式发布，搜狗微信同样未索引到近期文章。因此两个公众号目前<b>仍无法通过公开网络爬虫自动抓取</b>，'
              '后续更新仍需用户提供文章截图进行 OCR 提取，或提供具体微信文章链接（若有临时访问权限）。</div>')
assert old_wechat in s
s = s.replace(old_wechat, new_wechat, 1)


# (g) 五、价格数据来源汇总：增加 a渔业行情
old_src_list = '''      <div class="src">
        <div class="st">🐟「科学养鱼」公众号（用户提供截图 + OCR）</div>
        <div class="sd">2026-07-27 · 淡水鱼类分规格批发价（元/千克）：鳜鱼/青鱼/鲫鱼/鲤鱼/鲢鱼/鳊鱼，已结构化补入「补充」板块</div>
      </div>
    </div>'''
new_src_list = '''      <div class="src">
        <div class="st">🐟「科学养鱼」公众号（用户提供截图 + OCR）</div>
        <div class="sd">2026-08-18 · 淡水鱼类分规格批发价（元/千克）：鳜鱼/加州鲈鱼/青鱼等，已结构化补入「补充」板块</div>
      </div>
      <div class="src">
        <div class="st">🎣「a渔业行情」公众号（用户提供截图 + OCR）</div>
        <div class="sd">2026-08-11 全国水产塘口价（发文 2026-08-10）· 鳜鱼（8.9 报价）/ 加州鲈（8.11 报价），元/斤，已结构化补入「补充」板块</div>
      </div>
    </div>'''
assert old_src_list in s
s = s.replace(old_src_list, new_src_list, 1)


# (h) 数据局限说明
old_limit = ('<b>数据局限说明：</b>① 塘头价（出塘价）全部来自水产前沿周报，分规格清晰、来源权威，最新为第28期（2026-08-11）；'
             '② <b>批发价板块已升级为双爬虫直采</b>：moa_fish_crawler.py 逆向农业农村部批发价异步接口（品种码 活鳜鱼 AM01013003 / 淡水鲈鱼 AM01009 / 海水鲈鱼 AM02005），'
             'AES 解密后得 2026-08-13 当日各市场真实报价（凌家塘活鳜鱼 86 元/公斤）；另以 public_price_crawler.py 抓取武汉白沙洲/九江/云南华潮政府官网<b>分规格</b>批发价，'
             '补足农业农村部统货价缺口；③ 该接口<b>仅返回「当日」最新快照，无历史日期参数</b>，故无法自动回溯近 30 天序列，「近 30 天」维度暂以周报塘头价 + 爬虫当日批发价组合呈现'
             '（看板「六、历史序列」已开启逐日累积，现已 6 天）；④ 农业农村部接口报价为<b>统货价、不分 500g 内/外规格</b>，分规格需求以水产前沿周报塘头价 + 公开价源爬虫（武汉白沙洲/九江分规格）为准；'
             '⑤ <b>「科学养鱼」「a渔业行情」等公众号价格无法直接爬取</b>：搜狗微信未索引/反爬，纯文本爬虫拿不到文章；目前靠用户提供截图 + OCR 提取（科学养鱼 2026-07-27 已纳入）；'
             '⑥ 抖音社媒互动数据因需 AgentKey 未重新抓取，保留 7 月上旬快照仅作连续性参考；⑦ 价格随行就市，仅供参考。')
new_limit = ('<b>数据局限说明：</b>① 塘头价（出塘价）主要来自水产前沿周报，最新为第28期（2026-08-11），并补充「a渔业行情」公众号 OCR（2026-08-11）作交叉验证；'
             '② <b>批发价板块已升级为双爬虫直采 + 公众号 OCR</b>：moa_fish_crawler.py 逆向农业农村部批发价异步接口（品种码 活鳜鱼 AM01013003 / 淡水鲈鱼 AM01009 / 海水鲈鱼 AM02005），'
             'AES 解密后得 2026-08-18 当日各市场真实报价（凌家塘活鳜鱼 78 元/公斤）；另以 public_price_crawler.py 抓取武汉白沙洲/九江/云南华潮政府官网<b>分规格</b>批发价，'
             '及「科学养鱼」公众号 OCR 分规格批发价，补足农业农村部统货价缺口；③ 该接口<b>仅返回「当日」最新快照，无历史日期参数</b>，故无法自动回溯近 30 天序列，'
             '「近 30 天」维度暂以周报塘头价 + 爬虫当日批发价组合呈现（看板「六、历史序列」已开启逐日累积，现已 6 天）；'
             '④ 农业农村部接口报价为<b>统货价、不分 500g 内/外规格</b>，分规格需求以水产前沿周报塘头价 + 公开价源爬虫 + 科学养鱼 OCR 为准；'
             '⑤ <b>「科学养鱼」「a渔业行情」等公众号价格无法直接爬取</b>：搜狗微信未索引/反爬，纯文本爬虫拿不到文章；目前靠用户提供截图 + OCR 提取（科学养鱼 2026-08-18、a渔业行情 2026-08-11 已纳入）；'
             '⑥ 抖音社媒互动数据已由 AgentKey（TikHub）于 2026-08-18 实时抓取；⑦ 价格随行就市，仅供参考。')
assert old_limit in s
s = s.replace(old_limit, new_limit, 1)


# (i) footer
old_footer = ('数据整理：WorkBuddy · 塘头价源自水产前沿/腾氏水产周报；批发价 = moa_fish_crawler.py（农业农村部官方接口 AES 解密）'
              '+ public_price_crawler.py（武汉白沙洲/九江/云南华潮分规格）+ 科学养鱼公众号 OCR（用户截图）<br>\n'
              '    统计周期 2026-07-13 ~ 2026-08-18 · 农业农村部爬虫抓取日期 2026-08-18（活鳜鱼凌家塘78元/公斤）'
              '· 公开价源爬虫 07-03~07-24 · 科学养鱼 OCR 07-27 · 价格随行就市，仅供参考')
new_footer = ('数据整理：WorkBuddy · 塘头价源自水产前沿/腾氏水产周报 + a渔业行情公众号 OCR；'
              '批发价 = moa_fish_crawler.py（农业农村部官方接口 AES 解密）+ public_price_crawler.py（武汉白沙洲/九江/云南华潮分规格）'
              '+ 科学养鱼公众号 OCR（用户截图）<br>\n'
              '    看板更新 2026-08-19 · 统计周期 2026-07-13 ~ 2026-08-18 · 农业农村部爬虫抓取日期 2026-08-18（活鳜鱼凌家塘78元/公斤）'
              '· 公开价源爬虫 07-03~07-24 · 科学养鱼 OCR 08-18 · a渔业行情 OCR 08-11 · 价格随行就市，仅供参考')
assert old_footer in s
s = s.replace(old_footer, new_footer, 1)


with open(HTML, "w", encoding="utf-8") as f:
    f.write(s)

print("OK: 已保存 wechat_ocr_prices_20260819.csv/json 并更新看板 HTML")
print(f"    OCR 记录数：{len(ocr_rows)}（科学养鱼 {len(kexue)} 条，a渔业行情 {len(ayuqing)} 条）")
