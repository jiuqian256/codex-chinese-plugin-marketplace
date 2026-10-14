---
name: using-coze-cli
description: 扣子 CLI 项目与内容工具：使用 Coze CLI 创建或迭代项目、生成内容、操作会话及分享文件。 Coze CLI（`coze` 命令）的使用规则。触发条件：用户明确要求使用 Coze CLI / coze 命令 / 扣子编程（Coze Coding）、扣子空间等 Coze 平台能力，或输入以 /coze-cli、/coze 开头（仅作路由）时加载本技能。覆盖范围：coze code—扣子编程项目创建/迭代（网页、Web App、App、小程序、Agent/工作流/skill）及发需求、预览、部署、环境变量/域名/数据库；coze generate—文生图/语音 TTS/视频；coze session（Claw）—对话、PPT、播客、长任务产物；coze file—本地文件转在线链接。判定边界：不要仅因为用户在做软件开发、修改/调试/运行代码，或请求中出现 CLI、文件读写、HTML、可视化、卡片、报告、图片等词就加载本技能或导流到扣子编程；本地工程开发默认走常规本地开发链路。
metadata:
  requires:
    bins:
    - coze
  cliHelp: coze --help
  version: 0.3.7
---

## 中文名称与用法

**中文名称：** 扣子 CLI 项目与内容工具

**用途：** 使用 Coze CLI 创建或迭代项目、生成内容、操作会话及分享文件。

**调用示例：** 使用 $chinese-skills:using-coze-cli 使用 Coze CLI 处理这个项目任务。

文中的 `<SKILL_DIR>` 指本次加载的 SKILL.md 所在目录；从实际技能路径解析，不假定用户目录、操作系统或插件缓存版本。脚本接收的项目路径和输出路径仍使用当前任务的实际路径。


# Coze CLI 共享规则

本技能指导你如何通过 `coze` 命令完成基础配置和上下文管理，以及有哪些通用注意事项。

## 适用场景

- **`coze code`（核心）**：创建 Coze 编程项目（网页 / App / 小程序 / Agent / 工作流 / skill / 助手），并先按用户意图识别项目类型；发送需求 `message` 迭代开发、轮询状态、获取 preview、部署上线；以及环境变量 / 域名 / 默认会话技能 / 模型 / 工具 / 数据库 / Git 与远程仓库管理。
- `coze generate`：文本生成图片、语音合成（TTS）、视频生成。
- `coze file`：上传本地文件，将在线可访问链接返回给用户。
- `coze session`（Claw）：创建/找回 session、发送 session message、监听 reply、查询 progress、处理文件 / PPT / 播客产物。
- 用户输入以 `/coze-cli` 或 `/coze` 开头时，必须优先把这条消息视为显式路由到 Coze CLI skill；前缀只用于路由，不属于最终发给底层命令的正文。

不适用场景：

- 用户只是在本地做软件开发（写代码、改代码、调试、跑起来、迭代工程），且没有明确要求用 Coze CLI / 扣子编程时，不加载本技能，按常规本地开发链路处理。

## 模块化阅读顺序

本文件只保留 Coze CLI 的共享基础规则。进入具体命令族时，优先继续阅读对应模块文档：

- `coze session *`：先读 [coze-claw/MODULE.md](coze-claw/MODULE.md)
- `coze code *`：先读 [coze-code/MODULE.md](coze-code/MODULE.md)
- `coze file *`：先读 [coze-file/MODULE.md](coze-file/MODULE.md)
- `coze generate *`：先读 [coze-generate/MODULE.md](coze-generate/MODULE.md)

约束：

- 根 `SKILL.md` 只放共享规则，不堆积 Claw 专用长任务编排细节。
- Claw 相关的 agent 执行约束、恢复策略、长任务规则，尽量收敛到 `coze-claw/` 目录内。

## 必须遵守的执行原则

### 1. 用户明确指定 Coze CLI 时，禁止私自改用别的能力

- 如果用户明确要求"用 Coze CLI 生成语音/图片/视频"，就必须优先把 Coze CLI 路径跑通。
- **禁止**在未充分排查 Coze CLI 正确用法前，擅自改用 Agent 宿主、自带 TTS、第三方生成接口或 Web 页面手工下载流程。
- 只有在 Coze CLI 明确报错、能力缺失，且已经向用户解释并获得同意时，才允许退回到其他方案。

