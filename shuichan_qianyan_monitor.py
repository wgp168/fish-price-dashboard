#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水产前沿《特水鱼周报》监控 + 塘头价表自动替换
==============================================
目标：关注周报更新时间，发现新一期（如第 29 期）发布后，及时替换看板
「一、鳜鱼 / 二、鲈鱼」中的「出塘价（塘头价）分规格」卡片。

状态文件 qianyan_state.json：{latest_issue, latest_date, source}
看板锚点  ：<!-- 水产前沿塘头价-鳜鱼 start/end --> 与 <-鲈鱼 start/end -->

用法
----
  # 1) 检查官网是否有新一期（best-effort，依赖 fishfirst.cn 可访问）
  python shuichan_qianyan_monitor.py --check

  # 2) 拿到新一期截图 → 视觉 OCR 提取表格 → 写 rows.json → 应用替换
  python shuichan_qianyan_monitor.py --apply --issue 29 --date 2026-08-25 \
        --json qianyan_issue29.json

  # rows.json 结构：
  # {"gui":[{"region":"广东 佛山","spec":"2成中鳜","price":"40","change":"持平"},
  #         ...],
  #  "lu": [{"region":"广东","spec":"9两上","price":"8.8–9.3","change":"涨 0.5"}, ...]}

依赖：--check 需要联网；--apply 纯本地。
"""
import os, sys, json, re, argparse, subprocess, datetime, urllib.request, ssl

HERE = os.path.dirname(os.path.abspath(__file__))
DASHBOARD = os.path.join(HERE, "鳜鱼鲈鱼价格看板.html")
STATE = os.path.join(HERE, "qianyan_state.json")
QIANYAN_URL = os.environ.get("QIANYAN_URL",
                             "https://www.fishfirst.cn/")

GUI_START = "<!-- 水产前沿塘头价-鳜鱼 start -->"
GUI_END   = "<!-- 水产前沿塘头价-鳜鱼 end -->"
LU_START  = "<!-- 水产前沿塘头价-鲈鱼 start -->"
LU_END    = "<!-- 水产前沿塘头价-鲈鱼 end -->"


def load_state() -> dict:
    if os.path.exists(STATE):
        return json.load(open(STATE, encoding="utf-8"))
    return {"latest_issue": 28, "latest_date": "2026-08-11",
            "source": "水产前沿《特水鱼周报 2026 第28期》"}


def save_state(s: dict):
    json.dump(s, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def badge(change: str):
    c = (change or "").strip()
    if c.startswith("涨") or "▲" in c:
        return f'<span class="badge b-up">▲ {c.lstrip("▲").strip()}</span>'
    if c.startswith("跌") or "▼" in c:
        return f'<span class="badge b-down">▼ {c.lstrip("▼").strip()}</span>'
    return f'<span class="badge b-flat">■ {c or "持平"}</span>'


def build_card(species_label, tag_cls, issue, date, rows, note):
    trs = "".join(
        f'<tr><td>{r.get("region","")}</td>'
        f'<td><span class="spec spec-s">{r.get("spec","")}</span></td>'
        f'<td class="price">{r.get("price","")}</td>'
        f'<td>{badge(r.get("change",""))}</td></tr>'
        for r in rows)
    return (
        '      <div class="card">\n'
        f'        <h3><span class="tag {tag_cls}">{species_label}</span> 出塘价（塘头价）分规格</h3>\n'
        f'        <div class="csub">来源：水产前沿《特水鱼周报 2026 第{issue}期》· {date}（环比）</div>\n'
        '        <table>\n'
        '          <thead><tr><th>产区</th><th>规格</th><th>塘头价</th><th>较上周</th></tr></thead>\n'
        f'          <tbody>{trs}</tbody>\n'
        '        </table>\n'
        f'        <div class="csub" style="margin-top:12px">※ {note}</div>\n'
        '      </div>')


def merge(html, gui_card, lu_card):
    for start, end, block in ((GUI_START, GUI_END, gui_card),
                              (LU_START, LU_END, lu_card)):
        i = html.find(start)
        j = html.find(end)
        if i < 0 or j < 0 or j < i:
            raise RuntimeError(f"未找到锚点：{start} / {end}")
        html = html[:i + len(start)] + "\n" + block + "\n" + html[j:]
    return html


def do_check():
    state = load_state()
    print(f"[状态] 当前最新：第 {state['latest_issue']} 期（{state['latest_date']}）")
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(QIANYAN_URL,
                                     headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=20, context=ctx).read().decode("utf-8", "ignore")
        # 抓取「特水鱼周报」后的期号
        issues = re.findall(r"特水鱼周报[^<]*?第?\s*(\d+)\s*期", html)
        if issues:
            latest = max(int(x) for x in issues)
            print(f"[官网] 检测到最新期号：第 {latest} 期")
            if latest > state["latest_issue"]:
                print(f"🔔 发现新一期（第 {latest} 期）！请截图后运行 "
                      f"`python shuichan_qianyan_monitor.py --apply --issue {latest} "
                      f"--date <发布日> --json qianyan_issue{latest}.json`")
            else:
                print("[官网] 暂未发布比当前更新的期数。")
        else:
            print("[官网] 未从页面解析到期号，可能页面结构变化或需登录，建议手动访问 fishfirst.cn 核对。")
    except Exception as e:
        print(f"[WARN] 官网检查失败（{e}），请手动访问 fishfirst.cn 或等用户发来新一期截图。")


def do_apply(issue, date, json_path, no_commit):
    state = load_state()
    if issue <= state["latest_issue"]:
        print(f"[跳过] 第 {issue} 期 ≤ 当前最新第 {state['latest_issue']} 期，无需替换。")
        return
    data = json.load(open(json_path, encoding="utf-8"))
    gui_rows = data.get("gui", [])
    lu_rows = data.get("lu", [])
    # note 可由 json 提供，缺省占位
    gui_note = data.get("gui_note", f"据水产前沿第 {issue} 期（{date}）周报更新。")
    lu_note = data.get("lu_note", f"据水产前沿第 {issue} 期（{date}）周报更新。")
    gui_card = build_card("鳜鱼", "tag-gui", issue, date, gui_rows, gui_note)
    lu_card = build_card("鲈鱼", "tag-lu", issue, date, lu_rows, lu_note)
    html = open(DASHBOARD, encoding="utf-8").read()
    html = merge(html, gui_card, lu_card)
    open(DASHBOARD, "w", encoding="utf-8").write(html)
    state.update({"latest_issue": issue, "latest_date": date,
                  "source": f"水产前沿《特水鱼周报 2026 第{issue}期》"})
    save_state(state)
    print(f"[OK] 已替换塘头价表为第 {issue} 期（{date}）：鳜鱼 {len(gui_rows)} 行 / 鲈鱼 {len(lu_rows)} 行")
    if not no_commit:
        try:
            subprocess.run(["git", "add", "-A"], check=True, cwd=HERE)
            subprocess.run(["git", "commit", "-q", "-m",
                            f"update: 水产前沿周报更新至第{issue}期（{date}）"],
                           check=True, cwd=HERE)
            print("[OK] 已 git commit")
        except Exception as e:
            print(f"[WARN] git commit 失败: {e}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="检查官网是否有新一期")
    ap.add_argument("--apply", action="store_true", help="应用新一期数据替换塘头价表")
    ap.add_argument("--issue", type=int, help="新一期期号")
    ap.add_argument("--date", help="新一期发布日期 YYYY-MM-DD")
    ap.add_argument("--json", help="新一期结构化 rows.json")
    ap.add_argument("--no-commit", action="store_true")
    args = ap.parse_args()
    if args.check:
        do_check()
    elif args.apply:
        if not (args.issue and args.date and args.json):
            print("[ERR] --apply 需 --issue --date --json", file=sys.stderr)
            sys.exit(1)
        do_apply(args.issue, args.date, args.json, args.no_commit)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
