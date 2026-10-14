# code env commands

> **前置条件：** 先阅读 [`../../SKILL.md`](../../SKILL.md) 了解认证、全局参数和安全规则。

环境变量（Secrets）管理命令。用于管理项目级别的环境变量。

> **环境（`--env`）支持范围（重要）：**
> - 仅 **`env list`** 支持 `--env dev|prod`（默认 `dev`，且只有 `prod` 大小写不敏感生效，其它值静默回退 `dev`）。
> - **`env set` 没有 `--env` 选项**，写入开发环境。
> - **`env delete` 没有 `--env` 选项**，固定删除开发环境变量。

## 命令概览

| 命令 | 说明 |
|------|------|
| `coze code env set <key> <value> -p <id>` | 设置环境变量（dev） |
| `coze code env list -p <id>` | 列出环境变量（支持 `--env`） |
| `coze code env delete <key> -p <id>` | 删除环境变量（dev） |

### 共享参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `-p` / `--project-id` | 是 | 项目 ID（本命令组**不读取** `COZE_PROJECT_ID` 环境变量） |

---

## env set

设置项目环境变量（写入开发环境）。

> **Skill 类型项目暂不支持 `env set`**（会报 `E3008`）。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `<key>` | 是 | 环境变量名 |
| `<value>` | 是 | 环境变量值 |
| `-p` / `--project-id` | 是 | 项目 ID |

```bash
coze code env set API_KEY sk-xxxxx -p <project-id>
```

---

## env list

列出项目的环境变量，可按环境过滤。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `-p` / `--project-id` | 是 | 项目 ID |
| `--env` | 否 | 目标环境：`dev`（默认）/ `prod` |

```bash
# 列出开发环境变量（默认）
coze code env list -p <project-id>

# 列出生产环境变量
coze code env list -p <project-id> --env prod
```

---

## env delete

删除指定的开发环境变量（固定 dev，无 `--env` 选项）。若变量不存在报 `E3003`。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `<key>` | 是 | 要删除的环境变量名 |
| `-p` / `--project-id` | 是 | 项目 ID |

```bash
coze code env delete API_KEY -p <project-id>
```
