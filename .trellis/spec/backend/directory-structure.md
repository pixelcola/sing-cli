# 目录结构

`sing-cli` 采用标准 `src/` 布局。生产代码放在 `src/sing_cli/` 包内，Trellis 资料只放在 `.trellis/`。

## 当前布局

```text
.
|-- pyproject.toml
|-- README.md
`-- src/
    `-- sing_cli/
        `-- __init__.py
```

## 包和入口点

- `pyproject.toml` 是包名、Python 版本、构建后端、依赖和 CLI 脚本入口的来源。
- `[project.scripts]` 中的 `sing-cli = "sing_cli:main"` 指向 `src/sing_cli/__init__.py` 内的 `main()`。
- `main()` 只负责进入 Typer 应用；命令实现、Windows 服务调用、本地状态读写、HTTP 下载应拆到独立模块。

当前入口示例：

```python
def main() -> None:
    print("Hello from sing-cli!")
```

## 建议模块边界

新增实现时按职责拆分模块：

- `cli.py`：Typer 应用、命令参数和用户输出。
- `service.py`：`sc.exe` 调用、服务安装、卸载、启动、停止、重启。
- `state.py`：`state.json` 读写、配置名称校验、active 状态维护。
- `config.py`：配置 URL 下载、本地配置文件写入。
- `errors.py`：面向 CLI 的异常类型。

模块名使用小写加下划线。不要把服务管理、HTTP 下载和状态文件操作都堆在 `__init__.py`。

## 本地数据布局

本地配置和索引存放在 `typer.get_app_dir("sing-cli")` 返回的应用目录中：

```text
<app-dir>/
|-- state.json
`-- configs/
    |-- <name>.json
```

`state.json` 结构：

```json
{
  "bin": "C:\\path\\sing-box.exe",
  "active": "home",
  "configs": {
    "home": {
      "url": "https://example.com/sing-box.json",
      "path": "C:\\...\\configs\\home.json",
      "updated_at": "2026-05-12T00:00:00Z"
    }
  }
}
```

- `bin` 记录 `sing install` 解析到或通过 `--bin` 指定的 `sing-box.exe` 路径。
- `active` 表示最后一次成功写入 Windows 服务命令行并启动的配置名。
- `configs` 按配置名索引 URL、本地文件路径和更新时间。
- `configs/<name>.json` 保存 URL 下载到的完整 `sing-box` JSON 配置。

## 命名规则

- Windows 服务名固定为 `sing-box`。
- 配置名称用于文件名，只允许字母、数字、下划线、短横线和点。
- 第一版不支持 `--name` 管理多个 Windows 服务实例。
- CLI 命令名使用小写单词，保持 `sing <command>` 形式。

## 反例

- 不在仓库根目录新增生产脚本承载 CLI 逻辑。
- 不在 `.trellis/` 中放运行时代码或运行时数据。
- 不把 `state.json` 当作可选缓存；它是 CLI 的本地状态来源。
- 不在未确认多实例需求前引入服务名参数。
