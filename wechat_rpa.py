#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公众号 RPA 截图器（可选组件）
============================
与 wechat_ocr_pipeline.py 配合，把「人工发截图」升级为「自动截图」：

  搜狗微信（weixin.sogou.com）搜公众号 → 打开最新文章 → 整页截图 → 目录

说明
----
- 微信文章需登录/反爬，但搜狗微信可免登录检索并打开大部分文章（有频率限制/验证码）。
- 本脚本用 Playwright 驱动 Chromium；首次使用需：
      pip install playwright && playwright install chromium
- 在 CI（GitHub Actions）中直接跑 RPA 不稳定（需浏览器 + 可能的人机验证），
  建议：本地定时跑本脚本产出截图 → 提交 screenshots/ → Actions 里由 OCR 流水线消费；
  或直接沿用「用户发截图 + OCR」的半自动模式（已足够好用）。
- 截图后自动调用 wechat_ocr_pipeline.py 完成结构化与看板并入。

用法
----
  python wechat_rpa.py --accounts 科学养鱼 a渔业行情 --out screenshots
"""
import os, sys, argparse, subprocess, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_DEFAULT = ["科学养鱼", "a渔业行情"]


def ensure_playwright():
    try:
        import playwright  # noqa
    except ImportError:
        print("[SETUP] 安装 playwright + chromium：", file=sys.stderr)
        print("  pip install playwright && playwright install chromium", file=sys.stderr)
        sys.exit(1)


def screenshot_account(account, out_dir):
    """返回截图文件路径；失败返回 None。"""
    from playwright.sync_api import sync_playwright
    os.makedirs(out_dir, exist_ok=True)
    stamp = datetime.date.today().strftime("%Y%m%d")
    out = os.path.join(out_dir, f"{account}_{stamp}.png")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1200, "height": 2000})
        # 1) 搜狗微信搜号
        q = "https://weixin.sogou.com/weixin?type=1&query=" + account
        page.goto(q, timeout=30000)
        page.wait_for_timeout(2000)
        # 2) 点第一个公众号/文章结果
        try:
            page.click("a[uigs='account_name_0'], .news-list li a", timeout=10000)
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"[WARN] {account} 点击结果失败: {e}", file=sys.stderr)
            browser.close()
            return None
        # 3) 整页截图
        page.screenshot(path=out, full_page=True)
        browser.close()
    print(f"[OK] {account} 截图 → {out}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--accounts", nargs="+", default=ACCOUNTS_DEFAULT)
    ap.add_argument("--out", default=os.path.join(HERE, "screenshots"))
    ap.add_argument("--no-ocr", action="store_true", help="只截图，不调用 OCR 流水线")
    args = ap.parse_args()
    ensure_playwright()

    shots = []
    for acc in args.accounts:
        s = screenshot_account(acc, args.out)
        if s:
            shots.append((acc, s))

    if args.no_ocr or not shots:
        return
    # 截图后按来源调用 OCR 流水线
    for acc, path in shots:
        src = "科学养鱼" if "科学养鱼" in acc else "a渔业行情"
        print(f"[OCR] 处理 {src} ← {path}")
        subprocess.run([sys.executable, "wechat_ocr_pipeline.py",
                        "--images", path, "--source", src], cwd=HERE)


if __name__ == "__main__":
    main()
