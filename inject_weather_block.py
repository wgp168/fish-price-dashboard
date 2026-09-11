#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读 farm_weather_latest.json → 渲染"位置 + 实时气象 + 7天预报 + 双源校验"区块 → 注入看板 footer 之前
锚点：WEATHER_LIVE_START / WEATHER_LIVE_END 包裹整个 <section>（幂等可重跑，杜绝 sec-head 残留）

地图架构（2026-09-01 修复 — 改用高德矢量 tile，无 Key、国内稳）：
- Leaflet 1.9.4 框架（CDN: unpkg）
- 底图：高德矢量 tile `https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8`
  · 无需 API Key、HTTP 200 < 100ms、CartoCDN/OSM 均被 GFW 墙
- 反相 CSS filter: invert + hue-rotate + brightness/contrast → 把白底矢量变成"高德蓝科技感"深色主题
- 因底图本身就是 GCJ-02（中国火星坐标），marker 直接用 GCJ-02 坐标，
  Leaflet 不感知坐标系差异、忠实画到对应位置，无需偏移转换
- click 任意点 → e.latlng（WGS84）→ wgs84togcj02 → 高德 URI Scheme 导航（带 mode=car&coordinate=gaode&callnative=1）

外部资源一次注入：用占位符 LEAFLET_CSS_HERE/LEAFLET_JS_HERE/CN_TILE_FILTER_HERE 防止重渲染重复插入
"""
import json, os, re, html
from urllib.parse import quote
from dashboard_version import DASHBOARD_VERSION, DASHBOARD_VERSION_DATE

WS = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(WS, "鳜鱼鲈鱼价格看板.html")
JSON = os.path.join(WS, "farm_weather_latest.json")

# CLI 提示：版本号需要手动 bump，本脚本不自动升版本
# python dashboard_version.py --reason "气象数据双源校验接入" --level patch

# Leaflet CDN（Unpkg） + WGS84/GCJ-02 转换（仅在 click 起点时使用，把屏幕 WGS84 转回 GCJ-02 给高德导航 URI Scheme）
LEAFLET_CSS = '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="anonymous">'
LEAFLET_JS = '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin="anonymous"></script>'

# 高德矢量 tile 配色 — v1.0.2 起改为"标准地图配色"（不再反相）
# 浅米色陆地 + 浅蓝水系 + 深灰文字 + 灰色省道/国道路网，与高德官方地图观感一致
# 背景色 #e8f1e0（浅绿）作为 tile 加载前的占位，与底图风格无缝衔接
CN_TILE_FILTER_CSS = r"""
  <style id="cn-tile-filter">
  /* 标准配色 tile 不做任何 filter 变换；保留 popup 柔和阴影即可 */
  .farm-map .leaflet-popup-content-wrapper, .farm-map .leaflet-popup-tip {
    box-shadow: 0 4px 12px rgba(0, 0, 0, .12);
  }
  </style>"""

A_START = "<!-- WEATHER_LIVE_START -->"
A_END = "<!-- WEATHER_LIVE_END -->"
CN_TILE_FILTER_HERE = "<!-- CN_TILE_FILTER_HERE -->"
LEAFLET_CSS_HERE = "<!-- LEAFLET_CSS_HERE -->"
LEAFLET_JS_HERE = "<!-- LEAFLET_JS_HERE -->"

# WGS84 ↔ GCJ-02 转换（中国坐标系，公开算法）
# 高德坐标系 = GCJ-02，OSM/Leaflet 用 WGS84，差几百米必须转换
COORDTRANS_JS = r"""
<script>
// WGS84 (Leaflet/OSM) <-> GCJ-02 (高德/腾讯) 转换
// 标准公开算法；a=6378245.0, ee=0.00669342162296594323
const PI = Math.PI, A = 6378245.0, EE = 0.00669342162296594323;
function outOfChina(lng, lat){return lng<72.004||lng>137.8347||lat<0.8293||lat>55.8271;}
function _t(lng, lat){let t=Math.sqrt(lng*lng+lat*lat)+0.00002*Math.sin(lat*PI*3000/180);
  t+=0.000003*Math.cos(lng*PI*3000/180);return t;}
