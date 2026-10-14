# ui-ux-pro-max 中文使用说明

来源：社区维护的 `nextlevelbuilder/ui-ux-pro-max-skill`，不是 OpenAI、Anthropic 或 Vercel 官方技能。

用途：为 Web、移动和桌面界面查询设计资料；生成颜色、字体、间距、布局等设计系统建议；审查交互、可访问性、响应式和技术栈实现。支持 React、Next.js、HTML+Tailwind、shadcn 等。

完整中文入口说明见 `SKILL_CN.md`。自动加载入口 `SKILL.md` 保留英文 frontmatter。原版入口保存在 `SKILL_UPSTREAM.md`。上游技能子目录没有 README，本文件为本机新增使用指南。完整项目中文介绍可见上游 `README.zh.md`：

https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/477bcb28c9812b385cb51a4605ddf30d7b2266e2/README.zh.md

## 本机调用

```
$ui-ux-pro-max 请为电商后台建立设计系统，结合项目的 React、Tailwind 和 shadcn，重点检查移动端、表单反馈和可访问性。请用中文输出。
```

需要脚本搜索时，使用已适配的绝对路径：

```powershell
python "<SKILL_DIR>/scripts/search.py" "keyboard focus modal" --domain ux
python "<SKILL_DIR>/scripts/search.py" "responsive grid mobile" --stack html-tailwind
python "<SKILL_DIR>/scripts/search.py" "ecommerce dashboard modern" --design-system -p "Shop Admin"
```

Python 3.x 即可，无第三方包和 API key。若 `python` 不可用，可尝试 `python3` 或 `py -3`。本机已检测到 Python，无需额外安装。资料主要为英文，内部检索建议使用简短英文关键词，再让 AI 用中文解释结果。中文化的是说明文档，不是 CSV 搜索库或程序输出。

## 兼容适配与保存

原入口使用 `${CLAUDE_PLUGIN_ROOT}/.claude/skills/ui-ux-pro-max/scripts/search.py`。安装入口只替换为本机脚本路径，不翻译代码、命令参数或变量。Python 源码和数据文件保持上游原样。

普通搜索及未加 `--persist` 的设计系统生成只输出结果。添加 `--persist` 会写出 `design-system/<project-slug>/MASTER.md` 和页面覆盖文件，必须指向当前已批准的 write_scope，并显式设置 `--output-dir`。已有文件默认跳过。只有明确授权后才可使用 `--force`。

详细资料仍保留英文：`references/quick-reference.md`、`references/pro-rules.md`、`data/` 和 `scripts/`。它们不是本次逐文件翻译的范围。
