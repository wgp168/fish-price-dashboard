# 抖音鳜鱼·鲈鱼 视频互动数据 — API 申请与配置说明

> 适用：将「鳜鱼鲈鱼价格看板.html」社媒板块的抖音互动数据，从 08-18 快照升级为可定期刷新的实时抓取。
> 配套脚本：`douyin_search_crawler.py`

---

## 0. 背景与结论

原 `AgentKey（TikHub）` 连接器已于 2026-08-31 从本工作区移除；`八爪鱼（bazhuayu）` 在公开连接器市场中也搜不到。
经调研确认：

| 方案 | 是否公开开放 API | 费用 | 申请难度 | 字段完整度 | 推荐度 |
|------|----------------|------|----------|-----------|--------|
| **抖音开放平台官方 OpenAPI**（关键词搜索视频 v2） | ✅ 是 | 免费（按调用量配额） | 需企业主体认证（营业执照+对公打款），审核 2~3 工作日 | 赞/评/转/播 ✅；粉丝/收藏 ❌ | ⭐⭐⭐⭐⭐ |
| 飞瓜数据 | ❌ 仅企业定制 | 付费（专业版以上才有 API 权限） | 需购买会员 + 商务对接 | 最全（含粉丝、带货） | ⭐⭐⭐ |
| 新抖（新榜） | ❌ 仅企业定制 | 付费 | 需商务「新媒体 API 数据定制」 | 全 | ⭐⭐⭐ |
| 抖查查 | ❌ 仅企业定制 | 付费 | 需商务 | 全 | ⭐⭐⭐ |

**结论：主推「抖音开放平台官方 OpenAPI」**——免费、字段基本匹配、自己能申请；
飞瓜/新抖/抖查查 作为付费备选（脚本已预留适配层，拿到商务 endpoint 即可启用）。

⚠️ 官方「关键词搜索视频」接口**不含粉丝数与收藏数**，脚本统一记 `—`。若必须拿粉丝/收藏，需另购飞瓜/新抖等或申请用户级授权接口。

---

## 1. 抖音开放平台官方 OpenAPI（主推路径）

### 1.1 申请步骤
1. 打开 https://open.douyin.com ，用**企业主体**（营业执照 + 对公账户打款验证）注册/登录。
2. 控制台 → 我的应用 → 创建应用（选择「网站应用」或「移动应用」均可）。
3. 在应用「能力管理」中申请 **「视频垂搜 / 抖音视频关键词搜索」** 能力（scope：`aweme.dy.video_search_v2`）。
   - 填写真实使用场景（例：*"监测水产行情类短视频话题热度，辅助价格趋势研判"*）。
   - 平台审核 2~3 个工作日。
4. 审核通过后，在应用「基础信息」拿到 **Client Key / Client Secret**（即脚本所需的 `client_key` / `client_secret`）。

### 1.2 权限与限制
- 授权方式：`client_token`（应用级，无需用户 OAuth），接口为 `GET /dy_open_api/v2/search/video/`。
- 返回字段：`title`、`author.nickname/uid/avatar`、`create_time`、`statistics.digg_count / comment_count / share_count / play_count`、`share_url`。
- 频率：有 QPS 限制，正式环境可申请提额；单请求 `count` 最大 20。
- 内容受抖音内容安全策略过滤，仅返回公开可见视频。

### 1.3 配置与运行
在 `douyin_config.json`（与脚本同目录）填入：
```json
{
  "official": {
    "client_key": "你的ClientKey",
    "client_secret": "你的ClientSecret"
  }
}
```
或直接用环境变量 `DOUYIN_CLIENT_KEY` / `DOUYIN_CLIENT_SECRET`。

运行（真实抓取并注入看板）：
```bash
python3 douyin_search_crawler.py --platform official \
    --keywords "鳜鱼价格" "鲈鱼价格" --inject
```
也可先 `--demo --inject` 看效果（无需 Key）。

---

## 2. 飞瓜 / 新抖 / 抖查查（付费备选）

三家均为 **付费 SaaS**，数据 API 不公开，需：
1. 到对应官网注册并购买企业版 / 数据 API 套餐；
2. 向商务索取 **接口 endpoint + 鉴权方式 + 返回结构文档**；
3. 填入 `douyin_config.json` 对应字段（`feigua` / `xindou` / `douchacha` 的 `endpoint` + `api_key`）；
4. 在 `douyin_search_crawler.py` 里对应 Adapter 的 `_normalize` 实现字段映射（脚本已搭好骨架，按文档补全即可）。

> 这三家的优势是能拿到**粉丝数、收藏数**等官方搜索接口没有的字段，且覆盖快手/B站等多平台。

---

## 3. 脚本能力一览（`douyin_search_crawler.py`）

- 平台可切：`--platform official|feigua|xindou|douchacha`
- 关键词可配：`--keywords "鳜鱼价格" "鲈鱼价格"`
- 排序/时间窗：`--sort-type 0|1|2`（综合/最多赞/最新）、`--publish-time 0|1|7|180`
- 翻页/每页：`--page N --count 20`
- 导出：`--json out.json --csv out.csv`
- 注入看板：`--inject`（写入 `鳜鱼鲈鱼价格看板.html` 的 `<!-- DOUYIN_LIVE_START/END -->` 锚点区块）
- 无 Key 预览：`--demo --inject`

字段口径：官方接口**无粉丝数/收藏数**（记 `—`）；互动数为抓取时点快照，非实时滚动值。

---

## 4. 当前状态与下一步
- 看板社媒板块已保留 08-18 帖子快照 + 08-31 联网检索热点综述（WebSearch）。
- 待你完成「抖音开放平台企业认证 + 申请视频垂搜能力」后，把 Key 给我（或填进 `douyin_config.json`），我一键运行 `--inject` 刷新为真实互动数据。
- 本地 git 仍未推送 GitHub，待你提供仓库地址 + Token。
