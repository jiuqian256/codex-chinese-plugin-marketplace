---
name: web-design-guidelines
description: 网页界面规范审查：依据网页界面规范检查 UI、交互、无障碍和设计一致性。 Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".
metadata:
  author: vercel
  version: 1.0.0
  argument-hint: <file-or-pattern>
---

## 中文名称与用法

**中文名称：** 网页界面规范审查

**用途：** 依据网页界面规范检查 UI、交互、无障碍和设计一致性。

**调用示例：** 使用 $chinese-skills:web-design-guidelines 审查这个网页的交互和无障碍问题。

文中的 `<SKILL_DIR>` 指本次加载的 SKILL.md 所在目录；从实际技能路径解析，不假定用户目录、操作系统或插件缓存版本。脚本接收的项目路径和输出路径仍使用当前任务的实际路径。


# Web Interface Guidelines

Review files for compliance with Web Interface Guidelines.

## How It Works

1. Fetch the latest guidelines from the source URL below
2. Read the specified files (or prompt user for files/pattern)
3. Check against all rules in the fetched guidelines
4. Output findings in the terse `file:line` format

## Guidelines Source

Fetch fresh guidelines before each review:

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

Use WebFetch to retrieve the latest rules. The fetched content contains all the rules and output format instructions.

## Usage

When a user provides a file or pattern argument:
1. Fetch guidelines from the source URL above
2. Read the specified files
3. Apply all rules from the fetched guidelines
4. Output findings using the format specified in the guidelines

If no files specified, ask the user which files to review.
