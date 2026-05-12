# 后端开发规范

本目录记录 `sing-cli` 后端与命令行实现的项目约定。项目目标是在 Windows 上提供一个 Python CLI，用于安装、卸载和控制 `sing-box` Windows 服务，并管理命名的 `sing-box` JSON 配置来源。

## 规范索引

| 规范 | 内容 | 状态 |
|------|------|------|
| [目录结构](./directory-structure.md) | 包布局、入口点、本地数据布局 | 已填写 |
| [数据库规范](./database-guidelines.md) | 无数据库约束、本地 JSON 状态边界 | 已填写 |
| [错误处理](./error-handling.md) | CLI 错误、`sc.exe` 错误、配置状态错误 | 已填写 |
| [质量规范](./quality-guidelines.md) | Python 版本、依赖、命令契约、测试要求 | 已填写 |
| [日志规范](./logging-guidelines.md) | CLI 输出边界、stdout/stderr 规则 | 已填写 |

## 开发前检查清单

1. 阅读本索引和与改动相关的具体规范文件。
2. 修改命令、服务名、状态字段、路径或依赖前，先用 `rg` 搜索同名引用。
3. 保持 SPEC 和代码事实一致；不要写未确认的数据库、日志框架、下载器、订阅转换或多实例服务设计。
4. 面向用户的 CLI 行为变更必须同步测试或说明无法自动测试的原因。

## 项目事实

- 项目使用 Python，最低版本为 `>=3.13`。
- 构建后端是 `uv_build`。
- 可执行命令由 `pyproject.toml` 的 `[project.scripts]` 声明：`sing-cli = "sing_cli:main"`。
- 当前源码位于 `src/sing_cli/`。
- CLI 框架使用 `typer`，HTTP 下载使用 `httpx`。
- Windows 服务管理使用系统内置 `sc.exe`，不使用 `pywin32`。
- 固定 Windows 服务名为 `sing-box`。
- 本地应用数据目录使用 `typer.get_app_dir("sing-cli")`。

## 命令契约

第一版命令集合固定为：

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

- `sing install` 注册 `sing-box` Windows 服务并开启自启；默认使用 `PATH` 中的 `sing-box.exe`，`--bin` 可指定自定义路径。
- `sing install` 不下载、不升级 `sing-box.exe`，也不指定或写入业务配置。
- `sing start <name>` 使用 `<name>` 对应的本地配置启动服务；服务已运行时失败并提示使用 `sing restart <name>`。
- `sing restart <name>` 停止当前服务后，用 `<name>` 对应配置重新启动。
- `sing stop` 停止服务，不需要配置名。
- `sing add <name> <url>` 添加命名配置来源；URL 返回完整 `sing-box` JSON 配置。
- `sing update <name>` 从已保存 URL 重新下载配置。
- `sing remove <name>` 删除配置来源和本地配置文件。
- `sing list` 列出所有配置来源，并标出 active 配置。

## 服务命令行

`sing start <name>` 和 `sing restart <name>` 启动前必须先更新服务命令行：

```text
sc.exe config sing-box binPath= "<sing-box.exe> run -c <config-path>"
```

随后再启动 `sing-box` 服务。Windows 自启时沿用最后一次 `sing start <name>` 或 `sing restart <name>` 写入的配置。

调用 `sc.exe` 必须使用参数列表，不使用 shell 字符串拼接。