### 2. 优先使用 `--format json`

- 需要结构化解析结果时，优先增加 `--format json`。
- 注意：`coze code message send --format json` 输出 NDJSON 事件流，必须按行解析，不能直接整段 `JSON.parse()`；应找 `finish: true` 的行获取最终结果。
- 注意：`coze session message --wait --format json`、`coze session watch --format json`、`coze session progress watch --format json` 也会输出事件流，必须按行/事件解析，不能整段 `JSON.parse()`。
- `coze session message --wait --format json` 的最终 reply 事件是 `reply_completed`，不是 `finish: true`。
- 补充：`coze session message --wait --format json` 如果命中后台 `progress_id`，事件流后会额外给出一个稳定的 task 快照对象，至少包含 `task_id`、`progress_id`、`task_status`，后续优先改用 `coze session task *` 跟进。
- `--format` 默认值为 `text`，text 模式下输出人类可读的格式化文本。
- JSON 输出的顶层对象可能携带 `_notice` 字段（非业务数据）；两类子字段：`_notice.skill` 表示本机 skills 与 CLI 版本不一致，`_notice.update` 表示有 CLI 新版本可用。看到后在完成当前任务之余执行其 `command` 字段给出的修复命令（如 `coze self skill install` 或 `coze upgrade`），解析业务数据时忽略该字段即可。输出为数组时该提示会改走 stderr 单行文本。默认情况下 skill 不一致会被静默自动修复（`skill.mode=auto`），通常看不到 `_notice.skill`；仅当用户改为 `skill.mode=notify`、或自动同步失败时才会出现该提示。CI 环境（`CI` 环境变量为非 false/0 值）下不产生这两类提示；`COZE_CLI_NO_SKILL_NOTIFIER` 跳过本次 skill 检查（既不同步也不提示），`COZE_CLI_NO_UPDATE_NOTIFIER` 跳过本次升级检查。

### 3. 对用户交付 Coze Session 结果时，必须回传最终 reply，不要只回状态

- 对 `coze session *`，`message sent`、`watching`、`progress started`、`task finished`、`已完成/耗时 xx s` 都只是过程状态，不是最终用户可见结果。
- 短任务：拿到 `reply_completed.content/files` 后，必须把回复正文或产物链接整理回给用户。
- 长任务前置回复：如果 `message --wait --format json` 在命中 `progress_id` / `task_id` 之前，已经出现了有语义的 `reply_update.content` 或 `reply_completed.content`，必须先把这段前置回复回给用户，再继续进入后台任务跟进。
  - 典型场景：先回复“我先加载 PPT 技能/我先读一下风格参考”，随后才启动 `progress`。
  - 禁止把这类前置回复吞掉，只给用户返回“开始生成了/任务已启动/稍后给你链接”。
- 长任务 follow-up：如果当前回合已经拿到 `task_id` / `progress_id`，要么按 [`coze-claw/MODULE.md`](coze-claw/MODULE.md) 的 follow-up 规则立即创建独立后台任务，要么在同一回合明确告知“当前还没有创建后台 follow-up 任务”并给出下一步选项；禁止没创建也说“我会继续盯着/完成后自动回你”。
- 长任务：如果命中 `progress_id` / `task_id`，任务终态后必须继续：
  - 优先读取 `coze session replies <message_id> -s <session_id> --format json`
  - 或读取终态 `coze session task show/refresh/watch` 里的 `reply_content` 和 `artifacts`
- 只要已经有 `session_id`、`message_id`、`task_id` 这些恢复主键，即使等待过程被中断，也必须补查结果并回给用户。
- 禁止在用户侧只留下“已经发出去”“正在等结果”“已完成”而没有实际 reply 内容的收尾。

### 3.1 对 Coze Session，默认复用上一次 session，除非用户明确要求新建

