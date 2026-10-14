# code tools commands

> **前置条件：** 先阅读 [`../../SKILL.md`](../../SKILL.md) 了解认证、全局参数和安全规则。

工具管理命令。用于管理项目**默认会话**启用的工具（如联网搜索、图片生成等，会话维度）。

## 命令概览

| 命令 | 说明 |
|------|------|
| `coze code tools list -p <id>` | 列出可用工具及启用状态 |
| `coze code tools enable <toolName> -p <id>` | 在默认会话启用某工具 |
| `coze code tools disable <toolName> -p <id>` | 在默认会话禁用某工具 |

### 共享参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `-p` / `--project-id` | 是 | 项目 ID |

---

## tools list

列出指定项目类型下所有可用工具，`enabled` 字段标注当前默认会话是否启用。

```bash
coze code tools list -p <project-id>
```

---

## tools enable / disable

启用或禁用默认会话中的某个工具。会先校验 `toolName` 是否属于该项目类型的可用工具，不可用报 `E1000`；随后合并更新默认会话的 `agent_tools`（enable 置 `true`，disable 置 `false`）。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `<toolName>` | 是 | 工具名（位置参数，如 `enable_image_gen`） |
| `-p` / `--project-id` | 是 | 项目 ID |

```bash
coze code tools enable enable_image_gen -p <project-id>
coze code tools disable enable_image_gen -p <project-id>
```
