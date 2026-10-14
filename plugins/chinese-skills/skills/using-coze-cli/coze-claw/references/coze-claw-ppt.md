# claw PPT commands

> **前置条件：** 先阅读 [`../../SKILL.md`](../../SKILL.md) 和 [`coze-claw-artifacts.md`](coze-claw-artifacts.md)。

PPT 命令围绕 session 产物中的 PPT `file_uri` 工作。不要把 PPT `file_uri` 直接传给 `file download`。

## Agent 路由说明

通过 Agent 宿主的 `/coze-cli` 或 `/coze` 显式路由命中时，正文规范化规则统一见 [`coze-claw-agent-routing.md`](coze-claw-agent-routing.md)。

## 命令导航

| 命令 | 说明 |
|------|------|
| `coze session ppt info` | 获取 PPT 元信息、页数、file_url |
| `coze session ppt pages` | 提取页面标题和预览文本 |
| `coze session ppt export` | 导出 PPTX |
| `coze session ppt edit` | 通过 session message 发起页级编辑 |
| `coze session ppt share` | 生成分享链接 |

## info

```bash
coze session ppt info --file-uri "<file_uri>" --format json
```

用于确认 PPT 类型、页数和可访问 URL。

## pages

```bash
coze session ppt pages --file-uri "<file_uri>" --limit 5 --format json
```

用于快速理解 PPT 内容，再决定是否编辑或导出。

## export

```bash
coze session ppt export --file-uri "<file_uri>" --output-path ./deck.pptx --format json
coze session ppt export --file-uri "<file_uri>" --export-type editable --output-path ./deck.pptx --format json
```

`--export-type` 支持：

| 类型 | 含义 |
|------|------|
| `ppt` | 默认 PPTX 导出 |
| `editable` | 可编辑版本导出 |

## edit

```bash
coze session ppt edit "标题更突出，减少正文密度" \
  -s <session_id> \
  --page 2 \
  --wait \
  --timeout 120000 \
  --format json
```

`ppt edit` 本质是构造页级编辑 query，并复用 session message 链路。可重复传 `--page`。
省略 `-s/--session-id` 时，`ppt edit` 会默认复用当前本地默认 session。

## share

```bash
coze session ppt share --file-uri "<file_uri>" --format json
coze session ppt share --file-uri "<file_uri>" --no-short --format json
```

默认生成短链；`--no-short` 返回原始分享 URL。

## Agent 注意事项

- PPT 产物优先记录 `file_uri`。
- 要下载 PPTX 用 `ppt export`，不要用 `file download <file_uri>`。
- 编辑后仍需按 message/watch/replies 的恢复策略处理结果。
