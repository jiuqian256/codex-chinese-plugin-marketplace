---
name: gorden-ppt-skill
description: Gorden 中文模板 PPT：使用中文 PPTX 模板或用户自带模板制作幻灯片，保留版式；内置模板限非商业用途。 用 21 套内置中文 PPT 模板（或用户自带的 .pptx 模板）生成与编辑 PowerPoint 演示文稿：只替换文字、不破坏原排版/配色/字号，内置按文本框尺寸的出框检测与同级标题字号一致校验；也支持完全原创的简洁版式。当用户要"做 / 生成 / 制作 / 编辑一份 PPT / 演示文稿 / 幻灯片 / .pptx"，或需要工作汇报、年终与季度总结、述职竞聘、项目复盘、开题答辩、商务提案、教学课件、数据可视化等成品 PPTX 时使用。Use when the user wants to create or edit a PowerPoint / PPT / slides / .pptx deck, pick from built-in templates, or apply their own template without breaking the layout.
license: MIT source; non-commercial templates
---

## 中文名称与用法

**中文名称：** Gorden 中文模板 PPT

**用途：** 使用中文 PPTX 模板或用户自带模板制作幻灯片，保留版式；内置模板限非商业用途。

**调用示例：** 使用 $chinese-skills:gorden-ppt-skill 使用我提供的模板生成 PPT，保留版式和配色。

上游：https://github.com/GordenSun/GordenPPTSkill 。固定快照：`7d4a61cbd8363b92e4a30784f8ca460a0a2b0a33`。原许可随包保留。

技能资源路径以当前加载的 SKILL.md 所在目录为准，不假定用户目录或缓存版本。软件和生成服务凭据由使用者按任务配置。


# gorden-ppt-skill

> **版本** 见同目录 [`VERSION`](./VERSION)。

---

## 市场固定版本

此安装由中文技能市场管理，使用固定上游快照。保留更新工具供明确的更新任务使用，但日常制作 PPT 时不运行自动更新、不覆盖插件缓存。需要更新时通过市场新版本发布。

> **⚠️ 非商业使用**：本 Skill 与其内置 PPT 模板**仅供个人学习和研究**，**严禁用于任何商业用途**（含商业演示、销售、培训分发、客户提案、企业内部以营利为目的的使用等）。模板素材来自第三方设计师作品，二次商用需要获取原作者授权。

## 何时使用本 Skill

当用户的需求满足下列任何一项就调用本 Skill：

- 需要"做一份 PPT / 演示文稿 / 幻灯片"，无论是工作汇报、年终总结、季度复盘、项目提案、述职竞聘、教学课件、开题答辩、读书报告……
- 用户给了文字大纲或一段描述，希望"做成 PPT"
- 用户拿来一份 .pptx 文件，希望"按这个模板做一份新的"
- 用户希望"调整 / 编辑 PPT 的某些文字"，且要求"不破坏排版"
- 用户希望对比多个 PPT 模板，选一个合适的

## 更新机制说明

完整的更新工具有两个脚本：

| 脚本 | 干嘛 | 何时用 |
|---|---|---|
| `scripts/apply_update.py` | **检查 + 应用**（一步到位） | 用户明确请求独立更新时；市场安装使用市场版本更新 |
| `scripts/check_update.py` | 仅检查、不应用，列出会变的文件 | 当你只想预览改了什么、不想立即更新时 |

如果只想先看变化再决定要不要升级：

```bash
python3 scripts/check_update.py     # 列出 added / modified / removed
```

`updates.json` 的 `update_source` 已配置为 `git+https://github.com/GordenSun/GordenPPTSkill.git#main`，开箱即用，无需修改。

## 三种模式

收到用户需求后，先判断走哪种模式：

### 模式 A：从内置模板里挑

**默认走这条路。** 21 套内置模板覆盖了绝大多数中文场景。

1. **读 [`templates/INDEX.md`](./templates/INDEX.md)** ——一份精简清单，列出每套模板的风格、主色、适用场景、页数。
2. **匹配用户输入** —— 把用户描述（场景、风格关键词、所需页面类型、颜色偏好）和每个模板的 intro.md 对比。
3. **选模板的决策规则**：
   - **用户已明确指定模板** → 直接用。
   - **你高度确信只有 1 个模板最合适**（场景 + 风格 + 主色都强匹配，且明显优于其它）→ 可直接用，但开工前一句话告诉用户你选了哪个、为什么，给用户一个否决的机会。
   - **其余所有情况（用户没指定，或你不能完全把握哪个最合适）→ 必须让用户来选**：
     - 用 AskQuestion 提供 **正好 3 个**候选模板，每个附上一句话理由（风格 / 适用场景 / 页数），并**把对应的 `templates/<slug>/preview.png` 一并展示**给用户看图决策。
     - 选项里**始终额外带一个「都不满意，换一批」**。用户选它时，再按匹配度给出**另外 3 个**没出现过的候选（同样附预览图）。可反复换，直到用户选定或候选用尽。
     - 候选都用尽仍不满意 → 询问用户更具体的偏好（风格 / 颜色 / 场景），或转模式 C 原创。
   - ⚠️ 不要在没让用户看预览图的情况下，仅凭模糊匹配就自作主张定一个模板。