function _dlng(lng, lat){let r=300+s+2*l+3*lng+0.2*lng*lng+0.1*lng*lat+0.2*Math.sqrt(Math.abs(lng));
  r+=(20*Math.sin(6*lng*PI)+20*Math.sin(2*lng*PI))*2/3;r+=(20*Math.sin(lng*PI)+40*Math.sin(lng/3*PI))*2/3;
  r+=(150*Math.sin(lng/12*PI)+300*Math.sin(lng/30*PI))*2/3;return r;}
function _dlat(lng, lat){let r=-100+2*l+3*lat+0.2*lat*lat+0.1*lng*lat+0.2*Math.sqrt(Math.abs(lng));
  r+=(20*Math.sin(6*lat*PI)+20*Math.sin(2*lat*PI))*2/3;r+=(20*Math.sin(lat*PI)+40*Math.sin(lat/3*PI))*2/3;
  r+=(160*Math.sin(lat/12*PI)+320*Math.sin(lat*30*PI))*2/3;return r;}
let s = 0; // dummy
var s; function _s(){s = Math.sin(2*PI);} _s();
function gcj02towgs84(lng, lat){
  if(outOfChina(lng,lat)) return [lng,lat];
  let dlat=_dlat(lng-105,lat-35), dlng=_dlng(lng-105,lat-35);
  const radlat=lat/180*PI; let magic=Math.sin(radlat); magic=1-EE*magic*magic;
  const sqrtmagic=Math.sqrt(magic); dlat=(dlat*180)/((A*(1-EE))/magic*sqrtmagic)*PI;
  dlng=(dlng*180)/(A/sqrtmagic*Math.cos(radlat)*PI); return [lng-dlng*2, lat-dlat*2];
}
function wgs84togcj02(lng, lat){
  if(outOfChina(lng,lat)) return [lng,lat];
  let dlat=_dlat(lng-105,lat-35), dlng=_dlng(lng-105,lat-35);
  const radlat=lat/180*PI; let magic=Math.sin(radlat); magic=1-EE*magic*magic;
  const sqrtmagic=Math.sqrt(magic); dlat=(dlat*180)/((A*(1-EE))/magic*sqrtmagic)*PI;
  dlng=(dlng*180)/(A/sqrtmagic*Math.cos(radlat)*PI); return [lng+dlng*2, lat+dlat*2];
}
</script>
"""


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
        flags = []
        if d["weather_code"] >= 95: flags.append("⛈️")
        if d["wind_max_kmh"] >= 38: flags.append("💨")
        if d["precip_mm"] >= 25: flags.append("🌧️")
        if d["temp_max_c"] >= 33: flags.append("🔥")
        if d["temp_min_c"] <= 8: flags.append("❄️")
        flag_txt = " ".join(flags) if flags else "—"
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
          <td>{html.escape(d["wind_dir_text"])} <span class="deg">({d['wind_dir_deg']}°)</span></td>
          <td>{d["solar_mjm2"]:.1f}</td>
          <td>{flag_txt}</td>
        </tr>''')
    return "\n".join(rows)


def build_xcheck(rows):
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
    <div class="card xcheck-card">
      <h3>🔄 双源交叉校验 · 高德天气（中国气象局） vs Open-Meteo（WMO 模型）</h3>
      <div class="csub">高德仅提供 4 天中文预报（白/夜天气、气温、风向风力），用于校验 Open-Meteo 模型输出。<b>最高温偏差 ≥2°C 时高亮提示人工复核</b>；8 项完整气象指标仍以 Open-Meteo 为准。</div>
      <table class="weather-forecast xcheck-table">
        <thead><tr>
          <th>日期</th><th>高德·白天/夜间</th><th>高德气温</th><th>高德风力</th>
          <th>Open-Meteo 气温</th><th>校验结果</th>
        </tr></thead>
        <tbody>
{chr(10).join(body)}
        </tbody>
      </table>
      <div class="legend">数据源：高德天气 API（adcode 320282 宜兴市 · 中国气象局数据） × Open-Meteo（CC BY 4.0）</div>
    </div>
'''


def build_map_block(site):
    """Leaflet + 高德矢量 tile（公开，无 Key、国内 100ms） + CSS 反相成"高德蓝科技感"深色主题
    养殖场坐标是 GCJ-02（高德）；因底图本身也是 GCJ-02，marker 直接用 GCJ-02 坐标、
    无需转 WGS84（Leaflet 不感知坐标系，忠实投影到对应 tile 位置）。

    click 任意点：e.latlng 是 WGS84 → wgs84togcj02 转回 GCJ-02 → 高德 URI Scheme 导航
    """
    site_lon_gcj = site["lon"]
    site_lat_gcj = site["lat"]
    site_name = html.escape(site["name"])
    site_LL = [site_lat_gcj, site_lon_gcj]
    # tile URL 模板（在 f-string 外定义，避免大括号嵌套问题）
    TILE_URL = "https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}"
    return f'''
    <div class="map-wrap">
      <div id="farm-map" class="farm-map" data-site-lon="{site_lon_gcj}" data-site-lat="{site_lat_gcj}" data-site-name="{site_name}"></div>
      <div class="map-hint">
        🖱️ 滚轮缩放　·　＋/－ 按钮缩放　·　拖拽平移　·　<strong>点击地图任意点 → 该点设为起点 → 自动跳高德驾车导航到养殖场</strong>
      </div>
      <div class="map-tools">
        <button class="map-tool" onclick="farmMap && farmMap.setView(farmMap._siteLL, 16)">🔄 复位</button>
        <button class="map-tool" onclick="farmMap && farmMap.zoomIn()">＋ 放大</button>
        <button class="map-tool" onclick="farmMap && farmMap.zoomOut()">－ 缩小</button>
        <button class="map-tool map-tool-clear" onclick="clearRoute()">🗑️ 清除路线</button>
      </div>
    </div>
    <script>
    (function(){{
      const el = document.getElementById('farm-map');
      if (!el) return;
      const siteLon = parseFloat(el.dataset.siteLon);  // GCJ-02 经度
      const siteLat = parseFloat(el.dataset.siteLat);  // GCJ-02 纬度
      const siteName = el.dataset.siteName;
      // 高德矢量底图本身就是 GCJ-02，Leaflet 不感知坐标系，marker 直接 GCJ-02 显示
      const siteLL = [siteLat, siteLon];
      farmMap = L.map('farm-map', {{zoomControl: false, attributionControl: true}}).setView(siteLL, 15);
      farmMap._siteLL = siteLL;
      farmMap._siteName = siteName;
      farmMap._siteLonGcj = siteLon;
      farmMap._siteLatGcj = siteLat;
      // 高德矢量 tile（公开、无 Key、国内 < 100ms）+ CSS 反相（见 cn-tile-filter style）
      L.tileLayer("{TILE_URL}", {{
        subdomains: ['1','2','3','4'], maxZoom: 19,
        attribution: '© 高德地图 AutoNavi · 坐标 GCJ-02'
      }}).addTo(farmMap);
      // 自定义 marker（蓝脉冲+红心，模拟高德定位标）
      const destIcon = L.divIcon({{
        className: 'dest-marker',
        html: '<div class="dest-marker-pulse"></div><div class="dest-marker-dot"></div>',
        iconSize: [32, 32], iconAnchor: [16, 16]
      }});
      L.marker(siteLL, {{icon: destIcon}}).addTo(farmMap)
        .bindPopup(`<b>🎯 ${{siteName}}</b><br>高德坐标 ${{siteLon}}, ${{siteLat}}<br>（GCJ-02 国内标准）`);
      // 起点 marker
      farmMap._startMarker = null;
      farmMap.on('click', function(e){{
        // Leaflet 返回 WGS84，要转回 GCJ-02 喂高德 URI Scheme
        const clickLat = e.latlng.lat, clickLng = e.latlng.lng;
        const gcj = wgs84togcj02(clickLng, clickLat);  // [lng, lat]
        if (farmMap._startMarker) farmMap.removeLayer(farmMap._startMarker);
        const startIcon = L.divIcon({{
          className: 'start-marker',
          html: '<div class="start-marker-dot"></div>',
          iconSize: [22, 22], iconAnchor: [11, 11]
        }});
        farmMap._startMarker = L.marker(e.latlng, {{icon: startIcon}}).addTo(farmMap);
        // 画一条直线预览（终点用 WGS84 转换，避免与 Leaflet 默认坐标系一致）
        const siteWgs = gcj02towgs84(siteLon, siteLat);
        if (farmMap._routeLine) farmMap.removeLayer(farmMap._routeLine);
        farmMap._routeLine = L.polyline([e.latlng, [siteWgs[1], siteWgs[0]]], {{color: '#22d3ee', weight: 4, opacity: 0.85, dashArray: '6,8'}}).addTo(farmMap);
        // 弹窗 + 跳高德驾车导航
        const navUrl = `https://uri.amap.com/navigation?from=${{gcj[0].toFixed(6)}},${{gcj[1].toFixed(6)}},起点&to=${{siteLon}},${{siteLat}},${{encodeURIComponent(siteName)}}&mode=car&src=WorkBuddy&coordinate=gaode&callnative=1`;
        L.popup()
          .setLatLng(e.latlng)
          .setContent(`
            <div style="min-width:240px;font-size:13px;line-height:1.6">
              <b>📍 已设置起点</b><br>
              WGS84: ${{clickLat.toFixed(5)}}, ${{clickLng.toFixed(5)}}<br>
              GCJ-02: ${{gcj[1].toFixed(5)}}, ${{gcj[0].toFixed(5)}}<br>
              <a href="${{navUrl}}" target="_blank" style="display:inline-block;margin-top:8px;padding:6px 12px;background:#0ea5e9;color:#fff;border-radius:6px;text-decoration:none;font-weight:700">🚗 在高德地图中驾车导航 →</a>
            </div>
          `)
          .openOn(farmMap);
      }});
    }})();
    function clearRoute(){{
      if (!farmMap) return;
      if (farmMap._startMarker) {{ farmMap.removeLayer(farmMap._startMarker); farmMap._startMarker = null; }}
      if (farmMap._routeLine) {{ farmMap.removeLayer(farmMap._routeLine); farmMap._routeLine = null; }}
      farmMap.closePopup();
    }}
    </script>
'''


def build_today_farming_tips(cur, day0):
    """动态今日养殖提示：基于实时+当日预报（雾/溶氧、阴雨、气压趋势）。
    雾天判定：湿度 ≥85%（清晨辐射雾/高湿天典型表现，Open-Meteo 网格湿度常低于站点实测，
    如 2026-09-11 实况雾天湿度 100% 而 API 报 86%，故阈值取 85%）；
    阴雨判定：当日预报降水 ≥0.2mm 或实时降水 >0；
    气压：24h 变化量趋势由人工判读（脚本无历史气压），此处仅输出当前值提示线。"""
    tips = []
    hum = cur.get("humidity_pct") or 0
    precip_now = cur.get("precipitation_mm") or 0
    d0_precip = (day0 or {}).get("precip_mm") or 0
    d0_prob = (day0 or {}).get("precip_prob_pct") or 0
    if hum >= 85:
        tips.append(f"🌫️ <b>今日高湿（湿度 {hum}%，近饱和）</b>：清晨大概率有雾/低能见度——雾天光照弱、藻类产氧下降，"
                    "<b>鱼塘溶氧可能偏低</b>：延迟上午投喂、开启增氧机、加强巡塘观察浮头")
    if precip_now > 0 or d0_precip >= 0.2:
        tips.append(f"🌧️ <b>今日有降水（预报 {d0_precip}mm，概率 {d0_prob}%）</b>：阴雨期水温波动+溶氧下降，"
                    "控制投喂量（减 1–2 成）避免残饵，雨停后及时巡塘")
    if not tips:
        return ""
    return "      <br>".join("• " + t for t in tips) + "<br>\n"


def build_block(d):
    site = d["site"]
    cur = d["current"]
    days = d["daily"]
    alerts_html = build_alerts(d["alerts"])
    metrics_html = build_metrics(cur)
    daily_html = build_daily(days)
    xcheck_html = build_xcheck(d.get("cross_check", []))
    map_block = build_map_block(site)
    site_name_esc = html.escape(site["name"])
    today_tips = build_today_farming_tips(cur, days[0] if days else None)

    # AMap URI Scheme 备用按钮（不点击地图时直接以"当前定位"为起点）
    nav_to_only = f"https://uri.amap.com/navigation?to={site['lon']},{site['lat']},{quote(site['name'], safe='')}&mode=car&src=WorkBuddy&coordinate=gaode&callnative=1"

    return f'''
  {A_START}
  <!-- 八、江苏环荟·宜兴官林镇数字低碳生态养殖项目 · 位置 + 实时气象 -->
  <section data-page-node-id="farm-loc-weather">
    <div class="sec-head">
      <span class="bar" style="background:linear-gradient(180deg,#0ea5e9,#22d3ee)"></span>
      <h2>八、江苏环荟·宜兴官林镇数字低碳生态养殖项目 · 位置 + 实时气象</h2>
      <span class="note">📍 高德定位 · 🌡️ Open-Meteo 实时/预报 · 🔄 高德官方交叉校验 · 每日 09:00 自动刷新</span>
    </div>

    <!-- A. 位置 + 导航 -->
    <div class="card location-card">
      <h3>📍 养殖场位置</h3>
      <div class="csub">
        <b>{site_name_esc}</b><br>
        地址：{html.escape(site['address'])}<br>
        坐标：<code>({site['lon']}, {site['lat']})</code>　|　海拔：{fmt_num(cur.get('elevation_m'),' m')}<br>
        <span class="coord-src">📌 坐标来源：{html.escape(site.get('coord_source', '高德地理编码 API'))}　|　行政区 adcode：{site.get('adcode','—')}</span><br>
        运营：{html.escape(site['operator'])}　|　总面积：{site['total_area_mu']} 亩（一期丰义村 {site['phase1_area_mu']} 亩 + 二期白茫村 {site['phase2_area_mu']} 亩）　|　养殖品种：{html.escape(site['product'])}
      </div>

      <!-- 地图：Leaflet + CartoDB Dark Matter（高德蓝科技感） -->
      {map_block}

      <div class="nav-actions">
        <a href="{nav_to_only}" target="_blank" class="nav-btn nav-btn-primary">🚗 终点直达（高德）</a>
        <a href="https://uri.amap.com/marker?position={site['lon']},{site['lat']}&name={quote(site['name'], safe='')}&src=WorkBuddy&coordinate=gaode&callnative=1" target="_blank" class="nav-btn">📍 标记位置</a>
        <span class="nav-tip">地图 OSM 底图 · 坐标已自动从高德 GCJ-02 转换为 WGS84（误差 &lt;1m）</span>
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
        <thead><tr>
          <th>日期</th><th>天气</th><th>最高</th><th>最低</th><th>降水(mm)</th><th>概率</th>
          <th>风速max(km/h)</th><th>主导风向</th><th>辐射(MJ/m²)</th><th>关注</th>
        </tr></thead>
        <tbody>
{daily_html}
        </tbody>
      </table>
      <div class="legend">图例：⛈️雷暴 💨大风（≥38km/h） 🌧️≥25mm大雨 🔥≥33°C高温 ❄️≤8°C低温</div>
    </div>
{xcheck_html}
    <div class="callout">
      <b>⚙️ 养殖关注阈值（鳜鱼/鲈鱼 · 江苏环荟数字低碳生态养殖项目）：</b><br>
      {today_tips}      • <b>气温</b>：28–30°C 最适 · <b style="color:#dc2626">≥33°C 警戒</b>（增氧/加深水位）· ≥35°C 危险 · ≤8°C 冬季警戒<br>
      • <b>风速</b>：≤25 km/h 正常 · 25–38 km/h 关注 · <b style="color:#dc2626">≥38 km/h（6 级）警戒</b>（薄膜/光伏板/围网检查）· ≥50 km/h 危险<br>
      • <b>24h 降水</b>：≤10mm 正常 · 10–25mm 关注 · <b style="color:#dc2626">≥25mm 警戒</b> · ≥50mm 危险<br>
      • <b>气压</b>：≥1005 hPa 正常 · <b style="color:#dc2626">&lt;1005 hPa 警戒</b>（可能风暴前兆）· 24h 变化 <b>≥5 hPa</b> 提示天气转折（提前增氧防应激）；连续缓升属高压稳定控制、风险低；连续下降（哪怕未达标）需关注后续雷暴/对流<br>
      • <b>雾 / 低能见度</b>（湿度≥90%、清晨微风晴天最典型）：<b style="color:#dc2626">溶氧下降风险</b>——雾天夜间藻类不产氧、呼吸耗氧持续，黎明前后最易浮头；<b>开增氧机、推迟投喂、加强巡塘</b><br>
      • <b>连阴雨</b>（≥2 天连续降水/寡照）：藻类产氧持续偏低+水温波动 → <b>减料 1–2 成、全天增氧、防应激</b>；雨后转晴防藻类过度增殖（pH 飙升）<br>
      • <b>雷暴</b>（weather_code ≥ 95）：<b style="color:#dc2626">随时警戒</b>（增氧机/光伏/排水/用电）<br>
      • <b>太阳辐射</b>：>900 W/m² 时需关注水温上升（夏季中午可>1000），配合气温阈值判断
    </div>

    <div class="csub" style="margin-top:10px">
      ⏱️ 本次抓取时间：<code>{html.escape(d['meta']['fetched_at_cst'])}</code>　|　数据许可：{html.escape(d['meta']['license'])}
    </div>
  </section>
  {A_END}
'''


def inject_external_assets(html_content):
    """一次性注入 Leaflet CDN + WGS84↔GCJ-02 转换脚本 + 高德矢量反相 CSS。
    已注入（占位符存在）则跳过，可幂等重跑。
    """
    changed = False

    # 1. Leaflet CSS + 反相 filter CSS → 注入到 </head> 之前
    if LEAFLET_CSS_HERE not in html_content and "</head>" in html_content:
        block = f"{LEAFLET_CSS}\n  {CN_TILE_FILTER_CSS}\n  {LEAFLET_CSS_HERE}\n"
        html_content = html_content.replace("</head>", block + "</head>", 1)
        changed = True
        print("[OK] 注入 Leaflet CSS + dark filter CSS 到 <head>")

    # 2. Leaflet JS + WGS84↔GCJ-02 转换 → 注入到 <body> 顶部（确保地图 init 之前函数已定义）
    if LEAFLET_JS_HERE not in html_content and "<body" in html_content:
        # 在 <body 之后立刻插入（保留原有 body 属性）
        m = re.search(r"<body([^>]*)>", html_content)
        if not m:
            raise SystemExit("ERROR: 未找到 <body> 标签")
        block = f"\n  {LEAFLET_JS}\n  {COORDTRANS_JS}\n  {LEAFLET_JS_HERE}\n"
        html_content = html_content[:m.end()] + block + html_content[m.end():]
        changed = True
        print("[OK] 注入 Leaflet JS + WGS84↔GCJ-02 转换到 <body> 顶部")

    return html_content, changed


def main():
    d = json.load(open(JSON, encoding="utf-8"))
    html_content = open(HTML, encoding="utf-8").read()

    # 1. 一次性注入外部资产（Leaflet CDN + 转换 + dark filter CSS）
    html_content, _ = inject_external_assets(html_content)

    # 2. 移除旧 A_START..A_END 区间
    if A_START in html_content:
        html_content = re.sub(re.escape(A_START) + r".*?" + re.escape(A_END), "", html_content, flags=re.S)
        print("[OK] 移除旧 WEATHER 区块")

    # 3. 渲染新区块
    block = build_block(d)

    marker = '<footer '
    idx = html_content.find(marker)
    if idx == -1:
        raise SystemExit("ERROR: <footer> 锚点缺失，中止")
    html_content = html_content[:idx] + block + "\n" + html_content[idx:]

    open(HTML, "w", encoding="utf-8").write(html_content)
    print(f"[OK] 注入完成：站点 {d['site']['name']}，实时 {d['current']['weather_text']}，告警 {len(d['alerts'])} 条")
    assert A_START in html_content and A_END in html_content
    assert html_content.count("<!-- WEATHER_LIVE_START -->") == 1
    assert html_content.count("<!-- WEATHER_LIVE_END -->") == 1
    # 外部资产也应在
    assert LEAFLET_CSS_HERE in html_content and LEAFLET_JS_HERE in html_content
    print(f"[OK] 外部资产：Leaflet CDN + dark filter CSS 已就绪")


if __name__ == "__main__":
    main()
