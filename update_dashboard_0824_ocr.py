#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8/24 公众号截图 OCR 数据入看板
- 科学养鱼：2026-08-21 全国水产品批发价（元/千克）
- a渔业行情：8.19 报价（元/斤），发文 2026-08-19
"""
import csv, json, re
from pathlib import Path

ROOT = Path(__file__).parent

# ---------- 1. 结构化 OCR 数据 ----------
ocr_rows = []

# 科学养鱼 2026-08-21（元/千克）
science_fish = [
    ("鳜鱼（桂花鱼）", "山西太原五龙口海鲜市场", "500≤条重<750g", 65.00),
    ("鳜鱼（桂花鱼）", "上海江杨水产品批发市场经营管理有限公司", "500≤条重<750g", 102.00),
    ("鳜鱼（桂花鱼）", "湖北宜昌三峡物流园有限公司水产市场", "250≤条重<500g", 80.00),
    ("鳜鱼（桂花鱼）", "湖北宜昌三峡物流园有限公司水产市场", "500≤条重<750g", 100.00),
    ("鳜鱼（桂花鱼）", "湖北省武汉市白沙洲农副产品大市场", "250≤条重<500g", 87.00),
    ("鳜鱼（桂花鱼）", "湖北省武汉市白沙洲农副产品大市场", "500≤条重<750g", 99.00),
]
for species, market, spec, price in science_fish:
    ocr_rows.append({
        "source": "科学养鱼",
        "article_date": "2026-08-21",
        "price_date": "2026-08-21",
        "species": species,
        "market": market,
        "spec": spec,
        "price": price,
        "unit": "元/千克",
        "note": "",
    })

# a渔业行情 8.19 报价（元/斤）
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
csv_path = ROOT / "wechat_ocr_prices_20260824.csv"
json_path = ROOT / "wechat_ocr_prices_20260824.json"
fieldnames = ["source", "article_date", "price_date", "species", "market", "spec", "price", "unit", "note"]
with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(ocr_rows)
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(ocr_rows, f, ensure_ascii=False, indent=2)

print(f"[OK] wrote {csv_path.name}: {len(ocr_rows)} rows")

# ---------- 2. 替换看板 HTML 中公众号 OCR 板块 ----------
html_path = ROOT / "鳜鱼鲈鱼价格看板.html"
text = html_path.read_text(encoding="utf-8")

# 2.1 科学养鱼板块：整段替换
science_old = re.search(
    r'<!-- 科学养鱼公众号 OCR 数据 -->.*?<!-- /科学养鱼公众号 OCR 数据 -->',
    text, re.S
)
if not science_old:
    # 兼容没有结束标记的旧版：找到下一个 section 开始
    science_old = re.search(
        r'<!-- 科学养鱼公众号 OCR 数据 -->.*?(?=<!-- a渔业行情公众号 OCR 数据 -->)',
        text, re.S
    )

science_new = '''<!-- 科学养鱼公众号 OCR 数据 -->
  <section>
    <div class="sec-head">
      <span class="bar" style="background:#7c3aed"></span>
      <h2>补充 · 「科学养鱼」公众号批发价（OCR 提取）</h2>
      <span class="note">2026-08-21 · 元/千克 · 已按图片数字录入</span>
    </div>
    <div class="card">
      <h3>🌟 科学养鱼公众号 全国水产品批发价</h3>
      <div class="csub">来源：用户提供的「科学养鱼」公众号价格截图（截屏2026-08-24 16.34.14），单位<b>元/千克</b>；由 OCR 提取，发布日期 2026-08-21。本次截图仅包含鳜鱼（桂花鱼）条目。</div>
      <table>
        <thead><tr><th>市场</th><th>规格</th><th>价格（元/千克）</th></tr></thead>
        <tbody>
          <tr><td>山西太原五龙口海鲜市场</td><td><span class="spec spec-l">500≤条重<750g</span></td><td class="price">65.00</td></tr>
          <tr><td>上海江杨水产品批发市场经营管理有限公司</td><td><span class="spec spec-l">500≤条重<750g</span></td><td class="price">102.00</td></tr>
          <tr><td>湖北宜昌三峡物流园有限公司水产市场</td><td><span class="spec spec-s">250≤条重<500g</span></td><td class="price">80.00</td></tr>
          <tr><td>湖北宜昌三峡物流园有限公司水产市场</td><td><span class="spec spec-l">500≤条重<750g</span></td><td class="price">100.00</td></tr>
          <tr><td>湖北省武汉市白沙洲农副产品大市场</td><td><span class="spec spec-s">250≤条重<500g</span></td><td class="price">87.00</td></tr>
          <tr><td>湖北省武汉市白沙洲农副产品大市场</td><td><span class="spec spec-l">500≤条重<750g</span></td><td class="price">99.00</td></tr>
        </tbody>
      </table>
      <div class="callout" style="margin-top:14px"><b>数据说明：</b>该公众号价格以<b>图片</b>形式发布，纯文本爬虫取不到数字；本次由用户提供截图、我方 OCR 提取后录入。① 单位已确认为<b>元/千克</b>；② 上海江杨 500–750g 鳜鱼 102 元/公斤、武汉白沙洲 99 元/公斤，显著高于太原/宜昌，反映区域与品质差异；③ 发布日期 2026-08-21，与农业农村部爬虫 08-18 快照（凌家塘 78 元/公斤）可作最新交叉参考；④ 历史截图数据（加州鲈、青鱼等）仍保留于 <code>wechat_ocr_prices_20260819.csv</code>。</div>
    </div>
  </section>
  <!-- /科学养鱼公众号 OCR 数据 -->'''

if science_old:
    text = text[:science_old.start()] + science_new + text[science_old.end():]
    print("[OK] replaced 科学养鱼 section")
else:
    print("[WARN] 科学养鱼 section not found")

# 2.2 a渔业行情板块：整段替换
afish_old = re.search(
    r'<!-- a渔业行情公众号 OCR 数据 -->.*?(?=<!-- 图表 -->)',
    text, re.S
)

afish_new = '''<!-- a渔业行情公众号 OCR 数据 -->
  <section>
    <div class="sec-head">
      <span class="bar" style="background:#059669"></span>
      <h2>补充 · 「a渔业行情」公众号塘口价（OCR 提取）</h2>
      <span class="note">2026-08-19 全国水产塘口价 · 元/斤</span>
    </div>
    <div class="card">
      <h3>🎣 a渔业行情公众号 分产区塘口价</h3>
      <div class="csub">来源：用户提供的「a渔业行情」公众号文章截图（截屏2026-08-24 16.33.22 / 16.33.31），由 OCR 提取。鳜鱼与加州鲈报价日期均为 <b>8.19</b>；<b>单位元/斤</b>，属塘口/出塘价，与批发价不可直接比较。</div>
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
      <div class="callout" style="margin-top:14px"><b>数据说明：</b>「a渔业行情」公众号文章以<b>图片表格</b>形式发布，搜狗微信未索引且微信文章需登录/反爬，纯文本爬虫无法获取；本次由用户提供截图、OCR 提取。① <b>单位为元/斤</b>，属塘口（出塘）价；② 广东佛山小规格（6–9两）标注为「/」，表示当日无报价；③ 江苏标鳜 38.5 元/斤、江苏 9两上 10–10.5 元/斤，与水产前沿 8/11 周报中江苏产区数据基本持稳；④ 历史截图数据（08-11）仍保留于 <code>wechat_ocr_prices_20260819.csv</code>。</div>
    </div>
  </section>
'''

if afish_old:
    text = text[:afish_old.start()] + afish_new + text[afish_old.end():]
    print("[OK] replaced a渔业行情 section")
else:
    print("[WARN] a渔业行情 section not found")

# ---------- 3. 更新顶部与来源汇总、footer 日期 ----------
replacements = [
    # 标题/周期
    ("统计周期：2026-07-13 ~ 2026-08-18", "统计周期：2026-07-13 ~ 2026-08-24"),
    ("科学养鱼OCR（08-18）", "科学养鱼OCR（08-21）+ a渔业行情OCR（08-19）"),
    # 来源汇总卡片
    ("2026-08-18 · 淡水鱼类分规格批发价（元/千克）：鳜鱼/加州鲈鱼/青鱼等，已结构化补入「补充」板块",
     "2026-08-21 · 全国水产品批发价（元/千克）：鳜鱼（桂花鱼）分市场分规格，已结构化补入「补充」板块"),
    ("2026-08-11 全国水产塘口价（发文 2026-08-10）· 鳜鱼（8.9 报价）/ 加州鲈（8.11 报价），元/斤，已结构化补入「补充」板块",
     "2026-08-19 全国水产塘口价 · 鳜鱼/加州鲈（8.19 报价），元/斤，已结构化补入「补充」板块"),
    # 数据局限说明
    ("目前靠用户提供截图 + OCR 提取（科学养鱼 2026-08-18、a渔业行情 2026-08-11 已纳入）",
     "目前靠用户提供截图 + OCR 提取（科学养鱼 2026-08-21、a渔业行情 2026-08-19 已纳入；08-18/08-11 历史数据仍保留）"),
    # footer
    ("看板更新 2026-08-19 · 统计周期 2026-07-13 ~ 2026-08-18", "看板更新 2026-08-24 · 统计周期 2026-07-13 ~ 2026-08-24"),
    ("科学养鱼 OCR 08-18 · a渔业行情 OCR 08-11", "科学养鱼 OCR 08-21 · a渔业行情 OCR 08-19"),
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new)
        print(f"[OK] replaced: {old[:40]}...")
    else:
        print(f"[WARN] not found: {old[:40]}...")

html_path.write_text(text, encoding="utf-8")
print("[OK] dashboard HTML saved")
