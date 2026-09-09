# 看板 GitHub Pages 部署说明

用永久稳定的 `github.io` 链接替代会休眠的沙箱分享链接。

---

## 一、现状

| 项 | 状态 |
|---|---|
| 本地 git 仓库 | ✅ 有（main 分支） |
| GitHub 远端 | ✅ `git@github.com:wgp168/fish-price-dashboard.git` |
| SSH 主机指纹 | ✅ 已核验并加入 `~/.ssh/known_hosts`（三项指纹与 GitHub 官方一致） |
| SSH 公钥授权 | ✅ 已通过（`Hi wgp168!` 认证成功） |
| 代码推送 | ✅ 已推送 main 分支（看板 429,897 bytes / workflow / 气象 JSON 全部 200 可读取） |
| Pages 启用 | ⏳ **待用户在网页点一次**（`has_pages: false`） |
| Pages 工作流 | ✅ 已建 `.github/workflows/pages-deploy.yml` |
| 推送脚本 | ✅ 已建 `push_github.sh` |
| `.gitignore` | ✅ 已排除密钥（douyin_config / bazhuayu_config / tikhub）与 publish 副本 |

工作区 2.5M，推 GitHub 无压力。

**仓库**：https://github.com/wgp168/fish-price-dashboard
**Pages 地址（授权后生效）**：https://wgp168.github.io/fish-price-dashboard/

---

## 二、代码已推送，最后一步：开启 Pages

仓库：https://github.com/wgp168/fish-price-dashboard

SSH 授权已完成（`Hi wgp168! You've successfully authenticated`），main 分支已推送，
远端校验：看板 HTML 429,897 bytes、pages-deploy.yml、farm_weather_latest.json 全部 HTTP 200。

**当前 `has_pages: false`，需你在网页点一次**（我没法代劳：开启 Pages 要调 GitHub API，而 SSH 密钥不能用于 API，得用 PAT）。

### 操作（30 秒，一次性）

1. 打开 https://github.com/wgp168/fish-price-dashboard/settings/pages
2. **Build and deployment → Source** 选 **GitHub Actions**（不要选 "Deploy from a branch"）
3. 保存后，进 **Actions** 标签 → 左侧点「部署看板到 GitHub Pages」
4. 右上角 **Run workflow** → 选 main → 绿色按钮确认（等首次构建；之后每次 push 自动跑）

跑完约 1-2 分钟，链接生效：
```
https://wgp168.github.io/fish-price-dashboard/
```

> 备注：若你想让我以后也能直接调 API（自动开启、查运行状态、手动触发），
> 可以给我一个勾选 `repo` + `workflow` 的 Personal Access Token，我配到工作流里。

### 本机公钥（已授权，存档备查）
`~/.ssh/id_rsa` · 3072 SHA256:QpabR2iuVFotUPcPvw0+sa+r+BEjuEceewdj4llEAGw · wangganping@example.com

---

## 三、工作流做了什么

`.github/workflows/pages-deploy.yml`：
1. **触发**：main 分支上 `鳜鱼鲈鱼价格看板.html` 有变更即触发；另有每天北京 10:00 兜底重建；也可手动触发
2. **构建**：把看板 HTML 复制成 `_site/index.html`，加 `.nojekyll` 防止 Jekyll 误处理
3. **发布**：`configure-pages` → `upload-pages-artifact` → `deploy-pages`（GitHub 官方 action，无需第三方）

发布后约 1–2 分钟生效。

---

## 四、日常怎么用

每日气象自动化（09:00）已更新：会先尝试 `git push`，Pages 自动重建。
你什么都不用做，链接永远是最新数据，且**不会休眠、不会失效**。

沙箱链接（e2b）保留为兜底，但不再作为主渠道。

---

## 五、注意事项

- 仓库必须 **Public** 才能用免费 Pages
- 看板是单文件 HTML（已内联 Chart.js 与历史数据），离线也能开，Pages 只是托管
- `fish_prices_history.csv` 等数据文件会一起上传（无敏感信息）
- 密钥类文件已在 `.gitignore`，不会泄露