- 只要用户没有明确表达“新建话题”“新增话题”“开一个新会话”“不要沿用之前上下文”这类意图，就应优先复用上一次成功使用的 `session_id`。
- 当前 CLI 会把最近一次成功使用的 `session_id` 持久化到本地配置；Agent 可用 `coze session current --format json` 读取，用 `coze session use <session_id> --format json` 显式切换。
- `coze session message`、`coze session watch`、`coze session replies`、`coze session podcast message`、`coze session ppt edit` 在省略 `-s/--session-id` 时，会默认复用当前本地 session。
- 推荐顺序：
  1. 先执行 `coze session current --format json` 读取本地默认 `session_id`
  2. 用 `coze session status -s <session_id> --format json` 确认该 session 仍可用
  3. 如果需要切换到指定会话，执行 `coze session use <session_id> --format json`
  4. 如果本地没有最近 `session_id`，再用 `coze session list --limit 20 --format json` 找最近一个可复用 session，并在确认后 `coze session use <session_id> --format json`
  5. 只有在用户明确要求新开话题，或确实没有可复用 session 时，才执行 `coze session create --format json`
- 禁止因为“发起新请求”就默认创建新 session，这会丢失连续对话上下文，也会增加 agent 自己维护上下文的负担。

### 4. 对用户交付文件时，必须返回在线链接，不要返回本地路径

- 本地路径如 `/tmp/foo.mp3`、`./output/image.png`、相对路径或沙箱路径，对用户不可直接访问。
- 生成文件后，**必须**继续执行 `coze file upload <path>`。
- 最终返回给用户的应是上传后的在线 `URL`，而不是本地文件路径。

### 5. 不确定命令用法时，使用 `--help` 或 `--man` 查看

- 任何命令都支持 `--help` 查看简要帮助，`--man` 查看完整手册（含参数说明、示例、错误码）。
- 当不确定某个命令的参数、选项或用法时，**先执行 `<command> --help` 或 `<command> --man`** 获取准确信息，不要凭猜测拼命令。
- 示例：
  ```bash
  coze code project create --help
  coze code deploy --man
  coze generate video create --help
  ```

### 6. 显式路由前缀只用于命中 skill，不得透传给底层 prompt

- 当用户输入以 `/coze-cli` 或 `/coze` 开头时，首个 token 仅作 skill 路由用途。
- 在调用 `coze session message`、`coze session podcast message` 或其他 Coze CLI 子命令前，必须剥离该前缀。
- 示例：
  - `/coze-cli 制作一个介绍潮汕美食的 PPT` -> `制作一个介绍潮汕美食的 PPT`
  - `/coze-cli @PPT 制作介绍海南美食的 PPT` -> `@PPT 制作介绍海南美食的 PPT`
- 禁止把 `/coze-cli`、`/coze` 原样拼进最终发送给 Claw 的 message。

### 7. 长任务不得阻塞回合（通用总纲）

- Coze CLI 的多数核心动作是**异步长任务**：`coze code` 的项目创建 / `message send`（分钟级到几十分钟级）、`coze session message` 命中 `progress_id` / `task_id` 的长任务、部署等。**严禁**为了"等到终态"而让单次命令或单个回合一直前台阻塞——这会撞穿宿主工具超时（通常约 10 分钟），表现为 agent"卡住，除非任务完成"。
- 通用做法：**先 ACK 再跟进**。当前回合先把已有的中间结果（项目链接 / 前置 reply / 已接单说明）回给用户并收尾，再用**非阻塞**方式跟进终态。跟进机制按以下优先级选：
  1. **优先：子 session 后台任务（subagent / 独立子会话）**——先探测当前 agent 是否支持起一个独立的子 session / subagent 在后台运行。支持就用它：让子会话去轮询直到终态，再把最终结果回报到原上下文。这类机制能真正"自行跑完并回唤交付"，是非阻塞的首选。
  2. 次选：宿主其它后台 / 定时能力（cron、delayed job 等）登记独立 follow-up，任务结束再回填。
  3. 兜底：以上都不支持时，逐回合短轮询（每回合查一次、让出回合），**不要**把整段轮询 `sleep` 在一次调用里。
