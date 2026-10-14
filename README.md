# 中文技能市场

一个可添加到 Codex 的公开插件市场。市场提供 **中文技能全集（48 项）** 插件，一次安装 48 个独立技能，附中文名称、用途和调用示例。

当前发布标签为 **v1.01**，插件内部版本为 **1.0.1**。

仓库地址：<https://github.com/jiuqian256/codex-chinese-plugin-marketplace>

## 在截图中的入口添加

1. 在 Codex 的 **插件 → 添加 → 添加插件市场** 中，选择从仓库添加，填写：

   ```text
   https://github.com/jiuqian256/codex-chinese-plugin-marketplace
   ```

2. 选择同步，打开 **中文技能市场**，安装 **中文技能全集（48 项）**。
3. 在新聊天中使用技能。若客户端未立即显示新市场，重启客户端后再查看插件目录。

仓库当前为公开状态，其他使用者可以直接添加该地址。如果网络环境无法同步 GitHub，可以使用下方本地解压安装方式。

## 命令行添加

支持插件市场命令的 Codex CLI 可执行：

```powershell
codex plugin marketplace add https://github.com/jiuqian256/codex-chinese-plugin-marketplace --ref main
codex plugin add chinese-skills@chinese-skill-marketplace
```

查看市场和插件：

```powershell
codex plugin marketplace list
codex plugin list --json
```

Git 来源更新后，可以刷新市场，再安装当前版本：

```powershell
codex plugin marketplace upgrade chinese-skill-marketplace
codex plugin add chinese-skills@chinese-skill-marketplace
```

## 压缩包与本地安装

获得压缩包后，先解压到自己选定的目录，然后把**解压后的市场根目录**添加到 Codex。市场根目录内应有 `.agents/plugins/marketplace.json` 和 `plugins/`。

```powershell
codex plugin marketplace add "<解压后的市场根目录>"
codex plugin add chinese-skills@chinese-skill-marketplace
```

如已配置同名 Git 市场，请优先使用现有来源。不要把 ZIP 文件路径当成市场目录。

## 技能范围与用法

- 保留原有 40 个独立技能；`grill-me` 的两个相同副本只保留一份。v1.01 新增 8 个 PPT 与演示技能，共 48 项。
- **不包含 GPT/Codex 自带的系统技能**。
- **不包含已有插件缓存里的技能**；Figma、Remotion 等原有插件另行安装。
- 从独立目录安装的 HyperFrames 系列技能属于本合集；它们仍需要 HyperFrames 运行时及相关外部工具。
- 脚本、素材与参考资料随技能附带。Galaxy 包含 3802 个组件文件。
- 本机安装记录、Python 缓存及凭据文件不包含在分享包中。

完整清单和用途见 [技能目录.md](技能目录.md)，机器可读清单见 [SKILLS.json](SKILLS.json)。

显式调用格式：`$chinese-skills:技能标识`。例如：

```text
使用 $chinese-skills:gsap-scrolltrigger 制作随滚动切换的产品展示页面。
使用 $chinese-skills:galaxy-ui 挑选适合深色页面的发光按钮。
使用 $chinese-skills:kaoqin-tongji 汇总这些个人考勤日报。
使用 $chinese-skills:ui-ux-pro-max 为我的产品查找配色和字体方案。
使用 $chinese-skills:ppt-master 将文档制作成原生可编辑 PPTX。
使用 $chinese-skills:frontend-slides 制作单文件网页幻灯片。
使用 $chinese-skills:dashi-ppt-skill 生成浏览器可编辑 PPT 并导出 PPTX。
```

技能内的 `<SKILL_DIR>` 指实际加载的 SKILL.md 所在目录。助手应从已加载路径解析资源位置；不要直接执行含占位符的示例，也不要假定缓存目录或用户名。

## 外部工具与凭据

安装插件会安装技能指导和附带资源；不会自动安装操作系统软件或替使用者登录第三方服务。

