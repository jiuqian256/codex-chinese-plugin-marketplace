# UI/UX Pro Max — UI/UX 设计智能

本文是当前安装版本 `SKILL.md` 正文的中文译本。英文入口和 frontmatter 保留；代码、命令、路径、变量名、查询词及规则标识不翻译。唯一的运行适配是将 Claude 专用脚本路径改为本机绝对路径；原始入口保存在 `SKILL_UPSTREAM.md`。

本地可搜索资料包括：79 种可搜索风格（50 种活跃风格）、192 组产品配色与推理配置、74 组字体搭配、119 条 UX 指南、105 个精选图标、17 组 GSAP 预设、25 种图表和 22 种技术栈。

## 何时使用

任务涉及 **UI 结构、视觉决策、交互模式或用户体验质量控制** 时使用：设计新页面、创建或重构 UI 组件、选择颜色/字体/间距/布局体系、审查 UX/可访问性/一致性、实现导航/动画/响应式行为，或提升感知质量与易用性。

纯后端逻辑、API/数据库设计、非视觉性能优化、基础设施/DevOps 和非视觉脚本通常不适用，除非任务会改变界面的外观、感受、运动或交互方式。

## 规则优先级

按 1→10 决定首先关注的类别；用 `--domain <Domain>` 查询详情。完整分类规则位于 `references/quick-reference.md`，按需读取。

| 优先级 | 分类 | 影响 | Domain | 关键检查 | 应避免的反模式 |
|---|---|---|---|---|---|
| 1 | 可访问性 | CRITICAL | `ux` | 对比度 4.5:1、替代文本、键盘导航、Aria-labels | 移除焦点环、纯图标按钮没有标签 |
| 2 | 触控与交互 | CRITICAL | `ux` | 最小尺寸 44×44px、间距 8px+、加载反馈 | 只依赖 hover、状态瞬间改变（0ms） |
| 3 | 性能 | HIGH | `ux` | WebP/AVIF、懒加载、预留空间（CLS < 0.1） | 反复触发布局计算、累计布局偏移 |
| 4 | 风格选择 | HIGH | `style`, `product` | 匹配产品、一致性、SVG 图标 | 随意混合扁平与拟物风格、用 emoji 作图标 |
| 5 | 布局与响应式 | HIGH | `ux` | 移动优先断点、Viewport meta、无横向溢出 | 横向滚动、固定 px 容器宽度、禁用缩放 |
| 6 | 字体与颜色 | MEDIUM | `typography`, `color` | 基础字号 16px、行高 1.5、语义颜色 tokens | 正文字号 < 12px、灰底灰字、组件内硬编码 hex |
| 7 | 动画 | MEDIUM | `ux`, `gsap` | 时长符合上下文、动画表达意义、空间连续 | 所有过渡同一时长、动画改变 width/height、不支持减少动画 |
| 8 | 表单与反馈 | MEDIUM | `ux` | 可见标签、字段旁错误、辅助说明、渐进披露 | 仅 placeholder 标签、错误只在顶部、一次展示过多内容 |
| 9 | 导航模式 | HIGH | `ux` | 可预测返回、底部导航 ≤5、深链接 | 导航过载、返回失效、无深链接 |
| 10 | 图表与数据 | LOW | `chart` | 图例、工具提示、可访问配色 | 仅通过颜色传达信息 |

119 条 UX 指南及理由详见 `references/quick-reference.md`。应用界面的图标、触控反馈、暗色对比度、安全区域与标准交付检查清单见 `references/pro-rules.md`。

## 运行搜索工具

脚本位于技能目录中，不在项目目录。始终使用完整路径，不假设当前工作目录：

```bash
python "<SKILL_DIR>/scripts/search.py" "<query>" --domain <domain>
```

如果找不到 `python`，尝试 `python3`，再尝试 `py -3`。需要 Python 3.x，无第三方依赖。若缺少 Python，参考 README 的安装说明。

## 工作流程与查询约定

选择足以满足任务的最小搜索模式：

1. 新项目/新页面或全局视觉方向：使用 `--design-system`。
2. 特定问题或组件缺陷：指定一个明确的 `--domain`。
3. 已知实现技术栈：使用 `--stack`；只有独立的设计问题才额外搜索 domain。

每个查询围绕一个主要意图，使用 2–5 个有意义的词，加上产品、平台或交互等有用约束。应用前核对返回领域、分类、首条结果身份与产品/平台的适配性。结果为空或偏题时，缩小查询或显式指定 domain/stack，重试一次。仍失败时，说明未找到经过核实的匹配；通用建议应标记为回退方案。不要保存未经核实的输出。

