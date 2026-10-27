# 山泽插件库上传标准

按山泽插件库 v0.2.0 README 和实际实现整理。只适用于插件 ZIP，管理器和管理员端的 EXE 安装程序不是可上传插件包。基线哈希见 [validation-baseline.json](validation-baseline.json)。

## 规则来源

插件库根目录内：`README.md` 的上传说明；`CompanyPluginManager/pm_core.py` 的 `validate_manifest`、`safe_path`、`inspect_package`、`Client._install`；`server/server.py` 的 `Registry.publish`、`handler_for`；`CompanyPluginManager/pm_c4d.py` 的入口加载与命令注册。

使用者通过 `--registry-root` 指定目标部署的源码根目录；其中应包含上述相对路径。预检脚本只尝试当前工作目录及其 CompanyPluginManager 子目录，不扫描其他项目。明确目标部署后按其授权范围操作。

## ZIP 和路径的硬性要求

- 根目录直接有 `plugin.json` 和入口，不额外套插件名文件夹。
- ZIP 最大 **64 MiB（67,108,864 字节）**；累计解压最大 **256 MiB（268,435,456 字节）**；ZIP 条目数 **1–4096**，目录条目也计数。
- `plugin.json` 最大 **32 KiB（32,768 字节）**，须为合法 JSON；开发统一保存为 UTF-8 无 BOM。
- `entry` 必须是包内真实文件，大小写匹配；资源路径也匹配大小写。
- 路径使用 `/`。拒绝绝对路径、反斜杠、冒号、NUL、`.` / `..` / 空路径段、Windows 保留名及含 `< > " | ? *` 的路径。路径段不能以点或空格结尾。
- 拒绝大小写折叠后重复的路径、符号链接、加密条目。待打包源目录及子项也避免 Junction / Symlink。
- Python 命令包不能含 `.pyp`、`.pypv`、`.xdl64`、`.dylib` 自动注册组件；确需使用则走原生包。

打包工具排除 `.git`、`.venv`、`__pycache__`。只放运行内容，开发数据、凭据及历史输出另存；输出 ZIP 放在待打包目录之外。

## plugin.json

| 字段 | 当前校验与开发约定 |
|---|---|
| `schema` | 整数 `1` |
| `id` | `[a-z][a-z0-9-]{1,63}`：2–64 字符，小写字母开头，只用小写英文、数字、连字符；发布后固定 |
| `name` | 1–1000 字符的非空字符串，可用中文；是员工界面和搜索名称 |
| `version` | `\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?`，如 `1.0.0`、`1.1.0-beta.1`；不接受 `v1.0`、`1.0`、`+build`；更新递增 |
| `author` | 1–1000 字符的非空字符串 |
| `description` | 1–1000 字符的非空字符串，写明功能、选择要求及依赖 |
| `kind` | `python` / `native`；实现省略时按 `python`，开发清单始终显式填写 |
| `command_id` | JSON 整数，不接受字符串 / 布尔值；1,000,000–2,147,483,647；不占管理器 ID，不与其他工具重复 |
| `min_c4d` / `max_c4d` | JSON 整数，最小值不大于最大值；使用 `c4d.GetC4DVersion()` 的整数，如已实测 `2026400`；只填写有依据的兼容范围 |
| `entry` | 通过路径校验的包内相对路径；Python 为 `.py`，原生为 `.pyp` |
| `callable` | Python 必填，`[A-Za-z_]\w*`，通常 `execute`；入口须实际导出接受 `doc` 的同名可调用对象；原生可省略 |

`sha256`、`size` 由服务端生成，`path`、`restart_required` 由安装端生成，开发清单不填写这些运行字段。客户端会检查包摘要及目录元数据。

## 命令 ID 与版本不变量

- 当前保留：管理器 `1069983`、后台组件 `1069986`；目标部署若变更，以其 `pm_core.py` 为准。
- 已有编织 `weaveflow-managed` 使用 `1069984`；外被破损 `cable-damage-managed` 使用 `1069985`。新工具不复用这些 ID。
- README 的 `1069994` 只是示例，不能视为新工具已获分配的 ID；模板使用 `null` 强制填写实际 ID。
- 同一插件更新保持 `id` / `command_id` / `kind`；改 ID 变成另一工具，改命令 ID 或类型会被服务端 / 客户端拒绝。
- 相同 ID + 版本不可覆盖不同内容；相同内容重复提交可幂等。改包内容后递增版本。
- 服务端当前目录保存每个 ID 最近发布的记录，实际没有强制版本递增。因此开发预检额外阻止意外回退；历史同版本不可覆盖最终以服务端保存的 ZIP 为准。
- 当前目录无冲突不等于 Maxon 全局无冲突。推广使用公司持有的唯一 ID，不把开发值宣称为正式 ID；Skill 不会自动申请或猜测公司正式 ID。

## Python 入口和依赖

```text
plugin.json
entry.py
tool/
  __init__.py
  command.py
```

管理器从独立文件模块获取 callable 并执行 `execute(doc)`，返回 `False` 视为失败。入口自身不是常规包，直接 `from .tool import ...` 不可靠。使用模板的插件 ID + 版本命名空间加载器或经验证的等效入口，内部模块采用相对导入，资源从 `Path(__file__)` 定位，避免模块串用和机器绝对路径。

由管理器注册普通 Python 命令，入口只执行业务逻辑。导入不自动生成对象；C4D 对象和窗口在主线程操作；场景修改记录 Undo。生成器数据 ID、旧对象代码入口、持久化资源路径需要兼容性测试。

首次在运行中下载的命令可能不能立即注册到命令搜索，管理器会提示重启。脚本下能运行不代表已通过正式启动、菜单及 Shift+C 验收。

## 原生分支

`kind: "native"`，`entry` 是包内实际 `.pyp`，插件自行注册声明的 `command_id`。额外对象 / 标签 / 消息组件也需要独立合法 ID，附齐依赖与资源并验证 C4D / Python / 操作系统兼容性。

首次安装到所选 plugins 的 `company-<id>`，需要重启。当前管理器不支持覆盖正在运行的原生目录在线更新；由管理员关闭 C4D 后替换。自定义原生目录加入 C4D 插件搜索路径。不能把第三方 EXE / MSI 改后缀充当插件 ZIP。

## 发布与验收边界

管理员网页发布密码登录，上传正文 `application/zip`，最大 64 MiB；员工目录与下载免密码。开发和预检不是发布授权，预检不会调用真实 `/api/upload`。

预检以真实 `Registry.publish`、`Client.install` 在本地沙箱演练，不运行插件代码、不检测实际 DLL 或 UI。Python 语法检查使用预检解释器，若与 C4D 不同仍需目标 C4D 验证。分别报告格式预检、目录冲突、C4D 运行、正式注册、保存重开 / 升级的适用证据。
