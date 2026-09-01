#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
看板版本号管理 — 三个注入脚本共享
==================================

- 当前版本号 / 日期集中在 DASHBOARD_VERSION / DASHBOARD_VERSION_DATE
- bump_dashboard() 一次性同步：
    * HTML <title> 的版本号后缀
    * <meta name="dashboard-version"> 与 dashboard-version-date
    * Hero 区 chip-version 文本
    * 底部 VERSION_HISTORY 块里追加本次变更摘要
    * VERSION.md 表格追加一行

调用方式（注入脚本尾部）：
    from dashboard_version import bump_dashboard
    bump_dashboard(
        reason="天气数据刷新（无新增异常）",
        level="patch",            # patch / minor / major
    )

语义版本号规则（与 VERSION.md 对齐）：
- PATCH：数据/文案微调、社媒数据追加
- MINOR：新增板块、接入新数据源、引入双源校验
- MAJOR：整体改版、迁移到非 HTML 载体
"""
from __future__ import annotations
import os, re
from datetime import datetime

WS = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(WS, "鳜鱼鲈鱼价格看板.html")
VERSION_MD = os.path.join(WS, "VERSION.md")

# ============================================================
# 版本号常量 —— 改这里，所有脚本同步
# ============================================================
DASHBOARD_VERSION       = "v1.0.1"
DASHBOARD_VERSION_DATE  = "2026-09-01"
DASHBOARD_OPERATOR      = "江苏环荟"
DASHBOARD_LOCATION      = "江苏环荟·宜兴官林镇数字低碳生态养殖项目"


# ============================================================
# 内部 helper
# ============================================================
def _today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _bump(level: str, current: str) -> str:
    """语义化 bump：v1.2.3 + patch → v1.2.4"""
    m = re.match(r"^v(\d+)\.(\d+)\.(\d+)$", current.strip())
    if not m:
        raise ValueError(f"非法版本号: {current}")
    maj, minor, pat = map(int, m.groups())
    if level == "patch":
        pat += 1
    elif level == "minor":
        minor += 1
        pat = 0
    elif level == "major":
        maj += 1
        minor = 0
        pat = 0
    else:
        raise ValueError(f"未知 level: {level}，须为 patch/minor/major")
    return f"v{maj}.{minor}.{pat}"


def _sync_html(html_text: str, version: str, date_str: str, summary_line: str) -> str:
    """把新版号 + 变更摘要同步到看板 HTML（含 5 处锚点）"""
    # 1) <title> 里替换旧日期/版本号
    html_text = re.sub(
        r"（\d{4}-\d{2}-\d{2} 更新(?: · v\d+\.\d+\.\d+)?）",
        f"（{date_str} 更新 · {version}）",
        html_text,
        count=1,
    )
    # 2) <meta name="dashboard-version"> 版本号
    html_text = re.sub(
        r'(<meta name="dashboard-version" content=")v\d+\.\d+\.\d+(">)',
        rf"\g<1>{version}\g<2>",
        html_text,
    )
    # 3) <meta name="dashboard-version-date">
    html_text = re.sub(
        r'(<meta name="dashboard-version-date" content=")\d{4}-\d{2}-\d{2}(">)',
        rf"\g<1>{date_str}\g<2>",
        html_text,
    )
    # 4) chip-version 文本
    html_text = re.sub(
        r'<span class="chip chip-version"[^>]*>🏷️ 版本 v\d+\.\d+\.\d+ · \d{4}-\d{2}-\d{2}</span>',
        f'<span class="chip chip-version" data-page-node-id="VER01CHIP0001" title="看板版本号 · 完整历史见 VERSION.md">🏷️ 版本 {version} · {date_str}</span>',
        html_text,
    )
    # 5) 底部 VERSION_HISTORY 块：在 start/end 锚点之间替换「本次更新」h3 与首条 li（其余保留）
    new_block = re.sub(
        r"<strong[^>]*>本次更新 · v\d+\.\d+\.\d+（\d{4}-\d{2}-\d{2}）</strong>",
        f"<strong style=\"font-size:15px;letter-spacing:.5px\">本次更新 · {version}（{date_str}）</strong>",
        "",
        count=1,
    )  # 此处仅统计是否命中；下面单独做替换更稳

    block_re = re.compile(
        r"(<!-- VERSION_HISTORY_START -->)(.*?)(<!-- VERSION_HISTORY_END -->)",
        re.S,
    )
    m = block_re.search(html_text)
    if not m:
        return html_text

    head, body, tail = m.group(1), m.group(2), m.group(3)
    # 在 body 的第一个 <li> 前插入新变更摘要，再把"本次更新"标题改成最新
    body = re.sub(
        r"<strong[^>]*>本次更新 · v\d+\.\d+\.\d+（\d{4}-\d{2}-\d{2}）</strong>",
        f"<strong style=\"font-size:15px;letter-spacing:.5px\">本次更新 · {version}（{date_str}）</strong>",
        body,
        count=1,
    )
    new_li = f'      <li><b>{version} · {date_str}</b> · {summary_line}</li>\n'
    body = re.sub(
        r"(<ul[^>]*>\n)",
        r"\1" + new_li,
        body,
        count=1,
    )
    html_text = html_text[:m.start()] + head + body + tail + html_text[m.end():]
    return html_text


def _sync_version_md(version: str, date_str: str, summary_line: str) -> None:
    """在 VERSION.md 表格里追加一行"""
    if not os.path.exists(VERSION_MD):
        return
    with open(VERSION_MD, encoding="utf-8") as f:
        text = f.read()
    # 找到"## 历史记录"下方表格的"---"线，在其后插入新行
    marker = "| 版本 | 日期 | 变更摘要 |\n|------|------|---------|"
    new_row = f"| **{version}** | {date_str} | {summary_line} |\n"
    if marker in text:
        # 在 marker 紧跟着的下一行（即历史第一条 v1.0.1 那行）之前插入
        text = text.replace(marker, marker + "\n" + new_row, 1)
    else:
        # 兜底：直接在文件末尾追加
        text = text.rstrip() + "\n\n" + new_row
    with open(VERSION_MD, "w", encoding="utf-8") as f:
        f.write(text)


# ============================================================
# 公共入口
# ============================================================
def bump_dashboard(
    reason: str,
    level: str = "patch",
    version: str = "",
    date_str: str = "",
) -> str:
    """
    把看板版本号升级到下一级；同时把变更摘要同步到 HTML + VERSION.md

    参数:
        reason  : 本次变更摘要（中文一句话，写入 VERSION_HISTORY 第一个 <li> 与 VERSION.md 表格）
        level   : 'patch' / 'minor' / 'major'（默认 patch）
        version : 可选，强制指定版本号（默认自动按 level bump 当前 DASHBOARD_VERSION）
        date_str: 可选，强制日期（默认今天）

    返回: 升级后的版本号字符串，如 'v1.0.2'
    """
    global DASHBOARD_VERSION, DASHBOARD_VERSION_DATE

    target_version = version or _bump(level, DASHBOARD_VERSION)
    target_date    = date_str or _today_str()

    summary_line = reason.strip()
    if not summary_line:
        summary_line = "数据/文案微调"

    # 1) 同步看板 HTML
    if os.path.exists(HTML):
        with open(HTML, encoding="utf-8") as f:
            html_text = f.read()
        html_text = _sync_html(html_text, target_version, target_date, summary_line)
        with open(HTML, "w", encoding="utf-8") as f:
            f.write(html_text)

    # 2) 同步 VERSION.md
    _sync_version_md(target_version, target_date, summary_line)

    # 3) 更新模块常量（让调用方后续 print 用得到）
    DASHBOARD_VERSION = target_version
    DASHBOARD_VERSION_DATE = target_date

    return target_version


if __name__ == "__main__":
    # 单独调试：bump_dashboard(reason="手动测试 bump", level="patch")
    import sys, argparse
    ap = argparse.ArgumentParser(description="手动 bump 看板版本号")
    ap.add_argument("--reason", default="手动 bump")
    ap.add_argument("--level", default="patch", choices=["patch", "minor", "major"])
    ap.add_argument("--dry-run", action="store_true", help="只打印新版本号，不写文件")
    args = ap.parse_args()

    if args.dry_run:
        new_v = _bump(args.level, DASHBOARD_VERSION)
        print(f"[DRY-RUN] {DASHBOARD_VERSION} → {new_v}（{_today_str()}）· {args.reason}")
        sys.exit(0)

    new_v = bump_dashboard(reason=args.reason, level=args.level)
    print(f"✅ 已 bump 到 {new_v}（{_today_str()}） · {args.reason}")
    print(f"   HTML: {HTML}")
    print(f"   VERSION.md: {VERSION_MD}")
