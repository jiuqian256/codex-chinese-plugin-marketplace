# get-web-design

将任意线上网站的设计风格提取为一份结构化 `DESIGN.md`。本 skill 是 design-extractor Chrome 扩展的命令行 / AI Agent 移植版。

## 功能

- 从任意 URL 生成可用于 AI 编程提示词的 `DESIGN.md`
- 提取站点的设计 token（颜色 / 字体 / 间距 / 圆角 / 阴影 / 动效）
- 直接使用当前 AI Agent 分析，无需额外 API Key；支持图片时结合截图，否则使用 DOM/CSS
- 识别网页中真正有记忆点的标志性元素，并用纯文字输出视觉规则（不含代码）
- 通过 chrome-devtools MCP 采集 DOM、Computed CSS 与可选的最多 3 张截图
- 输出符合 Google DESIGN.md alpha 格式的实测 token 和八节正文，结合 Vercel 的任务导向、组件复用与验收方法

## 触发场景

- "生成 https://stripe.com 的 DESIGN.md"
- "分析 linear.app 的设计风格并保存"
- "extract design from <url>"

## 前置依赖

1. **chrome-devtools MCP** —— 通过 `/mcp` 验证是否有 `chrome-devtools` 服务
2. **Python ≥ 3.9** —— 仅使用标准库，无需安装 Python 依赖

当前模型无需支持视觉；能读取图片时自动结合截图，不能读取时依据 DOM/CSS 分析并标注视觉验证局限。无需单独配置 API Key、服务地址或模型名；宿主 AI 工具自身的订阅或计费仍适用。

详见 `references/setup.md`。

## 安装

### 一行命令（自动检测你的 AI 工具）

```bash
curl -fsSL https://raw.githubusercontent.com/liaocaoxuezhe/get-web-design/main/install.sh | bash
```

### 通过 npx skills 安装（推荐）

如果你已经安装了 [`skill.sh`](https://skill.sh) 生态，可以直接用以下命令安装：

```bash
npx skills add liaocaoxuezhe/get-web-design
```

安装完成后，skill 会自动注入到当前 AI Agent 的 context 中，无需手动复制文件。

### 指定平台安装

```bash
# Claude Code
curl -fsSL https://raw.githubusercontent.com/liaocaoxuezhe/get-web-design/main/install.sh | bash -s -- claude-code

# Cursor
curl -fsSL https://raw.githubusercontent.com/liaocaoxuezhe/get-web-design/main/install.sh | bash -s -- cursor

# OpenAI Codex CLI
curl -fsSL https://raw.githubusercontent.com/liaocaoxuezhe/get-web-design/main/install.sh | bash -s -- codex

# Gemini CLI
curl -fsSL https://raw.githubusercontent.com/liaocaoxuezhe/get-web-design/main/install.sh | bash -s -- gemini-cli
```

### 手动安装

复制完整仓库中的 `SKILL.md`、`skill.yaml`、`assets/`、`scripts/`、`references/` 到目标 skill 目录；仅复制 `SKILL.md` 无法运行生成脚本。

## 工作流

```
URL → [浏览器] DOM + computed CSS + 可选截图
    → [Python --prepare] analysis-input.md
    → [当前 Agent] 阅读证据，写 analysis.md
    → [Python --analysis] 校验并拼装 design.md
```

每次抽取的所有产物都收敛到一个 `output/<hostname>/` 文件夹，便于归档和复用。

详细步骤见 `references/workflow.md`。chrome-devtools MCP 调用配方见 `references/chrome_devtools_recipes.md`。

## 文件结构

| 路径 | 用途 |
|------|------|
| `SKILL.md` | Skill 核心定义与使用指南 |
| `assets/collect_design_data.js` | 注入目标页面的 DOM + CSS 采集脚本 |
| `assets/system_prompt_en.txt` / `system_prompt_zh.txt` | 当前 Agent 的分析要求 |
| `assets/design_thinking.md` / `core_principles.md` | DESIGN.md 固定头尾段落 |
| `scripts/generate_design_md.py` | 主入口 CLI：准备本地证据与最终拼装 |
| `scripts/css_evidence.py` | CSS computed-style → 证据摘要 |
| `scripts/design_document.py` | 规范 token 提取、YAML 序列化与八节正文验证 |
| `references/setup.md` | 浏览器与 Python 环境准备 |
| `references/workflow.md` | 完整数据流详解 |
| `references/chrome_devtools_recipes.md` | MCP 精确调用顺序与故障兜底 |

## License

MIT

## 1.2.0：无需额外 API Key

- 移除外部模型调用及凭据配置，复用当前运行 skill 的模型。
- 截图变为可选：支持视觉时查看截图，不支持时依据 DOM/CSS 完成分析。
- CLI 改为 `--prepare` 和 `--analysis` 两阶段，由 Agent 自动衔接；用户只需提供 URL。
- 保留实测 token、八节正文、证据附录与 Python 3.9 兼容性。

## 1.1.0：DESIGN.md 格式与复用规则

- 精确数值由程序从 CSS 样本提取，AI 解释用途；保留透明度和同一元素的排版组合，不补造未知值。
- 正文依次为 Overview、Colors、Typography、Layout、Elevation & Depth、Shapes、Components、Do's and Don'ts。中文模式保留英文标题。
- 移除覆盖原站风格的字体/渐变禁令，补充适用范围、读者任务、证据边界和可观察验收。
- Python 3.9 可运行，无新增 Python 依赖；安装脚本包含新的 `scripts/design_document.py`。

格式检查：`npx @google/design.md lint output/<hostname>/design.md`。格式通过不代表已完成 Stitch 实际导入或页面视觉验证。

参考：[Google 格式规范](https://github.com/google-labs-code/design.md/blob/main/docs/spec.md)、[Vercel 的使用方法](https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md)。
