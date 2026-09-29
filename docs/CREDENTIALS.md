# 凭据与登录恢复（换环境/重启后必读）

> **本文件不含任何凭据内容**。仓库中**永久禁止**提交私钥或 AccessToken（`.gitignore` 已排除 `.env`、`secrets/`）。

## 1. 已入库的登录脚本（✅ 换环境后可直接用）

| 脚本 | 作用 | 用法 |
|---|---|---|
| `scripts/github_login.sh` | 重建 `~/.ssh/config` 指向持久化私钥 + git 全局配置 + SSH 连通验证（幂等） | `bash scripts/github_login.sh` |
| `scripts/bootstrap_amd.sh` | 环境恢复（MODELSCOPE_CACHE 等路径设定） | `bash scripts/bootstrap_amd.sh` |
| `scripts/sync_ckpt_to_ms.sh` | ckpt → ModelScope（SDK 上传，按 `<run_id>/ckpts/<stage>/`） | `MS_TOKEN=<token> bash scripts/sync_ckpt_to_ms.sh <run_id>` |
| `scripts/upload_data_ms.sh` | 数据集 / 归档包 → ModelScope | `MS_TOKEN=<token> bash scripts/upload_data_ms.sh [dir]` |

## 2. 凭据（**不入 git，需手工迁移**）

### 2.1 GitHub SSH 私钥
- **位置**：`<项目>/secrets/id_ed25519`（权限 600；`.gitignore` 排除）
- **当前公钥指纹**：`SHA256:IK5TIx4XKXYEVMkSk/8TDRa6/eMlV8JOKv97tm4cMRs`（ED25519，注释 `quant-attack@amd-sandbox`）
- **换环境处理（二选一）**：
  1. **workspace 整体迁移**（推荐）：`secrets/` 随之保留，新环境直接跑 `github_login.sh` 即可
  2. **全新环境**：重建密钥并登记 →
     ```bash
     ssh-keygen -t ed25519 -C "quant-attack@new-env" -f secrets/id_ed25519 -N ''
     cat secrets/id_ed25519.pub   # 粘贴到 GitHub → Settings → SSH and GPG keys → New SSH key
     bash scripts/github_login.sh
     ```
- **校验指纹一致性**：`ssh-keygen -lf secrets/id_ed25519.pub`

### 2.2 ModelScope AccessToken
- **获取**：ModelScope 网页 → 个人中心 → 访问令牌（AccessToken）
- **传递方式**：环境变量 `MODELSCOPE_ACCESS_TOKEN` 或调用时传 `MS_TOKEN=<token>`
- **平台环境**：本沙箱中 `MODELSCOPE_ACCESS_TOKEN` 由 DSW 平台注入，另有缓存于 `~/.modelscope/credentials/`（**重启/换环境即失效**）
- **换环境处理**：新环境执行一次 `modelscope login --token <新token>`，或直接以 `MS_TOKEN=...` 前缀调用上传脚本
- **注意**：脚本内**无硬编码 token**；旧 token 若被 API 拒绝，请重新生成

### 2.3 GitHub 推送注意
- 本环境 GitHub 需 `git config --global http.version HTTP/1.1`（HTTP/2 会报 framing 错）——`github_login.sh` 已自动设置
- git 身份：`zht <zht@modelscope.cn>`（实现方）；设计方提交用 `[设计]` 前缀区分

## 3. 换环境恢复顺序（推荐）

```bash
git clone <repo> && cd quant-attack
tar xzf archive/quant_artifacts_predictions_logs.tar.gz   # 中间产物（predictions/logs/stage_info）
tar xzf archive/quant_datasets.tar.gz                     # 数据集 5 版本
bash scripts/github_login.sh                              # GitHub SSH（需 secrets/ 或新建密钥）
modelscope login --token <token>                          # MS（或按需用 MS_TOKEN= 前缀）
bash scripts/bootstrap_amd.sh                             # 环境路径
# 需要 ckpt 时：modelscope download --dataset ZHTODD/llm-study-data --local_dir data
#               模型 ckpt：ZHTODD/llm-study-model → <run_id>/ckpts/<stage>/
```

## 4. 核对清单

- [ ] `ssh -T git@github.com` 返回 "successfully authenticated"
- [ ] `git push` 成功（HTTP/1.1 已设）
- [ ] `modelscope login` 后能列出 `ZHTODD/llm-study-model` 与 `ZHTODD/llm-study-data`
- [ ] 归档包 SHA-256 与 `archive/SHA256SUMS` 一致