- **终态必须回传**：无论用哪种机制，跟进到终态后都必须主动把最终结果回给用户——只 ACK 不回终态等于任务丢了。
- **创建结果必须说实话（先动作、后文案）**：只有**真正调用创建工具并拿到回执**（子 session 的真实 `session_id` / 后台任务句柄）才可说"完成后自动回你"，且 ACK 要带上该回执 ID；没拿到回执就如实告知并给下一步选项，禁止凭"打算派 / 理论上能派"就声称"已在后台盯着"。
- 各模块的具体规范：`coze code` 见 [`coze-code/MODULE.md`](coze-code/MODULE.md) 的「阻塞与超时铁律」「长任务 follow-up」；`coze session` 见 [`coze-claw/references/coze-claw-async-followup.md`](coze-claw/references/coze-claw-async-followup.md)。

## 安装 CLI

```bash
npm install -g @coze/cli
```

如果找不到包，可执行：

```bash
npm config set registry https://registry.npmjs.org/
```

安装/升级后 CLI 会自动静默执行 `coze self skill install`，把自带 skills 安装到本机 AI agents。`coze self` 是 CLI 工具自身的能力集合（区别于操作 Coze 平台资源的命令）；若运行命令时提示 skills 缺失或版本不一致，手动执行：

```bash
coze self skill install
```

## 登录与身份验证

#### 避坑：OAuth 授权超时与阻塞问题

- `coze auth login` 的 OAuth 激活链接和设备码通常输出在 `stderr`，需要合并捕获。
- **致命问题**：设备码有 **10 分钟有效期**，且命令会前台阻塞等待。如果 Agent 同步等待该命令执行，可能会卡死流程，且用户往往来不及操作。
- **补充问题**：部分 Agent 宿主会回收 detached/`nohup` 子进程，导致 `coze auth login` 在用户完成授权前就异常消失，表面上看像“用户已授权但 CLI 一直未登录”。
- **当前推荐顺序**：
  1. 优先在一个可持续持有的 PTY/TTY 会话里直接运行 `coze auth login`
  2. 读取并返回授权链接给用户
  3. 保持该会话存活，等待 `Authentication successful. Credentials saved.`
  4. 成功后再执行 `coze auth status --format json`
- 只有在确认宿主不会回收 detached 子进程时，才使用下面的 `nohup` + 退出码文件方案。
- **推荐方案：后台执行 + 轮询获取链接 + 进程自记录退出码**：
  ```bash
  # 0. 清理上次残留的临时文件（避免误读旧状态）
  rm -f /tmp/coze-login.log /tmp/coze-login.pid /tmp/coze-auth-exit-code.txt

  # 1. 后台启动登录命令，让进程自己记录退出码
  nohup bash -c '
    coze auth login
    EC=$?
    echo $EC > /tmp/coze-auth-exit-code.txt
    exit $EC
  ' > /tmp/coze-login.log 2>&1 &
  echo $! > /tmp/coze-login.pid

  # 2. 轮询等待授权链接出现（最多等待 30 秒）
  for i in $(seq 1 15); do
    if grep -q "user_code=" /tmp/coze-login.log 2>/dev/null; then
      break
    fi
    sleep 2
  done

  # 2.1 检查是否成功获取到链接
  if ! grep -q "user_code=" /tmp/coze-login.log 2>/dev/null; then
    echo "获取授权链接超时，请检查网络连接或重试"
    cat /tmp/coze-login.log 2>/dev/null
  fi

  # 3. 提取并返回授权链接
  grep "user_code=" /tmp/coze-login.log | grep -oE 'https://[^ ]+'
  ```
- **为什么让进程自己记录退出码**：
  - `wait` 命令只能在启动进程的 shell 中使用，无法在后台子 shell 中跨进程等待。
  - 通过 `bash -c '...; EC=$?; echo $EC > file'` 让进程自己捕获并记录退出码。
  - 退出码精确反映**本次**授权结果，不受上次登录状态影响：
    - 退出码 `0`：用户完成授权
    - 非零退出码：授权失败（常见值：`1` 一般失败、`2` 认证错误、`4` 参数错误，具体原因看 JSON 输出中的错误码）
