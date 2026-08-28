# GitHub Secrets 配置说明（鳜鱼鲈鱼价格看板自动化）

本看板的每日自动更新由 `.github/workflows/daily-crawl.yml`（GitHub Actions）驱动，串联：
**农业农村部爬虫 → 公开价源爬虫 → 公众号 OCR 流水线 → 水产前沿监控 → 重新内联资产 → 提交推送**。

其中「公众号 OCR 流水线」需要一块视觉大模型 API 密钥（用于把公众号价格截图 OCR 成结构化数据），
该密钥**不能明文写进代码/仓库**，必须放在 GitHub **Repository Secrets** 里。本文档说明怎么配。

---

## 一、Secrets 一览表

| Secret 名称 | 作用 | 必填 | 默认值（未配置时） | 取值来源 |
|---|---|---|---|---|
| `OCR_API_KEY` | 视觉大模型 API 密钥，驱动截图 OCR | **可选**（配了才自动 OCR 新截图） | 无 | [siliconflow.cn](https://siliconflow.cn) 注册后「API 密钥」页复制 |
| `OCR_API_BASE` | 视觉接口 Base URL | 可选 | `https://api.siliconflow.cn/v1` | 一般不动（换服务商才改） |
| `OCR_MODEL` | 视觉模型名 | 可选 | `Qwen/Qwen2.5-VL-72B-Instruct` | 一般不动（换模型才改） |

> **说明**
> - **只需配 `OCR_API_KEY` 就够了**：`OCR_API_BASE` / `OCR_MODEL` 脚本已做兜底默认值（即使 secret 留空也会用默认）。
> - **不需要配抖音/AgentKey 相关 secret**：抖音互动数据走 WorkBuddy 的 AgentKey 连接器（本地 OAuth），不在 CI 范围，目前靠本地手动更新。
> - **不需要配 `GITHUB_TOKEN`**：工作流已声明 `permissions: contents: write`，`actions/checkout` 自动注入内置 Token，`git push` 可直接用。

---

## 二、配置步骤（GitHub 网页端）

1. 打开你的看板仓库页面 → 顶部菜单 **Settings**（设置）。
2. 左侧栏 **Secrets and variables** → **Actions**。
3. 点击绿色按钮 **New repository secret**。
4. 在 **Name** 填写 `OCR_API_KEY`（严格大小写，不要带引号）。
5. 在 **Secret** 粘贴你从 SiliconFlow 复制的密钥（形如 `sk-xxxxxxxxxxxx`）。
6. 点击 **Add secret** 保存。
7. （可选）如需换服务商/模型，重复 3–6 步，分别加 `OCR_API_BASE`、`OCR_MODEL`。
8. 配置完成后，进入仓库 **Actions** 标签，找到「每日鳜鱼鲈鱼价格看板更新」工作流，
   点 **Run workflow** 手动触发一次，验证日志中出现 `[OCR] vision 适配器：...` 即成功。

---

## 三、不配置会怎样（降级行为）

工作流对 OCR 做了**幂等降级**，没配密钥也绝不会失败：

- **未配 `OCR_API_KEY`**：CI 自动走 `wechat_ocr_pipeline.py --rebuild`，
  用仓库里已有的 `wechat_ocr_current.json` 重建公众号板块，看板照常更新（双爬虫、历史序列、水产前沿监控照跑）。
  但公众号 OCR 板块**不会随新截图自动变化**——此时仍靠你发截图 + 我本地半自动（`--json` / `--rebuild`）更新。
- **配了 key 但 `screenshots/` 里没有截图**：同样走 `--rebuild`，无新 OCR 数据。

---

## 四、怎么让 CI 真正自动 OCR 新截图（喂数据）

CI 本身拿不到你的手机截图，需要先把截图放进仓库的 `screenshots/` 目录，且**文件名带来源关键字**：

| 截图来源 | 文件名需包含 | 工作流匹配 |
|---|---|---|
| 科学养鱼 | `科学养鱼` | `*科学养鱼*` |
| a渔业行情 | `a渔业` | `*a渔业*` |

两种喂法：

- **手动**：把最新截图重命名为 `科学养鱼_2026xxxx.png` / `a渔业行情_2026xxxx.png`，
  放进 `screenshots/` 目录，`git add` 提交。下个工作日流检测到即 OCR 并入。
- **自动（推荐进阶）**：本地跑 `wechat_rpa.py`（Playwright 自动搜号→打开最新文章→整页截图到 `screenshots/`），
  再 `git push`，触发 CI 完成 OCR。注意 RPA 依赖本地浏览器环境，建议在本地定时任务跑，而非 CI。

> 截图未提交进仓库时，CI 即使配了 key 也只会 `--rebuild`，这是预期行为。

---

## 五、验证与排错

手动触发（Run workflow）后，在 Actions 日志里看这几行：

- `[OCR] vision 适配器：Qwen/Qwen2.5-VL-72B-Instruct` → 密钥生效，走视觉 OCR。
- `[OCR] 科学养鱼 提取 N 条` / `[OCR] a渔业行情 提取 N 条` → 提取成功。
- `[OK] 已并入看板：科学养鱼 N 条 / a渔业行情 N 条` → 板块已更新。
- 若只有 `公众号 OCR 流水线` 步骤无 `[OCR]` 行 → 说明走的是 `--rebuild`（没 key 或没截图），属正常降级。

常见错误：

| 现象 | 原因 | 处理 |
|---|---|---|
| `401 Unauthorized` | `OCR_API_KEY` 错误 / 额度失效 | 到 SiliconFlow 重新复制或充值 |
| 请求 URL 异常 / 连接失败 | `OCR_API_BASE` 填错 | 改回 `https://api.siliconflow.cn/v1` 或直接删掉该 secret |
| 模型名报错 `model not found` | `OCR_MODEL` 拼错 | 改回 `Qwen/Qwen2.5-VL-72B-Instruct` 或填你账户可用的视觉模型 |
| 配了 key 但仍是 rebuild | `screenshots/` 无匹配截图 | 按第四节命名提交截图 |

---

## 六、安全提醒

- Secret **不会**进入 git 历史、不会出现在仓库文件或 Actions 日志明文里（GitHub 自动打码）。
- **不要把密钥写进代码、README 或聊天记录**。
- 密钥泄露时，到 SiliconFlow 后台 **Revoke / 重新生成** 即可，再回 GitHub 覆盖原 secret。
- 仓库协作者也看不到 secret 明文，只有工作流运行时能读取。

---

## 七、当前仓库待办（与 secrets 无关，提醒用）

- 本地已累计多个 commit，但**尚未推送到 GitHub**（缺仓库地址 + 推送权限）。
  推送后即可由本工作流接管每日自动更新；要推送请给我仓库地址，或本地 `git remote add origin <url>` 后协助。
- 抖音板块目前为本地（AgentKey 已连接）手动抓取，计划后续如需 CI 化需另接 TikHub API token（非 GitHub secret 范畴）。
