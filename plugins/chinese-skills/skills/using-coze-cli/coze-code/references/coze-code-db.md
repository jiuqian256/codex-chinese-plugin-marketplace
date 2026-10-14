# code db commands

> **前置条件：** 先阅读 [`../../SKILL.md`](../../SKILL.md) 了解认证、全局参数和安全规则。

数据库管理命令索引。涵盖 Coze 空间中 Supabase 数据库的创建、查询、类型生成、Schema 导出、回滚和删除操作。

## 命令导航

| 文档 | 命令 | 说明 |
|------|------|------|
| 本文档 | `coze code db create` | 创建新数据库 |
| 本文档 | `coze code db list` | 列出空间中的数据库 |
| 本文档 | `coze code db get --db-id <id>` | 查看数据库详情（含连接信息） |
| 本文档 | `coze code db query --db-id <id> --sql "..."` | 执行 SQL 查询 |
| 本文档 | `coze code db gen-types --db-id <id>` | 生成 TypeScript 类型 |
| 本文档 | `coze code db dump --db-id <id>` | 导出数据库 Schema 或数据 |
| 本文档 | `coze code db rollback --db-id <id> --timestamp <ts> --confirm` | 回滚数据库到指定时间点 |
| 本文档 | `coze code db status --db-id <id>` | 查看数据库状态和回滚信息 |
| 本文档 | `coze code db delete --db-id <id> --confirm` | 删除数据库（不可逆） |

### 共享参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--space-id <spaceId>` | 否 | 空间 ID（可选，默认从上下文读取） |

> 所有 `db` 子命令都支持 `--space-id`，若未传入则从 `coze space use` 设置的上下文中读取。缺少空间 ID 时会报 `MISSING_SPACE_ID` 错误。

---

## db create

在当前空间中创建新的 Supabase 数据库。数据库名称和凭据自动生成。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--space-id <spaceId>` | 否 | 空间 ID（默认从上下文读取） |

### 推荐命令模板

```bash
# 创建数据库
coze code db create --format json
```

### 返回值

`--format json` 时返回：

| 字段 | 说明 |
|------|------|
| `database_id` | 创建的数据库 ID |
| `database_url` | 数据库连接 URL |
| `status` | 数据库状态（`active` / `creating`） |
| `database_env` | 环境（`dev` / `prod`） |
| `created_at` | 创建时间 |

### 坑点

- 创建后数据库可能处于 `creating` 状态，需等待变为 `active` 后才能执行 SQL 和生成类型。
- 空间有数据库配额限制，超出时报 `DB_QUOTA_EXCEEDED`，需先删除不用的数据库。

---

## db list

列出当前空间中的所有数据库。支持游标分页。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--space-id <spaceId>` | 否 | 空间 ID（默认从上下文读取） |
| `--limit <limit>` | 否 | 每页数量（1-100，默认 20） |
| `--cursor <cursorId>` | 否 | 分页游标 |
| `--all` | 否 | 获取所有数据库（自动翻页） |
| `--max-pages <maxPages>` | 否 | 文本模式下最大翻页数（默认 10） |

### 推荐命令模板

```bash
# 列出数据库
coze code db list --format json

# 获取所有数据库（自动翻页）
coze code db list --all --format json

# 分页查询
coze code db list --limit 5 --cursor <cursorId> --format json
```

### 返回值

返回数据库数组，每项包含：

| 字段 | 说明 |
|------|------|
| `database_id` | 数据库 ID |
| `name` | 数据库名称 |
| `status` | 状态（`active` / `creating`） |
| `database_env` | 环境（`dev` / `prod`） |
| `created_at` | 创建时间 |

> JSON 模式下还会返回 `next_cursor_id` 用于翻页。

---

## db get