- **授权流程（必须遵守）**：
  1. **先检查授权状态**：在发起任何需要认证的操作前，必须先执行 `coze auth status` 确认是否已完成授权。
  2. **若未授权，后台执行并轮询获取链接**：
     - 使用上述后台执行 + 轮询方案获取授权链接。
     - 一旦获取到链接，**立即返回给用户**。
     - 同时启动后台轮询任务自动检查授权状态。
  3. **检查退出码确认授权结果**：
     - 进程结束后，退出码会自动写入 `/tmp/coze-auth-exit-code.txt`。
     - 通过轮询检查该文件确认授权结果：
       ```bash
       # 轮询检查退出码文件（最长等待 10 分钟）
       for i in $(seq 1 60); do
         if [ -f /tmp/coze-auth-exit-code.txt ]; then
           exit_code=$(cat /tmp/coze-auth-exit-code.txt)
           if [ "$exit_code" = "0" ]; then
             echo "授权成功"
           else
             echo "授权失败（退出码: $exit_code）"
           fi
           break
         fi
         sleep 10
       done

       # 兜底：如果轮询结束仍未获得退出码，说明进程异常
       if [ ! -f /tmp/coze-auth-exit-code.txt ]; then
         echo "授权超时或进程异常退出"
         # 检查后台进程是否仍在运行
         if [ -f /tmp/coze-login.pid ] && kill -0 "$(cat /tmp/coze-login.pid)" 2>/dev/null; then
           echo "登录进程仍在运行，尝试终止"
           kill "$(cat /tmp/coze-login.pid)" 2>/dev/null
         fi
       fi
       ```
  4. **授权完成后，再启动后续任务**：
     - 授权是所有后续操作的前置条件。在确认已登录之前，**不要**创建任何后台任务或发起项目创建/部署等后续操作。
- 如果提示 `[Auth] No API token found`，先执行：

```bash
coze auth status
```

### 检查登录状态

- `coze auth status` 返回当前凭证状态。`--format json` 输出结构化数据，至少包含 `logged_in`，登录成功时通常还会返回 `user` 和 `token_expires_at`。
- Token 过期后 CLI 会在执行命令时自动尝试刷新，无需手动重新登录。

### 登出

- `coze auth logout` 清除本地凭证。

## 长时间命令处理

### 避坑：长耗时命令超时问题

- 部分命令（AI 生成、部署、OAuth 登录等）可能耗时数分钟甚至更久，超过沙箱超时限制（通常 600 秒）会导致命令被强制中断。
- 不同命令的阻塞行为不同，需要区分处理。

### 长耗时命令速查表

| 长耗时命令 | 默认行为 | `--wait` | 对应的轮询命令 |
|-----------|---------|:---:|--------------|
| `coze auth login` | 同步阻塞（等待用户浏览器授权） | — | 轮询退出码文件（见上文"登录与身份验证"） |
| `coze code message send` | **非阻塞**（发送后立即返回 `status:'sent'`） | ✅ 加后阻塞等待 AI 回答流完成 | `coze code message status -p <project_id>` |
| `coze code project create` | **非阻塞**（后台子进程执行 AI 生成） | ✅ 加后变阻塞 | `coze code message status -p <project_id>` |
| `coze code deploy <id>` | 触发部署后立即返回 | ✅ 加后内置轮询(3s) | `coze code deploy status <project_id>` |
| `coze code deploy fix <id>` | **非阻塞**（后台子进程执行修复） | ✅ 加后变阻塞 | `coze code message status -p <project_id>` |
| `coze generate video create` | 提交任务后立即返回 taskId | ✅ 加后内置轮询(2s/5min超时) | `coze generate video status <task_id>` |
| `coze generate audio` | 同步阻塞（SSE 流式返回） | — | — |
| `coze generate image` | 同步阻塞（单次 API 调用） | — | — |
| `coze session message` | 提交后立即返回 `message_id` | ✅ 加后变阻塞并输出事件流 | `coze session replies <message_id>` |
| `coze session task show/refresh/watch` | 单次查询 / 主动刷新 / 持续观察本地恢复任务 | — | `coze session replies <message_id>` / `coze session progress poll <progress_id>` |
| `coze session watch` | 持续监听 websocket | — | 必须加 `--timeout`，超时后用 `replies` 补偿 |
| `coze session progress watch` | 持续监听后台任务 | — | 必须加 `--timeout`，或改用 `progress poll` |

