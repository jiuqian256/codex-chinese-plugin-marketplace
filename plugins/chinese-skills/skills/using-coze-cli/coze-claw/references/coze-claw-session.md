# claw session commands

> **前置条件：** 先阅读 [`../../SKILL.md`](../../SKILL.md) 了解认证、全局参数和错误处理。

基础 session 命令用于确认 claw 状态、创建会话和找回历史会话。`coze session *` 跳过 org/space check，不需要先切换组织或空间。

## Agent 默认策略

- 除非用户明确要求“新建话题”“新增话题”“开新会话”，否则优先复用最近一次成功使用的 `session_id`。
- CLI 会把最近一次成功使用的 `session_id` 持久化到本地；优先用 `coze session current --format json` 读取，用 `coze session use <session_id> --format json` 切换。
- 推荐执行顺序：
  1. 如果已有最近 `session_id`，先执行 `coze session current --format json`
  2. 再执行 `coze session status -s <session_id> --format json`
  3. 如果没有最近 `session_id`，执行 `coze session list --limit 20 --format json` 找最近一个可复用 session，并在确认后执行 `coze session use <session_id> --format json`
  4. 只有用户明确要求新建，或没有任何可复用 session 时，才执行 `coze session create --format json`
- 不要因为用户发来一条新需求，就默认新建 session。

## 命令导航

| 命令 | 说明 |
|------|------|
| `coze session status` | 检查 token/claw，并刷新本地 `claw_id` |
| `coze session status -s <session_id>` | 查看指定 session runtime 状态和 claw 后台任务概览 |
| `coze session create` | 创建新 claw session |
| `coze session current` | 查看当前本地默认 session |
| `coze session use <session_id>` | 切换当前本地默认 session |
| `coze session list` | 分页列出 claw sessions |

## status

检查当前 token 是否可访问 claw。

```bash
coze session status --format json
```

关键输出：

| 字段 | 含义 |
|------|------|
| `auth_configured` | 是否配置 token |
| `auth_valid` | token 是否有效 |
| `claw_id` | 当前 claw id |
| `account_id` | fallback account/organization id |

如果 `auth_valid=false`，先执行 `coze auth status`，必要时重新登录。

## status -s

查看指定 session runtime 状态。

```bash
coze session status -s <session_id> --format json
```

关键输出：

| 字段 | 含义 |
|------|------|
| `display_status` | `idle` / `working` / `offline` |
| `runtime_status` | 当前进程内记录的 `idle` / `working` |
| `claw_busy` | 当前 claw 是否有后台任务 |
| `claw_progress_count` | 当前 claw 后台任务数量 |

`status -s` 不返回消息内容。要拿结果用 `watch` 或 `replies`。

## create

创建新 session，并记录 `session_id`。

```bash
coze session create --format json
```

关键输出：

```json
{
  "status": "created",
  "claw_id": "...",
  "session_id": "..."
}
```

Agent 必须保存 `session_id`，后续 `message/watch/replies/ppt edit` 都需要它。

补充：CLI 现在会在 `create` 成功后自动把这个 `session_id` 写入本地默认 session。

## current

查看当前本地默认 session。

```bash
coze session current --format json
```

关键输出：

```json
{
  "configured": true,
  "session_id": "...",
  "claw_id": "..."
}
```

如果 `configured=false`，说明当前没有本地默认 session；这时先 `list` 找回，或直接 `create` 新建。

## use

显式切换当前本地默认 session。

```bash
coze session use <session_id> --format json
```

适用场景：

- `list` 找回了历史 session，准备继续该话题
- 刚创建了多个 session，需要切换默认上下文
- Agent 需要确保接下来所有省略 `-s` 的命令都落到同一个 session

## list

找回已有 session。

```bash
coze session list --limit 20 --format json
coze session list --offset <next_offset> --limit 20 --format json
```

关键输出：

| 字段 | 含义 |
|------|------|
| `items` | session 列表 |
| `next_offset` | 下一页 offset |
| `has_more` | 是否还有更多 |

## 常见恢复

- 没有 `session_id`：先 `current` 看本地默认；没有再 `list` 找最近可复用 session，并用 `use` 切换；只有用户明确要求新话题或确实找不到可复用 session 时才 `create`。
- token 无效：先 `coze auth status`，不要盲目切 org/space。
- session 仍 working：用 `watch -s <session_id> --timeout <ms>` 或查 `progress list`。
