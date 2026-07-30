#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 Chart.js 源码与历史价格数据内联进看板 HTML，
使单个 HTML 文件在 file:// 离线打开时图表也能正常显示。

用法：python inline_assets.py
前置：chart.umd.min.js（本地 Chart.js）、fish_prices_history.js（爬虫累积数据） 与本脚本同目录。
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(BASE, "鳜鱼鲈鱼价格看板.html")
CHART = os.path.join(BASE, "chart.umd.min.js")
HIST = os.path.join(BASE, "fish_prices_history.js")

CDN_LINE = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>'
EXT_HIST_LINE = '<script src="fish_prices_history.js"></script>'


def main():
    html = open(HTML, encoding="utf-8").read()
    chart_src = open(CHART, encoding="utf-8").read()
    hist_src = open(HIST, encoding="utf-8").read().strip()

    # 防御：极少数压缩包可能含字面 </script>，拆断避免提前闭合
    if "</script" in chart_src.lower():
        chart_src = chart_src.replace("</script>", "<\\/script>")

    assert CDN_LINE in html, "未找到 Chart.js CDN 引用行，可能已内联或路径变化"
    assert EXT_HIST_LINE in html, "未找到 fish_prices_history.js 引用行"

    # 1) 内联 Chart.js（替换 CDN 行）
    html = html.replace(CDN_LINE, "<script>\n" + chart_src + "\n</script>")

    # 2) 内联历史数据（替换外部 script 引用）
    html = html.replace(EXT_HIST_LINE, "<script>\n" + hist_src + "\n</script>")

    open(HTML, "w", encoding="utf-8").write(html)

    print("✅ 内联完成")
    print("   - 仍含 CDN 引用:", "cdn.jsdelivr" in html)
    print("   - 含 Chart 定义:", "Chart" in html and "registerable" in html)
    print("   - 含 FISH_HISTORY:", "FISH_HISTORY" in html)
    print("   - HTML 体积:", round(len(html.encode('utf-8')) / 1024, 1), "KB")


if __name__ == "__main__":
    main()