> `coze code message status` 和 `coze code deploy status` 本身都是**单次查询**，不会自动轮询。需要在脚本中循环调用。
> `coze code message cancel -p <project_id>` 可取消进行中的消息任务。

### 场景一：命令支持非阻塞——不加 `--wait` 直接使用

`project create`、`deploy fix` 默认就是非阻塞的（通过 detached 子进程后台执行），`deploy`、`generate video create` 默认提交后立即返回。这些命令返回后，通过上表中对应的轮询命令检查结果即可。

```bash
# 示例：项目创建 + 轮询（默认非阻塞）
coze code project create --type web --message "需求描述" --create-source agent_cli
# 命令立即返回 project_id，然后轮询消息状态
for i in $(seq 1 60); do
  result=$(coze code message status -p <project_id> --format json)
  status=$(echo "$result" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
  echo "[$(date +%H:%M:%S)] 状态: $status"
  if [ "$status" = "done" ] || [ "$status" = "completed" ]; then
    echo "处理完成！"
    echo "$result"
    break
  elif [ "$status" = "failed" ]; then
    echo "处理失败"
    break
  fi
  sleep 30
done
```

> **注意**：这些命令加 `--wait` 后会变成同步阻塞，应按场景二处理。推荐**不加 `--wait`**，改用对应轮询命令手动轮询。

### 场景二：命令处于阻塞状态——需要 `nohup` 后台执行

以下情况命令会同步阻塞，如果预计耗时较长可能超出沙箱超时限制，必须通过 `nohup` 后台执行，再用对应轮询命令检查结果：

- **本身始终阻塞的命令**：`generate audio`、`generate image`、`auth login` 没有 `--wait` 选项，始终同步阻塞。
- **加了 `--wait` 的命令**：`message send --wait`、`project create --wait`、`deploy --wait`、`deploy fix --wait`、`generate video create --wait` 加上 `--wait` 后会变成同步阻塞（其中 `message send` 不加 `--wait` 时为非阻塞，发送后立即返回，用 `message status` 轮询）。

```bash
# 示例：阻塞型 message send --wait 后台执行 + 轮询
# 注意：message send 不加 --wait 时为非阻塞（发送即返回），无需 nohup，直接调用后用 message status 轮询即可；
#       只有加了 --wait（同步等待 AI 回答流完成）且预计耗时较长时，才需要下面的 nohup 后台执行方案。
rm -f /tmp/coze-message.log /tmp/coze-message-exit-code.txt

nohup bash -c '
  coze code message send "需求描述" -p <project_id> --wait
  EC=$?
  echo $EC > /tmp/coze-message-exit-code.txt
  exit $EC
' > /tmp/coze-message.log 2>&1 &

# 通过 message status 轮询进度（对应轮询命令见上表）
for i in $(seq 1 60); do
  result=$(coze code message status -p <project_id> --format json 2>/dev/null)
  status=$(echo "$result" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
  echo "[$(date +%H:%M:%S)] 状态: $status"
  if [ "$status" = "done" ] || [ "$status" = "completed" ]; then
    echo "处理完成！"
    echo "$result"
    break
  elif [ "$status" = "failed" ]; then
    echo "处理失败"
    break
  fi
  sleep 30
done

# 兜底：轮询结束仍未完成时检查后台进程退出码
if [ "$status" != "done" ] && [ "$status" != "completed" ]; then
  if [ -f /tmp/coze-message-exit-code.txt ]; then
    exit_code=$(cat /tmp/coze-message-exit-code.txt)
    echo "后台进程已退出，退出码: $exit_code"
  else
    echo "任务可能仍在进行中，请稍后再次执行轮询命令检查"
  fi
fi
```

**核心原则**：任何可能长时间阻塞的命令，都应后台执行或使用其内置的非阻塞模式，然后通过对应的轮询命令检查结果，避免沙箱超时中断。

## 组织与空间上下文

### 核心行为

