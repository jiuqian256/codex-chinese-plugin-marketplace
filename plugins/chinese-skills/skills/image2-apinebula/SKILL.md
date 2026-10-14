---
name: image2-apinebula
description: APINebula 图片生成与编辑：使用本人配置的 APINebula API 密钥生成或编辑图片，并保存和预览结果。 When the user asks with trigger phrases like 用image2生成：... or 用image2改图：..., automatically use APINebula's gpt-image-2 image APIs, including local-file edits, wait or save as needed, and render the final image inline in the conversation using absolute local file paths.
---

## 中文名称与用法

**中文名称：** APINebula 图片生成与编辑

**用途：** 使用本人配置的 APINebula API 密钥生成或编辑图片，并保存和预览结果。

**调用示例：** 使用 $chinese-skills:image2-apinebula 用 APINebula 生成一张产品海报。

文中的 `<SKILL_DIR>` 指本次加载的 SKILL.md 所在目录；从实际技能路径解析，不假定用户目录、操作系统或插件缓存版本。脚本接收的项目路径和输出路径仍使用当前任务的实际路径。


# image2-apinebula Skill

使用 APINebula 的图片接口调用 `gpt-image-2` / `image2`，支持 **自然语言直接触发**、**稳定命令词触发**、**本地图片改图**，并且在成功后 **直接在对话里预览图片**。

## 优先触发词
当用户消息包含以下任一前缀或明确意图时，应优先触发本 skill：

### 稳定命令词
- `用image2生成：`
- `用image2改图：`
- `用image2编辑：`
- `用image2出图：`
- `用APINebula生成：`
- `用gpt-image-2生成：`

这些写法应视为 **强触发**。
只要用户这样说，默认不要改用内置 `image_gen`，而要直接使用本 skill。

示例：
- `用image2生成：未来城市夜景`
- `用image2生成：一只戴宇航员头盔的橘猫，电影感，霓虹灯`
- `用image2改图：把这张商品图改成极简苹果风海报`

### 普通触发条件
当用户的意图符合以下任一条件时，也应优先使用本 skill：
- 用户明确提到 `APINebula`
- 用户明确提到 `image2`
- 用户明确提到 `gpt-image-2`
- 用户要求“不要用内置 image_gen，而是走第三方 API”
- 用户要求“直接帮我生成/编辑图片，并保存到工作区”

## 核心执行规则
**不要让用户手动敲 Python 命令。**

一旦命中本 skill，Codex 应该自己在后台执行脚本：
- 生成任务：调用 `generate`
- URL 图片编辑：调用异步 `edit`
- 本地图片编辑：调用脚本的本地文件 `edit` 模式
- 查询状态：调用 `status`
- 下载结果：必要时自动调用 `download`

默认应当：
- 自动等待任务完成（异步任务时）
- 自动下载或保存结果
- 自动把结果保存到当前工作区的 `outputs/image2-apinebula/`
- 自动在回复中展示最终图片预览
- 最终把保存路径返回给用户

