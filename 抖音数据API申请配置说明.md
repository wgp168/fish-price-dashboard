# 抖音鳜鱼·鲈鱼 视频互动数据 — API 申请与配置说明

> 适用：将「鳜鱼鲈鱼价格看板.html」社媒板块的抖音互动数据，从 08-18 快照升级为可定期刷新的实时抓取。
> 配套脚本：`douyin_search_crawler.py`

---

## 0. 背景与结论（2026-08-31 更新）

原 `AgentKey（TikHub）` 工作区连接器已移除，但用户于 **2026-08-31 用邮箱 wgp_168@163.com 直接注册了 TikHub 账号**并拿到 API Key。经脚本实测：

- ✅ **Key 有效、邮箱已验证、鉴权通过**（带浏览器 UA 后请求从 WAF 拦截 1010 变为业务层 402）；
- ⚠️ 抖音视频搜索 `fetch_video_search_v2` 是**付费路由**，新账号无余额、且不接受免费额度，需**小额充值**后才会返回数据；
- 失败的请求（非 200）**不扣费**，可放心探活。

| 方案 | 是否公开开放 API | 费用 | 申请难度 | 字段完整度 | 推荐度 |
|------|----------------|------|----------|-----------|--------|
| **TikHub（已接入 · 个人可注册）** | ✅ 是（第三方聚合） | 付费（按量，~$0.001/次）；该端点不接受免费额度 | 个人邮箱注册即可 | 赞/评/转/收/播 ✅；粉丝（若返回）✅ | ⭐⭐⭐⭐⭐ |
| 抖音开放平台官方 OpenAPI（关键词搜索视频 v2） | ✅ 是 | 免费（按调用量配额） | 需企业主体认证（营业执照+对公打款），审核 2~3 工作日 | 赞/评/转/播 ✅；粉丝/收藏 ❌ | ⭐⭐⭐⭐ |
| 飞瓜数据 / 新抖（新榜）/ 抖查查 | ❌ 仅企业定制 | 付费（专业版以上才有 API） | 需购买会员 + 商务对接 | 最全（含粉丝、带货） | ⭐⭐⭐ |

**结论：当前主推 TikHub**——已注册、Key 已验证、适配器已就绪，充值后即可一键抓取注入；
官方 OpenAPI 作为「免费但需企业认证」的备选；飞瓜/新抖/抖查查 作为需要粉丝/收藏等增强字段时的付费备选（脚本已预留适配层）。

---

## 1. TikHub（当前主路径 · 已接入）

### 1.1 接口与鉴权
- 端点：`POST https://api.tikhub.dev/api/v1/douyin/search/fetch_video_search_v2`
  - 国内用 `api.tikhub.dev`（绕 GFW）；非大陆用 `api.tikhub.io`。
- 鉴权：**请求头 `Authorization: Bearer <api_key>`**；**必须带浏览器 UA**，否则被 WAF 返回 `error code: 1010`。
- 请求体：`{"keyword":"鳜鱼价格","count":20,"sort_type":1,"publish_time":180,"search_id":"","offset":0}`
  - `sort_type`：0 综合 / 1 最多点赞 / 2 最新发布
  - `publish_time`：0 不限 / 1 一天内 / 7 七天 / 180 半年
  - 翻页：响应 `data.has_more` + `data.search_id` + `data.offset` 游标
- 字段：视频 `desc`（标题）、`author.nickname`、`statistics.digg_count / comment_count / share_count / collect_count / play_count`、`create_time`、`share_url`、`author.follower_count`（若有）。

### 1.2 充值（唯一待办）
抖音视频搜索为付费路由，需先充值：
1. 登录 https://user.tikhub.io → 右上角「签到」可领免费试用额度（但该端点不接受免费额度，仍需**付费余额**）；
2. 到 https://user.tikhub.io/users/add_credit 充值（支持支付宝 / 银联 / PayPal / USDT，按量付费，约 $0.001/次）；
3. 余额到位后，运行下方命令即出数据。

