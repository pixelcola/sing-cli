# 补充完善测试用例

## Goal

补充 `sing-cli` 现有 CLI、state、profile、service 模块的测试覆盖，锁定当前命令契约和错误处理行为，降低后续重构或修复时引入回归的风险。

## Requirements

* 只新增或调整测试，不改变当前业务行为。
* 覆盖主要 CLI 命令的成功路径：`install`、`add`、`remove`、`update`、`list`。
* 覆盖关键错误路径：已存在 profile、删除 active profile、未安装 bin 启动、下载 HTTP 错误、无效 state 字段、非 Windows 服务操作、缺失 `sing-box.exe`。
* 测试继续使用现有 pytest、Typer `CliRunner`、monkeypatch 和临时目录模式。
* 不添加 mock 成功路径到生产代码；外部依赖通过测试替身注入或 monkeypatch 隔离。

## Acceptance Criteria

* [ ] 新增测试能在本地稳定运行，不依赖真实 Windows、真实 NSSM、真实网络或真实用户 app data。
* [ ] `uv run pytest` 通过。
* [ ] `uv run ruff check src tests` 通过。
* [ ] `uv run ty check src tests` 或项目可用的类型检查命令通过；若工具不支持测试路径，使用项目约定命令并记录结果。

## Definition of Done

* Tests added or updated.
* Lint, type-check, and test suite pass.
* No production behavior changed unless tests expose an existing bug that must be fixed explicitly.
* No docs update unless behavior or documented command contract changes.

## Technical Approach

以现有测试风格为基准扩展覆盖：CLI 测试通过 `CliRunner` 调用命令并 monkeypatch `app_dir`、service/profile 函数；模块测试使用轻量 stub 验证状态解析、下载错误和 service 参数/平台边界。

## Decision (ADR-lite)

**Context**: 当前测试已经覆盖部分核心路径，但 CLI 命令集合和错误处理矩阵尚未完整锁定。  
**Decision**: 本任务优先补充行为测试，不引入新测试框架、不修改生产代码。  
**Consequences**: 覆盖面提升且变更风险低；如果测试暴露真实行为缺陷，再以最小生产代码修改修复。

## Out of Scope

* 不新增功能。
* 不重构生产代码。
* 不引入覆盖率工具或强制覆盖率阈值。
* 不测试真实 Windows service 或真实网络下载。

## Technical Notes

* 项目使用 Python `>=3.13`，测试框架为 pytest。
* 现有测试文件：`tests/test_cli.py`、`tests/test_profile.py`、`tests/test_state.py`、`tests/test_service.py`。
* 相关规范：`.trellis/spec/backend/index.md`、`.trellis/spec/backend/quality-guidelines.md`、`.trellis/spec/backend/error-handling.md`。
