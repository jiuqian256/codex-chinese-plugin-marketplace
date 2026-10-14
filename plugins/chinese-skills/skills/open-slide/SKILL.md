---
name: open-slide
description: Open Slide React 演示框架：创建、编辑或导出使用 open-slide 的 React 幻灯片，处理主题、设计系统、演讲备注、页面揭示、转场和批注。用户明确提到 open-slide 或要基于该框架制作演示时使用。
license: MIT
---


## 中文名称与用法

**中文名称：** Open Slide React 演示框架

**用途：** 基于 open-slide 上游指导创建和编辑 React 幻灯片，处理主题、讲稿和页面动画。

**调用示例：** 使用 $chinese-skills:open-slide 用 open-slide 创建带演讲者备注的产品演示。

上游：https://github.com/open-slide/open-slide 。固定快照：`4081bf973db1c4b81b2772fafa66f93004c98bde`。原许可随包保留。

技能资源路径以当前加载的 SKILL.md 所在目录为准，不假定用户目录或缓存版本。软件和生成服务凭据由使用者按任务配置。

# Open Slide React 演示框架

这是基于官方 open-slide 框架附带指导整理的 Codex 入口。上游没有单独名为 open-slide 的 SKILL.md；本入口把五份指导作为按需阅读的参考，未把框架本身冒充成技能包。

## 使用流程

1. 检查当前项目是否已有 open-slide。新项目可以按用户指定目录运行 `npx @open-slide/cli init <项目名>`，然后在该项目中使用 npm 或 pnpm。不要在技能安装目录创建演示项目或安装依赖。
2. 创建新演示先读 [create-slide](references/upstream/create-slide.md)，涉及任何 React 页面内容再读 [slide-authoring](references/upstream/slide-authoring.md)。文件位置、画布、讲稿、设计令牌和动画以技术参考为准。
3. 创建可复用主题时读 [create-theme](references/upstream/create-theme.md)；处理检查器批注时读 [apply-comments](references/upstream/apply-comments.md)；用户说“当前页”时先读 [current-slide](references/upstream/current-slide.md)。
4. 上游指导中的 AskUserQuestion、Bash 和 Claude 专用界面名称，对应当前宿主提供的问答、终端和浏览器能力。结合用户已给的信息询问缺失内容；不可调用不存在的工具。
5. 本技能的 primitive 参考位于 references/ 下。上游文中“slide-authoring 技能”在本包中指上述技术参考，不要求额外安装同名技能。
6. 修改后在实际项目中验证浏览器展示、窄屏适配、键盘导航和所需导出功能。可用 `pnpm dev` 预览，构建和导出命令以项目当前脚本为准。

## 技术参考

- [设计系统](references/design-system.md)
- [图片与素材](references/assets.md)
- [字体](references/webfonts.md)
- [页码](references/page-numbers.md)
- [分步揭示](references/steps.md)
- [页面转场](references/transitions.md)
- [Morph 动画](references/morph.md)

需要 Node.js 和 npm/pnpm；实际项目的 React、Vite 及 open-slide 运行时由官方 CLI 初始化。技能安装不自动生成项目或登录部署服务。