获取数据库详情，包括连接 URL 和凭据信息。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--db-id <dbId>` | 是 | 数据库 ID |
| `--space-id <spaceId>` | 否 | 空间 ID（默认从上下文读取） |

### 推荐命令模板

```bash
# 查看数据库详情
coze code db get --db-id <databaseId> --format json
```

### 返回值

`--format json` 时返回：

| 字段 | 说明 |
|------|------|
| `database_id` | 数据库 ID |
| `database_name` | 数据库名称 |
| `database_url` | PostgreSQL 连接 URL |
| `supabase_url` | Supabase 项目 URL |
| `super_user` | 超级用户名（pg-meta 认证用） |
| `super_user_password` | 超级用户密码（pg-meta 认证用） |
| `service_role_key` | Supabase service role 密钥 |
| `anon_key` | Supabase 匿名密钥（用于 PostgREST 访问） |
| `status` | 状态 |
| `database_env` | 环境 |
| `created_at` | 创建时间 |

> `database_url`、`super_user` / `super_user_password`、`service_role_key` 和 `anon_key` 是敏感信息，仅在 `db get` 中返回，用于应用连接和 CLI 内部操作。
>
> **文本模式（默认）下凭据会脱敏展示**（密码/密钥只保留前 4 位，连接串只遮蔽密码段）；需要完整凭据（如写 `.env`）时必须用 `--format json`，并把输出重定向到文件，不要回显到日志。
>
> ⚠️ **安全例外**：根 `SKILL.md` 安全规则要求"禁止输出密钥到终端明文"，而 `db get` 是该规则的**受控例外**——它必然返回凭据。使用时请：
> - 用 `--format json` 把输出**重定向到文件**（如 `> .env.local`），不要直接回显到日志或贴给最终用户；
> - 仅在需要凭据的工作流（写 `.env`、初始化连接）中调用，其余场景改用 `db list` / `db status`（不含凭据）。

---

## db query

在数据库上执行 SQL。支持内联 SQL、文件输入和 stdin 管道。危险操作需 `--confirm` 确认。

### 核心坑点（最高优先级标注）

**危险 SQL（DROP、TRUNCATE、`ALTER TABLE`、无 WHERE 的 DELETE/UPDATE）必须加 `--confirm`，否则在 JSON 模式下报错，在文本模式下弹出交互确认。**（注意：`ALTER TABLE` 虽为 `warning` 级，但同样被判为 dangerous，需要 `--confirm`。）

```bash
# 正确 ✅
coze code db query --db-id <id> --sql "DROP TABLE old_data" --confirm

# 错误 ❌（JSON 模式下会报 DB_SQL_DANGEROUS 错误）
coze code db query --db-id <id> --sql "DROP TABLE old_data"
```

### SQL 输入优先级

1. `--sql`（内联 SQL，最高优先级）
2. `--file`（从文件读取）
3. stdin 管道输入

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--db-id <dbId>` | 是 | 数据库 ID |
| `--sql <sql>` | 否 | 内联 SQL（最高优先级） |
| `--file <path>` | 否 | SQL 文件路径 |
| `--confirm` | 否 | 确认执行危险 SQL |
| `--space-id <spaceId>` | 否 | 空间 ID（默认从上下文读取） |

> `--sql`、`--file`、stdin 三者必须提供至少一个，否则报错。

### 推荐命令模板

```bash
# 执行内联 SQL
coze code db query --db-id <id> --sql "SELECT * FROM users LIMIT 10" --format json

# 执行 SQL 文件
coze code db query --db-id <id> --file ./query.sql --format json

# 通过 stdin 管道输入
echo "SELECT 1" | coze code db query --db-id <id> --format json

# 执行危险 SQL（需确认）
coze code db query --db-id <id> --sql "DROP TABLE old_data" --confirm --format json
```

### 返回值

`--format json` 时返回：

| 字段 | 说明 |
|------|------|
| `result` | 查询结果数组（SELECT） |
| `rows_affected` | 影响行数 |
| `command` | SQL 命令类型（`SELECT` / `DROP` / `INSERT` 等） |
| `warnings` | 安全警告（危险操作时非空） |

### 危险 SQL 检测规则

| 级别 | 模式 | 说明 |
|------|------|------|
| `critical` | `DROP TABLE/INDEX/SCHEMA/...` | 永久删除数据库对象 |
| `critical` | `TRUNCATE` | 清空表所有数据 |
| `critical` | `DELETE FROM` 无 WHERE | 删除所有行 |
| `critical` | `UPDATE ... SET` 无 WHERE | 更新所有行 |
| `warning` | `ALTER TABLE` | 可能导致数据丢失 |

> 检测会先剥离 SQL 注释（`--` 和 `/* */`）再匹配，避免误判。

---

## db gen-types

从数据库 Schema 生成 TypeScript 类型定义。使用 PostgREST OpenAPI 接口获取 Schema 信息。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--db-id <dbId>` | 是 | 数据库 ID |
| `--output <path>` | 否 | 输出文件路径（默认 `types/database.ts`） |
| `--include-schema <name>` | 否 | Schema 名称（可多次指定，默认 `public`） |
| `--space-id <spaceId>` | 否 | 空间 ID（默认从上下文读取） |

### 推荐命令模板

```bash
# 生成 public schema 的类型
coze code db gen-types --db-id <id> --format json

# 指定多个 schema
coze code db gen-types --db-id <id> --include-schema public --include-schema auth --format json

