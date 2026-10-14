# claw async follow-up

> **前置条件：** 先阅读 [`coze-claw-message.md`](coze-claw-message.md) 和 [`coze-claw-progress.md`](coze-claw-progress.md)。

当 `coze session message --wait` 或 `coze session message` 命中长任务后，Agent 不应依赖“当前这次对话进程还在”去等待终态。优先做法是登记一个独立的 follow-up 定时任务，周期刷新 `session task` 状态，任务完成后再在原消息上下文回复用户。

## 适用场景

- OpenClaw + 飞书：用户在飞书里发消息，长任务完成后仍然回飞书原位置
- 宿主支持 cron / delayed job / background workflow / schedule
- 当前回合只适合先 ACK，再后台继续跟进

## 核心原则

1. **ACK 和 follow-up 分离**
   - 当前回合负责快速确认“已接单/已转后台处理”
   - 后续通知由独立 follow-up task 负责

2. **回复位置必须持久化**
   - `session_id` 只能恢复 Coze 任务
   - `reply_target` 才决定最后把结果回到哪里

3. **在哪里收到，就在哪里回复**
   - 飞书 DM 回 DM
   - 飞书群消息回原群
   - 飞书 topic/thread 回原 thread
   - 飞书消息卡片优先更新原卡片
   - 飞书 Drive 评论必须 reply comment

4. **必须防重**
   - follow-up task 重试时不能重复通知用户
   - 如果宿主已有任务幂等、去重或回执能力，优先复用，不要重复维护一套平行状态

5. **创建结果必须说实话**
   - 真正创建了 follow-up task，才可以对用户说“已转后台持续跟进/完成后自动回你”
   - 如果当前没有创建成功，必须在同一回合明确告知“当前还没有创建后台 follow-up 任务”
   - 禁止把“我准备创建”“理论上可以创建”表述成“我已经在后台盯着”

## 执行分支

命中长任务后，Agent 必须先判断当前宿主是否真的支持并允许创建 follow-up 定时任务：

### 分支 A：当前就能创建

- 直接创建，不要把“要不要创建定时任务”再抛回给用户做默认选择题
- 当前回合应明确告诉用户：
  - 已创建后台 follow-up 定时任务
  - 结果会回到原消息上下文
  - 当前这条回复只是 ACK，不是最终结果

### 分支 B：当前不能创建

- 必须在同一回合明确告诉用户：
  - 当前还没有创建后台 follow-up 定时任务
  - 原因是当前宿主不支持、权限不允许，或本轮无法实际调用该能力
- 必须立即给出下一步，而不是停在“我继续盯着”
- 可给出的下一步至少包括：
  - 当前回合继续前台代查，查到终态再回复
  - 如果宿主支持后续补建，提醒用户当前可以创建一个后台定时轮询任务
- 没有真正创建 follow-up task 时，禁止说“完成后自动回你”“我会持续盯到结束”

## 最小数据契约

建议在宿主侧登记一条尽量轻量的 follow-up 记录。`coze session task show/refresh --format json` 已经能按 `task_id` 反查 `session_id`、`message_id`、`progress_id`、`status`、`reply_content`、`artifacts`，所以不要把这些 Coze task 元数据再重复存一份。

```ts
type FollowUpJob = {
  taskId: string;
  replyTarget: ReplyTarget;
};

type FollowUpJobWithHostState = FollowUpJob & {
  notifyPolicy?: NotifyPolicy;
  dedupeKey?: string;
  notifiedAt?: number;
  notifyStatus?: "pending" | "sent" | "failed";
};

type ReplyTarget = {
  source:
    | "feishu_dm"
    | "feishu_group"
    | "feishu_thread"
    | "feishu_card"
    | "feishu_drive_comment";
  accountId?: string;
  chatId?: string;
  threadId?: string;
  topicId?: string;
  messageId?: string;
  commentId?: string;
  replyMode:
    | "reply"
    | "thread_reply"
    | "update_card"
    | "reply_comment";
};

type NotifyPolicy = {
  pollIntervalSec: number;
  maxWaitSec: number;
  maxAttempts: number;
  backoff: "fixed" | "linear" | "exponential";
};
```

必填约束：

- `taskId` 必须保留
- `replyTarget` 必须在当前回合就确定

可选宿主字段：

- 如果宿主没有内建幂等或任务状态，可使用 `FollowUpJobWithHostState` 额外保存 `dedupeKey`、`notifiedAt`、`notifyStatus`
- 如果宿主调度器需要显式参数，也可在 `FollowUpJobWithHostState` 中补 `notifyPolicy`
- 如果宿主本身已经有 cron/workflow 元数据、重试策略、任务状态机，就不要在 follow-up 记录里再镜像保存一套

恢复说明：

