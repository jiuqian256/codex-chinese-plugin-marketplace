# 第三方来源与变更说明

本仓库整理独立安装的技能，保留原技能所附的许可、版权声明与来源链接；不把所有内容统一改成某个许可证。未附明确许可的技能保留原状态。各技能的原始许可字段及入口哈希记录在 SKILLS.json 中。

- GreenSock 官方 GSAP 技能：<https://github.com/greensock/gsap-skills>，快照 `aed9cfd3277740755f6bfc1155c7aa645403b760`，MIT。原 LICENSE 随每个技能保留。
- Uiverse Galaxy 组件：<https://github.com/uiverse-io/galaxy>，快照 `adbd2adde0a299a3956ea288fb444ec01891ca41`，MIT。原 LICENSE、README 与作者注释保留在组件素材目录。
- frontend-design：原 Apache 2.0 LICENSE.txt 保留在对应技能目录。
- ui-ux-pro-max：原 MIT LICENSE 保留在对应技能目录。
- 其余技能：保留各自 SKILL.md 中的许可字段、随附许可文件和原有来源说明。

分享适配的改动包括：为技能添加中文显示名称、用途和调用示例；调用示例采用插件命名空间；本机技能路径改为从实际加载目录解析；两个相同的 grill-me 副本去重；移除缓存和本机安装记录；APINebula 脚本移除内置用户密钥，改为使用每位使用者自己的环境变量。

这些改动只作用于分享副本，不修改原有独立技能或已有插件。
