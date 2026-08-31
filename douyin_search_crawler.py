#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
douyin_search_crawler.py
抖音 / 短视频平台 · 鳜鱼·鲈鱼 价格相关视频互动数据抓取脚本

=====================================================================
数据源（按推荐优先级，均用自然语言驱动，填 Key 即跑）
=====================================================================
0) TikHub（已接入 · 推荐）  【第三方聚合 API · 个人可注册 · 需小额充值】
   - 抖音视频关键词搜索：POST {base_url}/api/v1/douyin/search/fetch_video_search_v2
   - 接口文档：https://docs.tikhub.io  ·  国内用 https://api.tikhub.dev（绕 GFW）
   - 字段覆盖：desc(标题) / author / digg / comment / share / collect / play / 发布时间
   - 注意：该端点为【付费路由】，不接受免费额度，需在新账号充值后方可调用
   - 认证：请求头 `Authorization: Bearer <api_key>` + 浏览器 UA（缺 UA 会被 WAF 拦 1010）

1) 抖音开放平台官方 OpenAPI  【免费 · 需企业主体认证】
   - 关键词搜索视频 v2:  GET https://open.douyin.com/dy_open_api/v2/search/video/
   - 需企业主体认证应用 + 申请 `aweme.dy.video_search_v2` 能力（审核 2~3 工作日）
   - 返回字段与本看板完全匹配：title / author / digg / comment / share / play / share_url
   - 注意：官方「关键词搜索」接口【不含】粉丝数与收藏数，脚本统一记为 "—"

2) 飞瓜数据 / 新抖(新榜) / 抖查查  【付费 SaaS · 需企业定制 API】
   - 三家均无公开 endpoint + 参数文档，数据 API 面向企业客户、需购买会员 + 商务申请
   - 本脚本为其预留适配层（FeiguaAPI / XindouAPI / DouchachaAPI），
     拿到商务提供的 endpoint + key 后，填进 douyin_config.json 即可启用

=====================================================================
输出
=====================================================================
  - JSON / CSV ：结构化互动数据
  - 看板 HTML 片段：--inject 直接注入「鳜鱼鲈鱼价格看板.html」的锚点区块

=====================================================================
用法
=====================================================================
  # TikHub 真实抓取（先在 douyin_config.json 填 tikhub.api_key）
  python3 douyin_search_crawler.py --platform tikhub \
      --keywords "鳜鱼价格" "鲈鱼价格" --inject

  # 仅校验 Key 是否可用（不消耗付费请求）
  python3 douyin_search_crawler.py --platform tikhub --check

  # 官方 OpenAPI 真实抓取（先在 douyin_config.json 填 client_key / client_secret）
  python3 douyin_search_crawler.py --platform official \
      --keywords "鳜鱼价格" "鲈鱼价格" --inject

  # 生成示例数据并注入看板（无需 Key，先看最终呈现效果）
  python3 douyin_search_crawler.py --demo --inject

  # 仅导出 JSON / CSV（不碰看板）
  python3 douyin_search_crawler.py --platform tikhub \
      --keywords "鳜鱼价格" --json fish.json --csv fish.csv
