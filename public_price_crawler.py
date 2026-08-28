#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公开水产批发价爬虫（政府/市场官网，结构化 HTML 表格，可程序化抓取）
==============================================================
与 moa_fish_crawler.py（农业农村部官方接口）互补：
  - 农业农村部接口：全国主要批发市场「当日快照」、统货价、不分规格；
  - 本脚本    ：地方农业农村局/市场官网发布的「分规格」批发价（含最高/最低），
               来源权威、可批量化抓取，正好补足农业农村部「不分规格」的缺口。

当前覆盖来源：
  1) 武汉市农业农村局 · 白沙洲市场    （分规格，含最高/最低价）
  2) 九江市农业农村局 · 水产品价格采集表（分规格，单值）
  3) 昆明市农业农村局 · 云南华潮水产批发市场（单值，元/千克）
  4) 北京新发地市场 · 每日价格行情 API（分规格 低/均/高价，元/斤 → 转元/公斤）
     ※ 上海江杨的权威实时价在上蔬云采微信小程序（无开放网页接口），
       目前由「科学养鱼」公众号截图经 OCR 流水线覆盖（见 wechat_ocr_pipeline.py）。

输出：public_fish_prices.csv / public_fish_prices.json
      字段：来源, 发布日期, 品种, 规格, 价格_元公斤, 价格区间, 备注

用法：
  python public_price_crawler.py            # 抓取 + 写文件
