# 看板 GitHub Pages 部署说明

用永久稳定的 `github.io` 链接替代会休眠的沙箱分享链接。

---

## 一、现状

| 项 | 状态 |
|---|---|
| 本地 git 仓库 | ✅ 有（main 分支） |
| GitHub 远端 | ✅ `git@github.com:wgp168/fish-price-dashboard.git` |
| SSH 主机指纹 | ✅ 已核验并加入 `~/.ssh/known_hosts`（三项指纹与 GitHub 官方一致） |
| SSH 公钥授权 | ⏳ **待用户添加**（本机公钥未授权给 wgp168 账号） |
| Pages 工作流 | ✅ 已建 `.github/workflows/pages-deploy.yml` |
| 推送脚本 | ✅ 已建 `push_github.sh` |
| `.gitignore` | ✅ 已排除密钥（douyin_config / bazhuayu_config / tikhub）与 publish 副本 |

工作区 2.5M，推 GitHub 无压力。

**仓库**：https://github.com/wgp168/fish-price-dashboard
**Pages 地址（授权后生效）**：https://wgp168.github.io/fish-price-dashboard/

---

## 二、仓库已建，还差一步：SSH 公钥授权

仓库：https://github.com/wgp168/fish-price-dashboard
远端已配好，推送时报错 `Permission denied (publickey)` —— 本机公钥还没加进 GitHub 账号。

### 操作（1 分钟，一次性）

1. 登录 GitHub → 右上角头像 → **Settings**
2. 左侧 **SSH and GPG keys** → **New SSH key**
3. Title 填 `MacBook-wangganping`
4. Key type 选 **Authentication Key**
5. Key 粘贴下面这段**完整一行**：

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDAIunxeAukZS1CPUmaDQOsovYy+FVONZPSEi6oX0Qj4n75rn5jefX7Io1UdUQnoI8k2f1UE1GpkoREML9St9YJr4+WeT3yDqkW/SNsR4NG+WgIW90lcDjzrd3LpwTQJ73UjhKWi1iiFMNyioD/YwryTSCBKmPzF8vEPQLPKIbsOvPT6aosZ4sYHD1eG8EqAFCFY48hYURitXI6EwEtf2P42pEcNereWXrdLQLk1vX9TFfq4K96KO4qSfL6ESc1e0ytcP8qLPrbXH4LfZQSzgrpJMzr6EwKnx9EtNQbolFU9Q1/8lpYeiX6tjogSP3AWHpoOx6NPJSvBny6I4A42bRAn723F+deXdMOYWYY50n9pgbZ5peJiUIQLPW66RLVOX2OCSI1tUcOZIUXEtdjGtsNaii4hhx3+AeZtGmJszHnTU/h2CSjlRfixeHKq6Yss7krWYokGt5Am1xRPkCFc2reUept/yJupNAVRrnDrSfZ0RiHr0Qou1Vu5YHw/TEgBz0= wangganping@example.com
```

6. **Add SSH key**，然后告诉我一声，我立刻推送并开启 Pages。

> 备选：不想配 SSH 的话，也可以给我一个 Personal Access Token（勾选 `repo` 与 `workflow` 权限），我改用 HTTPS 推送。但 SSH 一劳永逸，后续每日自动推送都无需再管。

### 之后：开启 Pages（只需一次）
推送完成后，在仓库页面：
**Settings → Pages → Build and deployment → Source 选「GitHub Actions」**

然后进 **Actions** 标签，看「部署看板到 GitHub Pages」是否绿勾。成功后链接为：
```
https://wgp168.github.io/fish-price-dashboard/
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
