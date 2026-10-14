# html-ppt-studio

**像传统 PPT 一样，对 HTML 内容进行编辑、演示和导出。**

面向 Agent 的 HTML PPT / Web Deck 制作工作流：把网页、图片页、PPT 截图或 Agent 生成的页面，变成可翻页、可演示、可局部编辑、可保存状态、可导出的 HTML 演示文稿。

<p>
  <img src="assets/brand/logo.jpg" alt="杭州模力觉醒科技有限公司 logo" width="96" />
</p>

维护方：**杭州模力觉醒科技有限公司**

`html-ppt-studio` 是一个可开源、可移植的 skill / 工作流包，用来让 Codex、Hermes、Claude Code、Cursor、OpenCode 或其他具备文件读写能力的编程 Agent 生成和维护 HTML 形式的演示文稿。它的核心目标很直接：**让 HTML 内容具备接近传统 PPT 的编辑和演示体验**。

它适合做：

- HTML PPT / Web Deck。
- 把已有 HTML 内容变成可像 PPT 一样翻页、演示和局部编辑的 Deck。
- 已有 PPT 截图或页面图片的快速网页化。
- AI 快报、技术金融风报告、产品讲解、投资人风格汇报、教育培训课件和数据故事。
- 带演示者备注、观众窗口、全屏放映和导出入口的浏览器演示文稿。
- 可在网页里做少量手动修改，并把修改真实保存为 `deck-state.json` 的可编辑 Deck。

## 核心思路

`html-ppt-studio` 把 HTML PPT 拆成四层：

```text
页面内容层
  + 可复用 HTML 播放/编辑运行时
  + 可选本地保存/导出服务
  + 可选 Agent / 模型生成层
```

这样做的目的：

- 普通观看和演示不需要 API key。
- 小范围手动修改不需要每次调用模型。
- 模型主要用于生成初稿、复杂改稿、重做页面和理解自然语言修改要求。
- 用户已经满意的页面图、PPT 截图或图片页，默认应该包进 HTML Deck，而不是重新绘制。
- 只改一页时，不应该重写整套 Deck。

## 功能概览

### 生成 Deck

- 生成固定 16:9 的 HTML 演示文稿。
- 把已经确认的 16:9 页面图片快速包装成 HTML PPT。
- 支持纯图片类 PPT/PDF 导出的网页演示。
- 内置多种风格预设，例如深色科技金融、数据看板、政务蓝、Apple glass、Swiss grid、暖色工业报告。
- 整合多个 HTML Deck 时，优先保留原页面内容，统一替换外层运行时。

### 演示运行时

- 键盘翻页。
- 页码和当前页状态。
- 演示者视图。
- 可编辑演讲备注。
- 演讲备注按稳定页面 id 保存，关闭演示者视图后不丢失。
- 演讲计时。
- 计时暂停和继续，方便在编辑备注或临场改字时暂停计时。
- 干净观众窗口。
- 演示者窗口和观众窗口同步翻页。
- 演示者预览和观众窗口使用同一份保存状态，避免预览裁切或显示旧页面。
- 观众窗口全屏提示。
- 兼容翻页笔/键盘操作，但不使用空格键翻页，避免和中文输入法确认、文字编辑、按钮焦点冲突。

### 编辑运行时

- 浏览器内所见即所得式的轻量编辑。
- 文字编辑。
- 图片和对象移动、缩放。
- 页面插入、删除、复制、排序。
- 缩略图栏。
- 温度计式页码栏。
- 当前页生成入口。
- 任务状态提示。
- 通过本地服务把修改保存到 `deck-state.json`。

### 导出

- `publish.html`：用于转发观看的干净观众版。
- `editor.html`：用于本地编辑的版本。
- 本地服务可支持截图式高保真 PDF 导出。
- 提供 HTML 校验、图片 Deck 生成、修改页检测等辅助脚本。

### Agent 工作流

- `SKILL.md`：主工作流说明。
- `references/`：设计规则、运行模式、编辑、演示者视图、风格、图片工作流等分文件。
- `adapters/`：Codex、Hermes、通用 Agent 的使用说明。
- `examples/`：可直接运行的最小样例。
- `templates/`：可复用的本地服务模板。

## 它不是什么

`html-ppt-studio` 不是完整 PowerPoint 替代品，也不是在线设计工具。

它聚焦在这些实际场景：

