# code message commands

> **前置条件：** 先阅读 [`../../SKILL.md`](../../SKILL.md) 了解认证、全局参数和安全规则。

消息交互相关命令索引。涵盖向项目发送开发需求、查询任务状态、取消进行中的任务、查看对话历史。

## 命令导航

| 文档 | 命令 | 说明 |
|------|------|------|
| 本文档 | `coze code message send` | 发送需求（支持@文件引用、--stdin 附加上下文） |
| 本文档 | `coze code message status` | 查询任务状态（单次查询，需脚本轮询） |
| 本文档 | `coze code message cancel` | 取消正在进行的任务 |
| 本文档 | `coze code message history` | 查看项目对话历史 |

> 共享参数：`-p` / `--project-id` 指定项目 ID（或通过环境变量 `COZE_PROJECT_ID` 设置）。

---

## message send

向项目发送开发需求或指令，由 AI 异步处理。

### 核心警告

**部署前必须确认 message status 已结束！** 状态为 `processing` 时禁止直接部署，否则会出现 `refs/heads/main does not exist` 等错误。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `<message>` | 条件必填* | 需求文本 |
| `-p` / `--project-id` | 是 | 项目 ID |
| `--stdin` | 否 | 从 stdin 管道读取附加上下文 |
| `--wait` | 否 | 等待 AI 响应完成后再返回（默认后台发送） |
| `--format` | 否 | 输出格式；`json` 时输出 NDJSON 事件流 |

*\* `<message>` 必填，`--stdin` 为可选附加上下文*

### @语法引用本地文件

在 message 文本中可直接用 `@文件路径` 引用本地文件，CLI 会自动上传并作为附件发送：

```bash
# 引用单张图片
coze code message send "请使用这张图片作为头像 @./avatar.png" -p <project-id>

# 对比两个文件
coze code message send "对比 @src/old.ts 和 @src/new.ts 的差异" -p <project-id>
```

- 只支持引用**文件**（不支持目录）
- 文件路径可以是相对路径或绝对路径：**绝对路径不受工作目录限制**；相对路径解析后必须仍在当前工作目录内（`../` 越界会被忽略并输出 warning）。任何引用失败（文件不存在/是目录/越界）都会输出 warning 并把 `@路径` 原样作为普通文本发送

### stdin 管道输入（附加上下文）

使用 `--stdin` 显式声明从管道读取附加上下文，与 `<message>` 拼接后发送：

```bash
# 从文件管道输入作为上下文
cat error.log | coze code message send "分析这个错误" --stdin -p <project-id>

# 从其他命令管道输入
echo "修复登录页面的样式问题" | coze code message send "请查看以下日志" --stdin -p <project-id>
```

- **不传 `--stdin` 时 stdin 会被忽略**，不会阻塞等待
- 管道内容会追加在 `<message>` 之后，格式为 `消息\n\n上下文`
- 适合将日志、错误输出、代码片段等作为上下文附加到需求中

### NDJSON 解析规则（`--format json` 时）

当使用 `--format json` 时，输出为 NDJSON 事件流：

- 每行是一个独立的 JSON 对象
- 必须按行逐行解析，不能整段 `JSON.parse()`
- 关键字段：
  - `content`: 响应内容片段
  - `role`: 角色（`assistant` / `user`）
  - `finish`: 是否为最终结果（`true` / `false`）
  - `type`: 事件类型
- **找 `finish: true` 的行来获取最终结果**

### 推荐命令模板

```bash
# 基本发送
coze code message send "请优化应用配色方案" --project-id <project-id> --format json

# 带 @文件引用
coze code message send "分析 @src/app.ts 的代码质量" -p <project-id> --format json

# stdin 管道输入 + json 格式
cat spec.md | coze code message send "请按此规格实现" --stdin -p <project_id> --format json
```

### text 模式 vs json 模式

- **text 模式**（默认）：直接输出人类可读的 AI 响应内容，适合展示给用户
- **json 模式**：输出结构化 NDJSON 事件流，适合 Agent 提取和处理数据

---

## message status

查询项目中最近一次消息的处理状态。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--project-id` / `-p` | 是 | 项目 ID |
| `--format` | 否 | 输出格式，默认 `text` |

> `message status` 是**单次查询**，不会自动轮询。如需等待任务完成，**禁止把整段轮询 sleep 在一次工具调用里**：AI 开发是分钟级到几十分钟级的长任务，单次调用干等会撞穿宿主工具超时（通常约 10 分钟），表现就是"卡住"。请按宿主能力选非阻塞方式（详见 `coze-code/MODULE.md` 的「阻塞与超时铁律」与「长任务 follow-up」）。

### 推荐命令模板

**单次查询（默认，配合逐回合跟进）：**

```bash
coze code message status --project-id <project-id> --format json
```

**优先 / 分支 A：子 session 后台任务（subagent / 独立子会话）** —— 先探测 agent 是否支持起独立子会话 / subagent。支持就派一个子任务去做下面这件事，当前回合立即 ACK 返回；子会话自行跑完并把结果回报到原上下文，**天然避免"结果石沉大海"**：

> 子任务的职责：循环 `coze code message status -p <project-id> --format json`（间隔 30s，约 30 分钟封顶）→ 到 `done` / `completed` 终态 → 整理成「开发完成结果 + answer + `project_url`」回报给用户。

**次选 / 分支 A'：宿主其它后台执行** —— agent 不支持子 session，但宿主有 `run_in_background` / cron / delayed job 时，把轮询丢后台，当前回合 ACK 返回。**写文件只是中转，必须再配一个回唤 / 回读动作把结果交付出去**，否则就是"非阻塞后没有返回开发完成结果"：

```bash
# 后台轮询直到终态，结果写文件供后续回合读取（间隔 30s，约 30 分钟封顶）
nohup bash -c '
  for i in $(seq 1 60); do
    result=$(coze code message status -p <project-id> --format json)
    case "$result" in
      *\"status\":\"done\"*|*\"status\":\"completed\"*)
        printf "%s" "$result" > /tmp/coze-code-status.json; break;;
    esac
    sleep 30
  done
