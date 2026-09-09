# 看板 GitHub Pages 部署说明

用永久稳定的 `github.io` 链接替代会休眠的沙箱分享链接。

---

## 一、现状

| 项 | 状态 |
|---|---|
| 本地 git 仓库 | ✅ 有（main 分支） |
| GitHub 远端 | ❌ **尚未配置**（这是唯一缺的一步） |
| Pages 工作流 | ✅ 已建 `.github/workflows/pages-deploy.yml` |
| 推送脚本 | ✅ 已建 `push_github.sh` |
| `.gitignore` | ✅ 已排除密钥（douyin_config / bazhuayu_config / tikhub）与 publish 副本 |

工作区 2.5M，推 GitHub 无压力。

---

## 二、你需要做的（约 2 分钟）

### 1. 在 GitHub 建一个空仓库
打开 https://github.com/new
- Repository name 建议：`fish-price-dashboard`
- 选 **Public**（Pages 免费版要求公开仓库；私有仓库需 Pro）
- **不要**勾选 Add README / .gitignore / license（保持完全空仓库）

### 2. 把仓库地址发给我，或自己执行一条命令

**方式 A（推荐，最省事）**：把地址发我，例如 `git@github.com:wangganping/fish-price-dashboard.git`，我来完成后续全部步骤。

**方式 B（自己跑）**：在本目录执行
```bash
./push_github.sh git@github.com:<用户名>/<仓库名>.git
```
（用 HTTPS 地址也可以；若用 SSH 且未配密钥，改用 `https://github.com/<用户名>/<仓库名>.git`）

### 3. 开启 Pages（只需一次）
推送完成后，在仓库页面：
**Settings → Pages → Build and deployment → Source 选「GitHub Actions」**

然后进 **Actions** 标签，看「部署看板到 GitHub Pages」是否绿勾。成功后链接为：
```
https://<用户名>.github.io/<仓库名>/
```

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