- 生成 HTML PPT。
- 浏览器演示。
- 小范围编辑。
- 保存手动编辑状态。
- 导出可观看、可分享的结果。

完全可编辑的 PPTX 导出是另一个问题，通常需要在视觉还原度和可编辑性之间取舍。

## 目录结构

```text
html-ppt-studio/
├── SKILL.md
├── README.md
├── LICENSE
├── env.example
├── .gitignore
├── agents/
│   └── openai.yaml
├── adapters/
│   ├── codex/
│   ├── hermes/
│   └── generic-agent/
├── assets/
│   ├── brand/
│   │   └── logo.jpg
│   └── style-presets/
├── examples/
│   └── basic-deck/
├── references/
│   ├── design-rules.md
│   ├── runtime-modes.md
│   ├── editing-workflow.md
│   ├── presenter-view.md
│   ├── style-scene-options.md
│   └── image2-workflow.md
├── scripts/
│   ├── build_image_deck.py
│   ├── detect_changed_slides.py
│   └── validate_html_ppt.py
└── templates/
    └── edit-server/
```

## 安装方式

### 方式一：作为 Codex skill 使用

克隆仓库：

```bash
git clone https://github.com/YOUR-USER/html-ppt-studio.git
```

复制到 Codex skills 目录：

```bash
mkdir -p ~/.codex/skills
cp -R html-ppt-studio ~/.codex/skills/html-ppt-studio
```

重启 Codex 或重新加载 skills。

然后可以这样提需求：

```text
使用 html-ppt-studio，生成一个可编辑、可演示的 HTML PPT，主题是 AI 工具与效率提升。
```

### 方式二：本地直接使用

```bash
git clone https://github.com/YOUR-USER/html-ppt-studio.git
cd html-ppt-studio
```

让你的 Agent 先读：

```text
请先阅读 SKILL.md，再按任务需要阅读 references/ 里的相关文件。
```

示例：

```text
使用当前 html-ppt-studio 文件夹。
先阅读 SKILL.md 和 references/design-rules.md。
生成一个 10 页 HTML PPT，主题是面向非技术管理者解释 AI 基础设施。
```

### 方式三：运行内置样例

```bash
cd examples/basic-deck
node ../../templates/edit-server/server.js
```

打开：

```text
http://127.0.0.1:8801/
```

你可以试：

- `演示`：打开干净观众窗口。
- `编辑`：让页面文字进入可编辑状态。
- `保存`：写入 `deck-state.json`。
- `PDF`：调用可选的截图式 PDF 导出接口。

### 方式四：配合 Hermes 或其他 Agent 使用

Hermes 可阅读：

```text
adapters/hermes/HERMES.md
```

通用编程 Agent 可阅读：

```text
adapters/generic-agent/README.md
```

最低要求是 Agent 能够：

- 阅读 Markdown 说明。
- 读写本地文件。
- 修改 HTML/CSS/JavaScript。
- 运行本地脚本。
- 最好能做浏览器预览或截图验证。

## 环境要求

观看静态 Deck：

- 任意现代浏览器。
- 不需要模型。
- 不需要 API key。
- 不需要本地服务。

生成或修改 Deck：

- Python 3，用于辅助脚本。
- 一个具备前端代码能力的 Agent。
- 建议使用浏览器做视觉检查。

保存浏览器编辑：

- 浏览器。
- Node.js 或类似本地服务运行时。
- 能写入 `deck-state.json` 的本地服务。
- 本仓库已提供 `templates/edit-server/` 最小模板。

高保真 PDF 导出：

- Playwright 或其他浏览器自动化工具。
- `pdf-lib` 或类似 PDF 生成库。

AI 生成或复杂改稿：

- 具备较强代码和设计能力的模型。
- 只有在需要新图片或重绘时，才需要图片模型。

## API Key 和环境变量

观看、演示、手动编辑已有 Deck 不需要 API key。

如果你使用的 Agent 或图片模型需要 OpenAI 兼容接口，可以用环境变量配置，不要提交真实密钥：