| 用途 | 需要的外部能力 |
|---|---|
| Python 工具 | Python 3；按对应脚本需求使用依赖，APINebula 工具需要 `requests` |
| APINebula 图像生成 | 使用者自己的 `APINEBULA_API_KEY`，以及对应服务的额度 |
| 3D 转换 | 适合输入格式的 Blender、Rhino、3ds Max 等软件及所需许可 |
| 扣子 CLI | Coze CLI 和使用者自己的登录状态 |
| HyperFrames 视频 | HyperFrames CLI、相应运行时与渲染能力；媒体生成服务凭据按任务配置 |
| 图片与 Excel 工作流 | 当前客户端的图片生成或文档能力，以及任务要求的文件处理工具 |
| PPT Master | Python 3.10+ 与技能 requirements.txt 中的依赖；按所选工作流配置图片或语音能力 |
| 网页幻灯片、归藏、HTML PPT Studio | 浏览器；按任务使用 Python、Node.js 或导出工具，普通观看无需 API 密钥 |
| 花叔设计 | 按所选路线使用 Node.js、Python、浏览器和 FFmpeg 等导出工具；生成服务使用本人凭据 |
| Open Slide | Node.js、npm/pnpm；实际演示项目由官方 open-slide CLI 初始化 |
| 大师 PPT | Node.js 20+、npm；PPTX/PDF 导出需要 Chrome/Chromium/Edge |
| Gorden PPT | Python 与 python-pptx；渲染按需使用 LibreOffice 等工具；内置模板仅非商用 |

分享版 APINebula 脚本只读取环境变量，未携带原作者的 API 密钥。没有配置时会在发起请求前给出明确错误。不要把密钥写进技能、Git 仓库或分享压缩包。

APINebula 工具的 Python 依赖列在对应技能的 requirements.txt 中。由使用者在自己选定的 Python 环境里安装；助手执行脚本时应使用同一个 Python 解释器，避免多个 Python 环境混用。

## 验证与许可

在市场根目录运行：

```powershell
python scripts/validate_marketplace.py
```

该检查验证目录、相对路径、48 个技能入口、中文信息、上游来源与许可、组件素材和分享包中常见的凭据形状。它不会调用收费服务，不等于对每个外部软件和 API 的实际业务验收。

## v1.01 新增来源

| 技能 | GitHub 上游 | 用途 |
|---|---|---|
| ppt-master | [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) | 原生可编辑 PPTX、模板和动画 |
| frontend-slides | [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) | 单文件网页幻灯片 |
| guizang-ppt-skill | [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill) | 杂志风和瑞士风网页 PPT |
| huashu-design | [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design) | HTML 原型、幻灯片、动画与设计评审 |
| html-ppt-studio | [HZMLJX/html-ppt-studio](https://github.com/HZMLJX/html-ppt-studio) | 编辑、演示和导出 HTML PPT |
| open-slide | [open-slide/open-slide](https://github.com/open-slide/open-slide) | 基于官方创作指导整理的 Codex 入口 |
| dashi-ppt-skill | [chuspeeism/dashi-ppt-skill](https://github.com/chuspeeism/dashi-ppt-skill) | 多主题 HTML PPT 与 PPTX/PDF 导出 |
| gorden-ppt-skill | [GordenSun/GordenPPTSkill](https://github.com/GordenSun/GordenPPTSkill) | 中文模板 PPTX 与保留版式的文字编辑 |

每项新增技能的固定上游提交、原名称和适配记录见对应目录的 UPSTREAM.json。归藏与大师 PPT 使用 AGPL-3.0；Gorden 的代码和模板采用不同条款，模板限制见原 NOTICE.md，不能把它们用于未经授权的商业场景。

现有技能的上游许可和版权声明保持原样。合集不重新授权第三方内容，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

官方格式参考：[插件打包与市场格式](https://developers.openai.com/plugins/build/plugins)、[CLI 插件命令](https://learn.chatgpt.com/docs/cli/reference#codex-plugin)。