### 1.3 配置与运行
Key 已写入 `douyin_config.json`（已加入 .gitignore，勿提交）：
```json
{
  "tikhub": {
    "api_key": "你的TikHub_API_Key",
    "base_url": "https://api.tikhub.dev"
  }
}
```
也可用环境变量 `TIKHUB_API_KEY` / `TIKHUB_BASE_URL` 覆盖。

校验 Key 是否可用（发一次最小请求，不消耗付费额度）：
```bash
python3 douyin_search_crawler.py --platform tikhub --check
```
真实抓取并注入看板：
```bash
python3 douyin_search_crawler.py --platform tikhub \
    --keywords "鳜鱼价格" "鲈鱼价格" --inject
```
仅导出 JSON / CSV（不碰看板）：
```bash
python3 douyin_search_crawler.py --platform tikhub --keywords "鳜鱼价格" --json fish.json --csv fish.csv
```

---

## 2. 抖音开放平台官方 OpenAPI（免费备选）

### 2.1 申请步骤
1. 打开 https://open.douyin.com ，用**企业主体**（营业执照 + 对公账户打款验证）注册/登录。
2. 控制台 → 我的应用 → 创建应用。
3. 在应用「能力管理」中申请 **「视频垂搜 / 抖音视频关键词搜索」** 能力（scope：`aweme.dy.video_search_v2`），审核 2~3 工作日。
4. 拿到 **Client Key / Client Secret**（脚本的 `client_key` / `client_secret`）。

### 2.2 配置与运行
```json
{ "official": { "client_key": "你的ClientKey", "client_secret": "你的ClientSecret" } }
```
或直接用环境变量 `DOUYIN_CLIENT_KEY` / `DOUYIN_CLIENT_SECRET`。
```bash
python3 douyin_search_crawler.py --platform official \
    --keywords "鳜鱼价格" "鲈鱼价格" --inject
```
⚠️ 官方「关键词搜索视频」接口**不含粉丝数与收藏数**，脚本统一记 `—`。

---

## 3. 飞瓜 / 新抖 / 抖查查（付费增强备选）

三家均为 **付费 SaaS**，数据 API 不公开，需：
1. 到对应官网注册并购买企业版 / 数据 API 套餐；
2. 向商务索取 **接口 endpoint + 鉴权方式 + 返回结构文档**；
3. 填入 `douyin_config.json` 对应字段（`feigua` / `xindou` / `douchacha` 的 `endpoint` + `api_key`）；
4. 在 `douyin_search_crawler.py` 里对应 Adapter 的 `_normalize` 实现字段映射（脚本已搭好骨架）。

> 这三家的优势是能拿到**粉丝数、收藏数**等官方搜索接口没有的字段，且覆盖快手/B站等多平台。

---

## 4. 脚本能力一览（`douyin_search_crawler.py`）

- 平台可切：`--platform tikhub|official|feigua|xindou|douchacha`
- 仅校验 Key：`--check`（不消耗付费额度）
- 关键词可配：`--keywords "鳜鱼价格" "鲈鱼价格"`
- 排序/时间窗：`--sort-type 0|1|2`（综合/最多赞/最新）、`--publish-time 0|1|7|180`
- 翻页/每页：`--page N --count 20`
- 导出：`--json out.json --csv out.csv`
- 注入看板：`--inject`（写入 `鳜鱼鲈鱼价格看板.html` 的 `<!-- DOUYIN_LIVE_START/END -->` 锚点区块）
- 无 Key 预览：`--demo --inject`
- 清空实时区块：`--reset`

字段口径：互动数为抓取时点快照，非实时滚动值；TikHub 若返回 `author.follower_count` 则展示粉丝数，否则记 `—`。

---

## 5. 当前状态与下一步
- 看板社媒板块已保留 08-18 帖子快照 + 08-31 联网检索热点综述（WebSearch）。
- **TikHub 已注册、Key 已配置并验证有效**；唯一待办 = 在 TikHub 后台充值付费余额。
- 充值完成后，运行 `python3 douyin_search_crawler.py --platform tikhub --inject` 即可将精确互动数据（赞/评/转/收/播）注入看板。
- 本地 git 仍未推送 GitHub，待你提供仓库地址 + Token。
