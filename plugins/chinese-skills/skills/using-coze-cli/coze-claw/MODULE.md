---
name: coze-claw
version: 0.3.7
description: "Coze Claw Session 会话工作流：创建/找回 claw session、发送 session message、监听回复、查询后台 progress、处理文件/PPT/播客产物。当用户需要使用 coze session * 任意命令时触发。"
metadata:
  requires:
    bins: ["coze"]
  cliHelp: "coze session --help"
---

# Coze Claw Session 工作流

> **前置条件：** 先阅读 [`../SKILL.md`](../SKILL.md) 了解认证、全局参数、输出格式和错误处理。
> **上下文说明：** `coze session *` 跳过 org/space check，不要求先执行 `coze org use` 或 `coze space use`。只需确保 token 有效，并通过 `coze session status` 解析当前 claw。
> **执行前必做：** 从下方命令分组定位 reference，并先阅读对应 reference。涉及长任务 follow-up 时，再读 [`coze-claw-async-followup.md`](references/coze-claw-async-followup.md)。

## 核心概念

- **claw_id**：当前账号可用的 claw 实例，通常由 `coze session status` 解析并缓存。
- **session_id**：一条 claw chat 会话，CLI 会把最近一次成功使用的 session 持久化到本地，供后续 message/watch/replies/podcast/ppt edit 默认复用。
- **message_id**：用户提交的请求消息 ID，用于 `replies` 补偿查询。
- **answer_message_id**：assistant 回复消息 ID，用于对齐流式回复和最终回复。
- **progress_id**：claw 后台任务 ID，用于 progress 查询/监听。
- **file_uri**：平台内部文件引用，不能直接下载。
- **file_url**：可下载或可直接交付的文件 URL。

## Agent 快速执行顺序

1. **检查认证/claw**：`coze session status --format json`。
2. **优先复用本地默认 session**：除非用户明确要求“新建话题/新增话题/开新会话”，否则先执行 `coze session current --format json` 读取本地默认 `session_id`。
3. **检查指定 session runtime**：已有 `session_id` 时执行 `coze session status -s <session_id> --format json`。
4. **找回 / 切换 session，再决定是否创建**：如果本地没有可用的默认 `session_id`，先 `list` 找最近一个可复用 session，并用 `coze session use <session_id> --format json` 切换；只有用户明确要求新开话题，或确实没有可复用 session 时才 `create`。
5. **发送消息**：短任务用 `message --wait`；长任务用 `message` 无 `--wait` 获取 `message_id`，再 `watch/replies`。
6. **后台任务**：出现 `progress_id` 后，立即把它视为长任务句柄；如果 CLI 已返回 `task_id`，优先转 `session task show/refresh/watch`，并同时保留 `session_id`、`message_id`、`progress_id`。
7. **产物处理**：普通文件走 `file`；PPT 走 `ppt`；播客先查 voice，再用 `podcast message`。

## 用户回传闭环

- `message_id`、`progress_id`、`task_id`、`status=finished` 都只是恢复和编排主键，不是最终要回给用户的内容。
- 短任务：读取 `reply_completed.content/files` 后，必须把正文或文件链接回给用户。
- 长任务前置回复：如果同一轮在转入 `progress/task` 之前，已经通过 `reply_update` 或 `reply_completed` 产出了明确的说明性回复，必须先把这段内容回给用户，再继续后台跟进。
  - 不要只保留 `progress_id` / `task_id` 而丢掉这段首条回复。
- 长任务：`task/progress` 进入终态后，必须再取最终 reply。
  - 推荐：`coze session replies <message_id> -s <session_id> --format json`
  - 兜底：读取终态 `session task` 快照里的 `reply_content`、`artifacts`
- 禁止只回复“已发送”“已完成”“耗时 xx s”而不附带实际 reply。

## Session 复用原则

- 默认复用最近一次成功使用的 `session_id`。
- 可用 `coze session current --format json` 查看当前本地默认 session。
- 可用 `coze session use <session_id> --format json` 显式切换默认 session。
- 只有用户明确说“新建话题”“新增话题”“开一个新会话”“不要沿用之前上下文”时，才主动创建新 session。
- 如果最近 `session_id` 不可用，再退回 `coze session list --limit 20 --format json` 找最近一个可复用 session。
- 只有“用户明确要求新建”或“确实找不到可复用 session”这两种情况，才执行 `coze session create --format json`。

## 长任务 follow-up 原则

- 命中 `task_id` / `progress_id` 后，不要把“继续盯结果”绑定在当前 agent 进程上。
- 如果当前宿主支持 schedule/job/workflow，并且 Agent 能直接调用，必须在同一回合自动创建独立的 follow-up 定时任务去轮询 `coze session task refresh/show`，直到任务进入终态。
- 如果当前宿主不支持，或 Agent 当前无法真正创建 follow-up 定时任务，必须在同一回合明确告知用户“当前还没有创建后台 follow-up 任务”，并给出下一步选项。
- follow-up task 至少要保存：
  - `taskId`
  - `replyTarget`
