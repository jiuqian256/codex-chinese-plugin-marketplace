# claw podcast commands

> **前置条件：** 先阅读 [`../../SKILL.md`](../../SKILL.md) 和 [`coze-claw-message.md`](coze-claw-message.md)。

podcast 能力包含 voice 查询和播客消息发送。`podcast message` 是播客场景的独立入口，底层复用 session message 发送链路。
省略 `-s/--session-id` 时，`podcast message` 会默认复用当前本地默认 session。

## Agent 路由说明

通过 Agent 宿主的 `/coze-cli` 或 `/coze` 显式路由命中时，正文规范化规则统一见 [`coze-claw-agent-routing.md`](coze-claw-agent-routing.md)。

## 命令导航

| 命令 | 说明 |
|------|------|
| `coze session podcast voice list` | 查询可用 podcast voice |
| `coze session podcast message` | 发送播客消息 |

## voice list

```bash
coze session podcast voice list --format json
coze session podcast voice list --mode solo --format json
coze session podcast voice list --keyword 鸡汤 --format json
```

先查 voice，再发送播客消息。`--mode` 和 `--keyword` 都是筛选条件。

## podcast message

```bash
coze session podcast message "@播客 制作一个介绍潮汕美食的播客" \
  -s <session_id> \
  --voice "鸡汤女生" \
  --wait \
  --timeout 120000 \
  --format json
```

参数：

| 参数 | 必填 | 说明 |
|------|------|------|
| `<message>` | 条件必填 | 播客需求；也应支持 stdin |
| `-s` / `--session-id` | 否 | 目标 session；省略时默认复用当前本地默认 session |
| `--voice <voice>` | 否 | podcast voice，使用 `.option()`，不是 `.requiredOption()` |
| `--mode <mode>` | 否 | voice 歧义消解；传 `--mode` 时必须同时传 `--voice` |
| `--wait` | 否 | 等待当前 turn idle |
| `--timeout <ms>` | 否 | `--wait` 的超时 |
| `--file <path>` | 否 | 复用 message 附件逻辑，可重复 |

不指定 `--voice` 时，命令仍可发送播客消息，只是不注入指定 voice。

## 旧用法

保留兼容：

```bash
coze session message "@播客 制作一个介绍潮汕美食的播客" \
  -s <session_id> \
  --podcast-voice "鸡汤女生" \
  --wait
```

Agent 新流程推荐使用：

```bash
coze session podcast message ...
```

## 输出解析

`podcast message --wait --format json` 复用 session message 事件流。按 [`coze-claw-message.md`](coze-claw-message.md) 的事件规则解析，不要整段 `JSON.parse()`。
