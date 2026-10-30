# 环境准备

无需额外配置 API Key、服务地址或模型。分析由运行 skill 的当前 agent 完成；这不改变宿主 AI 工具自身的账号、订阅或计费要求。

## 浏览器

使用已连接、支持导航与执行页面 JavaScript 的浏览器工具，默认是 chrome-devtools MCP。没有该工具时，可使用宿主的等价浏览器能力并按其真实 schema 调用。

Claude Code 配置示例：

```bash
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest
```

也可在宿主 MCP 配置中添加：

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest"]
    }
  }
}
```

重新连接后确认能导航页面并运行采集 JavaScript。截图和图片读取能力仅在视觉模式需要；没有视觉能力也能正常分析 DOM/CSS。如果完全没有浏览器脚本执行能力，需先连接浏览器，不能用猜测代替实测。

## Python

Python ≥ 3.9，仅使用标准库，无需 pip 安装或虚拟环境。

## 升级说明

旧版 `WEB_DESIGN_API_KEY`、`WEB_DESIGN_BASE_URL`、`WEB_DESIGN_MODEL` 不再读取，`--api-key`、`--base-url`、`--model` 参数已移除。原来的单次外部 API 调用改为 `--prepare` → 当前 agent 写分析 → `--analysis`。用户仍只需向 agent 提供 URL。
