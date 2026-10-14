# code skill commands

> **前置条件：** 先阅读 [`../../SKILL.md`](../../SKILL.md) 了解认证、全局参数和安全规则。

技能管理命令。用于管理项目默认会话挂载的技能，以及上传/删除个人技能。

> **语义区分（重要）：**
> - `add` / `remove`：对项目**默认会话**挂载或解绑技能，不创建/删除技能本体。
> - `delete`：**永久删除个人技能本体**（与 `remove` 不同）。
> - `upload`：上传本地 `.skill` 文件为个人技能，命名冲突时**自动确认覆盖**。

## 命令概览

| 命令 | 说明 |
|------|------|
| `coze code skill list -p <id>` | 列出项目可用技能（含 `is_installed` 安装状态） |
| `coze code skill add <skill-id> -p <id>` | 将技能挂载到默认会话 |
| `coze code skill remove <skill-id> -p <id>` | 从默认会话解绑技能 |
| `coze code skill upload <file> -p <id>` | 上传 `.skill` 文件为个人技能 |
| `coze code skill delete <skill-id> -p <id>` | 永久删除个人技能本体 |

### 共享参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `-p` / `--project-id` | 是 | 项目 ID（本命令组**不读取** `COZE_PROJECT_ID` 环境变量） |

---

## skill list

列出指定项目类型下所有可用技能，并标注 `is_installed`（是否已挂载到默认会话）。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `-p` / `--project-id` | 是 | 项目 ID |
| `--space-id <spaceId>` | 否 | 空间 ID（缺省读取配置） |
| `--my` | 否 | 仅列出个人技能（此模式无需 spaceId，`is_installed` 恒为 false） |
| `--page <page>` | 否 | 页码（个人技能，默认 1） |
| `--size <size>` | 否 | 每页数量（个人技能，默认 20） |

### 推荐命令模板

```bash
coze code skill list -p <project-id>
coze code skill list -p <project-id> --my --page 1 --size 10
```

---

## skill add

将指定技能挂载到项目默认会话（`is_preload: true`）。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `<skill-id>` | 是 | 技能 ID（位置参数） |
| `-p` / `--project-id` | 是 | 项目 ID |

```bash
coze code skill add <skill-id> -p <project-id>
```

---

## skill remove

从项目默认会话解绑技能（不删除技能本体）。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `<skill-id>` | 是 | 技能 ID（位置参数） |
| `-p` / `--project-id` | 是 | 项目 ID |

```bash
coze code skill remove <skill-id> -p <project-id>
```

---

## skill upload

上传本地 `.skill` 文件为个人技能。仅校验文件存在；若与已有技能命名冲突，会自动取 `preview_skill_key` 确认覆盖（无交互）。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `<filePath>` | 是 | 本地 `.skill` 文件路径（位置参数） |
| `-p` / `--project-id` | 是 | 项目 ID |

```bash
coze code skill upload "./my-skill.skill" -p <project-id>
```

### 返回值

`--format json` 时输出 `{ project_id, message }`（`message` 为结果提示文本），**不包含 `skill_id`**。需要拿到新技能 ID 时，请在上传后用 `coze code skill list -p <project-id> --my` 查询。

---

## skill delete

永久删除个人技能本体（不可恢复，区别于仅解绑的 `remove`）。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `<skill-id>` | 是 | 技能 ID（位置参数） |
| `-p` / `--project-id` | 是 | 项目 ID（仅用于回显，删除本体不依赖它） |

```bash
coze code skill delete <skill-id> -p <project-id>
```
