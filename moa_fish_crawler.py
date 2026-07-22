#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
农业农村部「重点农产品市场信息平台」鳜鱼/鲈鱼批发价爬虫
=========================================================
数据源 : ncpscxx.moa.gov.cn  (全国农产品批发市场价格信息系统)
接口   : POST /product/homeWholesalePrice/selectWholesalePriceChart
         ?varietyCode=<品种编码>   （返回当日各批发市场该品种价格，AES-256-CBC 加密）
说明   :
  - 该接口返回「当日」全国有报价的批发市场分布，不支持历史日期查询。
  - 农业农村部官方批发价按「品种」提供，不细分 500g 内/外规格；
    分规格数据请参考行业塘头价周报。
  - 加密密钥逆向自前端 app.js：key="7s9K$pG2xQ8zR5mB7vA3sD9fH2jW40cV"，iv=密文前16字符。
用法   :
  python moa_fish_crawler.py            # 抓取并写出 fish_prices.csv / fish_prices.json
  python moa_fish_crawler.py --region   # 仅输出江苏及周边
"""
import urllib.request, ssl, json, urllib.parse, base64, csv, os, sys, argparse

try:
    from Crypto.Cipher import AES
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pycryptodome", "-q"])
    from Crypto.Cipher import AES

KEY = b"7s9K$pG2xQ8zR5mB7vA3sD9fH2jW40cV"
BASE = "https://ncpscxx.moa.gov.cn"
# 品种编码来自 /product/homeWholesaleProduct/selectTree（水产品 > 淡水鱼/海水鱼）
VARIETIES = {
    "活鳜鱼":  "AM01013003",
    "淡水鲈鱼": "AM01009",
    "鲈鱼(海水)": "AM02005",
}
# 江苏及周边（江浙沪皖）市场关键词
REGION_KW = ["江苏", "安徽", "浙江", "上海", "南京", "苏州",
             "凌家塘", "南环桥", "马鞍山", "合肥", "周谷堆"]

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def fetch_decrypt(variety_code: str) -> dict:
    """调用接口并 AES 解密，返回 {date, x:[市场...], y:[价格...]}"""
    url = (BASE + "/product/homeWholesalePrice/selectWholesalePriceChart?"
           + urllib.parse.urlencode({"varietyCode": variety_code}))
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0", "Accept": "application/json"}, method="POST")
    cipher_b64 = json.loads(urllib.request.urlopen(req, timeout=15, context=CTX)
                             .read().decode())["data"]
    iv = cipher_b64[:16].encode("utf-8")[:16]
    raw = base64.b64decode(cipher_b64[16:])
    pt = AES.new(KEY, AES.MODE_CBC, iv).decrypt(raw)
    pt = pt[:-pt[-1]]                     # PKCS7 去填充
    return json.loads(pt.decode("utf-8", "ignore"))


def crawl() -> list:
    rows = []
    for name, code in VARIETIES.items():
        try:
            o = fetch_decrypt(code)
        except Exception as e:
            print(f"[WARN] {name}({code}) 抓取失败: {e}", file=sys.stderr)
            continue
        date = o.get("date")
        for m, p in zip(o.get("x", []), o.get("y", [])):
            rows.append({
                "品种": name,
                "品种编码": code,
                "日期": date,
                "市场": m,
                "批发价_元公斤": p,
                "是否江苏周边": any(k in m for k in REGION_KW),
            })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", action="store_true", help="仅输出江苏及周边")
    args = ap.parse_args()

    rows = crawl()
    here = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(here, "fish_prices.csv")
    json_path = os.path.join(here, "fish_prices.json")

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=[
            "品种", "品种编码", "日期", "市场", "批发价_元公斤", "是否江苏周边"])
        w.writeheader()
        w.writerows(rows)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    region_rows = [r for r in rows if r["是否江苏周边"]]
    show = region_rows if args.region else rows
    print(f"抓取 {len(rows)} 条（江苏及周边 {len(region_rows)} 条），日期 {rows[0]['日期'] if rows else 'NA'}")
    for r in show:
        print(f"  {r['品种']:<8} | {r['市场']:<28} | {r['批发价_元公斤']} 元/公斤"
              + ("  [江苏周边]" if r["是否江苏周边"] else ""))
    print(f"\n已写出:\n  {csv_path}\n  {json_path}")


if __name__ == "__main__":
    main()
