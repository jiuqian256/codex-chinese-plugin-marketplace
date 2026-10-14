# `edits.json` / `detail.json` Schema 详解

本文件定义两套结构化数据的字段含义，是上下游 AI 都要遵守的契约。

## detail.json （由模板维护者写）

每套模板对应一份 detail.json。所有字段必填，除非标记 *(可选)*。

```jsonc
{
  "$schema": "ppt-template-detail/v1",
  "slug": "minimal-business-summary",                // 文件夹名，url-safe
  "name": "简约商务总结汇报",                          // 人类可读名
  "source_pptx": "template.pptx",                    // 同目录下的 pptx 文件名
  "slide_count": 16,                                 // 原 pptx 总页数
  "slide_size_cm": [33.87, 19.05],                   // 画布宽 / 高
  "aspect": "16:9",
  "style": "minimalist-business",                    // 风格标签 slug
  "theme_colors": ["#485275", "#44546A", "#E7E6E6", "#FFFFFF"],
  "fonts": {"cn": "微软雅黑", "en": "Arial"},

  "editing_rules": [                                 // 强约束，编辑端必须遵守
    "保留所有形状的位置 / 大小 / 字号 / 字体 / 颜色，只替换 run 文本。",
    "..."
  ],

  "skip_pages": [],                                  // 1-based slide 编号；模板自带的宣传 / 介绍页放这里
  "shape_caution_pages": [15],                       // 该页装饰图形（环形 / 旗帜 / 进度条）不会随文字同步变化
  "data_charts": [                                   // 该模板里的原生 PPT 图表
    {"slide_number": 8, "shape_id": 12, "chart_type": "BAR", "max_categories": 6,
     "series_count": 2, "guidance": "..."}
  ],

  "page_roles": {                                    // 索引：哪些页面是某种角色
    "cover": [1],
    "agenda": [2],
    "section_divider": [3, 7, 10, 13],
    "content": [4, 5, 6, 8, 9, 11, 12, 14, 15],
    "ending": [16]
  },

  "pages": [                                         // 每一页一个 entry
    {
      "slide_number": 1,                             // 1-based 编号
      "role": "cover",                               // 角色（cover / agenda / section_divider / content / ending / template_promo）
      "layout": "中央对齐的英文副标 + 中文主标，外加四角细线方框装饰。",
      "use_for": "演示文稿封面",                       // 该页推荐的用途
      "cautions": ["..."],                           // (可选) 用本页时的注意事项
      "preview_slot_in_2x2": "左上",                   // (可选) 该页在 preview.png 中的位置（左上/右上/左下/右下/null）
      "text_slots": [
        {
          "slot_id": "cover_title_en",               // 全局稳定 ID，AI 用它定位文本
          "role": "封面英文副标",                       // 该 slot 的语义
          "position": "中部居中",                       // 大致方位（顶部/中部/底部 × 左侧/居中/右侧）
          "address": {                               // 物理寻址：python-pptx 用它定位
            "shape_id": 46,                          // 形状 ID
            "paragraph": 0,                          // 段落索引（0-based）
            "run": 0                                 // (可选) run 索引；不写则整段替换并保留 run0 格式
          },
          "current_text": "Rice Husk",               // 原文本，用于 sanity check
          "max_chars": 30,                           // 推荐最大字符数（超出会换行 / 截断）
          "language": "en",                          // (可选) 语言提示
          "editable": true,                          // false 表示装饰序号 / 占位字符 / 不建议改的内容
          "guidance": "1-3 个英文单词点题，..."          // 给上层 AI 的提示
        }
      ]
    }
  ]
}
```

### address 取址规则

| 形式 | 含义 |
|---|---|
| `{"shape_id": 46, "paragraph": 1, "run": 0}` | 精确到一个 run。改它时其他 run 不动。 |
| `{"shape_id": 46, "paragraph": 1}` | 整段替换：新文本写入 run 0，其他 run 清空。run 0 的字体 / 颜色 / 字号被保留。 |

> **不支持** 跨段 / 跨形状的复合 slot。如果一个语义概念被切到多段，请拆成多个 slot_id。

### slot_id 命名规范

- 半角字母 + 数字 + 下划线
- 全局唯一在同一 detail.json 里
- 推荐风格：
  - 有语义角色用 `cover_title_cn`、`p4_item1_title`
  - 没语义角色用脚手架生成的 `s4_sh38_p0r0`

## edits.json （由编辑端 AI 写）

```jsonc
{
  "$schema": "ppt-edit-spec/v1",                     // (可选)
  "template_slug": "minimal-business-summary",
  "selected_slides": [1, 2, 3, 5, 7, 9, 10, 12, 13, 14, 16],
  "edits": [
    // 方式一：通过 slot_id（推荐，需要 --detail）
    {"slide": 1, "slot_id": "cover_title_cn", "new_text": "2026 年度汇报"},

    // 方式二：通过显式 address（不需要 detail.json）
    {
      "slide": 9,
      "address": {"shape_id": 9, "paragraph": 0, "run": 0},
      "expected_text": "METHOD",
      "new_text": "PILLARS"
    }
  ]
}
```

字段：

- `template_slug` *(可选)*：模板标识，仅用于审计。
- `selected_slides`：1-based slide 编号，按演示顺序写。**未被选的页会被删除。**
- `edits`：每个元素描述一处替换：
  - `slide`：要改的是**原模板**里的哪一页（1-based）。
  - `slot_id` 或 `address`：二选一。
  - `expected_text` *(可选)*：sanity check，--strict 模式下不匹配会报错。
  - `new_text`：替换为的新文本（必填）。
  - `chart_data` *(可选)*：见 [`chart-editing.md`](./chart-editing.md)。

### 强约束

1. **顺序无关**：edits 的顺序不影响结果。同一 slot 出现多次时以最后一条为准。
2. **覆盖所有 editable 字段**：editable=true 的 slot 必须在 edits 里出现（除非整页被丢弃）。否则会留下占位文字。
3. **不要碰 editable=false 的 slot**，除非用户明确要求。

## 兼容性策略

- detail.json 文件名 = `detail.json`，schema 字段 = `ppt-template-detail/v1`
- 未来 v2 出现时，老的 v1 detail.json 必须仍然能被 build_pptx.py 解析
- 字段添加按"可向后兼容默认值"原则
