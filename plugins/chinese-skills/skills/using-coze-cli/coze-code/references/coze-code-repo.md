# code repo commands

> **前置条件：** 先阅读 [`../../SKILL.md`](../../SKILL.md) 了解认证、全局参数和安全规则。

远程仓库管理命令。用于创建、绑定、解绑远程仓库，以及推送/拉取代码和查询同步状态。

## 命令导航

| 文档 | 命令 | 说明 |
|------|------|------|
| 本文档 | `coze code repo create` | 在 Git 平台创建新仓库 |
| 本文档 | `coze code repo bind` | 绑定远程仓库到项目 |
| 本文档 | `coze code repo unbind` | 解绑远程仓库 |
| 本文档 | `coze code repo push` | 推送本地提交到远程 |
| 本文档 | `coze code repo pull` | 拉取远程变更到本地 |
| 本文档 | `coze code repo status` | 查看绑定和同步状态 |

> 注意：所有命令均需先完成认证和组织/空间上下文配置。仓库操作需要先完成 Git 平台 OAuth 授权（`coze code git auth login`）。

### 共享参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--provider` | 否 | Git 平台：`github` / `gitlab`（默认 `github`） |

---

## repo create

在已授权的 Git 平台上创建新的空仓库。创建的仓库可通过 `repo bind` 绑定到项目。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `-n, --name <name>` | 是 | 仓库名称 |
| `--private` | 否 | 创建为私有仓库（推荐） |

### 推荐命令模板

```bash
# 创建公开仓库
coze code repo create --name my-app

# 创建私有仓库（推荐）
coze code repo create -n my-app --private

# 创建后立即绑定
coze code repo create -n my-repo --private && coze code repo bind -p <projectId> -r user/my-repo
```

### 返回值

| 字段 | 说明 |
|------|------|
| `full_name` | 仓库全名（如 `user/my-app`） |
| `html_url` | 仓库 URL |
| `private` | 是否私有 |

### 错误速查

| 错误码 | 名称 | 说明 | 修复方式 |
|--------|------|------|---------|
| E1014 | MISSING_REPO_CREATION_NAME | 未提供仓库名 | 使用 `--name <name>` |
| E2004 | GIT_NOT_AUTHORIZED | Git 平台未授权 | 先执行 `coze code git auth login` |
| E3009 | CONFLICT | 仓库名已存在 | 使用不同的名称 |

---

## repo bind

将空的远程仓库绑定到指定项目。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `-p, --project-id <projectId>` | 是 | 项目 ID |
| `-r, --repo <fullName>` | 是 | 远程仓库全名（如 `user/repo`） |

### 推荐命令模板

```bash
# 绑定仓库到项目
coze code repo bind -p <projectId> -r user/my-repo

# 创建新仓库后绑定（推荐流程）
coze code repo create --name my-repo --private
coze code repo bind -p <projectId> -r user/my-repo
```

### 返回值

| 字段 | 说明 |
|------|------|
| `project_id` | 项目 ID |
| `repo_full_name` | 绑定的仓库全名 |
| `status` | `bound` |

### 坑点

- **仅支持空仓库**：非空仓库绑定会失败
- **一个项目只能绑定一个仓库**：需要先 unbind 再绑定新仓库
- 通过 GitHub 导入创建的项目会自动绑定来源仓库，无需手动 bind
- 绑定前会先查 `GetRemote` 状态：`bindStatus=3`（已绑定）报 E3016；`bindStatus=1`（未授权）报 E2004；`bindStatus=2`（已授权未绑定）才放行

### 错误速查

| 错误码 | 名称 | 说明 | 修复方式 |
|--------|------|------|---------|
| E1013 | MISSING_REPO_NAME | 未提供仓库全名 | 使用 `--repo <owner/name>` |
| E2004 | GIT_NOT_AUTHORIZED | Git 平台未授权（bindStatus=1） | 先执行 `coze code git auth login` |
| E3015 | REPO_NOT_EMPTY | 仓库非空 | 使用 `repo create` 创建空仓库 |
| E3016 | REPO_ALREADY_BOUND | 项目已绑定仓库（bindStatus=3） | 先执行 `repo unbind` |

---

## repo unbind

解除项目与远程仓库的绑定关系。不会删除远程仓库本身。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `-p, --project-id <projectId>` | 是 | 项目 ID |
| `--force` | 否 | 跳过确认直接解绑 |

### 确认逻辑

- 不加 `--force` 时：**交互式终端（TTY）**会弹出确认提示，确认后才执行；**JSON 模式或非交互终端（非 TTY）**会直接报 `E1000`，必须加 `--force` 才能执行。
- 脚本/Agent 场景（通常非 TTY 或 `--format json`）应始终加 `--force`。

### 推荐命令模板

```bash
# 解绑（交互式终端会弹确认；仅 bindStatus=3 即已绑定时可解绑，否则报 E3014）
coze code repo unbind -p <projectId>

# 强制解绑（跳过确认，脚本/JSON 模式必须）
coze code repo unbind -p <projectId> --force
```

