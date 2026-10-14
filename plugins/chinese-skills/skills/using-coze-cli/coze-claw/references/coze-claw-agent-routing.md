# Agent routing contract

## 路由目标

- `/coze-cli`：显式命中 Coze CLI skill
- `/coze`：`/coze-cli` 的短别名，行为完全一致

## 适用范围

- 此规则适用于所有 Claw 子模块，不只限于 `session message`
- 只要最终会把用户正文转发到 Claw，会消费同一份规范化结果的链路都应遵守
- 当前至少覆盖：
  - 普通消息链路：[`coze-claw-message.md`](coze-claw-message.md)
  - PPT 场景：[`coze-claw-ppt.md`](coze-claw-ppt.md)
  - 播客场景：[`coze-claw-podcast.md`](coze-claw-podcast.md)

## 规范化规则

1. 只移除首个路由 token
2. 保留剩余正文中的所有业务 token
3. 不改写正文中的中间 `/coze-cli`
4. 不吞掉 `@PPT`、`@播客`、文件引用、引号和换行

## 正例

- 输入：`/coze-cli 制作一个介绍潮汕美食的 PPT`
  输出正文：`制作一个介绍潮汕美食的 PPT`
- 输入：`/coze-cli @PPT 制作介绍海南美食的 PPT`
  输出正文：`@PPT 制作介绍海南美食的 PPT`
- 输入：`/coze 制作一个冒泡排序 markdown`
  输出正文：`制作一个冒泡排序 markdown`

## 反例

- 错误：把 `/coze-cli` 原样发给 `coze session message`
- 错误：移除 `@PPT`
- 错误：移除 `@播客`
- 错误：把正文里的 `/coze-cli` 全局替换掉

## 最小验收样例

1. 不带前缀的自然语言，允许模型自行命中 skill，但不保证确定性
2. 带 `/coze-cli` 的请求，必须命中 skill
3. 命中后真正发给 Claw 的 message 不包含 `/coze-cli`
4. 同一规则适用于 `@PPT`、`@播客` 等子模块入口
