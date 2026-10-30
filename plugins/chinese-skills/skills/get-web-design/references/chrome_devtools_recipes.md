# chrome-devtools MCP 操作配方

本文给出从 URL 到 `collected.json + 可选截图` 的精确调用步骤，
所有工具均以 `mcp__chrome-devtools__*` 前缀提供。

最终产物目录：

```
output/<hostname>/design.md
output/<hostname>/shot1.jpg
output/<hostname>/shot2.jpg
output/<hostname>/shot3.jpg
```

`<hostname>` 即 URL 的 host（例如 `platform.moonshot.cn`）。

## 步骤 0：准备工作目录
```bash
mkdir -p output/<hostname>
mkdir -p /tmp/get-web-design/<run-id>     # 仅用于存放中间产物 collected.json
```
- 截图直接落到 `output/<hostname>/`（最终结果之一）。
- `collected.json` 是中间产物，放 `/tmp/...` 即可。

## 步骤 1：打开页面

```
mcp__chrome-devtools__new_page({ url: "<目标 URL>" })
```

等待页面就绪：
```
mcp__chrome-devtools__wait_for({ text: "<页面上出现的关键字>" })
# 或退而求其次：sleep 2 秒
```

## 步骤 2：可选截图（仅限当前模型能读取图片）

> 纯文本模型跳过此步骤。最多 3 张是本 skill 的采集预算；短页面避免重复截图。每次滚动后等待页面稳定再截图。

```
# 截图 1：顶部
mcp__chrome-devtools__evaluate_script({
  function: "() => window.scrollTo({ top: 0, behavior: 'instant' })"
})
mcp__chrome-devtools__take_screenshot({
  format: "jpeg", quality: 70,
  filePath: "output/<hostname>/shot1.jpg"
})

# 截图 2：35%
mcp__chrome-devtools__evaluate_script({
  function: "() => window.scrollTo({ top: Math.round((document.body.scrollHeight - window.innerHeight) * 0.35), behavior: 'instant' })"
})
# 实际等待至少 600ms 并确认页面稳定；空调用不保证等待时间。
mcp__chrome-devtools__take_screenshot({
  format: "jpeg", quality: 70,
  filePath: "output/<hostname>/shot2.jpg"
})

# 截图 3：70%
mcp__chrome-devtools__evaluate_script({
  function: "() => window.scrollTo({ top: Math.round((document.body.scrollHeight - window.innerHeight) * 0.70), behavior: 'instant' })"
})
mcp__chrome-devtools__take_screenshot({
  format: "jpeg", quality: 70,
  filePath: "output/<hostname>/shot3.jpg"
})

# 复位
mcp__chrome-devtools__evaluate_script({
  function: "() => window.scrollTo({ top: 0, behavior: 'instant' })"
})
```

> 若 `take_screenshot` 不支持 `filePath` 参数，使用 base64 返回值由 Bash `echo ... | base64 -d > shot1.jpg` 落盘。

## 步骤 3：注入采集脚本

读取 `assets/collect_design_data.js` 全文，将其包装成立即执行函数：

```
const SCRIPT = readFile('<skill_root>/assets/collect_design_data.js');
mcp__chrome-devtools__evaluate_script({
  function: `() => { ${SCRIPT} }`
})
```

`collect_design_data.js` 末尾自带 `return collectDesignData({ includeCss: true });`，
所以包装层只需 `() => { …全部… }` 即可拿到结构化返回值。

将返回值写入：
```bash
/tmp/get-web-design/<run-id>/collected.json
```

> 返回过大时可缩短 bodyTextSample 等字段后重新序列化，或分块读取完整结果。禁止截断 JSON 字符串；保存后验证 JSON 能解析。

## 步骤 4：准备分析并完成文档

按 `../SKILL.md` 第 2–4 步运行 `--prepare`，由当前 agent 阅读证据并写 `analysis.md`，最后运行 `--analysis`。纯文本模式不传截图参数；视觉模式传入实际可读取的截图。默认英文，中文加 `--language zh`。

工具名、参数和返回结构以宿主实际暴露的 schema 为准；上面的名称是配方示例。若截图工具直接返回图片，使用宿主支持的保存与读取方式，不把图片存在当作已查看。

## 故障兜底

- 截图限流：等待 1 秒重试一次，仍失败则继续 DOM/CSS 分析并说明局限。
- 返回 `[object Object]`：使用 `JSON.stringify` 返回完整 JSON。
- SPA 仍在加载：等待主要内容出现后重新采集。
- 仅关闭本次自行打开的页面，不关闭用户已有页面。