# 自定义输出路径
coze code db gen-types --db-id <id> --output src/types/db.ts --format json
```

### 返回值

`--format json` 时返回：

| 字段 | 说明 |
|------|------|
| `output_path` | 生成的文件路径 |
| `schemas` | 已生成类型的 schema 列表 |

### 前置条件

- 数据库状态必须为 `active`
- 数据库必须有 `supabase_url` 和 `anon_key`（PostgREST 依赖）

### 坑点

- 生成的文件头部包含 `Auto-generated by coze code db gen-types` 注释，不要手动编辑。
- 数据库处于 `creating` 状态时无法生成类型，需等待 `active`。

---

## db dump

导出数据库 Schema（DDL）或数据为 SQL 文件。使用 pg-meta API 查询 information_schema。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--db-id <dbId>` | 是 | 数据库 ID |
| `--output <path>` | 否 | 输出文件路径（默认 `db/schema.sql`） |
| `--schema-only` | 否 | 仅导出 Schema（默认行为） |
| `--data-only` | 否 | 仅导出数据 |
| `--include-schema <name>` | 否 | 要导出的 schema，可重复指定（默认 `public`） |
| `--space-id <spaceId>` | 否 | 空间 ID（默认从上下文读取） |

> `--schema-only` 和 `--data-only` 互斥。不指定时默认为 `--schema-only`。
>
> 默认只导出 `public` schema。需要系统 schema（如 `auth`、`storage`）时必须显式 `--include-schema auth --include-schema storage` 叠加，避免产出 Supabase 内部表导致无法 replay。
>
> ⚠️ 不要用 `--schema` 作 schema 筛选——`--schema` 是 CLI 框架保留的全局 flag（打印命令 JSON Schema），会被拦截。

### 推荐命令模板

```bash
# 导出 public schema（默认）
coze code db dump --db-id <id> --format json

# 仅导出数据
coze code db dump --db-id <id> --data-only --format json

# 指定多个 schema
coze code db dump --db-id <id> --include-schema public --include-schema auth --format json

# 自定义输出路径
coze code db dump --db-id <id> --output backups/schema.sql --format json
```

### 返回值

`--format json` 时返回：

| 字段 | 说明 |
|------|------|
| `output_path` | 输出文件路径 |
| `mode` | 导出模式（`schema-only` / `data-only`） |
| `schemas` | 实际导出的 schema 列表 |

### 导出内容

**Schema 模式**导出：
- `CREATE TABLE IF NOT EXISTS` 语句（含列定义、NOT NULL、DEFAULT）
- `CREATE INDEX` 语句

**Data 模式**导出：
- `INSERT INTO` 语句（逐行生成）

### 前置条件

- 数据库必须有 `supabase_url` 和 `super_user` / `super_user_password`（pg-meta 认证依赖）

---

## db rollback

将数据库回滚到指定时间点（PITR，Point-in-Time Recovery）。`--confirm` 为必填参数。

### 核心坑点（最高优先级标注）

**`--confirm` 和 `--timestamp` 都是必填参数！**

**`--timestamp` 必须是毫秒级整数时间戳且不能晚于当前时间**：非数字报 `E1000`；10 位秒级时间戳会被识别并报 `E1000`（提示乘以 1000）；未来时间报 `E1000`。

```bash
# 正确 ✅
coze code db rollback --db-id <id> --timestamp 1713254400000 --confirm

# 错误 ❌（缺少 --confirm 会报错）
coze code db rollback --db-id <id> --timestamp 1713254400000
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--db-id <dbId>` | 是 | 数据库 ID |
| `--timestamp <timestamp>` | 是 | 目标时间戳（毫秒级 Int64 字符串） |
| `--confirm` | 是 | 确认回滚操作 |
| `--space-id <spaceId>` | 否 | 空间 ID（默认从上下文读取） |

### 推荐命令模板

```bash
# 回滚数据库到指定时间点
coze code db rollback --db-id <id> --timestamp 1713254400000 --confirm --format json

# 回滚后检查状态
coze code db status --db-id <id> --format json
```

### 返回值

`--format json` 时返回：

| 字段 | 说明 |
|------|------|
| `restore_history_id` | 回滚记录 ID |

### 回滚状态查询

回滚是异步操作，发起后使用 `coze code db status --db-id <id>` 查看进度。

### 常见错误

| 错误 | 说明 | 修复 |
|------|------|------|
| `DB_RESTORE_WINDOW_EXCEEDED` | 回滚时间超出恢复窗口 | 使用 `db status` 查看 `earliest_restore_time` |
| `DB_RESTORE_IN_PROGRESS` | 已有回滚正在进行 | 等待当前回滚完成 |

---

## db status