可访问性查询一次关注一个可观察结果，并使用明确的结果词。先查询语义结果（`"error summary validation" --domain ux`），有需要再查询组件领域（`"decorative icon aria hidden" --domain icons` 或 `"icon button accessible label" --domain icons`），最后查实现技术栈。还可使用 `"focus not obscured" --domain ux`、`"dragging movements" --domain ux`、`"accessible authentication" --domain ux`。不要用泛泛的可访问性结果代替具体交互或 WCAG 条目的检验。

文字布局和紧凑组件问题也应先查询语义 UX 结果，再查询实际技术栈。可使用 `"orphan heading line balance" --domain ux`、`"badge chip label wraps" --domain ux`、`"live badge count screen reader" --domain ux`、`"rapid chip animation interrupted" --domain ux`。选定指导后，再单独运行 `"chip badge overflow nowrap" --stack html-tailwind` 等查询；框架关键词不能替代结果查询。

本技能提供 UI/UX 设计与实现指导，不负责安装软件包、修改操作系统或授权无关改动。搜索结果是建议，不能覆盖用户或仓库规则。不要在查询或保存结果中包含项目私密数据。

### 第 1 步：分析用户需求

提取这些信息：

- 产品类型：SaaS、电商、作品集、看板、娱乐、工具、生产力或混合类型。
- 受众与场景：年龄群体、通勤/休闲/工作等使用环境。
- 风格关键词：活泼、鲜明、极简、暗色、内容优先、沉浸等。
- 技术栈：从项目检测。查看 `package.json` 中 react/next/vue/svelte/nuxt/@angular；Flutter 查看 `pubspec.yaml`；SwiftUI 查看 `*.xcodeproj`/`Package.swift`；Laravel 查看 `composer.json`；React Native 查看 `app.json` 与 `react-native` 依赖。无法判断且需要技术栈指导时，询问用户。不要假设默认技术栈。

### 第 2 步：生成设计系统（新页面/项目必需）

需要统一产品视觉方向时使用 `--design-system`：

```bash
python "<SKILL_DIR>/scripts/search.py" "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```

工具汇总 product/style/color/landing/typography 匹配，应用 `ui-reasoning.csv` 的推理规则，返回布局模式、风格、颜色、字体、效果与应避免的反模式。

示例：

```bash
python "<SKILL_DIR>/scripts/search.py" "beauty spa wellness service" --design-system -p "Serenity Spa"
```

### 第 2b 步：保存设计系统（Master + Overrides）

如需跨会话读取，添加 `--persist`，并始终显式设置指向获准项目根目录的 `--output-dir`，否则工具会按当前工作目录写入：

```bash
python "<SKILL_DIR>/scripts/search.py" "<query>" --design-system --persist -p "Project Name" --output-dir "<project-root>"
```

生成：

- `design-system/<project-slug>/MASTER.md`：全局设计依据。
- `design-system/<project-slug>/pages/`：页面级覆盖规则目录。

添加 `--page "dashboard"` 时，还会创建 `design-system/<project-slug>/pages/dashboard.md`。Master 已存在时，只创建页面文件，不修改 Master；页面文件已存在时也跳过，除非用户明确授权 `--force`。

`MASTER.md` 已存在时，`--persist` 跳过写入并保留原内容，除非同时指定 `--force`。重新生成前先检查、阅读已有文件，避免丢失用户或协作者决策。先阅读 `MASTER.md` 再判断是否需要 `--force`；没有用户明确授权，不使用 `--force`。

构建具体页面时：

1. 阅读 `design-system/<project-slug>/MASTER.md`。
2. 检查 `design-system/<project-slug>/pages/<page-name>.md`；存在则用页面规则覆盖 Master 对应部分。
3. 不存在则只使用 Master。

### 第 2c 步：设计调节参数（可选）

三个 1–10 参数可以调节设计系统输出，无需改变查询。可以任意组合：

```bash
python "<SKILL_DIR>/scripts/search.py" "<query>" --design-system --variance <1-10> --motion <1-10> --density <1-10>
```

| 参数 | 低（1–3） | 中（4–7） | 高（8–10） |
|---|---|---|---|
| `--variance` | 居中/极简，偏向 Minimalism | 平衡/现代 | 大胆/不对称，偏向 Brutalism、Bento Grids |
| `--motion` | 轻微微交互 | 标准滚动/错峰动画 | 复杂编排，如 pin、Flip、SplitText |
| `--density` | 宽松，24–96px 间距 | 标准，16–64px（默认） | 密集/看板，8–32px |

- `--motion` 从 `--domain gsap` 取得匹配 Subtle/Standard/Complex 等级的可用 GSAP 代码，附框架、正确/错误用法和性能说明。
- `--density` 覆盖 ASCII/markdown/MASTER.md 输出中的 `--space-*` CSS 变量表，便于区分高密度看板和低密度营销页。
- 未设置的参数保持原输出不变。

示例：