## 接口信息
根据 APINebula 文档：
- Base URL: `https://apinebula.com`
- 鉴权: `Authorization: Bearer <API_KEY>`
- 异步生成接口: `POST /v1/image-tasks/generations`
- 异步编辑接口: `POST /v1/image-tasks/edits`
- 异步任务详情: `GET /v1/image-tasks/{task_id}?detail=true`
- 文档: [APINebula 图片异步任务接口](https://docs.apinebula.com/docs/advanced/image-tasks)

补充说明：
- 文档明确展示了异步生成与基于 URL 的异步编辑。
- 为了支持“本地图片直接改图”，脚本额外封装了 APINebula 图像编辑兼容接口 `https://img-api.apinebula.com/v1/images/edits` 的 multipart 文件上传方式。
- 这一部分是根据 APINebula 图片分组接口形态做的兼容实现，用于直接上传本地文件给编辑接口。

状态说明：
- `queued`
- `in_progress`
- `completed`
- `failed`

## 默认约定
- 默认生成模型：`gpt-image-2`
- 默认本地改图模型：`gpt-image-2-vip`
- 默认质量：`high`
- 输出目录：当前工作区下的 `outputs/image2-apinebula/`
- API Key 来源优先级：
  仅环境变量 `APINEBULA_API_KEY`。分享包不包含任何用户密钥；每个使用者配置自己的凭据。

## 后台执行命令
脚本路径：
`<SKILL_DIR>\scripts\image2_apinebula.py`

### 文生图
当用户请求“生成图片”时，Codex 应自动执行：

```powershell
python "<SKILL_DIR>\scripts\image2_apinebula.py" generate --prompt "<用户提示词>" --wait --download --outdir "<当前工作区>\outputs\image2-apinebula"
```

如果用户指定模型或质量，则追加：
- `--model <模型名>`
- `--quality <质量>`

### URL 改图
当用户提供的是远程图片 URL 时，Codex 应自动执行：

```powershell
python "<SKILL_DIR>\scripts\image2_apinebula.py" edit --prompt "<用户编辑提示词>" --image-url "<图片URL>" --wait --download --outdir "<当前工作区>\outputs\image2-apinebula"
```

如果有多张图，可重复传多个 `--image-url`。

### 本地文件改图
当用户提供的是本地文件路径，或者在对话里附加了本地图片文件时，应自动使用本地文件编辑模式，不要求用户先把图片上传成 URL。

```powershell
python "<SKILL_DIR>\scripts\image2_apinebula.py" edit --prompt "<用户编辑提示词>" --image-file "<本地图片绝对路径>" --outdir "<当前工作区>\outputs\image2-apinebula"
```

可选增强参数：
- `--mask-file <本地蒙版路径>`
- `--size <尺寸>`
- `--input-fidelity high`
- `--response-format b64_json`
- `--model gpt-image-2-vip`

如果用户给了多张本地图片，可重复传多个 `--image-file`。

### 查状态
当用户只想看任务状态时，自动执行：

```powershell
python "<SKILL_DIR>\scripts\image2_apinebula.py" status --task-id "<task_id>" --detail
```

## 本地图片输入规则
对于“本地图片改图”，按以下优先级识别输入：
1. 用户消息中明确给出的本地绝对路径
2. 当前工作区中的图片路径
3. 用户在对话里附加的图片文件

如果拿到的是本地文件：
- 不要要求用户自己先上传图床
- 直接走 `--image-file`
- 若用户附带了蒙版，也可走 `--mask-file`

支持的常见格式：
- `.png`
- `.jpg`
- `.jpeg`
- `.webp`

## 对话内直接预览图片
当脚本成功下载或保存图片后，Codex 不应只返回文件路径，还应在回复里直接插入本地图片预览。

必须使用 **绝对路径** 的 Markdown 图片语法，例如：

```markdown
![image2 result](<当前工作区绝对路径>/outputs/image2-apinebula/task_xxx-1.png)
```

如果有多张结果图：
- 优先展示第一张
- 如有必要，可列出全部保存路径
- 如果用户要求“都展示”，则全部渲染

## 执行流程
1. 判断用户是“生成图片”还是“编辑图片”。
2. 如果命中 `用image2生成：` 这类命令词：
   - 将冒号后的内容直接视为 prompt
   - 立即执行生成流程
3. 如果命中 `用image2改图：` / `用image2编辑：`：
   - 将冒号后的内容视为编辑 prompt
   - 优先寻找用户给的本地文件或附图；若没有，再使用图片 URL
4. 自动在后台运行脚本，不要要求用户手输命令。
5. 远程 URL 改图使用异步任务；本地文件改图直接保存同步结果。
6. 如果完成：
   - 告诉用户 `task_id`（如果是异步任务）
   - 告诉用户最终状态
   - 告诉用户保存到的本地路径
   - 直接把图片渲染出来预览
7. 如果失败：
   - 返回任务错误信息
   - 不要只说“失败了”，要尽量附带接口返回的错误详情

## 输出格式要求
每次成功执行后，回复中至少包含：
- 使用的模型
- prompt
- task_id（如果有）
- 最终状态
- 本地保存路径
- 至少一张预览图

## 注意事项
- 异步任务接口的客户端**不需要**自己传 `async=true`。
- 详情接口可传 `?detail=true` 获取更完整结果。
- 异步完成后的结果通常在 `data` 中，可能包含 `b64_json` 或 `download_url`；脚本会优先使用 `download_url` 下载。
- 如果用户没有明确说要用 APINebula / image2 / gpt-image-2，则可以按全局策略选择别的工具；但一旦用户明确指定，应优先使用本 skill。