- 切换组织时会**自动清空 Space ID**，需要重新选择工作空间。
- 指定不存在的组织 ID 会**报错且不修改配置**。
- 切换到个人账户有三种等价写法：`coze organization use`（省略 org_id）、`coze organization use ""`（显式空串）、`coze organization unset`（别名 `coze organization reset`）。均会清空 `organizationId`/`enterpriseId`（及 `spaceId`），且**不再校验个人账户是否可用**。
- 安装了 `default-space` 插件后，未显式传 `--space-id` 时会改为取**服务端为当前组织配置的默认工作空间**（而非"第一个可用空间"）。优先级：`--space-id` > 服务端默认空间 > 已存 `spaceId` 配置 > 第一个可用空间。详见"插件（Plugins）"章节。

### 遇到 `No permission` 的修正顺序

1. `coze config list` — 查看当前配置
2. `coze organization list` — 查看可用组织
3. `coze organization use <org_id>` — 切换到正确的组织（或 `coze organization unset` / `coze organization use` 切换到个人账户）
4. `coze space list` — 查看当前组织下的空间
5. `coze space use <space_id>` — 切换到正确的空间

### 环境变量覆盖

- `COZE_ORG_ID`、`COZE_SPACE_ID` 环境变量可临时覆盖配置，无需修改持久化配置。
- `--org-id`、`--space-id` 全局参数也可以临时覆盖。
- **项目访问链接的域名由项目类型决定**：`web` / `app` / `miniprogram` / `skill` / `general`（coze 3.0 项目）使用 `www.coze.cn`，其它类型（agent / workflow / assistant 等）使用 `code.coze.cn`。各命令输出的 URL（如 `project_url`、部署/预览链接）已由 CLI 据此生成，直接透传即可。
- `COZE_CLI_PLATFORM` 环境变量仅在**无法获知项目类型**的少数场景作为域名回退依据（取值 `ecs` / `vefaas` 时回退到 `www.coze.cn`，否则 `code.coze.cn`），不再覆盖按类型决定的链接。

## 配置管理概要

- `coze config get <keys...>` — 获取配置值
- `coze config set <key> <value>` — 设置配置值
- `coze config delete <keys...>` — 删除配置值
- `coze config list` — 列出所有配置

详细用法参见各业务模块 reference 文档中的配置相关章节。

## 插件（Plugins）

插件是**可选启用**的功能开关：只有安装后对应功能才生效，未安装时 CLI 行为与之前完全一致。"安装"只是把开关写进本地配置（`plugins.<id>.enabled`），不调用网络，故 `coze plugin *` 命令**免登录、跳过 org/space 检查**。

```bash
coze plugin list                      # 列出全部插件及安装状态
coze plugin install default-space     # 安装（启用）插件
coze plugin uninstall default-space   # 卸载（禁用）插件
```

- 传入未知插件 id 会报 `E1000`（`INVALID_ARGUMENT`），并提示可用插件清单。
- Agent 场景同样建议加 `--format json` 解析结果（`list` 返回 `{ id, name, description, installed }` 数组）。

### 内置插件：`default-space`

启用后，未显式传 `--space-id` 时，CLI 会取**服务端为当前组织配置的默认工作空间**，替代默认的"自动选第一个可用空间"。

- 优先级：`--space-id` > 服务端默认空间 > 已存 `spaceId` 配置 > 第一个可用空间。
- 默认工作空间是**组织维度**概念：个人账户（无组织上下文）下该插件不生效，回退到原有逻辑。
- 解析失败（无默认空间 / 接口异常）会静默回退，不会阻断主命令。

## 安全规则

- **禁止输出密钥**（token、API Key 等）到终端明文。
- **写入/删除操作前必须确认用户意图**。
- 用 `--dry-run` 预览危险请求（如适用）。

## 代理配置

如果需要通过代理访问 Coze API：

```bash
export HTTPS_PROXY=http://your-proxy:8080
export HTTP_PROXY=http://your-proxy:8080
```

CLI 会自动识别并使用配置的代理。

## 升级与补全

### 升级 CLI

CLI 默认开启后台自动升级（`auto` 模式）：检查走本地缓存零阻塞，发现新版后台静默安装、下次启动生效，通常无需手动干预。也可随时手动触发：

```bash
coze upgrade          # 升级到最新版本
coze upgrade --force  # 强制升级（即使已是最新）
coze upgrade --tag beta  # 升级到指定渠道
```

