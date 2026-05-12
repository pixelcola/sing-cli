# 数据库规范

当前项目没有数据库层、ORM、迁移工具或外部持久化服务。第一版只使用本地 JSON 文件保存 CLI 状态和命名配置索引。

## 当前状态

- 仓库没有 migrations、models、schema、repository 目录。
- 不使用 SQLite、PostgreSQL、MySQL 或 ORM。
- 本地状态文件为 `typer.get_app_dir("sing-cli") / "state.json"`。
- 配置内容保存到 `typer.get_app_dir("sing-cli") / "configs" / "<name>.json"`。

## 本地状态边界

`state.json` 是运行时状态文件，不是数据库抽象层。它只记录：

- `bin`：`sing-box.exe` 路径。
- `active`：最后一次成功启动的配置名。
- `configs`：配置名到 URL、本地路径、更新时间的映射。

不要为 `state.json` 再封装 repository、migration 或 ORM 风格接口。需要读写时使用标准库 `json` 和 `pathlib`，并在写入失败时显式报错。

## 数据一致性

- `sing add <name> <url>` 成功后，`configs` 中必须有 `<name>` 条目，并且本地配置文件存在。
- `sing update <name>` 成功后，保留原配置名，更新本地配置文件和 `updated_at`。
- `sing remove <name>` 删除非 active 配置时，同时删除 `configs` 条目和对应本地配置文件。
- 删除 active 配置必须失败，避免 `state.json` 与 Windows 服务命令行不一致。
- `sing stop` 不清空 `active`。

## 禁止模式

- 不引入数据库依赖。
- 不创建迁移模板或空数据访问层。
- 不用内存字典替代 `state.json` 持久化。
- 不把下载失败、写入失败或状态文件损坏伪装成成功。
