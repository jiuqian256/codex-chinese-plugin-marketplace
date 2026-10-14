# code model commands

> **前置条件：** 先阅读 [`../../SKILL.md`](../../SKILL.md) 了解认证、全局参数和安全规则。

模型管理命令。用于查看可用模型并设置项目**默认会话**使用的模型（会话维度，而非项目级）。

## 命令概览

| 命令 | 说明 |
|------|------|
| `coze code model list -p <id>` | 列出可用模型，并标记当前激活模型 |
| `coze code model list --type <type>` | 按项目类型列出可用模型（无项目 ID 时使用） |
| `coze code model set <modelName> -p <id>` | 设置默认会话使用的模型 |

---

## model list

列出可用模型。

- 传 `-p/--project-id`：从项目读取 `project_type` 与当前模型，结果中 `enable` 标记当前激活模型。
- 不传 `-p`：必须提供 `--type`，否则报 `E1000`；`--type` 经 `resolveProjectType` 解析（如 `web`、`app`、`agent` 等）。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `-p` / `--project-id` | 否 | 项目 ID |
| `--type <type>` | 否 | 项目类型（无 `-p` 时必填） |

```bash
coze code model list -p <project-id>
coze code model list --type web
```

---

## model set

设置默认会话使用的模型。会先调 `GetModelList` 校验 `modelName` 是否可用，不可用报 `E1000`。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `<modelName>` | 是 | 模型名（位置参数） |
| `-p` / `--project-id` | 是 | 项目 ID |

```bash
coze code model set doubao-dev-0213 -p <project-id>
```
