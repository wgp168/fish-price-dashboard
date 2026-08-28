#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8/28 综合更新：
- 运行 MOA/public 爬虫（外部已执行）
- OCR 新截图：科学养鱼 08-27 + a渔业行情 8.19
- 新增「主要信息发布渠道清单」板块
- 更新看板日期与说明
"""
import csv, json, re
from pathlib import Path

ROOT = Path(__file__).parent

# ---------- 1. 结构化 OCR 数据 ----------
ocr_rows = []

# 科学养鱼 2026-08-27（元/千克）
science_fish = [
    ("鳜鱼（桂花鱼）", "北京大红门京深海鲜批发市场有限公司", "条重≥750g", 72.00),
    ("鳜鱼（桂花鱼）", "江苏省苏州市南环桥农副产品批发市场", "250≤条重<500g", 78.00),
    ("鳜鱼（桂花鱼）", "江苏省苏州市南环桥农副产品批发市场", "500≤条重<750g", 94.00),
    ("鳜鱼（桂花鱼）", "湖北宜昌三峡物流园有限公司水产市场", "250≤条重<500g", 76.00),
    ("鳜鱼（桂花鱼）", "湖北宜昌三峡物流园有限公司水产市场", "500≤条重<750g", 100.00),
    ("加州鲈鱼", "湖州菱湖乌板桥水产品批发市场", "条重≥500g", 25.00),
    ("加州鲈鱼", "湖州菱湖乌板桥水产品批发市场", "条重<500g", 22.40),
    ("加州鲈鱼", "广州黄沙水产交易市场有限公司", "条重≥500g", 26.00),
    ("加州鲈鱼", "江西省萍乡市城南水产批发市场", "条重≥500g", 31.00),
    ("加州鲈鱼", "北京京丰岳各庄农副产品批发市场中心", "条重≥500g", 28.40),
]
for species, market, spec, price in science_fish:
    ocr_rows.append({
        "source": "科学养鱼",
        "article_date": "2026-08-27",
        "price_date": "2026-08-27",
        "species": species,
        "market": market,
        "spec": spec,
        "price": price,
        "unit": "元/千克",
        "note": "",
    })

# a渔业行情 8.19 报价（元/斤）——两张截图均为 8.19
afish_gui = [
    ("鳜鱼", "广东地区", "小鳜（0.8斤以下）", 34.0),
    ("鳜鱼", "广东地区", "标鳜（0.8-1.5斤）", 40.5),
    ("鳜鱼", "广东地区", "中鳜（1.5斤以上）", 40.5),
    ("鳜鱼", "湖北地区", "标鳜", 40.0),
    ("鳜鱼", "安徽地区", "标鳜", 38.5),
    ("鳜鱼", "江西地区", "标鳜", 37.5),
    ("鳜鱼", "湖南地区", "标鳜", 38.0),
    ("鳜鱼", "江苏地区", "标鳜", 38.5),
]
afish_lu = [
    ("加州鲈", "广东佛山", "1斤上", 9.5),
    ("加州鲈", "湖北", "8.5两上", "10-10.5"),
    ("加州鲈", "四川", "9两上", 13.0),
    ("加州鲈", "四川", "1斤上", 14.0),
    ("加州鲈", "江苏", "9两上", "10-10.5"),
    ("加州鲈", "河南", "1斤起", "10.5-11"),
    ("加州鲈", "浙江", "8成统货", "11-11.5"),
    ("加州鲈", "湖南", "9两上", 10.5),
]
for species, market, spec, price in afish_gui + afish_lu:
    ocr_rows.append({
        "source": "a渔业行情",
        "article_date": "2026-08-19",
        "price_date": "2026-08-19",
        "species": species,
        "market": market,
        "spec": spec,
        "price": price,
        "unit": "元/斤",
        "note": "",
    })

# 写入 CSV / JSON
csv_path = ROOT / "wechat_ocr_prices_20260828.csv"
json_path = ROOT / "wechat_ocr_prices_20260828.json"
fieldnames = ["source", "article_date", "price_date", "species", "market", "spec", "price", "unit", "note"]
with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(ocr_rows)
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(ocr_rows, f, ensure_ascii=False, indent=2)
print(f"[OK] wrote {csv_path.name}: {len(ocr_rows)} rows")

# ---------- 2. 读入并更新 HTML ----------
html_path = ROOT / "鳜鱼鲈鱼价格看板.html"
text = html_path.read_text(encoding="utf-8")

# 2.1 顶部周期 / chip 日期
replacements = [
    ("统计周期：2026-07-13 ~ 2026-08-24", "统计周期：2026-07-13 ~ 2026-08-28"),
    ("批发价：农业农村部接口爬虫（2026-08-18）+ 公开价源爬虫 + 科学养鱼OCR（08-21）+ a渔业行情OCR（08-19）",
     "批发价：农业农村部接口爬虫（2026-08-28，活鳜鱼当日无报价）+ 公开价源爬虫 + 科学养鱼OCR（08-27）+ a渔业行情OCR（08-19）"),
]
for old, new in replacements:
    if old in text:
        text = text.replace(old, new)
        print(f"[OK] replaced meta: {old[:50]}...")
    else:
        print(f"[WARN] meta not found: {old[:50]}...")

# 2.2 鳜鱼批发价板块：标题 + 说明 + 当日无报价提示
old_title = "<h3><span class=\"tag tag-gui\">鳜鱼</span> 批发价（农业农村部接口爬虫 · 2026-08-18）</h3>"
new_title = "<h3><span class=\"tag tag-gui\">鳜鱼</span> 批发价（农业农村部接口爬虫 · 2026-08-28）</h3>"
if old_title in text:
    text = text.replace(old_title, new_title)

old_callout = '''<div class="callout" style="margin-top:14px"><b>数据说明：</b>本表由爬虫直连农业农村部官方批发价接口（品种码 <b>AM01013003</b>）解密所得，<b>抓取日期 2026-08-18</b>。江苏凌家塘活鳜鱼 <b>78 元/公斤</b>，较 8/13 的 86 继续回落 8、回到 7/27 水平，与水产前沿 8/11 周报「新鱼上市、暴涨势头被遏制」趋势延续一致；流通加价约 0–15 元/公斤（塘头价 39–43 元/斤≈78–86 元/公斤）。另见「补充·科学养鱼」板块 08-21 全国多市场分规格鳜鱼及「补充·公开价源爬虫」板块 武汉白沙洲/九江分规格鳜鱼可作交叉参考。</div>'''
new_callout = '''<div class="callout" style="margin-top:14px"><b>数据说明：</b>本表由爬虫直连农业农村部官方批发价接口（品种码 <b>AM01013003</b>）解密所得，<b>最新抓取日期 2026-08-28</b>。2026-08-28 当日活鳜鱼接口返回 <b>data=null</b>，无新报价；上一条有效报价仍为 2026-08-18 江苏凌家塘 <b>78 元/公斤</b>。表中保留 08-18 全国样本作参考。另见「补充·科学养鱼」板块 08-27 全国多市场分规格鳜鱼及「补充·公开价源爬虫」板块 武汉白沙洲/九江分规格鳜鱼可作交叉参考。</div>'''
if old_callout in text:
    text = text.replace(old_callout, new_callout)
    print("[OK] replaced 鳜鱼批发价说明")
else:
    print("[WARN] 鳜鱼批发价说明 not found")

# 2.3 鲈鱼批发价板块：标题 + 说明（8/28 有更新）
old_lu_title = "<h3><span class=\"tag tag-lu\">鲈鱼</span> 批发价（农业农村部接口爬虫 · 2026-08-18）</h3>"
new_lu_title = "<h3><span class=\"tag tag-lu\">鲈鱼</span> 批发价（农业农村部接口爬虫 · 2026-08-28）</h3>"
if old_lu_title in text:
    text = text.replace(old_lu_title, new_lu_title)

# 更新鲈鱼批发价表格中的马鞍山 20→21
old_mas = '<tr><td>马鞍山 安民农贸</td><td><span class="spec spec-s">淡水鲈鱼</span></td><td class="price">20 <small>元/公斤</small></td><td>≈ 10</td></tr>'
new_mas = '<tr><td>马鞍山 安民农贸</td><td><span class="spec spec-s">淡水鲈鱼</span></td><td class="price">21 <small>元/公斤</small></td><td>≈ 10.5</td></tr>'
if old_mas in text:
    text = text.replace(old_mas, new_mas)

old_lu_callout = '''<div class="csub" style="margin-top:14px">※ 2026-08-18 爬虫实测：海水鲈鱼凌家塘 27 / 南环桥 23.5 / 合肥周谷堆 22.5（与 7 月持平），淡水鲈鱼马鞍山安民 20（较 7/27 的 22 回落）、云南华潮 35、长治紫坊 33 元/公斤；海水鲈鱼青岛城阳 36（较 8/13 的 44 回落）、北京大洋路 31、山东滨州 26、甘肃酒泉 59 等市场（均为统货、不分规格）。接口区分「淡水鲈鱼」与「海水鲈鱼」两个品种码。鲈鱼整体低位运行，与水产前沿 8/11 周报「外省产区稳中有跌」一致。</div>'''
new_lu_callout = '''<div class="csub" style="margin-top:14px">※ 2026-08-28 爬虫实测：海水鲈鱼凌家塘 27 / 南环桥 23.5 / 合肥周谷堆 22.5（与 7 月持平），淡水鲈鱼马鞍山安民 <b>21</b>（较 08-18 的 20 略涨 1）、云南华潮 35、长治紫坊 31 元/公斤；海水鲈鱼青岛城阳 36、北京大洋路 31、山东滨州 26、甘肃酒泉 59、山东威海 40、重庆西三街 43、河南万邦 29 等市场（均为统货、不分规格）。接口区分「淡水鲈鱼」与「海水鲈鱼」两个品种码。鲈鱼整体低位运行，略有企稳。</div>'''
if old_lu_callout in text:
    text = text.replace(old_lu_callout, new_lu_callout)
    print("[OK] replaced 鲈鱼批发价说明")
else:
    print("[WARN] 鲈鱼批发价说明 not found")

# 2.4 替换科学养鱼板块
sci_old = re.search(r'<!-- 科学养鱼公众号 OCR 数据 -->.*?<!-- /科学养鱼公众号 OCR 数据 -->', text, re.S)
if not sci_old:
    sci_old = re.search(r'<!-- 科学养鱼公众号 OCR 数据 -->.*?(?=<!-- a渔业行情公众号 OCR 数据 -->)', text, re.S)

sci_new = '''<!-- 科学养鱼公众号 OCR 数据 -->
  <section>
    <div class="sec-head">
      <span class="bar" style="background:#7c3aed"></span>
      <h2>补充 · 「科学养鱼」公众号批发价（OCR 提取）</h2>
      <span class="note">2026-08-27 · 元/千克 · 已按图片数字录入</span>
    </div>
    <div class="card">
      <h3>🌟 科学养鱼公众号 全国水产品批发价</h3>
      <div class="csub">来源：用户提供的「科学养鱼」公众号价格截图（截屏2026-08-28 09.33.50），单位<b>元/千克</b>；由 OCR 提取，发布日期 2026-08-27。本次截图包含鳜鱼（桂花鱼）与加州鲈鱼条目。</div>
      <div class="grid2">
        <div>
          <h3 style="font-size:14px;margin:6px 0 8px"><span class="tag tag-gui">鳜鱼</span> 桂花鱼 批发价（元/千克）</h3>
          <table>
            <thead><tr><th>市场</th><th>规格</th><th>价格</th></tr></thead>
            <tbody>
              <tr><td>北京大红门京深海鲜</td><td><span class="spec spec-l">条重≥750g</span></td><td class="price">72.00</td></tr>
              <tr><td>江苏苏州南环桥</td><td><span class="spec spec-s">250≤条重<500g</span></td><td class="price">78.00</td></tr>
              <tr><td>江苏苏州南环桥</td><td><span class="spec spec-l">500≤条重<750g</span></td><td class="price">94.00</td></tr>
              <tr><td>湖北宜昌三峡物流园</td><td><span class="spec spec-s">250≤条重<500g</span></td><td class="price">76.00</td></tr>
              <tr><td>湖北宜昌三峡物流园</td><td><span class="spec spec-l">500≤条重<750g</span></td><td class="price">100.00</td></tr>
            </tbody>
          </table>
        </div>
        <div>
          <h3 style="font-size:14px;margin:6px 0 8px"><span class="tag tag-lu">加州鲈鱼</span> 批发价（元/千克）</h3>
          <table>
            <thead><tr><th>市场</th><th>规格</th><th>价格</th></tr></thead>
            <tbody>
              <tr><td>湖州菱湖乌板桥</td><td><span class="spec spec-l">条重≥500g</span></td><td class="price">25.00</td></tr>
              <tr><td>湖州菱湖乌板桥</td><td><span class="spec spec-s">条重<500g</span></td><td class="price">22.40</td></tr>
              <tr><td>广州黄沙水产</td><td><span class="spec spec-l">条重≥500g</span></td><td class="price">26.00</td></tr>
              <tr><td>江西萍乡城南水产</td><td><span class="spec spec-l">条重≥500g</span></td><td class="price">31.00</td></tr>
              <tr><td>北京京丰岳各庄</td><td><span class="spec spec-l">条重≥500g</span></td><td class="price">28.40</td></tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="callout" style="margin-top:14px"><b>数据说明：</b>该公众号价格以<b>图片</b>形式发布，纯文本爬虫取不到数字；本次由用户提供截图、我方 OCR 提取后录入。① 单位已确认为<b>元/千克</b>；② 苏州南环桥 500–750g 鳜鱼 94 元/公斤、宜昌三峡 100 元/公斤，与 08-21 同市场报价基本一致；③ 加州鲈湖州菱湖分规格 25 / 22.4 元/公斤，可与农业农村部统货口径互补；④ 历史截图数据仍保留于 <code>wechat_ocr_prices_20260819.csv</code> / <code>20260824.csv</code>。</div>
    </div>
  </section>
  <!-- /科学养鱼公众号 OCR 数据 -->'''

if sci_old:
    text = text[:sci_old.start()] + sci_new + text[sci_old.end():]
    print("[OK] replaced 科学养鱼 section")
else:
    print("[WARN] 科学养鱼 section not found")

# 2.5 替换 a渔业行情板块
afish_old = re.search(r'<!-- a渔业行情公众号 OCR 数据 -->.*?(?=<!-- 图表 -->)', text, re.S)
afish_new = '''<!-- a渔业行情公众号 OCR 数据 -->
  <section>
    <div class="sec-head">
      <span class="bar" style="background:#059669"></span>
      <h2>补充 · 「a渔业行情」公众号塘口价（OCR 提取）</h2>
      <span class="note">2026-08-19 全国水产塘口价 · 元/斤</span>
    </div>
    <div class="card">
      <h3>🎣 a渔业行情公众号 分产区塘口价</h3>
      <div class="csub">来源：用户提供的「a渔业行情」公众号文章截图（截屏2026-08-28 09.34.48 / 09.35.00），由 OCR 提取。鳜鱼与加州鲈报价日期均为 <b>8.19</b>；<b>单位元/斤</b>，属塘口（出塘）价，与批发价不可直接比较。</div>
      <div class="grid2">
        <div>
          <h3 style="font-size:14px;margin:6px 0 8px"><span class="tag tag-gui">鳜鱼</span> 8.19 报价（元/斤）</h3>
          <table>
            <thead><tr><th>地区</th><th>规格</th><th>塘口价</th></tr></thead>
            <tbody>
              <tr><td>广东地区</td><td><span class="spec spec-s">小鳜（0.8斤以下）</span></td><td class="price">34</td></tr>
              <tr><td>广东地区</td><td><span class="spec spec-l">标鳜（0.8-1.5斤）</span></td><td class="price">40.5</td></tr>
              <tr><td>广东地区</td><td><span class="spec spec-l">中鳜（1.5斤以上）</span></td><td class="price">40.5</td></tr>
              <tr><td>湖北地区</td><td><span class="spec spec-l">标鳜</span></td><td class="price">40</td></tr>
              <tr><td>安徽地区</td><td><span class="spec spec-l">标鳜</span></td><td class="price">38.5</td></tr>
              <tr><td>江西地区</td><td><span class="spec spec-l">标鳜</span></td><td class="price">37.5</td></tr>
              <tr><td>湖南地区</td><td><span class="spec spec-l">标鳜</span></td><td class="price">38</td></tr>
              <tr><td>江苏地区</td><td><span class="spec spec-l">标鳜</span></td><td class="price">38.5</td></tr>
            </tbody>
          </table>
        </div>
        <div>
          <h3 style="font-size:14px;margin:6px 0 8px"><span class="tag tag-lu">加州鲈</span> 8.19 报价（元/斤）</h3>
          <table>
            <thead><tr><th>地区</th><th>规格</th><th>塘口价</th></tr></thead>
            <tbody>
              <tr><td>广东佛山</td><td><span class="spec spec-l">1斤上</span></td><td class="price">9.5</td></tr>
              <tr><td>湖北</td><td><span class="spec spec-s">8.5两上</span></td><td class="price">10–10.5</td></tr>
              <tr><td>四川</td><td><span class="spec spec-s">9两上</span></td><td class="price">13</td></tr>
              <tr><td>四川</td><td><span class="spec spec-l">1斤上</span></td><td class="price">14</td></tr>
              <tr><td>江苏</td><td><span class="spec spec-s">9两上</span></td><td class="price">10–10.5</td></tr>
              <tr><td>河南</td><td><span class="spec spec-l">1斤起</span></td><td class="price">10.5–11</td></tr>
              <tr><td>浙江</td><td><span class="spec">8成统货</span></td><td class="price">11–11.5</td></tr>
              <tr><td>湖南</td><td><span class="spec spec-s">9两上</span></td><td class="price">10.5</td></tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="callout" style="margin-top:14px"><b>数据说明：</b>「a渔业行情」公众号文章以<b>图片表格</b>形式发布，搜狗微信未索引且微信文章需登录/反爬，纯文本爬虫无法直接获取正文；本次由用户提供截图、OCR 提取。① <b>单位为元/斤</b>，属塘口（出塘）价；② 广东佛山小规格（6–9两）标注为「/」，表示当日无报价；③ 江苏标鳜 38.5 元/斤、江苏 9两上 10–10.5 元/斤，与水产前沿 8/11 周报中江苏产区数据基本持稳；④ 历史截图数据（08-11）仍保留于 <code>wechat_ocr_prices_20260819.csv</code>。</div>
    </div>
  </section>
'''

if afish_old:
    text = text[:afish_old.start()] + afish_new + text[afish_old.end():]
    print("[OK] replaced a渔业行情 section")
else:
    print("[WARN] a渔业行情 section not found")

# 2.6 来源汇总、数据局限、footer 日期
replacements2 = [
    ("2026-08-21 · 全国水产品批发价（元/千克）：鳜鱼（桂花鱼）分市场分规格，已结构化补入「补充」板块",
     "2026-08-27 · 全国水产品批发价（元/千克）：鳜鱼（桂花鱼）+ 加州鲈鱼分市场分规格，已结构化补入「补充」板块"),
    ("并补充「a渔业行情」公众号 OCR（2026-08-19）作交叉验证；",
     "并补充「a渔业行情」公众号 OCR（2026-08-19 塘口价）作交叉验证；"),
    ("科学养鱼 2026-08-21、a渔业行情 2026-08-19 已纳入；08-18/08-11 历史数据仍保留",
     "科学养鱼 2026-08-27、a渔业行情 2026-08-19 已纳入；08-21/08-18/08-11 历史数据仍保留"),
    ("看板更新 2026-08-24 · 统计周期 2026-07-13 ~ 2026-08-24",
     "看板更新 2026-08-28 · 统计周期 2026-07-13 ~ 2026-08-28"),
    ("科学养鱼 OCR 08-21 · a渔业行情 OCR 08-19",
     "科学养鱼 OCR 08-27 · a渔业行情 OCR 08-19 · MOA爬虫 08-28"),
]
for old, new in replacements2:
    if old in text:
        text = text.replace(old, new)
        print(f"[OK] replaced: {old[:45]}...")
    else:
        print(f"[WARN] not found: {old[:45]}...")

html_path.write_text(text, encoding="utf-8")
print("[OK] dashboard HTML saved")
