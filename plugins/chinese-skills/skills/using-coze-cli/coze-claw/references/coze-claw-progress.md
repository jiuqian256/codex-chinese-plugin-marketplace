# claw progress commands

> **前置条件：** 先阅读 [`../../SKILL.md`](../../SKILL.md) 和 [`coze-claw-message.md`](coze-claw-message.md)。

progress 表示 claw 级后台任务。收到 `progress_id` 后，不要继续等待 session reply；如果同轮还拿到了 `task_id`，优先转入 `session task` 查询。

对 Agent 而言，`progress_id` 是当前版本最稳定的长任务句柄。它本身不是最终结果，最终结果通常还要通过 `replies <message_id>` 回查。

## 命令导航

| 命令 | 说明 |
|------|------|
| `coze session progress list` | 列出当前 claw 后台任务 |
| `coze session task list` | 列出本地持久化的 session 长任务 |
| `coze session task show <task_id>` | 读取本地 task 快照 |
| `coze session task refresh <task_id>` | 刷新一个本地 task |
| `coze session task watch <task_id>` | 持续观察一个本地 task |
| `coze session progress show <progress_id>` | 单次查看任务快照 |
| `coze session progress poll <progress_id>` | 单次轮询，查不到按 finished |
| `coze session progress watch [progress_id]` | 监听一个或全部 progress 更新 |

## task

```bash
coze session task list --format json
coze session task show <task_id> --format json
coze session task refresh <task_id> --format json
coze session task watch <task_id> --timeout 300000 --format json
```

- `task_id` 是 CLI 本地恢复句柄，由 `coze session message --wait` 在命中 `progress_id` 时创建。
- `show` 只读本地快照，不请求服务端。
- `refresh` 会基于 `progress_id` 做一次服务端刷新，并把最新状态写回本地 task store。
- `watch` 是前台轮询封装，适合 Agent 周期跟踪与外部通知闭环。
- 当 task 进入终态且 CLI 已经补查到 reply 时，快照会带上 `reply_content` 和 `artifacts`，可直接作为用户交付结果使用。
- 如果宿主支持后台 schedule/job，推荐把 `task refresh/show` 放进独立的 follow-up 定时任务，而不是让当前 agent 持续前台 `watch`。

## list

```bash
coze session progress list --format json
```

用于判断当前 claw 是否有后台任务，或在 `watch` 超时后确认任务是否转入后台。

## show

```bash
coze session progress show <progress_id> --format json
```

单次查看一个任务。查不到时 `found=false`。

## poll

```bash
coze session progress poll <progress_id> --format json
```

脚本轮询优先使用 `poll`。它的特殊语义是：查不到 progress 时按 `finished` 输出。

示例：

```bash
for i in $(seq 1 60); do
  result=$(coze session progress poll <progress_id> --format json)
  status=$(echo "$result" | grep -o '"progress_status":"[^"]*"' | cut -d'"' -f4)
  [ "$status" = "finished" ] && break
  sleep 10
done
```

## watch

```bash
coze session progress watch <progress_id> --timeout 300000 --format json
coze session progress watch --timeout 300000 --format json
```

- 指定 `progress_id` 时，任务 finished 后会退出。
- 不指定时监听全部 progress，需要依赖 `--timeout` 退出。

## 完成后下一步

task/progress finished 后通常还需要：

```bash
coze session replies <message_id> -s <session_id> --format json
```

如果产物是文件或 PPT，继续阅读：

- [`coze-claw-artifacts.md`](coze-claw-artifacts.md)
- [`coze-claw-ppt.md`](coze-claw-ppt.md)

## Agent 最小恢复集

只要任务已经转入 progress，至少保留这三个 ID：

- `session_id`
- `message_id`
- `progress_id`

最小恢复流程：

1. 优先用 `task refresh/watch` 跟进是否 finished；没有 `task_id` 时退回 `progress poll/watch`
2. finished 后用 `replies <message_id>` 回查最终回复；如果 task 快照已经有 `reply_content` / `artifacts`，也要把这些内容回给用户
3. 如果回复里带文件，再进入 artifacts 或 PPT 流程

如果需要“后台查到终态后自动在原消息处通知用户”，继续阅读：

- [`coze-claw-async-followup.md`](coze-claw-async-followup.md)