查看数据库状态，包括 PITR 回滚信息和恢复进度。

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--db-id <dbId>` | 是 | 数据库 ID |
| `--space-id <spaceId>` | 否 | 空间 ID（默认从上下文读取） |

### 推荐命令模板

```bash
# 查看数据库状态
coze code db status --db-id <databaseId> --format json
```

### 返回值

`--format json` 时返回：

| 字段 | 说明 |
|------|------|
| `can_restore` | 是否支持 PITR 回滚 |
| `is_restoring` | 是否正在回滚中 |
| `earliest_restore_time` | 最早可回滚时间 |
| `latest_restore_status` | 最近回滚状态（`restoring` / `success` / `failed`） |
| `latest_restore_error` | 最近回滚错误信息（失败时有值） |
| `latest_restore_start_time` | 最近回滚开始时间 |
| `latest_restore_end_time` | 最近回滚结束时间 |

### 数据库状态枚举

| 状态 | 含义 |
|------|------|
| `active` | 正常运行 |
| `creating` | 创建中 |

### 回滚状态枚举

| 状态 | 含义 |
|------|------|
| `restoring` | 回滚进行中 |
| `success` | 回滚成功 |
| `failed` | 回滚失败 |

---

## db delete

删除数据库。**不可逆操作**，`--confirm` 为必填参数。

### 核心坑点（最高优先级标注）

**`--confirm` 是必填参数！不加会报错。**

```bash
# 正确 ✅
coze code db delete --db-id <id> --confirm

# 错误 ❌（缺少 --confirm 会报 DB_SQL_DANGEROUS 错误）
coze code db delete --db-id <id>
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--db-id <dbId>` | 是 | 数据库 ID |
| `--confirm` | 是 | 确认删除 |
| `--space-id <spaceId>` | 否 | 空间 ID（默认从上下文读取） |

### 推荐命令模板

```bash
# 删除数据库
coze code db delete --db-id <databaseId> --confirm --format json
```

### 返回值

`--format json` 时返回：

| 字段 | 说明 |
|------|------|
| `deleted` | 删除状态（`true`） |
| `database_id` | 已删除的数据库 ID |

### 注意事项

- **不可逆操作**，执行前确认用户意图。
- 用户已经明确要求删除且目标明确时可直接执行。

---

## 常见错误速查

| 错误码 | 名称 | 说明 | 修复 |
|--------|------|------|------|
| E1003 | `MISSING_SPACE_ID` | 缺少空间 ID | 使用 `--space-id` 或先执行 `coze space use <spaceId>` |
| E1007 | `DB_SQL_DANGEROUS` | 危险操作未确认；在 `db delete` / `db rollback` 中表示破坏性操作需要 `--confirm` 才能执行 | 添加 `--confirm` 参数 |
| E3010 | `DB_NOT_FOUND` | 数据库不存在或无权限 | 检查 `--db-id`，执行 `coze code db list` 确认 |
| E3012 | `DB_RESTORE_WINDOW_EXCEEDED` | 回滚时间超出恢复窗口 | 使用 `db status` 查看 `earliest_restore_time` |
| E3013 | `DB_RESTORE_IN_PROGRESS` | 已有回滚正在进行 | 等待当前回滚完成 |
| E4002 | `DB_QUOTA_EXCEEDED` | 空间数据库配额已满 | 删除不用的数据库 |
| E5004 | `DB_SQL_EXECUTION_FAILED` | SQL 执行失败 | 检查 SQL 语法和表结构 |
| E5005 | `DB_CONNECTION_FAILED` | 数据库连接失败 | 检查数据库状态和网络 |
| E5006 | `DB_GEN_TYPES_FAILED` | 类型生成失败 | 确认数据库为 `active` 状态且 PostgREST 可用 |
| E5007 | `DB_DUMP_FAILED` | Schema 导出失败 | 检查数据库状态和权限 |

## 典型工作流

### 创建并使用数据库

```bash
# 1. 创建数据库
coze code db create --format json
# 记录返回的 database_id

# 2. 等待状态变为 active
coze code db status --db-id <id> --format json

# 3. 执行建表 SQL
coze code db query --db-id <id> --sql "CREATE TABLE users (id SERIAL PRIMARY KEY, name TEXT NOT NULL)" --format json

# 4. 生成 TypeScript 类型
coze code db gen-types --db-id <id> --format json

# 5. 导出 Schema 备份
coze code db dump --db-id <id> --output backups/schema.sql --format json
```

### 回滚数据库

```bash
# 1. 检查是否可回滚
coze code db status --db-id <id> --format json
# 确认 can_restore 为 true，记录 earliest_restore_time

# 2. 执行回滚
coze code db rollback --db-id <id> --timestamp 1713254400000 --confirm --format json

# 3. 查看回滚进度
coze code db status --db-id <id> --format json
# 等待 latest_restore_status 变为 success
```