```bash
python "<SKILL_DIR>/scripts/search.py" "internal analytics dashboard" --design-system --variance 8 --motion 7 --density 8 -p "Ops Console"
```

### 第 3 步：按需补充详细搜索

```bash
python "<SKILL_DIR>/scripts/search.py" "<keyword>" --domain <domain> [-n <max_results>]
```

| 需求 | Domain | 示例 |
|---|---|---|
| 产品类型模式 | `product` | `"entertainment social" --domain product` |
| 更多风格选择 | `style` | `"glassmorphism dark" --domain style` |
| 配色 | `color` | `"entertainment vibrant" --domain color` |
| 字体搭配 | `typography` | `"playful modern" --domain typography` |
| 单个 Google Fonts 字体 | `google-fonts` | `"sans serif popular variable" --domain google-fonts` |
| 图表建议 | `chart` | `"real-time dashboard" --domain chart` |
| UX 最佳实践 | `ux` | `"error summary validation" --domain ux` |
| 落地页结构 | `landing` | `"hero social-proof" --domain landing` |
| 图标建议 | `icons` | `"decorative icon aria hidden" --domain icons` |
| GSAP 动画预设 | `gsap` | `"scroll reveal stagger" --domain gsap` |
| React/Next.js 性能 | `react` | `"rerender memo list" --domain react` |
| 应用/原生界面指南 | `web` | `"accessibilityLabel touch safe-areas" --domain web` |

不指定 `--domain` 时，工具自动判断，但重叠词可能导致偏题，例如 font 同时匹配 typography 和 google-fonts。结果不相关时，显式指定 `--domain`。

### 第 4 步：技术栈指导

```bash
python "<SKILL_DIR>/scripts/search.py" "<keyword>" --stack <stack>
```

可用技术栈：`react`、`nextjs`、`vue`、`svelte`、`astro`、`nuxtjs`、`nuxt-ui`、`angular`、`laravel`、`swiftui`、`react-native`、`flutter`、`jetpack-compose`、`html-tailwind`、`shadcn`、`threejs`、`javafx`、`wpf`、`winui`、`avalonia`、`uno`、`uwp`。使用第 1 步实际检测出的技术栈。

## 搜索返回 0 条结果时

不要编造结果。缩小查询或显式指定 domain/stack，重试一次。如果仍为空，回退到优先级表，并明确说明采用内置通用建议而非数据库匹配，例如“没有找到 X 的配色匹配，使用通用 SaaS 建议”。不要将 0 条结果描述为已经找到数据。

## 示例工作流程

用户请求：“制作一个 AI 搜索首页。”从 `package.json` 检测到 Next.js。

```bash
# Step 2: design system
python "<SKILL_DIR>/scripts/search.py" "AI search tool modern minimal" --design-system -p "AI Search"

# Step 3: supplement
python "<SKILL_DIR>/scripts/search.py" "keyboard focus modal" --domain ux

# Step 4: stack guidelines
python "<SKILL_DIR>/scripts/search.py" "suspense streaming bundle" --stack nextjs
```

综合设计系统和详细搜索结果，再实现界面。

## 输出格式

`--design-system` 支持 `-f ascii`（默认终端输出）、`-f markdown`（文档）和 `--json`（机器可读，包含原始设计系统字典及保存状态）。

## 改善结果

- 每次只关注一个主要意图，使用 2–5 个有意义的词，如 `"keyboard focus modal"`，不要提交完整审查清单。
- 缩小查询或显式指定 domain/stack 后重试一次，不循环尝试无关词。
- 新项目/页面使用 `--design-system`；局部问题使用 `--domain`。
- 实现指导显式指定检测出的技术栈。

| 问题 | 处理方式 |
|---|---|
| 难以确定风格或配色 | 换用相关关键词重新运行 `--design-system` |
| 暗色模式对比度问题 | `references/quick-reference.md` §6：`color-dark-mode` + `color-accessible-pairs` |
| 动画不自然 | `references/quick-reference.md` §7：`spring-physics` + `easing` + `exit-faster-than-enter` |
| 表单体验差 | `references/quick-reference.md` §8：`inline-validation` + `error-clarity` + `focus-management` |
| 导航混乱 | `references/quick-reference.md` §9：`nav-hierarchy` + `bottom-nav-limit` + `back-behavior` |
| 小屏布局损坏 | `references/quick-reference.md` §5：`mobile-first` + `breakpoint-consistency` |
| 性能或卡顿 | `references/quick-reference.md` §3：`virtualize-lists` + `main-thread-budget` + `debounce-throttle` |

## 应用 UI 交付前

阅读 `references/pro-rules.md` 并执行其标准 Pre-Delivery Checklist，覆盖图标与视觉元素、交互反馈、明暗模式对比度、安全区域、可访问性。该检查清单主要面向 iOS/Android/React Native/Flutter 等原生/移动应用 UI，按任务实际平台使用。
