# React 组件组合模式（vercel-composition-patterns）

本文是 `SKILL.md` 正文的中文译本；英文元数据、规则标识、路径与 API 名称保留原样。

这些模式用于构建灵活、可维护的 React 组件。通过复合组件、提升状态和组合内部结构，避免大量 boolean props。项目扩展时，人和 AI 都能更容易理解与维护代码。

## 适用场景

- 重构包含大量 boolean props 的组件。
- 构建可复用组件库。
- 设计灵活的组件 API。
- 审查组件架构。
- 使用复合组件或 context providers。

## 按优先级分类

| 优先级 | 分类 | 影响 | 前缀 |
|---|---|---|---|
| 1 | 组件架构 | HIGH | `architecture-` |
| 2 | 状态管理 | MEDIUM | `state-` |
| 3 | 实现模式 | MEDIUM | `patterns-` |
| 4 | React 19 API | MEDIUM | `react19-` |

## 快速参考

### 1. 组件架构（HIGH）

- `architecture-avoid-boolean-props`：用组合表达行为差异，而非继续添加 boolean props。
- `architecture-compound-components`：用共享 context 组织复杂组件。

### 2. 状态管理（MEDIUM）

- `state-decouple-implementation`：只有 Provider 了解状态的具体管理方式。
- `state-context-interface`：定义包含 state、actions、meta 的通用接口，支持依赖注入。
- `state-lift-state`：将状态提升至 Provider，使兄弟组件可以访问。

### 3. 实现模式（MEDIUM）

- `patterns-explicit-variants`：创建明确的变体组件，而非 boolean 模式。
- `patterns-children-over-render-props`：优先使用 children 组合，而非 renderX props。

### 4. React 19 API（MEDIUM）

仅适用于 React 19+。React 18 或更早版本跳过此节。

- `react19-no-forwardref`：上游建议避免 `forwardRef`；以 `use()` 读取 context，取代 `useContext()`。应用前确认项目版本及对应规则中的具体例子。

## 如何使用

阅读单独的规则文件，获取详细解释与代码示例：

```
rules/architecture-avoid-boolean-props.md
rules/state-context-interface.md
```

每个规则文件包含重要性说明、错误示例及解释、正确示例及解释，以及其他背景和参考资料。

## 完整汇编文档

全部展开的规则位于 `AGENTS.md`。此文件是技能内部参考资料，不是用户项目的全局治理入口。