```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

可以复制示例文件：

```bash
cp env.example .env
```

`.env` 应该只保存在本地。仓库的 `.gitignore` 默认会忽略 `.env` 和 `.env.*`，但保留 `env.example`。

## 常见用法

### 生成新 Deck

```text
使用 html-ppt-studio。
主题：AI 工具与效率革命。
受众：县区级政府部门负责人。
生成 12 页可编辑 HTML PPT。
先给我风格和场景选项，再生成初稿。
```

### 已有满意图片，快速做成 HTML PPT

```text
使用 html-ppt-studio 快路径。
我已经有满意的 16:9 页面图片。
不要重绘图片。
直接包装成 HTML PPT，加导航、页码、演示者模式和可编辑覆盖层。
```

也可以直接运行：

```bash
python3 scripts/build_image_deck.py ./slide-images --title "AI Tools" --out ./html-deck
```

### 执行网页里保存过的编辑

```text
执行保存的网页编辑。
先读取 deck-state.json。
确认哪些页面改过。
只更新受影响页面。
```

### 校验 HTML Deck

```bash
python3 scripts/validate_html_ppt.py path/to/index.html
```

### 检测改动页

```bash
python3 scripts/detect_changed_slides.py path/to/deck-state.json
```

## 三种运行模式

### A. 极速初稿模式

适合快速出初稿和确认视觉方向。

包含：

- 16:9 舞台。
- 键盘翻页。
- 基础页码。
- 轻量动画。

默认不包含完整编辑器、本地保存服务或高保真导出。

### B. 正式演示模式

适合会议、课堂、讲座和正式汇报。

包含：

- 演示者视图。
- 可编辑备注。
- 计时器。
- 干净观众窗口。
- 演示者和观众同步翻页。
- 观众窗口全屏提示。
- 键盘和翻页笔支持，不绑定空格键翻页。
- 计时暂停和继续。

### C. 完整编辑模式

适合精确修改。

包含：

- 正式演示模式的全部能力。
- 文字编辑。
- 图片/对象编辑。
- 缩略图栏。
- 温度计式页码栏。
- 插入、删除、复制、排序页面。
- 当前页生成入口。
- 任务状态提示。
- 通过本地服务保存状态。

原则：普通编辑不调用模型；当前页生成只处理当前页或明确改动页；全局复杂改稿回到 Agent 对话里处理。

## 设计默认值

默认风格偏深色科技金融数据叙事：

- 黑色或黑蓝背景。
- 细网格和报告式信息层级。
- 克制蓝色/青色，加少量暖橙强调。
- 优先使用图表、模块和视觉结构，不默认堆表格。
- 固定 1920×1080 的 16:9 舞台。
- 内层页面保持 1920×1080 设计坐标，外层窗口/iframe 等比缩放居中；不要把已设计好的页面强行改成 `100vw/100vh`。
- 平滑网页动画。
- 需要后续修改的文字尽量保留可编辑结构。

完整规则见：

```text
references/design-rules.md
```

## 风格预设

内置风格预设位于：

```text
assets/style-presets/
```

当前包含：

- Apple glass。
- Dark finance。
- Data dashboard。
- Government blue。
- Swiss grid。
- Warm industry。

Agent 应优先使用这些本地预设，不要在普通任务里重新搜索或生成风格缩略图。

## 可编辑 Deck 的保存契约

浏览器编辑必须保存为真实文件，例如：

- `deck-state.json`
- `edits.json`
- `index.edited.html`

只存在于 DOM 或 localStorage 里的临时状态不算保存成功。

保存状态应包含：

- 页面顺序。
- 页面 id。
- 改动页。
- 插入/删除页。
- 文字改动。
- 元素位置和尺寸。
- 图片地址或 data URL。
- 演讲备注。

演讲备注也属于保存状态。建议按稳定 `slideId` 保存，例如：

```json
{
  "notes": {
    "slide-1": "第一页演讲提示",
    "slide-2": "第二页演讲提示"
  }
}
```

如果存在 `deck-state.json`，Agent 后续修改前必须先读它。

最小本地服务模板在：

```text
templates/edit-server/
```

运行任意 Deck：

```bash
HTML_PPT_DECK_DIR=/path/to/deck HTML_PPT_EDIT_PORT=8801 node templates/edit-server/server.js
```

如果需要可选 PDF 导出，先安装模板依赖：

```bash
cd templates/edit-server
npm install
```

## 演示者视图契约

演示者视图必须支持独立的干净观众窗口。

观众窗口只显示页面内容。演示者窗口可以显示备注、控制按钮、缩略图和计时器。

演示者预览必须和普通播放/观众窗口使用同一份已保存页面状态。若页面 HTML 来自 `deck-state.json` 或 `slideHtmlOverrides`，预览也必须按稳定 `slideId` 走同一个渲染函数，不能绕过状态文件另算一份 `srcdoc`。

预览 iframe 或容器应保持 `width:100%; height:100%; transform:none`，由内部 16:9 页面自行适配容器。不要对已经适配的 iframe 再做一次外层缩放，否则容易出现“观众窗口正常，但演示者预览裁切”的问题。

正式投屏时：

1. 使用扩展显示器，不要使用镜像显示器。
2. 把观众窗口拖到投影屏或外接屏。
3. 在观众窗口点击全屏。
4. 演讲者自己的电脑保留演示者窗口。

## 只发布小目录和发布完整项目的区别

推荐开源范围是 `html-ppt-studio/` 这个小目录。

### 只发布 `html-ppt-studio/`

优点：

- 仓库小，当前约几 MB。
- 用户容易 clone 和安装。
- 只包含可复用的 skill 规则、适配器、脚本、风格预设、样例和模板。
- 不会发布历史 Deck、备份、导出文件、临时文件或私人项目上下文。
- 更适合作为公开工具维护。
- 降低误泄露草稿、客户材料、本机路径和生成产物的风险。

取舍：

- 不包含所有历史成品 Deck。
- 用户看到的是通用能力包，不是内部工作档案。

### 发布完整父项目

完整父项目通常会包含 `outputs/`、历史 Deck、导出 PDF、服务副本、实验文件、备份和临时工作目录。

优点：

- 示例和历史材料更多。
- 如果目标是公开一个完整研究档案，会更完整。

风险：

- 仓库大。
- 用户不知道应该安装哪一层。
- 容易混入私人草稿、旧版本、缓存文件、生成产物或本机状态。
- GitHub 首页会变乱，维护成本更高。

推荐做法：

- 公开发布 `html-ppt-studio/`。
- 完整父项目继续作为私有工作档案保留。
- 需要展示效果时，只把清理过的样例放进 `examples/`。
- 可复用服务和运行时模板放进 `templates/`，不要直接发布项目专用工作文件。

## 开发者信息

项目名：

```text
html-ppt-studio
```

维护方：

```text
杭州模力觉醒科技有限公司
```

项目用途：

```text
通过 Agent-compatible 工作流创建、编辑、演示和导出高质量 HTML PPT。
```

GitHub 仓库描述建议：

```text
面向 Agent 的 HTML PPT / Web Deck 制作、编辑、演示和导出工作流。
```

GitHub topics 建议：

```text
html-ppt
web-deck
presentation
codex-skill
agent-workflow
presenter-view
html-slides
deck-editor
```

首个版本号建议：

```text
v0.1.0
```

公开兼容目标：

- Codex skill。
- Hermes 本地 Agent。
- 通用文件型编程 Agent。
- 静态浏览器 Deck 观看。
- 本地编辑保存和可选导出。

开发原则：

- 保持可移植。
- 避免本机绝对路径。
- 避免绑定单一模型供应商。
- 默认保留用户已经认可的页面视觉。
- 小改动优先只改受影响页面。
- 不提交凭据。
- 把保存状态当作后续修改的事实来源。

## 安全和隐私

不要提交：

- `.env` 文件。
- API key。
- access token。
- 私人客户 Deck。
- 个人工作笔记。
- 大量生成结果。
- 浏览器缓存或本地服务状态。

适合提交：

- 可复用 skill 说明。
- 通用适配器说明。
- 已脱敏样例。
- 辅助脚本。
- 公开风格预设。
- 通用服务模板。

## 贡献方向

欢迎改进：

- 校验脚本。
- 演示者/观众窗口同步。
- 本地编辑状态保存。
- 已脱敏示例 Deck。
- 新风格预设。
- 更多 Agent 适配说明。
- 导出和浏览器兼容问题。

不建议把项目变成：

- 完整设计工具。
- 依赖特定模型供应商的闭环产品。
- 观看或演示也必须配置 API key 的系统。
- 会重绘用户已认可页面的自动化工具。
- 包含大量生成输出的素材仓库。

## Roadmap

后续可继续补：

- 更多中文样例 Deck。
- 更完整的本地编辑/导出服务模板。
- 更多风格预设包。
- 截图式 PDF 导出最佳实践。
- PPTX 导出策略说明。
- 浏览器视觉回归检查。
- 更多 Agent 适配器。

## License

MIT.