"""
import urllib.request, ssl, json, os, csv, sys, re, urllib.parse
try:
    from bs4 import BeautifulSoup
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "beautifulsoup4", "lxml"])
    from bs4 import BeautifulSoup

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

# 关注品种（含别名归一）
TARGET = {
    "鳜鱼": ["鳜鱼", "桂花鱼", "桂鱼"],
    "鲈鱼": ["鲈鱼", "花鲈"],
    "青鱼": ["青鱼"],
    "鲫鱼": ["鲫鱼"],
    "鲤鱼": ["鲤鱼"],
    "鲢鱼": ["鲢鱼", "鲢子鱼"],
    "鳊鱼": ["鳊鱼"],
    "鳙鱼(花鲢)": ["花鲢", "鳙鱼", "胖头鱼"],
}

SOURCES = {
    "武汉白沙洲市场": {
        "url": "https://nyncj.wuhan.gov.cn/zwgk_25/fdzdgknr/snsj/scppfjg/202607/t20260703_2816549.html",
        "date": "2026-07-03",
    },
    "九江市农业农村局": {
        "url": "https://nyncj.jiujiang.gov.cn/zwgk_203/zdly/tjxx/ncpscjgxq/202607/t20260724_7279637.html",
        "date": "2026-07-24",
    },
    "云南华潮水产批发市场": {
        "url": "https://nyncj.km.gov.cn/c/2026-07-16/5097406.shtml",
        "date": "2026-07-16",
    },
}


def fetch(u: str) -> str:
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}, method="GET")
    return urllib.request.urlopen(req, timeout=20, context=CTX).read().decode("utf-8", "ignore")


def norm_species(name: str):
    for std, aliases in TARGET.items():
        for a in aliases:
            if a in name:
                return std
    return None


def parse_wuhan(soup) -> list:
    """市场名称/水产名称/等级规格/最高价/最低价/上报时间"""
    out = []
    for tbl in soup.find_all("table"):
        for tr in tbl.find_all("tr"):
            c = [x.get_text(strip=True) for x in tr.find_all(["td", "th"])]
            if len(c) < 5:
                continue
            species, spec, hi, lo = c[1], c[2], c[3], c[4]
            std = norm_species(species)
            if not std:
                continue
            try:
                hi_f, lo_f = float(hi), float(lo)
            except ValueError:
                continue
            if hi_f == 0 and lo_f == 0:
                continue
            avg = round((hi_f + lo_f) / 2, 2)
            out.append({
                "来源": "武汉白沙洲市场", "发布日期": "2026-07-03",
                "品种": std, "规格": spec, "价格_元公斤": avg,
                "价格区间": f"{lo_f}~{hi_f}", "备注": "最高/最低均价",
            })
    return out


def parse_jiujiang(soup) -> list:
    """品种/规格/价格（单值）"""
    out = []
    for tbl in soup.find_all("table"):
        for tr in tbl.find_all("tr"):
            c = [x.get_text(strip=True) for x in tr.find_all(["td", "th"])]
            if len(c) < 3:
                continue
            species, spec, price = c[0], c[1], c[2]
            std = norm_species(species)
            if not std:
                continue
            m = re.search(r"[\d.]+", price)
            if not m:
                continue
            out.append({
                "来源": "九江市农业农村局", "发布日期": "2026-07-24",
                "品种": std, "规格": spec, "价格_元公斤": float(m.group()),
                "价格区间": "", "备注": "单值",
            })
    return out


def parse_huachao(soup) -> list:
    """序号/品种/价格-元-千克/交易量（首行为标题，需跳过非数据行）"""
    out = []
    for tbl in soup.find_all("table"):
        for tr in tbl.find_all("tr"):
            c = [x.get_text(strip=True) for x in tr.find_all(["td", "th"])]
            if len(c) < 3:
                continue
            species, price = c[1], c[2]
            if species in ("品种",) or not re.search(r"[\d.]+", price):
                continue
            std = norm_species(species)
            if not std:
                continue
            out.append({
                "来源": "云南华潮水产批发市场", "发布日期": "2026-07-16",
                "品种": std, "规格": "统货", "价格_元公斤": float(re.search(r"[\d.]+", price).group()),
                "价格区间": "", "备注": "统货价",
            })
    return out


def post_xinfadi(data: dict) -> dict:
    """调用新发地 /getPriceData.html 接口（form 表单，返回 JSON 列表）"""
    url = "http://xinfadi.com.cn:8099/getPriceData.html"
    req = urllib.request.Request(
        url, data=urllib.parse.urlencode(data).encode("utf-8"),
        headers={"User-Agent": "Mozilla/5.0",
                 "Content-Type": "application/x-www-form-urlencoded"},
        method="POST")
    raw = urllib.request.urlopen(req, timeout=25, context=CTX).read().decode("utf-8", "ignore")
    return json.loads(raw)


def parse_xinfadi() -> list:
    """北京新发地每日价格行情（水产分类 cat=1190）。
    站点单位为「元/斤」，统一 ×2 换算为「元/公斤」以对齐看板口径。
    鳜鱼在新发地登记为「桂鱼」；鲈鱼含「淡水鲈鱼/海鲈鱼」两类。
    """
    out = []
    # query 词 -> 标准品种
    for q, std in (("桂鱼", "鳜鱼"), ("鲈鱼", "鲈鱼")):
        data = {"limit": "200", "current": "1", "pubDateStartTime": "",
                "pubDateEndTime": "", "prodPcatid": "1190", "prodCatid": "",
                "prodName": q, "selectClassId": ""}
        try:
            j = post_xinfadi(data)
        except Exception as e:
            print(f"[WARN] 新发地 {q} 接口失败: {e}", file=sys.stderr)
            continue
        rows = j.get("list", [])
        if not rows:
            continue
        latest = rows[0]["pubDate"][:10]          # 接口按日期倒序
        for it in rows:
            if it["pubDate"][:10] != latest:
                break
            pn = it.get("prodName", "")
            spec = it.get("specInfo", "") or "统货"
            if "海" in pn:
                spec2 = f"海水 {spec}"
            elif "淡" in pn:
                spec2 = f"淡水 {spec}"
            else:
                spec2 = spec
            try:
                lo = float(it["lowPrice"]) * 2
                av = float(it["avgPrice"]) * 2
                hi = float(it["highPrice"]) * 2
            except (TypeError, ValueError):
                continue
            out.append({
                "来源": "北京新发地市场", "发布日期": latest,
                "品种": std, "规格": spec2, "价格_元公斤": round(av, 2),
                "价格区间": f"{lo:.1f}~{hi:.1f}", "备注": "新发地每日行情(斤→公斤)",
            })
        print(f"[OK] 北京新发地市场（{q}）：最新 {latest}，本日 {len(out)} 条目标品种")
    return out


def main():
    rows = []
    parsers = {"武汉白沙洲市场": parse_wuhan, "九江市农业农村局": parse_jiujiang,
               "云南华潮水产批发市场": parse_huachao}
    for name, cfg in SOURCES.items():
        try:
            soup = BeautifulSoup(fetch(cfg["url"]), "lxml")
            got = parsers[name](soup)
            print(f"[OK] {name}：抓到 {len(got)} 条目标品种")
            rows.extend(got)
        except Exception as e:
            print(f"[WARN] {name} 抓取失败: {e}", file=sys.stderr)

    # 北京新发地（动态 API，不走 SOURCES 静态 URL）
    try:
        rows.extend(parse_xinfadi())
    except Exception as e:
        print(f"[WARN] 北京新发地 抓取失败: {e}", file=sys.stderr)

    here = os.path.dirname(os.path.abspath(__file__))
    fields = ["来源", "发布日期", "品种", "规格", "价格_元公斤", "价格区间", "备注"]
    with open(os.path.join(here, "public_fish_prices.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(here, "public_fish_prices.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"\n合计 {len(rows)} 条，已写出 public_fish_prices.csv / .json")
    # 仅展示鳜鱼/鲈鱼
    for r in rows:
        if r["品种"] in ("鳜鱼", "鲈鱼"):
            print(f"  {r['来源']:<14} | {r['品种']:<4} | {r['规格']:<10} | {r['价格_元公斤']} 元/公斤")


if __name__ == "__main__":
    main()
