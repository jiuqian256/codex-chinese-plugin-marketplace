# 中文技能市场

一个可添加到 Codex 的私有插件市场。市场提供 **中文技能全集（40 项）** 插件，一次安装 40 个独立技能，附中文名称、用途和调用示例。

仓库地址：<https://github.com/jiuqian256/codex-chinese-plugin-marketplace>

## 在截图中的入口添加

1. 仓库所有者在 GitHub 仓库的 Settings → Collaborators 中邀请使用者，给予所需的读取权限。
2. 使用者接受邀请，并在本机登录具有仓库读取权限的 GitHub 账号。
3. 在 Codex 的 **插件 → 添加 → 添加插件市场** 中，选择从仓库添加，填写：

   ```text
   https://github.com/jiuqian256/codex-chinese-plugin-marketplace
   ```

4. 选择同步，打开 **中文技能市场**，安装 **中文技能全集（40 项）**。
5. 在新聊天中使用技能。若客户端未立即显示新市场，重启客户端后再查看插件目录。

私有仓库 URL 只有在使用者已获访问权限时才可同步；仅转发链接不会授予访问权限。网页已登录 GitHub 不一定意味着本机 Git 已完成认证。若客户端同步提示无权限，先完成本机 Git/GitHub 认证，或使用下方本地解压安装方式。

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

- 包含独立技能目录中的 40 个技能；`grill-me` 的两个相同副本只保留一份。
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

分享版 APINebula 脚本只读取环境变量，未携带原作者的 API 密钥。没有配置时会在发起请求前给出明确错误。不要把密钥写进技能、Git 仓库或分享压缩包。

APINebula 工具的 Python 依赖列在对应技能的 requirements.txt 中。由使用者在自己选定的 Python 环境里安装；助手执行脚本时应使用同一个 Python 解释器，避免多个 Python 环境混用。

## 验证与许可

在市场根目录运行：

```powershell
python scripts/validate_marketplace.py
```

该检查验证目录、相对路径、40 个技能入口、中文信息、组件素材和分享包中常见的凭据形状。它不会调用收费服务，不等于对每个外部软件和 API 的实际业务验收。

现有技能的上游许可和版权声明保持原样。合集不重新授权第三方内容，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

官方格式参考：[插件打包与市场格式](https://developers.openai.com/plugins/build/plugins)、[CLI 插件命令](https://learn.chatgpt.com/docs/cli/reference#codex-plugin)。
