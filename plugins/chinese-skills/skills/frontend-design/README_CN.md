# frontend-design 中文使用说明

来源：Anthropic 官方 `anthropics/skills` 仓库。

用途：为新页面或现有页面改版确定视觉方向，建立配色、字体、布局与文案原则，再实现并评审界面。适用于品牌网站、落地页、产品页面和应用 UI。

中文译本见 `SKILL_CN.md`；自动加载入口为原版 `SKILL.md`，其英文元数据完整保留。上游此技能目录没有 README，本文件为新增的中文使用说明。许可证保留在 `LICENSE.txt`。

在 Codex 中调用：

```
$frontend-design 请为一个咖啡品牌设计响应式首页，先确定配色、字体和布局，再按项目约定实现。
```

可以补充“请参考此技能目录中的 SKILL_CN.md，并用中文解释设计选择”。这不会把中文文件变成第二个自动加载技能。

说明型技能自身不执行安装命令或自动修改配置。实际页面实现必须遵守项目授权与 write_scope。适合搭配已有的 `build-web-apps:frontend-app-builder` 和新增的 `web-design-guidelines`。
