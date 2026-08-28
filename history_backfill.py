#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回溯采集北京新发地 2024-01 ~ 2026-08 每月「鳜鱼(桂鱼)/鲈鱼」真实批发均价
=========================================================================
数据源：北京新发地农产品批发市场 每日价格行情接口
        http://xinfadi.com.cn:8099/getPriceData.html  (POST)
口径  ：水产分类 cat=1190；品种名 桂鱼=鳜鱼，鲈鱼=综合鲈类（含淡水/海水鲈）
单位  ：元/斤（新发地原始口径）；脚本同时给出 元/公斤(×2) 便于与看板统一
方法  ：按月查询该月全部交易日，取 avgPrice 平均 = 当月均价（即用户建议的「当月平均价」）

输出：monthly_xinfadi_prices.csv / .json
      字段：年份,月份,品种,样本数,月均价_元斤,月均价_元公斤,最低_元斤,最高_元斤,口径

用法：python history_backfill.py
"""
import urllib.request, ssl, json, urllib.parse, csv, os, time, calendar, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
URL = "http://xinfadi.com.cn:8099/getPriceData.html"

NAME_MAP = {"鳜鱼": "桂鱼", "鲈鱼": "鲈鱼"}   # 看板品种 -> 新发地查询名


def post(payload, retries=4):
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(
        URL, data=data,
        headers={"User-Agent": "Mozilla/5.0",
                 "Content-Type": "application/x-www-form-urlencoded"},
        method="POST")
    last = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=25, context=CTX) as resp:
                return json.loads(resp.read().decode("utf-8", "ignore"))
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    raise last


def month_avg(year, month, species, query_name):
    last_day = calendar.monthrange(year, month)[1]
    payload = {
        "limit": "400", "current": "1",
        "pubDateStartTime": f"{year}-{month:02d}-01",
        "pubDateEndTime": f"{year}-{month:02d}-{last_day:02d}",
        "prodPcatid": "1190", "prodCatid": "",
        "prodName": query_name, "selectClassId": "",
    }
    j = post(payload)
    rows = j.get("list", []) or []
    prices = []
    for r in rows:
        v = r.get("avgPrice")
        if v in (None, ""):
            continue
        try:
            prices.append(float(v))
        except (TypeError, ValueError):
            pass
    if not prices:
        return None
    avg = sum(prices) / len(prices)
    return {
        "年份": year, "月份": month, "品种": species,
        "样本数": len(prices),
        "月均价_元斤": round(avg, 2),
        "月均价_元公斤": round(avg * 2, 2),
        "最低_元斤": round(min(prices), 2),
        "最高_元斤": round(max(prices), 2),
        "口径": "北京新发地批发价(元/斤)",
    }


def main():
    rows = []
    end = (2026, 8)
    print("开始回溯采集新发地 2024-01 ~ 2026-08 月度均价 ...")
    for y in (2024, 2025, 2026):
        for m in range(1, 13):
            if (y, m) > end:
                break
            for sp, nm in NAME_MAP.items():
                try:
                    r = month_avg(y, m, sp, nm)
                    if r:
                        rows.append(r)
                        print(f"  [OK] {y}-{m:02d} {sp}: {r['月均价_元斤']} 元/斤 "
                              f"(n={r['样本数']}, {r['最低_元斤']}~{r['最高_元斤']})")
                    else:
                        print(f"  [--] {y}-{m:02d} {sp}: 无数据", file=sys.stderr)
                except Exception as e:
                    print(f"  [ERR] {y}-{m:02d} {sp}: {e}", file=sys.stderr)
                time.sleep(0.4)
    # 输出
    fields = ["年份", "月份", "品种", "样本数", "月均价_元斤", "月均价_元公斤",
              "最低_元斤", "最高_元斤", "口径"]
    csv_path = os.path.join(HERE, "monthly_xinfadi_prices.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    json_path = os.path.join(HERE, "monthly_xinfadi_prices.json")
    json.dump(rows, open(json_path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"\n合计 {len(rows)} 条 → {csv_path} / {json_path}")


if __name__ == "__main__":
    main()