4. **拿到目标模板后**：
   - 读 `templates/<slug>/intro.md`（高度浓缩，告诉你这个模板的特性）
   - 读 `templates/<slug>/detail.json`（结构化数据，告诉你每页 / 每个文本位的细节）
   - 按 [模式 A 工作流](./references/workflow.md#mode-a) 选页、写 `edits.json`、跑 `build_pptx.py`

### 模式 B：用户自己带 PPT 模板

当用户提供了 .pptx 文件且明确希望以它作模板时：

1. 把用户的 pptx 当作"未知模板"
2. 用 `scripts/render_slides.py` 把每页渲染成 PNG，再用 `python-pptx` 现场探查每页的 shape / paragraph / run 结构（无需额外脚本）
3. 自己看每页（PNG + shape 输出）：
   - 推断每页是什么角色（封面 / 目录 / 章节扉页 / 内容页 / 结束 / 模板宣传）
   - 推断每页适合放什么内容
   - 跳过模板宣传 / "稻壳儿" / 感谢下载 之类
4. 按 [模式 B 工作流](./references/custom-template-workflow.md) 用 explicit `address` 写 `edits.json` 选页 + 文字替换
5. **不要修改用户模板原文件**；所有改动写到新的 output.pptx

### 模式 C：完全原创（不基于任何模板）

当用户明确要求"原创设计 / 不用模板 / 简单干净的样式"时：

1. **创建尽量简洁的版式** —— 大量留白、对齐严格、装饰极少
2. 单页元素 ≤ 4 个，避免复杂图形 / 图标群组
3. 字体：英文 Arial / Helvetica；中文 微软雅黑 / 思源黑体；标题加粗即可
4. 主色 1 个 + 灰阶 + 白底；不要拼凑多种风格
5. 用 `python-pptx` 直接代码生成，参考 [`references/original-design-guide.md`](./references/original-design-guide.md)

## 编辑铁律（所有模式通用）

1. **不改排版** —— 只改文字。形状的位置、大小、颜色、字体、字号、行距，都不动。
2. **所有占位文字必须替换** —— 模板里的 "Question 1" / "Vivamus..." / "Key Words Here" / "项目名称" 等占位文本都必须用真实内容替换。一份完成的 PPT 里不应出现任何示例占位词。
3. **`max_chars` 是软性参考，不是硬性上限；严禁用省略号截断** —— detail.json 每个 slot 的 `max_chars` / `chars_per_line` / `max_lines` 是按文本框尺寸估算的容量，**仅供参考**，帮助你把握"这格大概能放多少字"。
   - 优先写**自然、完整、精炼**的文字。略微超出通常没关系（容量已留 20% 余量，PPT 文本框本身也有弹性）。
   - **绝对禁止为了凑数而砍掉后半句、在结尾加 `...` / `…` / `等等` 来硬凑长度** —— 被省略号截断的半句话，比轻微超框难看得多，是最差的结果。
   - 真的太长时，按优先级处理：① 用更精炼的措辞**重写**（真正的概括，不是切断）；② 减少要点条数 / 换一个空间更大的版式或页面；③ 实在不行，**宁可让它轻微超出一点，也不要出现省略号**。
   - `build_pptx.py` 的出框检测**只是提示、不阻断**保存。**日常不要加 `--strict`**（它会因超框拒绝保存，从而诱导截断）。`capacity_unknown:true` 的槽测不准，凭目测把握。
4. **数字 / 序号默认不动** —— `editable: false` 的 slot 是装饰性 "01/02/1/2/%" 之类，除非用户明确要求改顺序，否则保持。
5. **图形 / 图表通常无法同步** —— 装饰性的进度条 / 圆环 / 旗帜路径 / 流程箭头是固定形状；改了百分比文字不会改弧长。每个模板 detail.json 里如有这类页面会在 `cautions` 字段列出。
6. **真实数据图表才能改数据** —— 如果某页有 PPT 原生 chart（`shape.has_chart=True`），可以用 `build_pptx.py --chart-data` 同步更新；详见 [`references/chart-editing.md`](./references/chart-editing.md)。
7. **章节名前后呼应** —— 改了目录章节名，对应的分章扉页 + 内容页面包屑文字都要同步改。
8. **封面 / 致谢页按模板能力来，不要硬造** ——
   - 读 `detail.json` 的 `page_roles`，如果 `cover` 数组为空，**直接从第一张内容页开始**，不要拿一张内容页当封面用，更不要从其他模板临时凑一张封面页。
   - 如果 `ending` 数组为空，**直接以最后一张内容页收尾**，不要硬造"感谢聆听"。
   - 同理，`agenda` 空 → 不强加目录；`section_divider` 空 → 不强加分章扉页。
   - 也就是说：**模板有什么角色就用什么角色**，少一个角色就少一页，不要破坏视觉一致性去拼凑。这条规则在 v1.0.3 起对所有模板生效。
9. **同级标题字号必须一致，不要逐处改字号** ——
   - detail.json 顶部有 `type_scale`（字号层级表，level 1 = 最大），每个 slot 标了 `level`。**同一 level 的文字保持模板原字号，不要改字号。**
   - 某处文字偏长时，用**更精炼的措辞重写**来控制长度（见第 3 条），**不要把这一处字号改小**（会破坏同级一致），**也不要截断加省略号**。
   - 选多页拼一份 PPT 时，让各页同 level 的标题用词长度相近，整体才齐整。

## 标准工作流（模式 A）

```bash
# 1. 从 templates/INDEX.md 选定一个模板，例如 minimal-business-summary
TEMPLATE=templates/minimal-business-summary

# 2. 读两个文件
#    - $TEMPLATE/intro.md     -> 模板风格 / 适用场景 / 结构概述
#    - $TEMPLATE/detail.json  -> 每页 / 每个文本位的详细描述

# 3. 自己决定要用哪些页（用 detail.json 的 page.role 和 use_for）
#    生成 edits.json：
#    {
#      "template_slug": "minimal-business-summary",
#      "selected_slides": [1, 2, 3, 5, 7, 9, 10, 12, 13, 14, 16],
#      "edits": [
#        {"slide": 1, "slot_id": "cover_title_cn", "new_text": "2026 年度复盘"},
#        ...
#      ]
#    }

# 4. 跑构建（不要加 --strict：出框检测只作提示，不应阻断；超框宁可轻微超出也别截断加省略号）
python3 scripts/build_pptx.py \
    $TEMPLATE/template.pptx \
    edits.json \
    out/final.pptx \
    --detail $TEMPLATE/detail.json

# 5. （可选）渲染最终 pptx 给用户预览 / 自检（每页一张 PNG）
python3 scripts/render_slides.py out/final.pptx out/renders --dpi 144
```

## 目录结构

```
GordenPPTSkill/
├── SKILL.md               ← 本文件
├── VERSION                ← 当前版本号
├── CHANGELOG.md           ← 人类可读变更日志
├── updates.json           ← 机器可读版本增量索引
├── manifest.json          ← 所有文件的 sha256 与版本归属
├── README.md              ← 仓库概览（用户阅读）
├── scripts/
│   ├── build_pptx.py          # 按 edits.json 选页 + 换字 → 输出 pptx（含出框检测）
│   ├── render_slides.py       # pptx → PDF → 每页 PNG（预览/自检）
│   ├── compute_capacity.py    # 由 template.pptx 计算每个 slot 的容量字段（数据准备）
│   ├── check_update.py        # 检查远端是否有更新
│   ├── apply_update.py        # 增量更新本地文件
│   └── build_manifest.py      # 重建 manifest.json
├── references/
│   ├── workflow.md
│   ├── pptx-edit-schema.md
│   ├── custom-template-workflow.md
│   ├── chart-editing.md
│   └── original-design-guide.md
└── templates/
    ├── INDEX.md
    └── <slug>/
        ├── template.pptx
        ├── intro.md       # 高度浓缩简介
        ├── detail.json    # 详细页面 / slot 数据（含容量字段 + type_scale）
        └── preview.png    # 4 页 2×2 拼接预览图
```

## 关键脚本一句话说明

| 脚本 | 干嘛用 |
|---|---|
| `build_pptx.py` | 按 `edits.json`（选页 + 文字替换）从模板生成最终 pptx；带出框检测，`--strict` 时出框拒绝保存 |
| `render_slides.py` | 把任意 pptx 渲染成每页一张 PNG（用 LibreOffice + pdftoppm），用于预览 / 自检 |
| `compute_capacity.py` | 由 template.pptx 算出每个 slot 的 `chars_per_line/max_lines/max_chars` 等容量字段（自带模板已算好，仅在加新模板时需要） |
| `check_update.py` | 对比本地 VERSION 和远端 updates.json，告诉你要不要更新 |
| `apply_update.py` | 按 updates.json 的 delta 列表只下载变动文件 |
| `build_manifest.py` | 重新计算 manifest.json |

## 字体说明

模板 XML 里大量使用 `微软雅黑`。如果运行环境没有该字体，配合 `~/.config/fontconfig/fonts.conf` 把它别名到本地已安装的字体（推荐顺序：WenQuanYi Micro Hei → DengXian → Noto Sans SC → PingFang SC）。预览图正是用这条 fallback 链渲染的。

最终交给用户的 .pptx 在 PowerPoint / WPS / Keynote 里打开时会自动用宿主机的字体渲染，因此不需要担心字体丢失问题。

## 一些常见误区

- **不要**只改文字不改章节名一致性 —— 改 agenda 必须同步改分章扉页
- **不要**在装饰图上加文字以为是真图表
- **不要**把 lorem ipsum 留在最终 PPT 里
- **不要**为了塞下文字而忽略 `max_chars`
- **不要**修改用户原始模板文件 —— 所有产出都到新文件
- **不要**用本 Skill 做商业项目 —— 见顶部声明
