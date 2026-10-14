# 第三方来源与变更说明

本仓库整理独立安装的技能，保留原技能所附的许可、版权声明与来源链接；不把所有内容统一改成某个许可证。未附明确许可的技能保留原状态。各技能的原始许可字段及入口哈希记录在 SKILLS.json 中。

- GreenSock 官方 GSAP 技能：<https://github.com/greensock/gsap-skills>，快照 `aed9cfd3277740755f6bfc1155c7aa645403b760`，MIT。原 LICENSE 随每个技能保留。
- Uiverse Galaxy 组件：<https://github.com/uiverse-io/galaxy>，快照 `adbd2adde0a299a3956ea288fb444ec01891ca41`，MIT。原 LICENSE、README 与作者注释保留在组件素材目录。
- frontend-design：原 Apache 2.0 LICENSE.txt 保留在对应技能目录。
- ui-ux-pro-max：原 MIT LICENSE 保留在对应技能目录。
- 其余技能：保留各自 SKILL.md 中的许可字段、随附许可文件和原有来源说明。

分享适配的改动包括：为技能添加中文显示名称、用途和调用示例；调用示例采用插件命名空间；本机技能路径改为从实际加载目录解析；两个相同的 grill-me 副本去重；移除缓存和本机安装记录；APINebula 脚本移除内置用户密钥，改为使用每位使用者自己的环境变量。

这些改动只作用于分享副本，不修改原有独立技能或已有插件。

## v1.01 新增内容

新增来源和固定提交记录在每项技能的 UPSTREAM.json 中，完整保留上游 LICENSE：

- ppt-master：MIT，保留 Hugo He 版权、赞助说明与原有完整性检查脚本；不修改检查脚本或执行门槛。
- frontend-slides：MIT，保留 Zara Zhang 版权与原有配套资源。
- guizang-ppt-skill：AGPL-3.0，保留完整许可，源代码随包公开；新增中文入口信息属于本市场的适配修改。
- huashu-design：MIT，保留原许可、设计资料和媒体素材。
- html-ppt-studio：MIT，保留原许可、运行时和导出脚本。
- open-slide：MIT；Codex 入口基于上游五份创作指导整理，框架运行时仍由官方 CLI 提供。指导与技术参考随包附带。
- dashi-ppt-skill：AGPL-3.0，保留完整许可，源代码随包公开；本市场技能标识为 dashi-ppt-skill，上游标识是 dashi-ppt。
- gorden-ppt-skill：代码采用 MIT；templates/ 中的第三方模板和预览受原 NOTICE.md 的非商用限制。原版权归模板作者，仓库维护者无法授予模板商用权；完整保留该 NOTICE 和模板内作者信息。市场副本采用固定快照，通过市场更新版本，不在日常使用时自动覆盖安装缓存。

本版本将非秘密环境变量示例保存为 env.example；不会分发包含使用者凭据的 .env 文件。除了名称、中文说明、路径和宿主适配外，保持实际实现及所附素材的来源信息。