' >/tmp/coze-code-poll.log 2>&1 &

# 后续回合回读后台结果；存在且为终态就整理成「开发完成结果 + answer + project_url」交付给用户
[ -f /tmp/coze-code-status.json ] && cat /tmp/coze-code-status.json
```

**兜底 / 分支 B：都不支持** —— **每个回合只查一次 + 让出回合**，下个回合再查；不要在一个调用里长 sleep：

```bash
# 单回合查一次，未到 done 就把当前进度回给用户，由下一回合继续
result=$(coze code message status -p <project-id> --format json)
printf "%s\n" "$result"   # 解析 status：非 done 则报进度、收尾本回合，下一回合再查；done 则把 answer + project_url 交付给用户
```

### 状态含义

> **完成态判定以源码为准**：CLI 仅当 `status === 'done'` 时才判定为完成并自动拉取 answer（见 `status.ts`）。其它取值（如 `running` 等）一律按"未完成"原样返回 `status` 字段。轮询脚本可同时兼容 `done` / `completed` 以防服务端文案差异，但**真正的完成哨兵值是 `done`**。

| 状态 | 含义 | 可执行的操作 |
|------|------|-------------|
| 非 `done`（如 `running`） | 仍在处理中 | 禁止部署，必须等待 |
| `done` | 处理完成（自动返回 answer） | 可以部署 |
| 失败态 | 处理失败 | 检查错误信息后重试 |

---

## message cancel

取消当前正在进行的消息任务。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--project-id` / `-p` | 是 | 项目 ID |

### 推荐命令模板

```bash
coze code message cancel --project-id <project-id>
```

---

## message history

查看项目的对话历史，默认返回最新 10 条对话记录。支持通过游标分页加载更旧或更新的消息。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--project-id` / `-p` | 是 | 项目 ID |
| `--after <msg_id>` | 否* | 游标，获取该消息之后（更新）的消息。新消息 index 更小 |
| `--before <msg_id>` | 否* | 游标，获取该消息之前（更旧）的消息。旧消息 index 更大 |
| `--format` | 否 | 输出格式，默认 `text` |

*\* `--after` 和 `--before` 不能同时使用*

### 推荐命令模板

```bash
# 查看最新 10 条对话（人类可读格式）
coze code message history -p <project-id>

# JSON 格式输出（适合 Agent 解析，含游标信息）
coze code message history -p <project-id> --format json

# 使用 before 游标加载更旧的消息
coze code message history -p <project-id> --before <msg_id_from_cursor>

# 使用 after 游标加载更新的消息
coze code message history -p <project-id> --after <msg_id_from_cursor>
```

### 分页机制

- 不传游标时，默认返回**最新 10 条**记录，方向为 `loadPrev`（向更旧方向翻页）
- 返回结果中包含游标信息，用于下一页请求：
  - `after`：当前结果中**最新**消息的 ID，用作 `--after` 可获取更新的消息
  - `before`：当前结果中**最旧**消息的 ID，用作 `--before` 可获取更旧的消息
  - `has_more`：是否还有更多消息
  - `loadDirection`：本次请求的加载方向（`loadNext` / `loadPrev`）

### 输出格式

**text 模式**（默认）：按条目展示问答记录，末尾附带游标信息

```
--- #1 ---
Q: 添加暗黑模式支持
A: 已完成暗黑模式的实现...

--- #2 ---
Q: 修复登录页面的样式问题
A: 已修复，调整了 CSS 布局...

[cursor] after=msg_abc, before=msg_xyz, has_more=true, loadDirection=loadPrev
```

> `#N` 为当前页面的条目序号，不代表全局轮次序号。

**json 模式**：输出结构化对象，包含 `histories` 数组和 `cursor` 游标对象

```json
{
  "histories": [
    { "userMessage": "添加暗黑模式支持", "answer": "已完成暗黑模式的实现..." },
    { "userMessage": "修复登录页面的样式问题", "answer": "已修复，调整了 CSS 布局..." }
  ],
  "cursor": {
    "after": "msg_abc",
    "before": "msg_xyz",
    "has_more": true,
    "loadDirection": "loadPrev"
  }
}
```

> 仅返回有 AI 回答的记录，按时间正序排列（最早的在前）。如果没有对话历史，text 模式输出 `No conversation history found.`。
