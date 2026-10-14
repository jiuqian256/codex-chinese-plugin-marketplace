# 标准工作流详解

本文档说明三种模式的具体执行步骤，是 `SKILL.md` 的延伸。

## 通用前置：理解用户需求

不论走哪条路，先抽取下列信息：

| 维度 | 例子 |
|---|---|
| 主题/场景 | 工作总结、开题答辩、述职竞聘、教学课件、商务提案 |
| 主色偏好 | 红色（党政/爱国）、蓝色（商务）、橙色（活泼）、绿色（环保）、黑白（高级） |
| 风格关键词 | 简约、商务、卡通、复古、麦肯锡、扁平、插画、几何 |
| 受众 | 领导、同事、客户、学生、答辩老师 |
| 篇幅 | 5-10 页（短）、15-25 页（中）、30+ 页（长） |
| 数据图表需求 | 有没有真实数据需要可视化 |
| 时间紧迫度 | 是否需要先给预览图让用户确认 |

如果用户没说清楚，先用 1-2 个简短问题搞清楚，再决定模式。

## <a id="mode-a"></a>模式 A：从内置模板挑

### A1. 读 INDEX

```bash
cat templates/INDEX.md
```

INDEX 把所有内置模板按风格分类列出，每个条目带一句 30 字内的特点描述。先按用户输入的"主色 + 风格 + 场景"在 INDEX 里大致缩小候选。

### A2. 读候选模板的 intro.md

```bash
cat templates/<slug>/intro.md
```

intro.md 是高度浓缩简介，包含：
- 一句话定位
- 风格标签 + 排版复杂度
- 主题色（hex）
- 字体
- 适用场景（**故意写得宽泛**，不要被模板原标题局限）
- 包含的页面结构 + 版式类型
- 不要选用的页面

### A3. 决定 / 跟用户确认

- **用户已指定模板** → 直接用。
- **你高度确信唯一最佳**（场景+风格+主色强匹配且明显胜出）→ 可直接用，但先一句话告知选了哪个 + 理由，留否决余地。
- **用户没指定，或你拿不准哪个最合适（默认情形）** → 让用户选：
  - 用 AskQuestion 给 **正好 3 个**候选，每个附一句话理由 + 展示其 `templates/<slug>/preview.png`。
  - 选项里**永远多放一个「都不满意，换一批」**；用户选它就再给**另外 3 个**没出现过的候选（带预览图），可反复换。
  - 候选用尽仍不满意 → 追问更具体偏好，或转模式 C 原创。
- ⚠️ 不要不看预览图就凭模糊匹配自作主张定模板。

### A4. 读 detail.json，选页

```bash
python3 -c "import json; d=json.load(open('templates/<slug>/detail.json')); print(json.dumps([{'n':p['slide_number'],'role':p['role'],'use_for':p['use_for']} for p in d['pages']], ensure_ascii=False, indent=2))"
```

按用户内容规模选页：
- **封面 / 致谢页：按模板能力来** —— 读 `page_roles`：
  - `cover` 非空 → 加一张封面页；`cover` 为空 → **直接从第一张内容页开始**，不要把别的页当封面用
  - `ending` 非空 → 加一张致谢/结束页；`ending` 为空 → **直接以最后一张内容页收尾**，不要硬造"感谢聆听"
- **目录页**：`agenda` 非空时按需选；多章节才有意义；章节数要和你后面要选的章节扉页数一致
- **章节扉页 + 内容页**：`section_divider` 非空时按章节大纲挑；为空就直接列内容页
- **跳过的页面**：`skip_pages` 数组列出的 + 任何 `auto_promo_flag=true` 的页面

⚠️ 简单说："模板有什么角色就用什么角色"。不要为了凑齐"封面 / 目录 / 内容 / 致谢"四段式而从模板里强行挑出一张内容页冒充封面 —— 那会破坏视觉一致性。绝大多数 v1.0.2+ 的内置模板都**只有内容页**，请直接接受这种"纯内容"deck 形态。

把选定页面的原模板编号（1-based）按演示顺序放到 `selected_slides` 数组。

### A5. 写 edits.json

完整 schema 见 [`pptx-edit-schema.md`](./pptx-edit-schema.md)。核心要点：

```json
{
  "template_slug": "<slug>",
  "selected_slides": [1, 2, 3, 5, 7, 9, 10, 12, 13, 14, 16],
  "edits": [
    {"slide": 1, "slot_id": "cover_title_cn", "new_text": "..."},
    {"slide": 2, "slot_id": "agenda_ch1_cn", "new_text": "..."},
    ...
  ]
}
```

约束：
- **每个 editable=true 的 slot 都必须出现在 edits 里**（不留占位文字）
- **`max_chars` 是软性参考、不是硬上限**（中文 1 字=1，英文/数字≈0.5）。尽量靠近容量，但**略微超出没关系**；**严禁为凑数而截断文字、在结尾加 `...` / `…` / `等等`** —— 被省略号截断的半句话比轻微超框难看得多。太长就用更精炼的措辞**重写**，或换更大的版式/页面。
- **同一 `level` 的标题保持原字号，不要逐处改字号**（见 `type_scale`）；靠精炼用词控制长度，不要改字号也不要加省略号。
- **改了 agenda 的章节文字，必须同步改对应分章扉页 / 面包屑**
- editable=false 的 slot（"01"、"02"、"%" 之类）通常不出现在 edits 里
- 构建时务必带 `--detail`。**不要加 `--strict`** —— 出框检测只作提示、不应阻断保存（`--strict` 会因超框拒绝保存，反而诱导截断）。

### A6. 跑构建

```bash
python3 scripts/build_pptx.py \
    templates/<slug>/template.pptx \
    edits.json \
    out/<name>.pptx \
    --detail templates/<slug>/detail.json
```

默认会自动 sibling-lookup detail.json，但显式 `--detail` 更稳。出框检测默认只打印提示、不阻断；`--strict` 仅在你确实想"出框就失败"时才用（日常不建议，会诱导截断）。

### A7. 自检

跑 `render_slides.py` 渲染最终 pptx，目测：
- 没有遗留占位文字
- **没有被省略号截断的半句话**（宁可轻微超框，也不该出现 `...`）
- 文字换行没有明显错乱
- 章节名前后一致
- 顺序符合大纲

发现问题 → 修改 edits.json → 再跑一次。

## 模式 B：用户带 PPT

详见 [`custom-template-workflow.md`](./custom-template-workflow.md)。

## 模式 C：完全原创

详见 [`original-design-guide.md`](./original-design-guide.md)。

## 失败兜底

| 现象 | 处理 |
|---|---|
| `expected_text mismatch` | 模板被改过；放弃 --strict 或重新核对 detail.json 的 current_text |
| `shape_id not found` | 模板被替换了；要么用其他模板，要么重新提取 detail.json |
| 文字溢出 | 看 `max_chars`；缩短文字或换更宽的版式 |
| 字体不一样 | 见 [`SKILL.md` 字体说明](../SKILL.md)，配置 fontconfig 别名 |
| 图表数据没改 | 见 [`chart-editing.md`](./chart-editing.md) |