- `sessionId`、`messageId`、`progressId` 这类 Coze task 元数据，优先在 follow-up 执行时通过 `task show/refresh` 现查，不要重复持久化。
- `dedupeKey`、`notifiedAt`、`notifyStatus` 只在宿主没有现成幂等/状态能力时才额外保存。
- 终态后必须在原消息上下文回复用户，而不是换一个新地方通知。
- 禁止在没有真正创建 follow-up task 的情况下，对用户说“我继续盯着”“完成后自动回你”“我会持续跟进到结束”。
- 如果没有创建 follow-up task，可提供的下一步至少包括：
  - 当前回合继续前台代查
  - 提醒用户当前可以创建后台定时轮询任务（如果宿主支持后续补建）
- 具体数据契约、轮询规则、原地回复策略见 [`coze-claw-async-followup.md`](references/coze-claw-async-followup.md)。

## 标准工作流

### 短任务：同步等待当前 turn

```bash
coze session create --format json

coze session message "请分析这份需求" \
  -s <session_id> \
  --wait \
  --timeout 120000 \
  --format json
```

`message --wait --format json` 是事件流，必须按事件/行解析。

### 长任务：提交与监听分离

```bash
coze session message "执行这个长任务" -s <session_id> --format json
coze session watch -s <session_id> --timeout 120000 --format json
coze session replies <message_id> -s <session_id> --format json
```

优先记录 `session_id` 和 `message_id`，这是恢复流程的主键。

## 意图 → 命令索引

| 意图 | 推荐命令 | Reference |
|------|---------|-----------|
| 检查 token/claw | `coze session status` | [session](references/coze-claw-session.md) |
| 查看当前默认 session | `coze session current` | [session](references/coze-claw-session.md) |
| 切换当前默认 session | `coze session use <session_id>` | [session](references/coze-claw-session.md) |
| 检查指定 session runtime | `coze session status -s <session_id>` | [session](references/coze-claw-session.md) |
| 新建 claw session | `coze session create` | [session](references/coze-claw-session.md) |
| 找回已有 session | `coze session list` | [session](references/coze-claw-session.md) |
| 发送消息并等待回复 | `coze session message --wait` | [message](references/coze-claw-message.md) |
| 长任务提交与监听分离 | `coze session message` + `coze session watch` | [message](references/coze-claw-message.md) |
| 超时/断线后补偿查询 | `coze session replies <message_id>` | [message](references/coze-claw-message.md) |
| 查询本地可恢复长任务 | `coze session task list/show/refresh/watch` | [progress](references/coze-claw-progress.md) |
| 查询后台任务 | `coze session progress list/show/poll/watch` | [progress](references/coze-claw-progress.md) |
| 下载回复文件 | `coze session file download <file_url>` | [artifacts](references/coze-claw-artifacts.md) |
| 处理 PPT 产物 | `coze session ppt *` | [ppt](references/coze-claw-ppt.md) |
| 选择播客 voice | `coze session podcast voice list` | [podcast](references/coze-claw-podcast.md) |
| 发送播客消息 | `coze session podcast message` | [podcast](references/coze-claw-podcast.md) |

## 命令分组

| 命令分组 | 说明 | Reference |
|----------|------|-----------|
| `session status/create/current/use/list` | claw 状态、本地默认 session 与 session 生命周期 | [coze-claw-session.md](references/coze-claw-session.md) |
| `message/watch/replies` | 消息发送、流式监听、补偿查询 | [coze-claw-message.md](references/coze-claw-message.md) |
| `task list/show/refresh/watch/gc` | 本地可恢复长任务查询、刷新与清理 | [coze-claw-progress.md](references/coze-claw-progress.md) |
| `progress list/show/poll/watch` | claw 后台任务查询和监听 | [coze-claw-progress.md](references/coze-claw-progress.md) |
| `async follow-up` | 长任务登记、定时轮询、原地回复、幂等与 fallback | [coze-claw-async-followup.md](references/coze-claw-async-followup.md) |
| `file download` | 普通文件产物下载与交付 | [coze-claw-artifacts.md](references/coze-claw-artifacts.md) |
| `ppt info/pages/export/edit/share` | PPT 产物处理 | [coze-claw-ppt.md](references/coze-claw-ppt.md) |
| `podcast voice/message` | 播客 voice 查询与播客消息发送 | [coze-claw-podcast.md](references/coze-claw-podcast.md) |
| `agent routing` | `/coze-cli`、`/coze` 前缀路由、strip 规则、验收样例 | [coze-claw-agent-routing.md](references/coze-claw-agent-routing.md) |