### 返回值

| 字段 | 说明 |
|------|------|
| `project_id` | 项目 ID |
| `status` | `unbound` |

### 错误速查

| 错误码 | 名称 | 说明 | 修复方式 |
|--------|------|------|---------|
| E1000 | INVALID_ARGUMENT | JSON 模式或非交互终端下未加 `--force` | 加 `--force` 跳过确认 |
| E3014 | REPO_NOT_BOUND | 项目未绑定仓库 | 用 `coze code repo status -p <id>` 查看状态 |

---

## repo push

将本地提交推送到已绑定的远程仓库。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `-p, --project-id <projectId>` | 是 | 项目 ID |

### 推荐命令模板

```bash
# 推送变更
coze code repo push -p <projectId>

# 推送后检查状态
coze code repo push -p <projectId> && coze code repo status -p <projectId>
```

### 返回值

| 字段 | 说明 |
|------|------|
| `status` | `success` 或 `failed` |
| `pushed_commits` | 推送的提交数量 |

### 错误速查

| 错误码 | 名称 | 说明 | 修复方式 |
|--------|------|------|---------|
| E3014 | REPO_NOT_BOUND | 项目未绑定仓库 | 先执行 `repo bind` |
| E3017 | NOTHING_TO_PUSH | 无需推送（placeholder 阶段暂不触发） | 已与远程同步 |
| E3018 | REMOTE_HAS_UPDATES | 远程有更新（placeholder 阶段暂不触发） | 先执行 `repo pull` |

### 坑点

- 当远程有新提交时，必须先 pull 再 push
- **当前为 placeholder 实现**：仅做绑定状态校验后恒返回 `{ status: 'success', pushed_commits: 0 }`，实际 push 走 Web 端 WebSocket，尚未接入

---

## repo pull

从已绑定的远程仓库拉取最新变更。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `-p, --project-id <projectId>` | 是 | 项目 ID |
| `--conflict-strategy <strategy>` | 否 | 冲突解决策略：`ours`（保留本地）/ `theirs`（使用远程） |

### 推荐命令模板

```bash
# 拉取变更
coze code repo pull -p <projectId>

# 自动解决冲突（保留本地）
coze code repo pull -p <projectId> --conflict-strategy ours

# 自动解决冲突（使用远程）
coze code repo pull -p <projectId> --conflict-strategy theirs

# 拉取后推送
coze code repo pull -p <projectId> --conflict-strategy ours && coze code repo push -p <projectId>
```

### 返回值

| 字段 | 说明 |
|------|------|
| `status` | `success`、`conflict_resolved` 或 `failed` |
| `conflict_resolved` | 是否解决了冲突 |
| `conflict_strategy` | 使用的冲突策略 |
| `conflict_files` | 冲突文件列表 |

### 坑点

- **不指定 `--conflict-strategy` 时遇到冲突会失败**
- 冲突解决策略会应用到所有冲突文件（不支持逐文件选择）
- `--conflict-strategy` 仅文档声明 `ours`/`theirs`，代码不做运行时校验
- **当前为 placeholder 实现**：恒返回 `success`，从不真正解决冲突

### 错误速查

| 错误码 | 名称 | 说明 | 修复方式 |
|--------|------|------|---------|
| E3014 | REPO_NOT_BOUND | 项目未绑定仓库 | 先执行 `repo bind` |
| E3019 | MERGE_CONFLICT | 未指定策略遇到冲突（placeholder 阶段暂不触发） | 加 `--conflict-strategy ours` 或 `theirs` |
| E3020 | WOULD_OVERWRITE | 本地改动会被覆盖（placeholder 阶段暂不触发） | 先提交本地改动 |

---

## repo status

查看项目的远程仓库绑定状态和同步信息。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `-p, --project-id <projectId>` | 是 | 项目 ID |

### 推荐命令模板

```bash
# 查看状态
coze code repo status -p <projectId>

# JSON 输出
coze code repo status -p <projectId> --format json

# 流水线中判断绑定状态
coze code repo status -p <projectId> --format json | jq .bind_status
```

### 返回值

| 字段 | 说明 |
|------|------|
| `bind_status` | `unauth`、`not-bound` 或 `bound`（`bindStatus` 1/2/3 映射） |
| `repo_full_name` | 仓库全名（仅 bound 时输出） |
| `html_url` | 仓库 URL（仅 bound 时输出） |

### 错误速查

`repo status` 自身没有专属业务错误码：未授权 / 未绑定不会报错，而是通过返回值 `bind_status`（`unauth` / `not-bound`）体现，请根据该字段分支处理。

### 状态枚举

| 状态值 | 含义 |
|--------|------|
| `unauth` | Git 平台未授权 |
| `not-bound` | 已授权但未绑定仓库 |
| `bound` | 已绑定仓库 |
