# 看板版本历史（鳜鱼·鲈鱼价格数据看板）

> 每次更新务必在本表追加一行，并把看板 HTML 里 `chip-version` / `<meta name="dashboard-version">` 的版本号同步更新。
> 自动化脚本：`inject_weather_block.py` / `inject_90d_block.py` / `update_dashboard_douyin.py`
> 三者顶部均带 `DASHBOARD_VERSION` / `DASHBOARD_VERSION_DATE` 常量，与本页同步推进。

---

## 当前版本

- **v1.0.2** · **2026-09-01**
  - 地图改回**标准高德原生配色** — 取消 CSS 反相 (`invert(1) hue-rotate(180deg) …`)，路名/地名/POI 全部清晰可读，与高德官方观感一致；容器背景、控件、popup 配色同步切换到浅底
  - `dashboard_version.py` 同步增强：
    - `_sync_html` 新增「Dashboard vX.Y.Z · ...」HTML 注释行的自动 sync（之前漏了头部注释）
    - `_current_version_from_html()` 从 HTML `<meta>` 实时读当前版本，杜绝 bump_dashboard 调用前后模块常量与 HTML 漂移
    - dry-run 同步从 HTML 读 base，避免反复测试时打印陈旧版本号

---

## 历史记录

| 版本 | 日期 | 变更摘要 |
|------|------|---------|
| **v1.0.2** | 2026-09-01 | 地图改回标准高德配色 — 取消 CSS 反相、修复文字看不清，路名/地名/POI 全部清晰可读，与高德原生观感一致 |

| **v1.0.1** | 2026-09-01 | 🏷️ **新增版本号 chip + `<meta>` + `VERSION.md` 机制**，看板底部加「本次更新」变更摘要区；为后续每日自动化 bump 铺路。 |
| **v1.0.0** | 2026-09-01 | 🗺️ **江苏环荟 · 宜兴官林镇**板块正式上线：Leaflet + 高德矢量 tile + CSS 反相 → 蓝科技感地图；8 项实时气象 + 7 天预报 + 高德 vs Open-Meteo 双源校验 + 分级告警；点击任意点作为出发点 → 高德驾车导航；运营方显示「江苏环荟」，八/九编号修正。 |
| v0.9.4 | 2026-08-31 | 📈 注入抖音近 90 天热帖新区块（8 条，按热度重排），独立锚点 `DOUYIN_90D`，不覆盖 08-18 快照。 |
| v0.9.3 | 2026-08-31 | 🎬 TikHub 抖音搜索接口真实数据注入看板社媒板块（鳜鱼 7 + 鲈鱼 6 = 13 条，含赞/评/转/藏/粉丝数），并配置 `.gitignore` 排除含密钥配置。 |
| v0.9.2 | 2026-08-31 | 🐙 八爪鱼跨平台（B站）补抓：16 条鳜鱼/鲈鱼价格行情视频，新增 `process_bilibili.py` 与锚点 `CROSSPLATFORM_LIVE`；沉淀为 Skill `bazhuayu-crossplatform-crawler`。 |
| v0.9.1 | 2026-08-30 | 🐟 看板主体七节：实时出塘价、批发价、出塘 vs 批发对比、社媒板块、多平台来源、月度价格对比、历史价格序列（含 GitHub Actions 自动追加脚手架）。 |
| v0.8.0 | 2026-08-29 | 🧪 工程脚手架：农产品价格爬虫（moa_fish_crawler / public_price_crawler）、江浙沪皖区域筛选规则、可视化色板、涨红/跌绿中文习惯。 |

---

## 自动化 bump 规则（建议，写入注入脚本顶部 docstring）

```
DASHBOARD_VERSION       = "v1.0.1"   ← 模块常量；版本真值以 HTML 为准
DASHBOARD_VERSION_DATE  = "2026-09-01"
```
> 实际 bump 时 `dashboard_version.py._current_version_from_html()` 会从 HTML `<meta name="dashboard-version">` 读真值再 +1，杜绝模块常量陈旧。

- 注入脚本每次跑完，应调用公共函数 `bump_dashboard_version(reason: str)`：
  - 自动写入 HTML `<meta name="dashboard-version">`、`<title>`、`chip-version` 与底部 `VERSION_HISTORY` 摘要块
  - 末尾追加一行到 `VERSION.md`
  - 默认走 PATCH 级别，需要 MINOR/MAJOR 时显式声明
- 若脚本每天 09:00 自动化跑，每天都加一个 PATCH 太碎 → 由 automation 定时任务里维护一个"当日数据是否变化"的差分判断，仅当数据有变化时才 PATCH（详见 `automation_update` 3c5213f0 的扩展计划）。

---

## 维护备忘

- `inject_weather_block.py`：必带 `DASHBOARD_VERSION`，写入到 `WEATHER_LIVE` 注入完成后顺带 bump
- `inject_90d_block.py`：必带 `DASHBOARD_VERSION`，写入到 `DOUYIN_90D` 注入完成后顺带 bump
- `update_dashboard_douyin.py`：必带 `DASHBOARD_VERSION`，写入到 `DOUYIN_LIVE` 注入完成后顺带 bump
- HTML `chip-version` 锚点定位：`data-page-node-id="VER01CHIP0001"`（注入脚本用 `re` 精准匹配）
- HTML `VERSION_HISTORY` 锚点：`<!-- VERSION_HISTORY_START/END -->`（注入脚本用 `re.escape` 替换整段）
