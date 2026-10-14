# 编辑图表数据

## 三种"图表"形态

| 形态 | 怎么识别 | 能不能改 |
|---|---|---|
| **原生 PPT 图表** (`shape.has_chart == True`) | python-pptx 能读到 `chart` 对象，包括 series / categories / values | **可以**，用本文方法 |
| **装饰形状组**（环形 / 旗帜 / 进度条 / 箭头流程） | 由 `<p:grpSp>` 或一堆 `<p:sp>` 拼成，没有 chart 对象 | **不能直接改弧长 / 占比**，仅能改伴随的文字。详见 [SKILL.md 编辑铁律 #5](../SKILL.md) |
| **图片图表**（截图 / 嵌入的 .png） | shape_type=PICTURE | **不能改**；要么保留要么整张替换 |

对每个模板，原生图表会在 `detail.json` 的 `data_charts` 数组里列出；装饰形状会通过 `shape_caution_pages` 标记。

## 编辑原生图表

### 在 edits.json 里写

```json
{
  "slide": 8,
  "address": {"shape_id": 12},          // 仅 shape_id，不写 paragraph
  "chart_data": {
    "categories": ["Q1", "Q2", "Q3", "Q4"],
    "series": [
      {"name": "营收", "values": [120, 145, 168, 192]},
      {"name": "利润", "values": [30, 38, 45, 56]}
    ]
  }
}
```

`build_pptx.py` 看到 `chart_data` 字段会调用 python-pptx 的 `chart.replace_data(CategoryChartData)` 替换数据。**注意**：
- 类别数（categories 长度）建议 ≤ detail.json 里的 `max_categories`，超过会挤；少于也可，会变短
- series 数量、类型（柱/线/饼）由模板决定，**不能动态改图表类型**；要换类型请换页面
- 颜色 / 标签字体仍然继承模板

### 编辑后预期效果

- 柱状图 / 折线图 / 饼图 的数据点会按新值重画
- 类别名（X 轴标签 / 饼图扇区标签）会替换
- 图例（legend）跟着 series.name 走
- 图表标题如果是 `<c:title>` 嵌入图表内部，可以通过 `chart_title` 字段单独改

### 不支持的图表操作

- 改坐标轴范围 / 网格线
- 改单个数据点的颜色
- 添加 / 删除 series
- 改图表类型（柱 ↔ 饼）

需要上述变更 → 让用户在 PowerPoint 里直接打开调整，或换一个版式。

## 装饰形状的情况

很多模板的"图表"其实是设计师手绘的形状组合，例如：

- 圆环进度条：两条 `<a:arc>` 拼成
- 旗帜路线图：4 个 `<a:flag>` + 一条 `<a:bezier>` 曲线
- 流程箭头：连续 `<a:rightArrow>` 串
- 柱状图风格的色块：固定高度的 `<a:rect>` 数列

这些**形状不会自动随数据变化**。如果你改了"85%" → "92%"，但环形依然显示 85% 的弧度。

**处理策略**：
- 在 detail.json 里把这页放进 `shape_caution_pages` 并写明 cautions
- 选页时如果数据偏差不大（差异 ≤ 5%），可以容忍
- 偏差大时 → 选另一个版式，或者跟用户说明"这个页面的图形是装饰，无法严格匹配数据"

## 图片图表

如果模板某页放了一张已经渲染好的图表 .png，那只能：

1. 让 AI 用 matplotlib / plotly / 其他方式画一张新图，存成 .png
2. 用 python-pptx 的 `shape.element.getparent().replace(...)` 替换图片关系
3. 这超出本 Skill 的核心范围，复杂度较高；推荐选用别的版式

## 检测当前模板有没有原生图表

```bash
python3 -c "
from pptx import Presentation
p = Presentation('templates/<slug>/template.pptx')
for i, s in enumerate(p.slides, 1):
    for sh in s.shapes:
        if getattr(sh, 'has_chart', False):
            print(f'slide {i} shape {sh.shape_id}: {sh.chart.chart_type}')
"
```