## 长耗时任务处理

| 命令 | 默认行为 | 等待/超时建议 | 恢复命令 |
|------|----------|---------------|----------|
| `coze session message` | 提交后返回 `message_id` | 推荐 Agent 默认使用 | `replies <message_id>` / `watch` |
| `coze session message --wait` | 阻塞并输出事件流 | 必须加 `--timeout` | 有 `message_id` 则 `replies`，否则 `watch/status/list` |
| `coze session watch` | 持续监听 websocket | 必须加 `--timeout` | 再次 `watch` 或查 `progress list` |
| `coze session task watch` | 持续观察本地 task 快照 | 必须加 `--timeout` | `task refresh <task_id>` / `replies <message_id>` |
| `coze session progress watch` | 持续监听 progress | 必须加 `--timeout` | `progress poll <progress_id>` |
| `coze session progress poll` | 单次查询 | 适合脚本循环 | 查不到按 `finished` 处理 |

补充规则：

- `message --wait` 一旦返回 `progress_id`，就不要把它继续当作“同一条同步回复”处理。
- 对 Agent 而言，`progress_id` 就是当前版本最稳定的长任务句柄。
- 如果 `message --wait` 同时返回了 `task_id`，优先改走：
  - `coze session task show <task_id> --format json`
  - `coze session task refresh <task_id> --format json`
  - `coze session task watch <task_id> --timeout <ms> --format json`
- `task_id` 是 CLI 本地恢复点，`progress_id` 仍然是服务端长任务句柄；两者都要保留。
- `task` 进入终态后，再用 `replies <message_id>` 回查最终回复或产物；至少也要读取 task 快照里的 `reply_content` / `artifacts` 并回给用户。

## 常见错误速查（Claw 专用）

| 症状/误用 | 一句话修复 |
|----------|------------|
| token 失效或未登录 | 先 `coze auth status`，必要时登录；多步处理见“恢复策略速查”。 |
| 未记录 `session_id` | 先 `current` 看本地默认；没有再 `list` 找回，必要时 `use` 切换。 |
| `message --wait` 超时 | 有 `message_id` 走 `replies`；否则看“恢复策略速查”。 |
| 对事件流整段 `JSON.parse()` | 改为按行/事件处理。 |
| `progress_id` 查不到 | 用 `progress poll` 缺失即 finished 的语义，再回查结果。 |
| 把 `file_uri` 当 `file_url` 下载 | 先解析为 `file_url`；PPT 走 `ppt info/export/share`。 |
| 监听命令没有 `--timeout` | 补 `--timeout`，避免 Agent 挂死。 |

## 恢复策略速查

| 场景 | Agent 执行步骤 |
|------|----------------|
| token 不可用 | 先 `coze auth status`；未登录或过期时引导 `coze auth login`；成功后重试 session 命令。 |
| 没有 `session_id` | 先 `coze session current --format json`；无默认时执行 `coze session list --limit 20 --format json` 找回，必要时 `coze session use <session_id>`；只有确实没有可复用 session 时才 `create`。 |
| 只知道历史上下文但没有 session | 执行 `coze session list --format json`，必要时用 `--offset` 分页找回。 |
| `message --wait` 超时 | 如果已记录 `message_id`，执行 `coze session replies <message_id> -s <session_id> --format json`；否则执行 `watch -s <session_id>` 或 `status -s <session_id>`。 |
| `watch` 超时但 session 仍 working | 再次执行 `watch -s <session_id> --timeout <ms>`；或查 `progress list` 判断是否转为后台任务。 |
| 有 `task_id` | 优先 `task show/refresh/watch`；必要时再退回 `progress poll/watch` 与 `replies`。 |
| 有 `progress_id` 没有最终产物 | 视为长任务恢复流程：优先 `task refresh/watch` 或 `progress poll/watch` 到 finished，再用 `replies <message_id>` 回查。 |
| 有 `file_url` | 直接 `coze session file download <file_url>`，或把 `file_url` 作为在线链接交付。 |
| 只有 `file_uri` | 不能直接下载；用对应能力解析。PPT 使用 `ppt info/export/share`。 |
| 监听输出解析困难 | 改用非监听命令：`message` 无 `--wait`、`replies`、`progress poll/show`。 |

## Agent 禁止行为

- 不要对 `message --wait`、`watch`、`progress watch` 的输出整段 `JSON.parse()`。
- 不要执行监听命令但不设置 `--timeout`。
- 不要丢失 `session_id`、`message_id`、`progress_id`。
- 不要把 `file_uri` 当作 `file_url` 下载。
- 不要只返回本地下载路径作为最终交付，除非用户明确只要本机路径。
