# 质量规范

项目是面向 Windows 的 Python CLI。质量标准以命令契约清晰、服务操作显式、本地状态一致为核心。

## 基础约束

- Python 版本下限是 `>=3.13`。
- 生产代码放在 `src/sing_cli/`。
- 构建后端是 `uv_build`。
- CLI 框架使用 `typer`。
- HTTP 客户端使用 `httpx`。
- Windows 服务管理使用 `sc.exe`，不使用 `pywin32`。
- 文档和 Trellis SPEC 使用中文编写。

## 命令契约

必须实现并保持以下命令语义：

```text
sing install [--bin <path>]
sing uninstall
sing start <name>
sing stop
sing restart <name>
sing add <name> <url>
sing remove <name>
sing update <name>
sing list
```

- `sing install` 只注册服务并开启自启；不处理业务配置。
- `sing start <name>` 负责把服务命令行更新到 `<name>` 对应配置，再启动服务。
- `sing restart <name>` 先停止服务，再更新服务命令行并启动服务。
- `sing stop` 不需要配置名。
- `sing list` 必须标出 active 配置。

## 必需模式

- 函数签名保持类型标注。
- 外部命令调用使用参数列表。
- 配置名称必须先校验再用于文件路径。
- 写入 `state.json` 和配置文件时，失败必须显式暴露。
- 修改服务命令行、状态字段、命令参数或依赖前，先搜索相关引用。
- 新增复杂逻辑时拆成可测试函数，由 Typer 命令函数调用。

## 禁止模式

- 不添加静默回退、假成功或 mock 成功路径。
- 不吞掉异常后继续返回成功。
- 不为了未来功能添加未使用的框架、依赖或空目录。
- 不引入数据库、ORM、迁移系统或 pywin32。
- 不实现 sing-box 下载、升级、代理订阅转换或多服务实例管理。
- 不在文档里保留占位符、作者过程说明或编辑建议。

## 测试要求

新增实现时优先覆盖：

- Typer 命令参数和错误提示。
- `sing install` 的 PATH 解析、`--bin` 覆盖、找不到二进制失败。
- `sc.exe` 参数列表构造，不通过 shell 字符串执行。
- `sing start <name>` 服务已运行时失败。
- `sing restart <name>` 停止失败时不继续启动。
- `state.json` 读写、active 更新和删除 active 配置失败。
- 配置名称校验。
- HTTP 下载失败、写入失败和更新成功路径。

只改 Trellis SPEC 等文档时，至少检查占位符已移除、语言一致、引用路径真实存在。

## 评审清单

- 命令行为是否符合本 SPEC。
- 本地状态是否和 Windows 服务命令行保持一致。
- 错误是否显式暴露。
- 外部命令是否使用参数列表。
- 新增依赖是否已经在 SPEC 中确认。
- 文档是否使用中文，并且没有额外备注、迁移说明或自我说明式废话。
