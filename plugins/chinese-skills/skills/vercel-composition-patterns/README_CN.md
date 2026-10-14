# React 组件组合模式

这是上游 `README.md` 的中文译本，附有本机调用说明。

这是可扩展的 React 组件组合模式资料库。通过复合组件、提升状态和组合内部结构，避免 boolean props 不断膨胀。

## 目录结构

- `rules/`：每条规则一个文件。
- `rules/_sections.md`：分类元数据，包括标题、影响和描述。
- `rules/_template.md`：新规则模板。
- `rules/area-description.md`：单条规则文件的命名示例。
- `metadata.json`：文档元数据，包括版本、组织、摘要。
- `AGENTS.md`：生成的规则汇编文档。

## 规则

### 组件架构（CRITICAL）

- `architecture-avoid-boolean-props.md`：避免添加 boolean props 定制行为。
- `architecture-compound-components.md`：将组件组织为共享 context 的复合组件。

### 状态管理（HIGH）

- `state-lift-state.md`：将状态提升到 Provider。
- `state-context-interface.md`：定义明确的 state/actions/meta context 接口。
- `state-decouple-implementation.md`：将状态管理实现与 UI 解耦。

### 实现模式（MEDIUM）

- `patterns-children-over-render-props.md`：优先使用 children，而非 renderX props。
- `patterns-explicit-variants.md`：创建明确的组件变体。

## 核心原则

1. 组合优于配置：让调用方组合组件，而非不断添加 props。
2. 提升状态：将状态放在 Provider 中，避免封闭在单个组件内部。
3. 组合内部结构：子组件通过 context 获取共享信息。
4. 明确的变体：创建 ThreadComposer、EditComposer，而非带 isThread 的 Composer。

## 创建新规则

1. 将 `rules/_template.md` 复制到 `rules/area-description.md`。
2. 为对应领域选择前缀：组件架构使用 `architecture-`，状态管理使用 `state-`，实现模式使用 `patterns-`。
3. 填写 frontmatter 和正文。
4. 提供清晰示例及解释。

## 影响等级

- `CRITICAL`：基础性模式，防止代码变得不可维护。
- `HIGH`：显著改善可维护性。
- `MEDIUM`：提升代码清晰度的良好实践。

## 本机调用

在 Codex 中输入 `$vercel-composition-patterns`，并说明要设计或审查的组件。详细中文入口见 `SKILL_CN.md`。英文规则及代码示例保持原样。实际修改遵循当前项目批准的 write_scope。
