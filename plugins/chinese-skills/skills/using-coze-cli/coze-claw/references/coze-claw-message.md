# claw message commands

> **前置条件：** 先阅读 [`../../SKILL.md`](../../SKILL.md) 和 [`coze-claw-session.md`](coze-claw-session.md)。

消息相关命令覆盖发送、监听和补偿查询。Agent 应优先记录 `session_id` 和 `message_id`。当省略 `-s/--session-id` 时，这些命令会默认复用当前本地默认 session。

## 命令导航

| 命令 | 说明 |
|------|------|
| `coze session message [message]` | 向 session 发送消息 |
| `coze session message --wait` | 等待当前 turn 回复并输出事件流 |
| `coze session task <subcommand>` | 查询或恢复本地持久化的 session 长任务 |
| `coze session watch` | 监听指定 session 的 websocket 回复 |
| `coze session replies <message_id>` | 回查某条请求消息的全部回复 |

## message

提交消息并立即返回 `message_id`，适合 Agent 长任务编排。

```bash
coze session message "执行这个长任务" -s <session_id> --format json
coze session message "继续当前默认话题" --format json
```

关键输出：

```json
{
  "session_id": "...",
  "message_id": "...",
  "status": "accepted"
}
```

必须记录 `message_id`，后续断线或超时时用 `replies` 恢复。

## Agent 路由前缀清洗

通过 Agent 宿主的 `/coze-cli` 或 `/coze` 显式路由命中时，正文规范化规则统一见 [`coze-claw-agent-routing.md`](coze-claw-agent-routing.md)。

## message --wait

短任务可直接等待当前 turn。

```bash
coze session message "请分析这份需求" \
  -s <session_id> \
  --wait \
  --timeout 120000 \
  --format json
```

`--format json` 输出事件流，每行一个事件。不要整段 `JSON.parse()`。

| `type` | 含义 | 关键字段 |
|--------|------|----------|
| `reply_chunk` | 增量文本 | `delta`、`answer_message_id` |
| `reply_update` | 回复快照 | `content`、`answer_message_id` |
| `reply_completed` | 当前 turn 完成 | `content`、`files`、`event_source` |
| `background_progress_started` | 检测到后台任务 | `progress_id`、`progress_status` |

收到 `background_progress_started` 后，优先读取末尾的 task 快照对象；如果拿到 `task_id`，转 [`coze-claw-progress.md`](coze-claw-progress.md) 里的 `session task *` 流程。

### Agent 交付约束

- `reply_completed` 才是当前 turn 的最终 reply 事件；拿到后必须把 `content/files` 回给用户。
- 如果命中 `background_progress_started` 之前已经收到有语义的 `reply_update.content`，必须先把这段前置回复回给用户，不能吞掉。
  - 推荐做法：记录同一 `message_id` 下最后一条有语义的 `reply_update.content`，一旦确认转入后台任务，先把它作为“当前已知回复”返回，再继续查 `task/progress`。
- 禁止把“已发送”“等待中”“已完成”“耗时 xx s”当作最终答复。
- 如果等待过程被打断，但已经拿到 `session_id` + `message_id`，必须用 `replies` 补查并回传结果。

## Agent 编排约束：命中 `progress_id`

当 `message --wait` 的事件流中出现 `background_progress_started`，Agent 应立刻切换心智模型：

- 不再把这次请求当作“继续同步等一会儿就会结束”的短任务
- 把 `progress_id` 视为当前版本的长任务句柄
- 必须同时保留：
  - `session_id`
  - `message_id`
  - `progress_id`

当前版本推荐恢复链路：

```bash
coze session task show <task_id> --format json
coze session task refresh <task_id> --format json
coze session task watch <task_id> --timeout 300000 --format json
coze session replies <message_id> -s <session_id> --format json
```

如果当前宿主支持后台 schedule/job，优先改走 [`coze-claw-async-followup.md`](coze-claw-async-followup.md) 里的 follow-up 流程，而不是让当前 agent 进程前台等待到任务结束。

规则：

- 有 `task_id` 后，优先查 task，不要重复发送同一条 message。
- `task_id` 是 CLI 本地恢复点，`progress_id` 仍要保留，必要时可退回 `progress poll/watch`。
- 如果命中 `progress_id` 之前已经出现前置回复，不要等终态才回给用户；应先回传前置回复，再继续后台跟进。
- 如果宿主支持后台 follow-up task，应在这里登记独立定时任务，保存 `reply_target`，后续由它负责终态通知。
- task/progress 结束后，再回查 `replies <message_id>` 获取最终回复或产物。
- 终态 `session task` 快照如果已包含 `reply_content` / `artifacts`，应把它们视为可直接交付给用户的缓存结果，而不是只报任务状态。

## 输入文件

两种方式都会作为 session 附件上传：

```bash
coze session message "总结这些文件" -s <session_id> --file ./a.pdf --file ./b.png
coze session message "总结 @docs/notes.md" -s <session_id>
coze session message "总结这份默认会话里的材料" --file ./a.pdf
```

- `--file` 可重复。
- `@<path>` 只引用文件，不引用目录。

## watch

监听 session 回复。Agent 使用时必须加 `--timeout`。

```bash
coze session watch -s <session_id> --timeout 120000 --format json
coze session watch -s <session_id> --snapshot --timeout 120000 --format json
```

- 默认输出流式增量。
- `--snapshot` 输出完整回复快照。
- 超时后如果仍未拿到结果，用 `replies <message_id>` 补偿查询。

## replies

按用户请求消息回查全部回复。

```bash
coze session replies <message_id> -s <session_id> --format json
```

适用场景：

- `message --wait` 超时。
- `watch` 断线或超时。
- 已有 `message_id`，需要稳定结果而非实时流。

## 推荐 Agent 流程

短任务：

```bash
coze session message "需求" -s <session_id> --wait --timeout 120000 --format json
coze session message "继续当前默认话题" --wait --timeout 120000 --format json
```

长任务：

```bash
coze session message "需求" -s <session_id> --format json
coze session watch -s <session_id> --timeout 120000 --format json
coze session replies <message_id> -s <session_id> --format json
```

如果 `message --wait` 已经返回 `task_id` / `progress_id`，则改走：

```bash
coze session task refresh <task_id> --format json
coze session task watch <task_id> --timeout 300000 --format json
coze session replies <message_id> -s <session_id> --format json
```

如果 Agent 宿主支持定时任务，推荐替换为：

1. 当前回合先 ACK 原消息
2. 记录 `task_id + reply_target`
3. 创建独立 follow-up 定时任务
4. follow-up 轮询 `task refresh/show`，按需从输出恢复 `session_id/message_id`
5. 终态后读取 `reply_content/artifacts` 或 `replies`
6. 在原渠道原消息上下文回复用户