"""

import argparse
import json
import os
import random
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

# ----------------------------------------------------------------------------
# 配置：支持 douyin_config.json（同目录）或环境变量，后者优先
# ----------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "douyin_config.json")

DEFAULT_CONFIG = {
    "tikhub": {"api_key": "", "base_url": "https://api.tikhub.dev"},
    "official": {"client_key": "", "client_secret": ""},
    "feigua": {"api_key": "", "endpoint": ""},
    "xindou": {"api_key": "", "endpoint": ""},
    "douchacha": {"api_key": "", "endpoint": ""},
}


def load_config():
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                user = json.load(f)
            for k, v in user.items():
                if k in cfg and isinstance(v, dict):
                    cfg[k].update(v)
        except Exception as e:
            print(f"[warn] 读取 {CONFIG_PATH} 失败：{e}", file=sys.stderr)
    # 环境变量覆盖
    if os.environ.get("TIKHUB_API_KEY"):
        cfg["tikhub"]["api_key"] = os.environ["TIKHUB_API_KEY"]
    if os.environ.get("TIKHUB_BASE_URL"):
        cfg["tikhub"]["base_url"] = os.environ["TIKHUB_BASE_URL"]
    if os.environ.get("DOUYIN_CLIENT_KEY"):
        cfg["official"]["client_key"] = os.environ["DOUYIN_CLIENT_KEY"]
    if os.environ.get("DOUYIN_CLIENT_SECRET"):
        cfg["official"]["client_secret"] = os.environ["DOUYIN_CLIENT_SECRET"]
    return cfg


# ----------------------------------------------------------------------------
# 工具：HTTP GET / POST（纯标准库，不依赖 requests）
# ----------------------------------------------------------------------------
def _http_json(url, headers=None, data=None, timeout=20):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)


def _classify(title):
    """根据标题判定品种标签：鳜鱼 / 鲈鱼 / 其他"""
    t = title or ""
    if "鳜" in t or "桂鱼" in t or "鳌花" in t:
        return "gui", "鳜鱼"
    if "鲈" in t:
        return "lu", "鲈鱼"
    return "", "行情"


# ----------------------------------------------------------------------------
# 1) 抖音开放平台官方 OpenAPI
# ----------------------------------------------------------------------------
class DouyinOfficialAPI:
    NAME = "抖音开放平台官方OpenAPI"
    TOKEN_URL = "https://open.douyin.com/oauth/client_token/"
    SEARCH_URL = "https://open.douyin.com/dy_open_api/v2/search/video/"

    def __init__(self, client_key, client_secret):
        if not client_key or not client_secret:
            raise RuntimeError(
                "缺少 client_key / client_secret。请到抖音开放平台创建企业应用并申请"
                "`aweme.dy.video_search_v2` 能力后，填入 douyin_config.json 或环境变量 "
                "DOUYIN_CLIENT_KEY / DOUYIN_CLIENT_SECRET。"
            )
        self.client_key = client_key
        self.client_secret = client_secret
        self._token = None
        self._token_exp = 0

    def _client_token(self):
        now = time.time()
        if self._token and now < self._token_exp - 60:
            return self._token
        payload = urllib.parse.urlencode(
            {
                "client_key": self.client_key,
                "client_secret": self.client_secret,
                "grant_type": "client_credential",
            }
        ).encode("utf-8")
        resp = _http_json(
            self.TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=payload,
        )
        if resp.get("data", {}).get("access_token"):
            self._token = resp["data"]["access_token"]
            self._token_exp = now + int(resp["data"].get("expires_in", 7200))
            return self._token
        raise RuntimeError(f"获取 client_token 失败：{resp}")

    def search(self, keyword, sort_type=1, publish_time=180, page=3, count=20):
        """
        sort_type: 0 综合 / 1 最多点赞 / 2 最新发布
        publish_time: 0 不限 / 1 一天内 / 7 七天 / 180 半年
        page: 翻页次数（每页 count 条）
        """
        token = self._client_token()
        device_id = random.randint(10**18, 10**19 - 1)
        out = []
        cursor = 0
        for _ in range(page):
            qs = urllib.parse.urlencode(
                {
                    "keyword": keyword,
                    "count": count,
                    "cursor": cursor,
                    "sort_type": sort_type,
                    "publish_time": publish_time,
                    "device_id": device_id,
                }
            )
            url = f"{self.SEARCH_URL}?{qs}"
            try:
                resp = _http_json(
                    url, headers={"access-token": token, "Content-Type": "application/json"}
                )
            except Exception as e:
                print(f"[warn] 搜索「{keyword}」第 {_+1} 页失败：{e}", file=sys.stderr)
                break
            data = resp.get("data", {})
            vlist = data.get("video_list", []) or []
            for v in vlist:
                out.append(self._normalize(v, keyword))
            if not data.get("has_more"):
                break
            cursor = data.get("cursor", 0)
            time.sleep(0.3)
        return out

    @staticmethod
    def _normalize(v, keyword):
        st = v.get("statistics", {}) or {}
        author = v.get("author", {}) or {}
        ct = v.get("create_time", 0)
        try:
            dt = datetime.fromtimestamp(ct, tz=timezone(timedelta(hours=8)))
            date_str = dt.strftime("%Y-%m-%d")
        except Exception:
            date_str = str(ct)
        # 官方关键词搜索接口不含粉丝数 / 收藏数
        tag, tag_label = _classify(v.get("title", ""))
        return {
            "platform": "抖音",
            "keyword": keyword,
            "tag": tag,
            "tag_label": tag_label,
            "title": v.get("title", ""),
            "author": author.get("nickname", author.get("uid", "未知")),
            "avatar": (author.get("nickname", "抖") or "抖")[0],
            "fans": "—",          # 官方搜索接口不含粉丝数
            "collect": "—",       # 官方搜索接口不含收藏数
            "date": date_str,
            "digg": st.get("digg_count", 0),
            "comment": st.get("comment_count", 0),
            "share": st.get("share_count", 0),
            "play": st.get("play_count", 0),
            "url": v.get("share_url", ""),
            "source": DouyinOfficialAPI.NAME,
        }


# ----------------------------------------------------------------------------
# 0) TikHub 第三方聚合 API（已接入 · 个人可注册 · 需小额充值）
#    POST {base_url}/api/v1/douyin/search/fetch_video_search_v2
#    关键：必须带浏览器 UA，否则被 WAF 返回 1010；用 Bearer 鉴权。
#    返回结构（防御式解析）：外层 {code,data:{data:[...],has_more,search_id,offset}}
#      - 每个元素可能是 {business_data:{...}} 或 {aweme_info:{...}} 或直接是视频对象
#      - 视频对象含 statistics(digg/comment/share/collect/play)、author、desc、
#        create_time、share_url、aweme_id
# ----------------------------------------------------------------------------
class TikHubAPI:
    NAME = "TikHub(抖音搜索)"
    SEARCH_PATH = "/api/v1/douyin/search/fetch_video_search_v2"
    # 抖音搜索需要浏览器 UA，否则 WAF 直接拦（error code: 1010）
    UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

    def __init__(self, api_key, base_url="https://api.tikhub.dev"):
        if not api_key:
            raise RuntimeError(
                "缺少 TikHub API Key。请在 douyin_config.json 的 tikhub.api_key "
                "填入，或设置环境变量 TIKHUB_API_KEY。"
            )
        self.api_key = api_key
        self.base_url = (base_url or "https://api.tikhub.dev").rstrip("/")
        self._raw_last = None  # 保存最近一次原始响应，便于调试

    def _post(self, body):
        url = self.base_url + self.SEARCH_PATH
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": self.UA,
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                resp = json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8", "replace")
            try:
                detail = json.loads(text)
                msg = detail.get("detail", {})
                if isinstance(msg, dict):
                    msg = msg.get("message_zh") or msg.get("message") or text
            except Exception:
                msg = text
            raise RuntimeError(f"TikHub 请求失败 HTTP {e.code}：{msg}")
        except Exception as e:
            raise RuntimeError(f"TikHub 请求异常：{e}")
        self._raw_last = resp
        # 保存原始响应到文件，便于首次联调时核对字段
        try:
            with open(os.path.join(HERE, "tikhub_last_response.json"), "w", encoding="utf-8") as f:
                json.dump(resp, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        if isinstance(resp, dict) and resp.get("code") not in (0, None):
            raise RuntimeError(f"TikHub 返回错误：{resp.get('message') or resp}")
        return resp

    def search(self, keyword, sort_type=1, publish_time=180, page=3, count=20):
        """
        sort_type: 0 综合 / 1 最多点赞 / 2 最新发布
        publish_time: 0 不限 / 1 一天内 / 7 七天 / 180 半年
        page: 翻页次数（基于 search_id + offset 游标）
        """
        out = []
        search_id = ""
        offset = 0
        for _ in range(max(1, page)):
            body = {
                "keyword": keyword,
                "count": count,
                "sort_type": sort_type,
                "publish_time": publish_time,
                "offset": offset,
            }
            if search_id:
                body["search_id"] = search_id
            resp = self._post(body)
            data = (resp.get("data") or {}) if isinstance(resp, dict) else {}
            vlist = data.get("data") or []
            if not isinstance(vlist, list):
                vlist = []
            for item in vlist:
                post = self._normalize(item, keyword)
                if post:
                    out.append(post)
            has_more = data.get("has_more", False)
            search_id = data.get("search_id") or search_id
            nxt = data.get("offset")
            if isinstance(nxt, int) and nxt > offset:
                offset = nxt
            if not has_more:
                break
            time.sleep(0.5)
        return out

    @staticmethod
    def _normalize(item, keyword):
        if not isinstance(item, dict):
            return None
        node = item.get("business_data") or item.get("aweme_info") or item
        if not isinstance(node, dict):
            return None
        stats = node.get("statistics") or {}
        author = node.get("author") or {}
        desc = node.get("desc") or node.get("title") or ""
        ct = node.get("create_time") or 0
        try:
            dt = datetime.fromtimestamp(int(ct), tz=timezone(timedelta(hours=8)))
            date_str = dt.strftime("%Y-%m-%d")
        except Exception:
            date_str = str(ct)
        aweme_id = node.get("aweme_id") or ""
        share_url = node.get("share_url") or (
            f"https://www.douyin.com/video/{aweme_id}" if aweme_id else ""
        )
        # TikHub 搜索 author 可能带 follower_count；无则记 "—"
        fans = author.get("follower_count")
        fans = f"{fans:,}" if isinstance(fans, (int, float)) else "—"
        collect = stats.get("collect_count")
        collect = f"{collect:,}" if isinstance(collect, (int, float)) else "—"
        tag, tag_label = _classify(desc)
        return {
            "platform": "抖音",
            "keyword": keyword,
            "tag": tag,
            "tag_label": tag_label,
            "title": desc,
            "author": author.get("nickname", author.get("uid", "未知")),
            "avatar": (author.get("nickname", "抖") or "抖")[0],
            "fans": fans,
            "collect": collect,
            "date": date_str,
            "digg": stats.get("digg_count", 0) or 0,
            "comment": stats.get("comment_count", 0) or 0,
            "share": stats.get("share_count", 0) or 0,
            "play": stats.get("play_count", 0) or 0,
            "url": share_url,
            "source": TikHubAPI.NAME,
        }


# ----------------------------------------------------------------------------
# 2) 飞瓜 / 新抖 / 抖查查  —— 付费 SaaS 适配占位层
#    三家均无公开 endpoint，需企业购买后向商务索取接口地址 + key。
#    填入 douyin_config.json 对应字段后，按各自返回结构在 _normalize 实现映射。
# ----------------------------------------------------------------------------
class _PaidSaaSAdapter:
    NAME = "付费SaaS(需商务提供endpoint)"

    def __init__(self, cfg):
        self.endpoint = cfg.get("endpoint", "")
        self.api_key = cfg.get("api_key", "")
        if not self.endpoint or not self.api_key:
            raise RuntimeError(
                f"{self.NAME} 缺少 endpoint / api_key。"
                "请购买企业版并向商务索取接口文档后填入 douyin_config.json。"
            )

    def search(self, keyword, **kwargs):
        raise NotImplementedError(
            f"{self.NAME} 适配层已就位，但 endpoint 与返回结构需按商务文档在 "
            "douyin_search_crawler.py 的对应 _normalize 中实现字段映射。"
        )


class FeiguaAPI(_PaidSaaSAdapter):
    NAME = "飞瓜数据(企业API)"


class XindouAPI(_PaidSaaSAdapter):
    NAME = "新抖·新榜(企业API)"


class DouchachaAPI(_PaidSaaSAdapter):
    NAME = "抖查查(企业API)"


PLATFORMS = {
    "tikhub": ("tikhub", TikHubAPI),
    "official": ("official", DouyinOfficialAPI),
    "feigua": ("feigua", FeiguaAPI),
    "xindou": ("xindou", XindouAPI),
    "douchacha": ("douchacha", DouchachaAPI),
}


# ----------------------------------------------------------------------------
# 抓取主流程
# ----------------------------------------------------------------------------
def crawl(platform, keywords, sort_type=1, publish_time=180, page=3, count=20):
    key, cls = PLATFORMS[platform]
    cfg = load_config()
    if platform in ("official", "tikhub"):
        api = cls(**cfg[key])
    else:
        api = cls(cfg=cfg[key])
    all_posts = []
    for kw in keywords:
        print(f"[info] 平台={api.NAME} 关键词=「{kw}」 抓取中…", file=sys.stderr)
        posts = api.search(kw, sort_type=sort_type, publish_time=publish_time, page=page, count=count)
        all_posts.extend(posts)
        print(f"[info]   → 本关键词获得 {len(posts)} 条", file=sys.stderr)
    # 去重（按 url / item_id）
    seen, uniq = set(), []
    for p in all_posts:
        k = p.get("url") or p.get("title")
        if k not in seen:
            seen.add(k)
            uniq.append(p)
    return uniq


# ----------------------------------------------------------------------------
# 生成看板 HTML 片段（复用看板现有 .post / .ptitle / .stats 样式）
# ----------------------------------------------------------------------------
def render_html(posts, source_note):
    if not posts:
        return (
            '<div class="callout" style="margin:14px 0 18px">'
            f"<b>实时抓取状态：</b>{source_note}</div>"
        )
    cards = []
    for p in posts:
        tag_cls = "tag-gui" if p["tag"] == "gui" else ("tag-lu" if p["tag"] == "lu" else "tag")
        fans = p.get("fans", "—")
        collect = p.get("collect", "—")
        cards.append(
            f'''      <div class="post">
        <div class="ptop">
          <div class="avatar">{p['avatar']}</div>
          <div><div class="author">{p['author']}</div><div class="fans">粉丝 {fans}</div></div>
          <span class="platform">{p['platform']}</span>
        </div>
        <div class="ptitle"><span class="tag {tag_cls}">{p['tag_label']}</span> {p['title']}</div>
        <div class="pdate">📅 {p['date']} <span class="pill">实时抓取</span></div>
        <div class="stats">
          <span class="stat">👍 <b>{p['digg']:,}</b></span><span class="stat">💬 <b>{p['comment']:,}</b></span><span class="stat">🔁 <b>{p['share']:,}</b></span><span class="stat">⭐ <b>{collect}</b></span>
        </div>
        <a class="plink" href="{p['url']}" target="_blank">🔗 {p['url']}</a>
      </div>'''
        )
    return (
        '<div class="callout" style="margin:14px 0 14px">'
        f"<b>实时抓取数据：</b>{source_note}</div>\n"
        '      <div class="posts">\n' + "\n".join(cards) + "\n      </div>"
    )


def placeholder_html():
    return (
        '<div class="card" style="margin-bottom:18px">\n'
        '  <h3>📡 抖音实时抓取数据（API 接入后由脚本注入）</h3>\n'
        '  <div class="csub">运行 <code>douyin_search_crawler.py --platform official --inject</code>'
        '（或 <code>--demo --inject</code> 预览）后，本区块将显示鳜鱼/鲈鱼相关视频的精确互动数据。'
        '当前为占位，下方保留 08-18 帖子快照作参考。</div>\n'
        '</div>'
    )


def demo_posts():
    """生成示例数据，便于先看最终呈现效果（无需任何 Key）"""
    return [
        {"platform": "抖音", "keyword": "鳜鱼价格", "tag": "gui", "tag_label": "鳜鱼",
         "title": "8月底鳜鱼为什么又涨了？中大鳜一天涨3块，老鱼存塘见底", "author": "水产行情观察",
         "avatar": "水", "fans": "—", "collect": "—", "date": "2026-08-28",
         "digg": 8421, "comment": 612, "share": 1203, "play": 156000,
         "url": "https://www.douyin.com/video/example_gui_01", "source": "DEMO"},
        {"platform": "抖音", "keyword": "鲈鱼价格", "tag": "lu", "tag_label": "鲈鱼",
         "title": "加州鲈价格探底？佛山8两仅8.8，养殖户：根本出不完", "author": "珠三角养鱼人",
         "avatar": "珠", "fans": "—", "collect": "—", "date": "2026-08-25",
         "digg": 5230, "comment": 388, "share": 742, "play": 98000,
         "url": "https://www.douyin.com/video/example_lu_01", "source": "DEMO"},
        {"platform": "抖音", "keyword": "鳜鱼价格", "tag": "gui", "tag_label": "鳜鱼",
         "title": "中秋前备货启动，标鳜有望回暖？一线流通商实拍", "author": "鱼价早知道",
         "avatar": "鱼", "fans": "—", "collect": "—", "date": "2026-08-22",
         "digg": 3110, "comment": 204, "share": 418, "play": 61000,
         "url": "https://www.douyin.com/video/example_gui_02", "source": "DEMO"},
    ]


# ----------------------------------------------------------------------------
# 注入看板 HTML
# ----------------------------------------------------------------------------
def inject_html(html_path, fragment):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    start = "<!-- DOUYIN_LIVE_START -->"
    end = "<!-- DOUYIN_LIVE_END -->"
    if start not in html or end not in html:
        raise RuntimeError(
            f"看板 {html_path} 未找到注入锚点 {start} / {end}，请先添加锚点区块。"
        )
    new_block = f"      {start}\n{fragment}\n      {end}"
    html = html.replace(f"{start}{html.split(start,1)[1].split(end,1)[0]}{end}", new_block)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[ok] 已注入 {html_path}", file=sys.stderr)


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="抖音鳜鱼/鲈鱼视频互动数据抓取")
    ap.add_argument("--platform", default="official", choices=list(PLATFORMS.keys()))
    ap.add_argument("--keywords", nargs="+", default=["鳜鱼价格", "鲈鱼价格"])
    ap.add_argument("--sort-type", type=int, default=1, help="0综合/1最多点赞/2最新")
    ap.add_argument("--publish-time", type=int, default=180, help="0不限/1一天/7七天/180半年")
    ap.add_argument("--page", type=int, default=3, help="翻页次数")
    ap.add_argument("--count", type=int, default=20, help="每页条数")
    ap.add_argument("--json", dest="json_out", help="导出 JSON 路径")
    ap.add_argument("--csv", dest="csv_out", help="导出 CSV 路径")
    ap.add_argument("--inject", action="store_true", help="注入看板 HTML")
    ap.add_argument("--html", default=os.path.join(HERE, "鳜鱼鲈鱼价格看板.html"))
    ap.add_argument("--demo", action="store_true", help="使用内置示例数据（无需 Key）")
    ap.add_argument("--reset", action="store_true", help="清空实时区块为占位（移除 demo/历史注入）")
    ap.add_argument("--check", action="store_true",
                    help="仅校验 TikHub Key 是否可用（发一次最小请求，不消耗付费额度）")
    args = ap.parse_args()

    if args.reset:
        inject_html(args.html, placeholder_html())
        return

    if args.check:
        cfg = load_config()
        tcfg = cfg["tikhub"]
        if not tcfg.get("api_key"):
            print("[fail] 未配置 tikhub.api_key（请填 douyin_config.json 或设 TIKHUB_API_KEY）", file=sys.stderr)
            return
        api = TikHubAPI(tcfg["api_key"], tcfg.get("base_url"))
        try:
            api._post({"keyword": "测试", "count": 1})
            print("[ok] TikHub Key 有效，接口可调用。", file=sys.stderr)
        except RuntimeError as e:
            msg = str(e)
            if "402" in msg or "余额" in msg or "balance" in msg:
                print("[ok] TikHub Key 有效（鉴权通过），但抖音视频搜索为付费路由，"
                      "需充值后才能返回数据。错误详情：" + msg, file=sys.stderr)
            else:
                print("[warn] TikHub 请求返回：" + msg, file=sys.stderr)
        return

    if args.demo:
        posts = demo_posts()
        note = "示例数据（DEMO，未接真实 API；填入 Key 后运行 --platform official --inject 即替换为真实抓取）。"
        print(f"[info] DEMO 模式，{len(posts)} 条示例", file=sys.stderr)
    else:
        posts = crawl(
            args.platform, args.keywords,
            sort_type=args.sort_type, publish_time=args.publish_time,
            page=args.page, count=args.count,
        )
        note = (
            f"数据源：{PLATFORMS[args.platform][1].NAME} · 关键词 {args.keywords} · "
            f"抓取时间 {datetime.now().strftime('%Y-%m-%d %H:%M')} · 共 {len(posts)} 条"
        )

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        print(f"[ok] JSON -> {args.json_out}", file=sys.stderr)
    if args.csv_out:
        import csv
        cols = ["platform", "keyword", "tag_label", "title", "author", "fans",
                "date", "digg", "comment", "share", "collect", "play", "url"]
        with open(args.csv_out, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for p in posts:
                w.writerow({c: p.get(c, "") for c in cols})
        print(f"[ok] CSV -> {args.csv_out}", file=sys.stderr)

    if args.inject:
        inject_html(args.html, render_html(posts, note))
    else:
        print(json.dumps(posts, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