升级策略与渠道用 `coze config set` 调整：

```bash
coze config set upgrade.mode notify    # 仅提示，不自动安装
coze config set upgrade.mode off       # 完全关闭升级检查
coze config set upgrade.channel beta   # 切换升级渠道（npm dist-tag）
```

CI 环境、dev/本地构建版本、设置 `COZE_CLI_NO_UPDATE_NOTIFIER` 时自动跳过升级检查；版本检查每 4h 最多联网一次，后台升级失败后 10min 内不重试。

### Shell 自动补全

```bash
coze completion --setup    # 安装补全脚本
coze completion --cleanup   # 移除补全脚本
```

支持的 Shell：bash, zsh, fish, powershell。

## 退出码参考

Agent 在判断命令执行结果时，应根据退出码判断：

| 退出码 | 名称 | 含义 |
|--------|------|------|
| `0` | `SUCCESS` | 成功 |
| `1` | `FAILURE` | 一般失败（包含所有业务错误：E3xxx 资源类 / E4xxx 配额类 / E5xxx 服务端类，退出码均为 1） |
| `2` | `AUTH_ERROR` | 认证/授权错误（E2xxx，含 `PERMISSION_DENIED`（E2003）权限不足） |
| `4` | `INPUT_ERROR` | 输入参数错误（E1xxx） |

> 退出码只有以上 4 个（源码 `ExitCode`），映射规则：E1xxx → 4、E2xxx → 2、其余（含 E3xxx/E4xxx/E5xxx）→ 1。具体业务错误需解析 JSON 输出中的错误码（`code` 字段），不要依赖退出码细分。

### 退出码处理建议

- 退出码 `2`：认证类先执行 `coze auth login` 重新登录；若 JSON 错误码为 `E2003`（`PERMISSION_DENIED`），按"组织与空间上下文"章节的修正顺序排查。
- 退出码 `4`：检查参数拼写和格式。
- 退出码 `1`：解析 JSON 输出中的具体错误码（E3xxx/E4xxx/E5xxx）定位原因；E5xxx 网络/服务端类可重试一次。

## 业务模块导航

| 模块 | 触发场景 | 入口 |
|------|---------|------|
| [`coze-code`](./coze-code/MODULE.md) | 创建项目、发送需求、部署应用、环境变量/域名/技能管理 | `coze code *` |
| [`coze-claw`](./coze-claw/MODULE.md) | Claw Session 对话、回复监听、后台 progress、文件/PPT/播客产物 | `coze session *` |
| [`coze-generate`](./coze-generate/MODULE.md) | 生成图片、语音合成(TTS)、视频生成 | `coze generate *` |
| [`coze-file`](./coze-file/MODULE.md) | 上传本地文件获取在线访问地址 | `coze file upload` |

## 典型错误速查（基础类）

### 错误 1：用户要求用 Coze CLI，但 agent 改用别的 TTS

- 问题：偏离用户指令，且掩盖了 Coze CLI 实际可用路径。
- 修正：先补上 `--output-path`，完整跑完 Coze CLI 生成与上传闭环。

### 错误 2：OAuth 登录卡死或用户来不及授权

- 问题：直接后台执行 `coze auth login` 后继续发起后续任务，导致后续任务因未授权而全部失败；或前台阻塞等待导致 Agent 卡死；或使用 `wait` 在后台子 shell 中跨进程等待导致失败。
- 修正：
  1. **用 `bash -c` 包装命令**，让进程自己记录退出码到文件。
  2. **轮询获取授权链接**，拿到后立即返回给用户。
  3. **轮询检查退出码文件**，判断本次授权结果（0=成功，非0=失败）。

### 错误 3：未使用 `--format json` 导致输出无法解析

- 问题：Agent 需要从输出中提取 projectId、taskId 等结构化数据，但默认 text 格式不方便解析。
- 修正：Agent 场景下始终加 `--format json`，然后按 JSON 解析输出。

### 错误 4：忽视退出码直接认为命令成功

- 问题：命令可能返回非零退出码表示失败，但 Agent 只看了 stdout 输出。
- 修正：始终检查命令退出码，非零时根据退出码参考表排查问题。
