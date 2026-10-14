---
name: handoff
description: 聊天任务交接：把当前任务的目标、决定、进度和未完成事项整理为可继续执行的交接文档。 Compact the current conversation into a handoff document for another agent to pick up.
metadata:
  argument-hint: What will the next session be used for?
---

## 中文名称与用法

**中文名称：** 聊天任务交接

**用途：** 把当前任务的目标、决定、进度和未完成事项整理为可继续执行的交接文档。

**调用示例：** 使用 $chinese-skills:handoff 把当前任务整理成可交给下一位助手的交接文档。

文中的 `<SKILL_DIR>` 指本次加载的 SKILL.md 所在目录；从实际技能路径解析，不假定用户目录、操作系统或插件缓存版本。脚本接收的项目路径和输出路径仍使用当前任务的实际路径。


Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the temporary directory of the user's OS - not the current workspace.

Include a "suggested skills" section in the document, naming which skills the next agent should call the Skill tool for.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
