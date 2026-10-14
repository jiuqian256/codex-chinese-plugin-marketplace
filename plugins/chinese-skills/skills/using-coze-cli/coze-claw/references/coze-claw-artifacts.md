# claw artifact commands

> **前置条件：** 先阅读 [`../../SKILL.md`](../../SKILL.md) 和 [`coze-claw-message.md`](coze-claw-message.md)。

本文档覆盖普通 session 产物处理。PPT 产物见 [`coze-claw-ppt.md`](coze-claw-ppt.md)。

## 核心区别

| 字段 | 含义 | 处理方式 |
|------|------|----------|
| `file_url` | 可下载或可直接交付的 URL | 可传给 `file download` |
| `file_uri` | 平台内部文件引用 | 不能直接下载，需要先解析 |

Agent 不要猜测 `file_uri` 的公网 URL。

## file download

```bash
coze session file download "<file_url>" --format json
coze session file download "<file_url>" --output-path ./downloads/result.md --format json
```

关键输出：

| 字段 | 含义 |
|------|------|
| `status` | `saved` |
| `path` | 本地保存路径 |
| `filename` | 文件名 |
| `size` | 文件大小 |
| `url` | 原始下载 URL |

如果用户需要在线链接，已有 `file_url` 时可直接返回它。不要只返回本地路径，除非用户明确只需要本机文件。

## 普通文件链路

```text
reply_completed.files[].file_url
  -> coze session file download <file_url>
```

如果回复中只有 `file_uri`：

- 普通回复产物需要先通过 session 文件 URL 解析逻辑或后续命令拿到 `file_url`。
- PPT 类 `file_uri` 交给 [`coze-claw-ppt.md`](coze-claw-ppt.md)。
- 不要直接把 `file_uri` 拼成 URL。

## 上传和下载边界

- 上传本地输入文件给 session message：使用 `coze session message --file` 或正文 `@<path>`。
- 下载 session 回复产物：使用 `coze session file download <file_url>`。
- 对用户交付产物：优先返回在线 `file_url`；如果需要本地落盘，再给出下载后的 `path`。
