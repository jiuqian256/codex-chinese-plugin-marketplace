# 模式 C：完全原创 PPT 设计原则

当用户明确要求"不要用模板 / 原创设计 / 简单干净"时走本流程。

## 顶层原则

> **越简单越好。**

模式 C 的存在不是为了让你设计华丽的版式，而是为了在没有模板时也能产出**不丑、不出错、不偷工**的结果。

## 不要做的事

- 不要堆砌装饰：避免边框、阴影、渐变、纹理、icon 集群
- 不要用超过 1 个主色 + 1 个强调色
- 不要把超过 4 个信息点塞一页
- 不要混搭风格（既复古又卡通）
- 不要用奇怪的字体（华文琥珀、隶书、楷体等装饰字体）
- 不要做层级嵌套的"卡片里套卡片"

## 推荐做的事

- 4:3 或 16:9 标准画布
- 大量留白（每个元素离画布边距 ≥ 1.5 cm）
- 一页最多：1 个标题 + 1 个副标 + 3-4 项核心内容
- 主色 1 个 (#1F3A68 / #2C3E50 / #B22222 之类的稳重色)
- 字体：
  - 中文：微软雅黑 / 思源黑体 CN
  - 英文：Inter / Helvetica / Arial
  - 标题加粗，正文常规，不用斜体
- 字号梯度：48-54pt（封面） / 32-40pt（章节标题） / 18-22pt（正文）/ 12-14pt（脚注）
- 颜色对比：纯白底 + 深色文字 / 深色底 + 纯白文字

## 推荐版式（按内容类型）

| 内容类型 | 版式 |
|---|---|
| 封面 | 全屏居中：主标题 + 副标题 + 日期/作者 |
| 目录 | 居中竖排：序号 + 章节名（无图标无装饰） |
| 章节扉页 | 全屏居中：超大序号 + 章节标题 |
| 单一观点 | 居中大字（一句话） |
| 3 个并列要点 | 横向 3 列（图标可选 + 标题 + 1-2 行说明） |
| 5+ 个并列要点 | 改成纵向列表（每行一个） |
| 对比 | 2 列对照（左 / 右）+ 中间分隔线 |
| 时间线 | 横向轴 + 节点 |
| 数据 | 1 个大数字（占页面 50%）+ 解释 |
| 结束 | "感谢聆听 / 欢迎交流" + 联系方式 |

## 代码模板

```python
from pptx import Presentation
from pptx.util import Cm, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()
prs.slide_width = Cm(33.87)   # 16:9
prs.slide_height = Cm(19.05)

PRIMARY = RGBColor(0x1F, 0x3A, 0x68)
GREY = RGBColor(0x66, 0x66, 0x66)

def add_textbox(slide, text, *, left, top, width, height,
                size_pt=24, bold=False, color=PRIMARY, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(Cm(left), Cm(top), Cm(width), Cm(height))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = "Microsoft YaHei"
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.color.rgb = color
    return tb

blank = prs.slide_layouts[6]  # blank layout

# 封面
s = prs.slides.add_slide(blank)
add_textbox(s, "2026 年度产品规划", left=4, top=7, width=26, height=2.5,
            size_pt=44, bold=True, align=PP_ALIGN.CENTER)
add_textbox(s, "ACME · 产品部 · 2026.05", left=4, top=10, width=26, height=1.2,
            size_pt=18, color=GREY, align=PP_ALIGN.CENTER)

# 3 列要点
s = prs.slides.add_slide(blank)
add_textbox(s, "本季度三大重点", left=2, top=1.5, width=29, height=1.5,
            size_pt=32, bold=True)
for i, (title, body) in enumerate([
    ("用户增长", "新增 200 万 DAU\n留存提升 8 pp"),
    ("商业化", "广告 ROI +20%\n会员转化 +15%"),
    ("效率", "迭代周期减少 30%\n生产事故 0 起"),
]):
    x = 2 + i * 10
    add_textbox(s, title, left=x, top=5, width=8, height=1.5, size_pt=22, bold=True)
    add_textbox(s, body, left=x, top=7, width=8, height=4, size_pt=16, color=GREY)

prs.save("out.pptx")
```

## 何时该提示用户考虑用模板

如果用户的需求是：
- 需要颜色丰富 / 插画风 / 漂亮的视觉
- 需要图标 / 装饰元素
- 需要展示给客户 / 领导（要"够格"）

那么**主动建议**：

> "我手头有 21 套精心整理的模板（含党政、商务、教学、答辩、述职等），其中 X 风格 / Y 风格更适合您的场景。要不要先看一下预览图？"

模式 C 是兜底，不是首选。
