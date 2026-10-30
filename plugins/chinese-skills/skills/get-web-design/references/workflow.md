# 完整工作流

```text
URL → 浏览器执行 collect_design_data.js → collected.json
    → 支持图片且能够读取时，额外截图并查看（最多 3 张）
    → Python --prepare → analysis-input.md
    → 当前 agent 阅读证据并撰写 → analysis.md
    → Python --analysis → 校验与拼装 → design.md
```

## 证据准备

采集对象包含 `meta`、`domSnapshot`、`engineeredCssEvidence`。DOM 提供标题、导航、CTA、landmark、正文样本及标志性模块候选；CSS 采样提供选择器、元素角色、矩形、字体、颜色、盒模型与动效声明。原始 JSON 必须完整，不要截断序列化字符串。

`--prepare` 将 DOM、`design_document.py` 提取的 `designTokens`/`tokenEvidence` 和 `css_evidence.py` 压缩的 CSS 摘要写入 `analysis-input.md`，附带当前语言的分析要求。截图以本地文件路径列出，不编码、不上传、不调用外部模型。

## 分析分支

视觉能力由当前宿主实际可用的图片输入/读取能力决定，Python 不探测模型。能查看截图时结合截图；不能查看、能力未知或截图失败时不传 `--screenshots`，基于 DOM/CSS 完成同样八节正文，并在 Overview 标注未检查截图。若部分截图失败，仅使用实际看过的其余图片，说明覆盖范围。

精确规范值只引用 designTokens；CSS 汇总属于启发式证据。保留透明度、零圆角和同一元素的排版组合。CSS 动效声明不能证明运行表现，DOM 中的图片链接不能证明图像内容。推断要标注。

## 拼装

`--analysis <analysis.md>` 接收当前 agent 写好的正文，用原始 collected.json 重新提取 token，校验八个 H2 的顺序、唯一性、内容及禁止代码块的要求，然后写出：

1. 实测 token YAML frontmatter（version: alpha）及使用说明。
2. 八节分析正文及实施检查。
3. Token evidence 和 Evidence Appendix。

失败时返回非零状态，不覆盖原 design.md。最终目录包含 collected.json、analysis-input.md、analysis.md、design.md，视觉模式另有 1–3 张截图。准备成功只代表证据已整理，必须完成分析与拼装才能向用户报告完成。

## 排查

| 现象 | 处理 |
|---|---|
| 页面未加载或登录墙 | 等主要内容加载或报告访问限制，再采集 |
| CSS 缺失或样本过少 | 检查采集返回值，重新采集；仍不足则明确证据局限 |
| 无法截图或读取图片 | 不传截图，重新准备并使用 DOM/CSS 分析 |
| 正文校验失败 | 按错误修正八节正文，重新拼装 |
