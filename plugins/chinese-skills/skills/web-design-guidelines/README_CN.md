# web-design-guidelines 中文使用说明

来源：Vercel 官方 `vercel-labs/agent-skills` 仓库。

用途：按 Vercel Web Interface Guidelines 审查界面代码，包括可访问性、表单、交互、布局和用户体验，输出可定位的问题。

中文译本见 `SKILL_CN.md`；英文运行入口为 `SKILL.md`。上游此目录没有 README，本文件为新增使用说明。

在 Codex 中调用：

```
$web-design-guidelines 请审查 src/components 下的 UI，检查键盘操作、焦点、表单和响应式问题，用中文说明发现，并标注文件和行号。
```

上述项目路径只是调用示例，以实际项目为准。

每次使用会从以下地址读取最新规则，需要联网：

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

上游入口提到 WebFetch；Codex 可以使用当前环境等效的网页读取工具。无法获取最新规则时，明确报告限制。此技能不提供自动 WCAG 合规认证，也不授权改动项目范围外文件。
