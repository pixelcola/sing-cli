# 错误处理

CLI 必须让失败清晰暴露。不要为了让命令“看起来成功”添加静默回退、假成功或吞异常逻辑。

## CLI 错误约定

- 用户输入错误使用 Typer 的参数校验或显式错误输出，并返回非零退出码。
- 面向用户的错误信息写到 stderr，说明失败原因和可执行修正。
- 程序缺陷和未预期异常不做宽泛捕获后伪装成功。
- 不使用裸 `except:`。
- 不用 `except Exception: pass`、返回 `None` 或固定成功消息吞掉失败。

## `sing-box.exe` 解析错误

- `sing install` 默认从 `PATH` 解析 `sing-box.exe`。
- `sing install --bin <path>` 使用用户指定路径。
- 找不到 `sing-box.exe`、路径不存在或路径不是文件时，命令失败。
- `sing install` 不下载或升级 `sing-box.exe`。

## `sc.exe` 错误

Windows 服务注册和控制统一调用 `sc.exe`。调用时必须使用参数列表：

```python
subprocess.run(["sc.exe", "start", "sing-box"], ...)
```

不要使用 shell 字符串拼接：

```python
subprocess.run(f"sc.exe start {service_name}", shell=True)
```

`sc.exe` 返回非零退出码时，CLI 命令失败，并把 stderr 或 stdout 中的系统错误摘要展示给用户。

## 服务状态错误

- `sing start <name>` 在服务已运行时失败，并提示使用 `sing restart <name>`。
- `sing restart <name>` 停止失败时不得继续启动。
- `sing stop` 在服务停止失败时返回失败。
- `sing uninstall` 删除服务失败时返回失败。
- 第一版不做隐式重试，不做自动修复服务状态。

## Profile 状态错误

- profile 名不符合命名规则时失败。
- `sing start <name>`、`sing restart <name>`、`sing update <name>` 找不到 profile 名时失败。
- `sing remove <name>` 删除 active profile 时失败。
- 下载 profile URL 失败、HTTP 状态失败、写入本地文件失败时命令失败。
- `sing add` 和 `sing update` 不主动调用 `sing-box check`；profile 有效性由 `sing start <name>` 启动时的 `sing-box` 行为暴露。

## 常见错误

- 捕获所有异常后继续执行，会让用户误以为服务已经安装或启动。
- 在服务已运行时让 `start` 自动重启，会隐藏用户选择的配置切换行为。
- 删除 active profile 会让 `state.json` 和 Windows 服务命令行分离。
- 把 `sc.exe` 命令拼成 shell 字符串会破坏带空格路径，并增加注入风险。
