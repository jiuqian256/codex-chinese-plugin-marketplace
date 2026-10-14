# code git commands

> **前置条件：** 先阅读 [`../../SKILL.md`](../../SKILL.md) 了解认证、全局参数和安全规则。

Git 平台集成管理命令。用于管理 Git 平台的 OAuth 授权和仓库搜索。

## 命令导航

| 文档 | 命令 | 说明 |
|------|------|------|
| 本文档 | `coze code git auth login` | 通过 OAuth 授权 Git 平台 |
| 本文档 | `coze code git auth status` | 检查 OAuth 授权状态 |
| 本文档 | `coze code git auth logout` | 取消 OAuth 授权 |
| 本文档 | `coze code git search` | 搜索远程仓库 |

> 注意：所有命令均需先完成认证和组织/空间上下文配置。授权存储在空间（Space）级别，同空间项目共享。

### 共享参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--provider` | 否 | Git 平台：`github` / `gitlab`（默认 `github`，gitlab 暂未支持） |

---

## auth login

通过 OAuth 授权 Git 平台（如 GitHub）。命令会打开浏览器让用户完成授权，并轮询等待授权完成（超时 120 秒）。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--provider` | 否 | Git 平台（继承自 `git` 父命令，默认 `github`） |

### 推荐命令模板

```bash
# 授权 GitHub（最常用）
coze code git auth login

# 显式指定 provider
coze code git auth login --provider github
```

### 行为说明

1. 获取 Git 集成列表，找到对应 provider 的 `integration_id`
2. 获取 OAuth 授权 URL 并输出到终端
3. 等待用户在浏览器中完成授权（轮询间隔 2 秒，超时 120 秒）
4. 授权成功后获取用户信息并输出

### 返回值

| 字段 | 说明 |
|------|------|
| `provider` | Git 平台名称 |
| `status` | `authorized` |
| `user` | 授权用户名 |

### 坑点

- **需要浏览器环境**：在无头环境中需手动复制终端输出的 URL 到浏览器
- **授权是空间级别的**：授权成功后，同空间下所有项目可复用
- **超时后需要重新执行命令**

### 错误速查

| 错误码 | 名称 | 说明 | 修复方式 |
|--------|------|------|---------|
| E1015 | INVALID_PROVIDER | 不支持的 Git 平台 | 使用 `github`（代码 `VALID_PROVIDERS` 也放行 `gitlab`，但后端支持尚不完整） |
| E2005 | OAUTH_TIMEOUT | 授权超时（轮询 120 秒） | 重新执行 `coze code git auth login` |

---

## auth status

检查指定 Git 平台的 OAuth 授权状态和用户信息。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--provider` | 否 | Git 平台（默认 `github`） |

### 推荐命令模板

```bash
# 检查 GitHub 授权状态
coze code git auth status

# JSON 输出
coze code git auth status --format json

# 流水线中判断是否已授权
coze code git auth status --format json | jq .status
```

### 返回值

| 字段 | 说明 |
|------|------|
| `provider` | Git 平台名称 |
| `status` | `authorized` 或 `not-authorized` |
| `user` | 已授权时返回用户信息（`login`, `avatar_url`） |

---

## auth logout

取消 Git 平台的 OAuth 授权。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--provider` | 否 | Git 平台（默认 `github`） |
| `--force` | 否 | 跳过确认直接取消 |

### 确认逻辑

- 不加 `--force` 时：**交互式终端（TTY）**会弹出确认提示，确认后才执行；**JSON 模式或非交互终端（非 TTY）**会直接报 `E1000`，必须加 `--force` 才能执行。
- 脚本/Agent 场景（通常非 TTY 或 `--format json`）应始终加 `--force`。

### 推荐命令模板

```bash
# 取消 GitHub 授权（交互式终端会弹确认）
coze code git auth logout

# 强制取消（跳过确认，脚本/JSON 模式必须）
coze code git auth logout --force
```

### 注意事项

- **影响范围**：取消授权会影响当前空间下所有使用该 provider 的项目
- 已绑定仓库的项目将失去同步能力，直到重新授权

### 错误速查

| 错误码 | 名称 | 说明 | 修复方式 |
|--------|------|------|---------|
| E1000 | INVALID_ARGUMENT | JSON 模式或非交互终端下未加 `--force` | 加 `--force` 跳过确认 |
| E1015 | INVALID_PROVIDER | 不支持的 Git 平台 | 使用 `github` / `gitlab` |
| E2007 | NOT_AUTHORIZED | 尚未授权 | 先执行 `coze code git auth login` |

---

## search

搜索已授权 Git 平台上可访问的仓库。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `-k, --keyword <keyword>` | 否 | 搜索关键词 |
| `--page <page>` | 否 | 页码 |
| `--page-size <size>` | 否 | 每页数量（默认 20） |
| `--provider` | 否 | Git 平台（继承自 `git` 父命令）：`github` / `gitlab`，默认 `github` |

### 推荐命令模板

```bash
# 列出所有可访问仓库
coze code git search

# 按关键词搜索
coze code git search --keyword react

# 分页搜索
coze code git search -k react --page 2 --page-size 10

# JSON 输出用于脚本处理
coze code git search -k my-repo --format json
```

### 返回值

| 字段 | 说明 |
|------|------|
| `items` | 仓库列表（`full_name`, `private`, `size`, `updated_at`） |
| `total_count` | 总匹配数量 |

### 坑点

- **需要先完成授权**：未授权时搜索会失败
- 搜索范围是授权用户有访问权限的所有仓库
