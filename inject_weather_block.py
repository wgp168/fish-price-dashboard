#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读 farm_weather_latest.json → 渲染"位置 + 实时气象 + 7天预报"区块 → 注入看板 footer 之前
锚点：WEATHER_LIVE_START / WEATHER_LIVE_END（幂等可重跑）
"""
import json, os, re, html

WS = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(WS, "鳜鱼鲈鱼价格看板.html")
JSON = os.path.join(WS, "farm_weather_latest.json")

A_START = "<!-- WEATHER_LIVE_START -->"
A_END = "<!-- WEATHER_LIVE_END -->"


def fmt_num(v, suffix=""):
    if v is None:
        return "—"
    return f"{v:,.1f}{suffix}" if isinstance(v, float) else f"{v}{suffix}"


def build_alerts(alerts):
    if not alerts:
        return '<div class="alert alert-ok">✅ 当前所有指标均在正常范围内，安心作业</div>'
    parts = []
    for a in alerts:
        cls = "alert-high" if a["level"] == "high" else "alert-warn"
        parts.append(f'<div class="alert {cls}">{a["icon"]} <b>[{"HIGH" if a["level"]=="high" else "WARN"}]</b> {html.escape(a["msg"])}</div>')
    return "\n".join(parts)


def build_metrics(c):
    metrics = [
        ("🌡️", "气温", fmt_num(c["temperature_c"], " °C")),
        ("💨", "风速", fmt_num(c["wind_speed_kmh"], " km/h")),
        ("🧭", "风向", html.escape(c["wind_dir_text"]) + f" <span class='deg'>({c['wind_dir_deg']}°)</span>"),
        ("☀️", "太阳辐射", fmt_num(c["solar_radiation_wm2"], " W/m²")),
        ("🌧️", "降水量", fmt_num(c["precipitation_mm"], " mm")),
        ("💧", "相对湿度", fmt_num(c["humidity_pct"], " %")),
        ("🔵", "气压", fmt_num(c["pressure_hpa"], " hPa")),
        ("☁️", "天气", html.escape(c["weather_text"])),
    ]
    cards = []
    for icon, label, val in metrics:
        cards.append(f'''<div class="met">
          <div class="met-icon">{icon}</div>
          <div class="met-label">{label}</div>
          <div class="met-val">{val}</div>
        </div>''')
    return "\n".join(cards)


def build_daily(days):
    rows = []
    for d in days:
        prob = d.get("precip_prob_pct")
        prob_txt = f"{prob}%" if prob is not None else "—"
        # 关注标记
        flags = []
        if d["weather_code"] >= 95: flags.append("⛈️")
        if d["wind_max_kmh"] >= 38: flags.append("💨")
        if d["precip_mm"] >= 25: flags.append("🌧️")
        if d["temp_max_c"] >= 33: flags.append("🔥")
        if d["temp_min_c"] <= 8: flags.append("❄️")
        flag_txt = " ".join(flags) if flags else "—"
        # 标记颜色
        row_class = ""
        if any(c in flags for c in ["⛈️", "💨", "🌧️"]) or "🔥" in flags:
            row_class = " class=\"row-warn\""
        rows.append(f'''<tr{row_class}>
          <td>{d["date"]}</td>
          <td>{d["weather_icon"]} {html.escape(d["weather_text"])}</td>
          <td><b>{d["temp_max_c"]:.1f}</b>°C</td>
          <td>{d["temp_min_c"]:.1f}°C</td>
          <td>{d["precip_mm"]:.1f}</td>
          <td>{prob_txt}</td>
          <td>{d["wind_max_kmh"]:.1f}</td>
          <td>{html.escape(d["wind_dir_text"])} <span class="deg">({d["wind_dir_deg"]}°)</span></td>
          <td>{d["solar_mjm2"]:.1f}</td>
          <td>{flag_txt}</td>
        </tr>''')
    return "\n".join(rows)


def build_xcheck(rows):
    """高德（中国气象局）vs Open-Meteo 最高温交叉校验表"""
    if not rows:
        return ""
    body = []
    for x in rows:
        bad = x["status"] == "mismatch"
        cls = " class=\"row-warn\"" if bad else ""
        verdict = f"⚠️ 偏差 {x['delta_max']:+.1f}°C" if bad else f"✅ 一致 (Δ{x['delta_max']:+.1f}°C)"
        body.append(f'''<tr{cls}>
          <td>{x["date"]}</td>
          <td>{html.escape(x["amap_day"])} / {html.escape(x["amap_night"])}</td>
          <td>{x["amap_min"]:.1f} ~ <b>{x["amap_max"]:.1f}</b>°C</td>
          <td>{html.escape(x["amap_wind"])}风 {html.escape(x["amap_power"])} 级</td>
          <td>{x["openmeteo_min"]:.1f} ~ <b>{x["openmeteo_max"]:.1f}</b>°C</td>
          <td>{verdict}</td>
        </tr>''')
    return f'''
    <!-- D. 双源交叉校验（高德官方 vs Open-Meteo） -->
    <div class="card xcheck-card">
      <h3>🔄 双源交叉校验 · 高德天气（中国气象局） vs Open-Meteo（WMO 模型）</h3>
      <div class="csub">
        高德仅提供 4 天中文预报（白/夜天气、气温、风向风力），用于校验 Open-Meteo 模型输出。
        <b>最高温偏差 ≥2°C 时高亮提示人工复核</b>；8 项完整气象指标仍以 Open-Meteo 为准。
      </div>
      <table class="weather-forecast xcheck-table">
        <thead>
          <tr>
            <th>日期</th><th>高德·白天/夜间</th><th>高德气温</th><th>高德风力</th>
            <th>Open-Meteo 气温</th><th>校验结果</th>
          </tr>
        </thead>
        <tbody>
{chr(10).join(body)}
        </tbody>
      </table>
      <div class="legend">数据源：高德天气 API（adcode 320282 宜兴市 · 中国气象局数据） × Open-Meteo（CC BY 4.0）</div>
    </div>
'''


def build_block(d):
    site = d["site"]
    cur = d["current"]
    days = d["daily"]
    alerts_html = build_alerts(d["alerts"])
    metrics_html = build_metrics(cur)
    daily_html = build_daily(days)
    xcheck_html = build_xcheck(d.get("cross_check", []))
    nav_url = f"https://uri.amap.com/navigation?to={site['lon']},{site['lat']},{urllib_quote(site['name'])}&mode=car&src=WorkBuddy&coordinate=gaode&callnative=1"
    walk_url = f"https://uri.amap.com/navigation?to={site['lon']},{site['lat']},{urllib_quote(site['name'])}&mode=walk&src=WorkBuddy&coordinate=gaode&callnative=1"
    mark_url = f"https://uri.amap.com/marker?position={site['lon']},{site['lat']}&name={urllib_quote(site['name'])}&src=WorkBuddy&coordinate=gaode&callnative=1"

    return f'''
  <!-- 八、养殖场位置 + 实时气象 -->
  <section data-page-node-id="farm-loc-weather">
    <div class="sec-head">
      <span class="bar" style="background:#0ea5e9"></span>
      <h2>八、宜兴官林镇数字低碳生态养殖项目 · 位置 + 实时气象</h2>
      <span class="note">📍 高德定位 · 🌡️ Open-Meteo 实时/预报 · 🔄 高德官方交叉校验 · 每日 09:00 自动刷新</span>
    </div>

    {A_START}

    <!-- A. 位置 + 导航 -->
    <div class="card location-card">
      <h3>📍 养殖场位置</h3>
      <div class="csub">
        <b>{html.escape(site['name'])}</b><br>
        地址：{html.escape(site['address'])}<br>
        坐标：<code>({site['lon']}, {site['lat']})</code>　|　海拔：{fmt_num(cur.get('elevation_m'),' m')}<br>
        <span class="coord-src">📌 坐标来源：{html.escape(site.get('coord_source', '高德地理编码 API'))}　|　行政区 adcode：{site.get('adcode','—')}</span><br>
        运营：{html.escape(site['operator'])}　|　总面积：{site['total_area_mu']} 亩（一期丰义村 {site['phase1_area_mu']} 亩 + 二期白茫村 {site['phase2_area_mu']} 亩）　|　养殖品种：{html.escape(site['product'])}
      </div>

      <!-- SVG 轻量地图（点击调起高德导航） -->
      <a href="{nav_url}" target="_blank" class="mini-map-link" title="点击调起高德地图导航">
        <svg class="mini-map" viewBox="0 0 600 320" preserveAspectRatio="xMidYMid slice">
          <!-- 底色：滆湖西岸农田区（淡绿） -->
          <rect width="600" height="320" fill="#e8f1e0"/>
          <!-- 田块纹理 -->
          <g opacity="0.4" stroke="#a7c4a0" stroke-width="0.6" fill="none">
            <line x1="0" y1="60" x2="600" y2="50"/>
            <line x1="0" y1="120" x2="600" y2="125"/>
            <line x1="0" y1="200" x2="600" y2="195"/>
            <line x1="0" y1="260" x2="600" y2="265"/>
            <line x1="120" y1="0" x2="125" y2="320"/>
            <line x1="260" y1="0" x2="258" y2="320"/>
            <line x1="400" y1="0" x2="403" y2="320"/>
            <line x1="500" y1="0" x2="495" y2="320"/>
          </g>
          <!-- 河道（滆湖西岸水域） -->
          <path d="M0,40 Q200,90 400,70 T600,100" stroke="#7eb6d4" stroke-width="14" fill="none" opacity="0.7" stroke-linecap="round"/>
          <path d="M120,200 Q250,230 380,210 T600,250" stroke="#7eb6d4" stroke-width="8" fill="none" opacity="0.5" stroke-linecap="round"/>
          <!-- 古庄路 -->
          <line x1="0" y1="170" x2="600" y2="165" stroke="#d4b075" stroke-width="3" opacity="0.85"/>
          <text x="540" y="160" font-size="11" fill="#8a7250" font-family="sans-serif">古庄路</text>
          <!-- 大棚区域（白底+蓝边） -->
          <rect x="260" y="140" width="80" height="40" fill="#f5f9fc" stroke="#7c9ad4" stroke-width="1.2" rx="3" opacity="0.85"/>
          <text x="300" y="164" text-anchor="middle" font-size="10" fill="#3a5a8a" font-family="sans-serif">养殖大棚</text>
          <!-- 周边村名 -->
          <text x="60" y="30" font-size="11" fill="#5a6a4a" font-family="sans-serif">大如庙</text>
          <text x="500" y="25" font-size="11" fill="#5a6a4a" font-family="sans-serif">古庄</text>
          <text x="100" y="245" font-size="11" fill="#5a6a4a" font-family="sans-serif">小如庙</text>
          <text x="270" y="245" font-size="11" fill="#5a6a4a" font-family="sans-serif">青年农场</text>
          <text x="450" y="245" font-size="11" fill="#5a6a4a" font-family="sans-serif">庄西村</text>
          <!-- 定位标记 -->
          <circle cx="300" cy="160" r="20" fill="#0ea5e9" opacity="0.25"/>
          <circle cx="300" cy="160" r="12" fill="#0ea5e9" opacity="0.45"/>
          <circle cx="300" cy="160" r="6" fill="#dc2626"/>
          <text x="300" y="200" text-anchor="middle" font-size="13" fill="#0c4a6e" font-weight="700" font-family="sans-serif">数字低碳生态养殖项目</text>
          <text x="300" y="216" text-anchor="middle" font-size="10" fill="#0c4a6e" font-family="sans-serif">{site['lon']}, {site['lat']}</text>
        </svg>
        <div class="map-overlay">点击调起高德地图导航 →</div>
      </a>

      <div class="nav-actions">
        <a href="{nav_url}" target="_blank" class="nav-btn nav-btn-primary">🚗 驾车导航</a>
        <a href="{walk_url}" target="_blank" class="nav-btn">🚶 步行导航</a>
        <a href="{mark_url}" target="_blank" class="nav-btn">📍 标记位置</a>
        <span class="nav-tip">点击以上按钮可调起高德地图 APP 或网页版导航（无需 API Key）</span>
      </div>
    </div>

    <!-- B. 实时气象 -->
    <div class="card weather-card">
      <h3>🌡️ 实时气象（{html.escape(cur['time'])} · Asia/Shanghai）</h3>
      <div class="csub">天气：<b>{cur['weather_icon']} {html.escape(cur['weather_text'])}</b>　|　数据源：Open-Meteo（WMO 标准 · 15min 更新 · 免费公开）</div>
      <div class="mets-grid">
{metrics_html}
      </div>
      <div class="alerts-row">
        {alerts_html}
      </div>
    </div>

    <!-- C. 7天预报 -->
    <div class="card">
      <h3>📅 7天预报（养殖视角 · 关注极端天气）</h3>
      <table class="weather-forecast">
        <thead>
          <tr>
            <th>日期</th><th>天气</th><th>最高</th><th>最低</th><th>降水(mm)</th><th>概率</th>
            <th>风速max(km/h)</th><th>主导风向</th><th>辐射(MJ/m²)</th><th>关注</th>
          </tr>
        </thead>
        <tbody>
{daily_html}
        </tbody>
      </table>
      <div class="legend">图例：⛈️雷暴 💨大风（≥38km/h） 🌧️≥25mm大雨 🔥≥33°C高温 ❄️≤8°C低温</div>
    </div>
{xcheck_html}
    <!-- E. 关注阈值说明 -->
    <div class="callout">
      <b>⚙️ 养殖关注阈值（鳜鱼/鲈鱼 · 无锡市环保集团数字低碳生态养殖项目）：</b><br>
      • <b>气温</b>：28–30°C 最适 · <b style="color:#dc2626">≥33°C 警戒</b>（增氧/加深水位）· ≥35°C 危险 · ≤8°C 冬季警戒<br>
      • <b>风速</b>：≤25 km/h 正常 · 25–38 km/h 关注 · <b style="color:#dc2626">≥38 km/h（6 级）警戒</b>（薄膜/光伏板/围网检查）· ≥50 km/h 危险<br>
      • <b>24h 降水</b>：≤10mm 正常 · 10–25mm 关注 · <b style="color:#dc2626">≥25mm 警戒</b> · ≥50mm 危险<br>
      • <b>气压</b>：≥1005 hPa 正常 · <b style="color:#dc2626">&lt;1005 hPa 警戒</b>（可能风暴前兆）<br>
      • <b>雷暴</b>（weather_code ≥ 95）：<b style="color:#dc2626">随时警戒</b>（增氧机/光伏/排水/用电）<br>
      • <b>太阳辐射</b>：>900 W/m² 时需关注水温上升（夏季中午可>1000），配合气温阈值判断
    </div>

    <div class="csub" style="margin-top:10px">
      ⏱️ 本次抓取时间：<code>{html.escape(d['meta']['fetched_at_cst'])}</code>　|　数据许可：{html.escape(d['meta']['license'])}
    </div>

    {A_END}
  </section>
'''


def urllib_quote(s):
    from urllib.parse import quote
    return quote(s, safe="")


def main():
    d = json.load(open(JSON, encoding="utf-8"))
    html_content = open(HTML, encoding="utf-8").read()

    # 若锚点已存在，先移除旧区块
    if A_START in html_content:
        html_content = re.sub(re.escape(A_START) + r".*?" + re.escape(A_END) + r"\s*", "", html_content, flags=re.S)
        print("[OK] 移除旧 WEATHER 区块")

    block = build_block(d)

    # 在 </div> 主容器关闭之前（即 footer 之前）插入
    marker = '<footer '
    idx = html_content.find(marker)
    if idx == -1:
        raise SystemExit("ERROR: <footer> 锚点缺失，中止")
    html_content = html_content[:idx] + block + "\n" + html_content[idx:]

    open(HTML, "w", encoding="utf-8").write(html_content)
    print(f"[OK] 注入完成：站点 {d['site']['name']}，实时 {d['current']['weather_text']}，告警 {len(d['alerts'])} 条")
    assert A_START in html_content and A_END in html_content


if __name__ == "__main__":
    main()