- `taskId` 足够恢复 Coze 长任务
- follow-up 执行时，如需 `session_id`、`message_id`、`progress_id`，先执行：

```bash
coze session task refresh <task_id> --format json
coze session task show <task_id> --format json
```

- 只有 `replyTarget` 这类“Coze CLI 无法帮你恢复的宿主上下文”才值得持久化

## 标准流程

### 1. 当前回合 ACK

当前回合只做三件事：

1. 把前置回复回给用户
2. 说明 follow-up 是否已经创建成功
3. 创建成功则登记 follow-up task；未创建成功则明确给出下一步选项

只有真正创建成功，才可以明确说“已登记后台跟进任务”。

### 2. 创建 follow-up task

follow-up task 至少要能执行：

```bash
coze session task refresh <task_id> --format json
coze session task show <task_id> --format json
# message_id 和 session_id 从上一步 task refresh/show 输出中获取
coze session replies <message_id> -s <session_id> --format json
```

推荐顺序：

1. 先 `task refresh`
2. 从输出里读取 `status`，并按需取 `session_id`、`message_id`
3. 如果仍是 `running`，按宿主自己的 schedule/workflow 策略继续下一次调度
4. 如果是 `finished/failed/cancelled`，进入终态回复流程

### 3. 终态回复流程

优先级：

1. 如果 `task show/refresh` 已带 `reply_content` 或 `artifacts`，直接用它
2. 否则调用 `replies <message_id>`
3. 整理为最终用户可见结果
4. 通过 `replyTarget` 回复到原上下文

### 4. 回复成功后收口

- 如果宿主使用 `FollowUpJobWithHostState`，写入 `notifiedAt`
- 如果宿主使用 `FollowUpJobWithHostState`，写入 `notifyStatus=sent`
- 后续轮询不再重复发送

如果宿主已有任务完成回执或幂等键，也可以不额外维护这两个字段，只要能保证“同一终态结果只通知一次”即可。

## 飞书优先级规则

OpenClaw + 飞书场景，建议按这个顺序回复：

1. `feishu_drive_comment`
   - 必须 `reply_comment`
2. `feishu_card`
   - 优先 `update_card`
   - 更新失败时退回 `thread_reply` 或普通 `reply`
3. `feishu_thread`
   - 优先回原 thread/topic
4. `feishu_group`
   - 回原群消息上下文
5. `feishu_dm`
   - 回原 DM

禁止：

- 在飞书收到，最后却发到另一个渠道
- 原线程还能回复，却新开一条无关联消息
- 当前回合和 follow-up task 各发一次终态结果

## 轮询与重试建议

默认轮询建议：

- `pollIntervalSec`: 30
- `maxWaitSec`: 1800
- `maxAttempts`: 60
- `backoff`: `fixed`

这是一组调度建议，不要求一定落成 `FollowUpJob` 字段。能复用宿主自己的 cron / delayed job / workflow 配置时，优先复用。

更长任务可用：

- 前 600 秒（10 分钟）每 30 秒
- 之后每 120 秒（2 分钟）

如果宿主调度成本高，可改成：

- 前 3 次 15 秒
- 之后 60 秒固定间隔

## 幂等与 fallback

### 幂等

- 每次发送前先检查 `notifiedAt`
- 如果宿主已有幂等键，优先用宿主能力；否则可用 `dedupeKey=<source>:<taskId>:terminal`
- 如果发送 API 超时但结果未知，也不要立即重发全文；应先查发送结果或写入待人工确认状态

### fallback

如果原上下文失效，按这个顺序退化：

1. 原 thread/topic 不可用，退回同一 chat 的普通 reply
2. 原 card 无法更新，退回同一 thread reply
3. 原 comment 无法 reply，退回同一文档或同一会话中的普通通知
4. 仍失败时，记录 `notifyStatus=failed` 并保留人工补发所需上下文

禁止直接静默丢失通知。

## 推荐示例

### 示例 1：普通长任务

1. 当前回合收到 `task_id`
2. 先回复“任务已转后台处理，完成后我会在这里回复你”
3. 保存 `replyTarget=feishu_dm`
4. 创建 follow-up task
5. follow-up `task refresh`
6. 终态后读取 `reply_content`
7. 回原 DM

### 示例 2：PPT 长任务

1. 当前回合先回前置回复
2. 命中 `task_id`
3. 保存 `replyTarget=feishu_group` 或 `feishu_thread`
4. follow-up 定时轮询
5. 终态后读取 `artifacts`
6. 把 PPT 链接或导出产物回原消息位置

### 示例 3：飞书评论触发

1. 用户在文档评论区触发任务
2. 保存 `replyTarget=feishu_drive_comment`
3. follow-up 轮询 `task`
4. 终态后用评论回复接口回结果
5. 不再额外发一条普通 IM 消息
