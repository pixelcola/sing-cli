# 质量规范

项目是面向 Windows 的 Python CLI。质量标准以命令契约清晰、服务操作显式、本地状态一致为核心。

## 基础约束

- Python 版本下限是 `>=3.13`。
- 生产代码放在 `src/sing_cli/`。
- 构建后端是 `hatchling.build`。
- 版本由 `uv-dynamic-versioning` 从 Git 元数据生成。
- 开发依赖通过 `pyproject.toml` 的 `[dependency-groups].dev` 声明。
- Ruff、ty 和 pytest 是当前已确认的代码质量工具。
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

## Ruff 工具链契约

### 1. Scope / Trigger

- Trigger: 修改 Python 源码、`pyproject.toml`、开发依赖、lint 规则或格式化相关配置。

### 2. Signatures

```toml
[dependency-groups]
dev = ["pytest>=9.0.2", "ruff>=0.15.12", "ty>=0.0.35"]

[tool.ruff]
line-length = 120
target-version = "py313"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP"]
ignore = ["B904", "E501", "B008", "C901", "W191"]
```

### 3. Contracts

- `uv.lock` 必须和 `pyproject.toml` 中的开发依赖保持一致。
- Ruff 配置只放在 `pyproject.toml`，不新增独立 Ruff 配置文件。
- Python 语法目标必须和项目 Python 下限一致，当前为 `py313`。
- Ruff 的项目检查范围是 `src`，不要默认检查 `.trellis/scripts`。
- 单行长度上限为 120；`E501` 已忽略，不用为纯粹行宽拆分降低可读性。

### 4. Validation & Error Matrix

| 条件 | 行为 |
|------|------|
| Python 代码变更后 `uv run ruff check src` 失败 | 修复 lint 错误后再交付 |
| `pyproject.toml` 开发依赖变更但 `uv.lock` 未更新 | 更新 lockfile 后再交付 |
| 新增 lint 规则导致 `src` 下现有代码大面积失败 | 先修复或缩小规则范围，不提交破坏性规则 |
| 需要忽略单个 lint 问题 | 使用局部 `# noqa`，并让原因能从代码上下文看出 |

### 5. Good/Base/Bad Cases

- Good: 新增 Python 代码后运行 `uv run ruff check src`，并修复导入顺序、未使用变量和现代语法提示。
- Base: 只改文档时不强制运行 Ruff，但要检查文档语言、路径和占位符。
- Bad: 修改 Ruff 规则或开发依赖后不更新 `uv.lock`。
- Bad: 在 CI 里运行 `ruff check .`，把 Trellis 管理脚本纳入项目业务 lint 范围。

### 6. Tests Required

- Python 源码改动：运行 `uv run ruff check src`，断言退出码为 0。
- `pyproject.toml` 开发依赖改动：确认 `uv.lock` 包含对应依赖版本。
- Ruff 规则改动：运行 `uv run ruff check src`，断言业务源码不会因规则漂移失败。

### 7. Wrong vs Correct

#### Wrong

```toml
[tool.ruff]
target-version = "py312"
```

#### Correct

```toml
[tool.ruff]
target-version = "py313"
```

## ty 工具链契约

### 1. Scope / Trigger

- Trigger: 修改 Python 源码、`pyproject.toml`、开发依赖、类型检查配置或 Windows 平台相关代码。

### 2. Signatures

```toml
[dependency-groups]
dev = [
    "pytest>=9.0.2",
    "ruff>=0.15.12",
    "ty>=0.0.35",
]

[tool.ty.environment]
python-version = "3.13"

[tool.ty.src]
include = ["src"]
```

### 3. Contracts

- ty 配置只放在 `pyproject.toml` 的 `[tool.ty]` 下，不新增 `ty.toml`。
- `python-version` 必须和项目 Python 下限一致，当前为 `3.13`。
- `include` 必须覆盖 `src` 布局。
- 不添加与当前检查范围重复的 `root` 配置。
- 不添加只影响输出展示的 `terminal.output-format` 配置，保持基础配置最小。
- `uv.lock` 必须和 `pyproject.toml` 中的 ty 开发依赖保持一致。

### 4. Validation & Error Matrix

| 条件 | 行为 |
|------|------|
| Python 代码变更后 `uv run ty check src` 失败 | 修复类型错误后再交付 |
| `pyproject.toml` ty 依赖变更但 `uv.lock` 未更新 | 更新 lockfile 后再交付 |
| 需要忽略单个 ty 问题 | 使用局部忽略，不添加全局静默规则 |

### 5. Good/Base/Bad Cases

- Good: 新增 Python 代码后运行 `uv run ty check src`，并修复类型错误。
- Base: 只改文档时不强制运行 ty。
- Bad: 同时写 `root = ["./src"]` 和 `include = ["src"]` 表达同一个基础源码范围。

### 6. Tests Required

- Python 源码改动：运行 `uv run ty check src`，断言退出码为 0。
- ty 配置改动：运行 `uv run ty check src`，断言 `src` 下代码被检查。
- `pyproject.toml` 开发依赖改动：确认 `uv.lock` 包含对应 ty 版本。

### 7. Wrong vs Correct

#### Wrong

```toml
[tool.ty.environment]
root = ["./src"]

[tool.ty.src]
include = ["src"]
```

#### Correct

```toml
[tool.ty.src]
include = ["src"]
```

## CI 契约

### 1. Scope / Trigger

- Trigger: 修改 `.github/workflows/ci.yml`、`.github/dependabot.yml`、开发依赖、`pyproject.toml`、`uv.lock` 或质量检查命令。

### 2. Signatures

```yaml
on:
  push:
    branches:
      - main
  pull_request:

jobs:
  lint-and-format-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b
      - run: uv python install
      - run: uv sync --locked --all-extras --dev
      - run: uv run ruff check --output-format=github src
      - run: uv run ruff format --check --diff src
      - run: uv run ty check src
      - run: uv run pytest
```

### 3. Contracts

- CI 只在 `push` 到 `main` 和 `pull_request` 时运行。
- CI 使用 `uv sync --locked --all-extras --dev`，lockfile 不一致时失败。
- CI 中的开发工具必须通过 `uv run` 执行，不依赖 shell 环境是否激活 `.venv`。
- Ruff 和 ty 的 CI 检查范围是 `src`。
- Python 测试使用 `pytest` 执行。
- CI 不发布包、不创建 GitHub Release、不上传构建产物。
- 发布逻辑只放在 `.github/workflows/release.yml`，不并入 CI workflow。

### 4. Validation & Error Matrix

| 条件 | 行为 |
|------|------|
| CI 命令直接调用 `ruff`、`ty` 或 `pytest` | 改为 `uv run ruff ...`、`uv run ty ...` 或 `uv run pytest` |
| CI 中 `uv sync --locked` 失败 | 更新并提交 `uv.lock` |
| CI 把 Ruff 检查范围设为 `.` | 改为 `src` |
| CI workflow 创建 GitHub Release 或发布 PyPI | 移到 `.github/workflows/release.yml` |

### 5. Good/Base/Bad Cases

- Good: CI 使用 `uv run ruff check --output-format=github src`、`uv run ty check src` 和 `uv run pytest`。
- Base: 只改 README 或 SPEC 时不需要新增 CI job。
- Bad: 在第一版 CLI 功能完成前添加自动发布 GitHub Release 的 workflow。

### 6. Tests Required

- CI workflow 改动：本地运行 `uv run ruff check src`、`uv run ruff format --check --diff src`、`uv run ty check src` 和 `uv run pytest`。
- 依赖或 lockfile 改动：确认 `uv sync --locked --all-extras --dev` 可解析。
- 发布 workflow 改动：按发布 workflow 契约检查 tag 规则、权限、构建产物和 PyPI 发布步骤。

### 7. Wrong vs Correct

#### Wrong

```yaml
- run: ruff check .
```

#### Correct

```yaml
- run: uv run ruff check --output-format=github src
```

## 发布 workflow 契约

### 1. Scope / Trigger

- Trigger: 修改 `.github/workflows/release.yml`、发布 tag 规则、构建产物、GitHub Release 上传步骤、PyPI trusted publishing 环境或发布权限。

### 2. Signatures

```yaml
on:
  push:
    tags:
      - "v*"

jobs:
  build-and-release:
    runs-on: ubuntu-latest
    environment:
      name: pypi
    permissions:
      id-token: write
      contents: write
    steps:
      - uses: actions/checkout@v6
      - uses: astral-sh/setup-uv@v7
      - run: uv build
      - uses: softprops/action-gh-release@v2
        with:
          files: |
            dist/*.whl
            dist/*.tar.gz
          generate_release_notes: true
      - run: uv publish
```

### 3. Contracts

- 发布 workflow 文件固定为 `.github/workflows/release.yml`。
- 发布只由 `v*` tag push 触发，不在 branch push 或 pull request 上运行。
- 发布 job 使用 GitHub environment `pypi`，匹配 PyPI trusted publishing 配置。
- `id-token: write` 是 `uv publish` 使用 PyPI trusted publishing 的必需权限。
- `contents: write` 是创建 GitHub Release 和上传 release assets 的必需权限。
- 构建命令固定为 `uv build`，发布前必须生成 wheel 和 source distribution。
- GitHub Release 必须上传 `dist/*.whl` 和 `dist/*.tar.gz`。
- PyPI 发布固定使用 `uv publish`，不在 workflow 中配置长期 PyPI token。

### 4. Validation & Error Matrix

| 条件 | 行为 |
|------|------|
| release workflow 在 pull request 或普通 branch push 上运行 | 改为只监听 `push.tags: ["v*"]` |
| 缺少 `id-token: write` | 添加该权限，否则 PyPI trusted publishing 无法签发 OIDC token |
| 缺少 `contents: write` | 添加该权限，否则 GitHub Release 创建或资产上传会失败 |
| 发布前未运行 `uv build` | 添加构建步骤并确保产物位于 `dist/` |
| release assets 未覆盖 wheel 或 sdist | 同时上传 `dist/*.whl` 和 `dist/*.tar.gz` |
| workflow 使用 PyPI API token secret | 改为 trusted publishing，通过 `uv publish` 使用 OIDC |

### 5. Good/Base/Bad Cases

- Good: 推送 `v1.2.3` tag 后构建 wheel 和 sdist，创建 GitHub Release，上传两个产物，再执行 `uv publish`。
- Base: 普通 PR 只运行 CI，不运行发布 workflow。
- Bad: 在 `pull_request` 事件里执行 `uv publish`。
- Bad: 使用 `contents: read` 后调用 `softprops/action-gh-release` 创建 release。

### 6. Tests Required

- release workflow 改动：检查 YAML 缩进、触发条件、job 权限和 step 顺序。
- 发布权限改动：确认 `permissions` 同时包含 `id-token: write` 和 `contents: write`。
- 发布产物改动：确认 `uv build` 会生成 `dist/*.whl` 和 `dist/*.tar.gz`。
- PyPI 环境改动：确认 GitHub environment 名称和 PyPI trusted publishing 配置一致。

### 7. Wrong vs Correct

#### Wrong

```yaml
permissions:
  id-token: write
  contents: read
```

#### Correct

```yaml
permissions:
  id-token: write
  contents: write
```

## Dependabot 契约

### 1. Scope / Trigger

- Trigger: 修改 GitHub Actions 版本、uv 依赖、`uv.lock` 或 `.github/dependabot.yml`。

### 2. Signatures

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"

  - package-ecosystem: "uv"
    directory: "/"
    schedule:
      interval: "monthly"
```

### 3. Contracts

- Dependabot 只跟踪 GitHub Actions 和 uv 依赖。
- 检查周期固定为 monthly。
- 依赖更新必须经过 CI，不直接绕过 `uv sync --locked --all-extras --dev`。
- 不为未使用的生态系统添加 Dependabot 配置。

### 4. Validation & Error Matrix

| 条件 | 行为 |
|------|------|
| 新增开发依赖后 Dependabot 不覆盖对应生态系统 | 更新 `.github/dependabot.yml` |
| Dependabot PR 导致 CI 失败 | 修复配置或依赖约束后再合并 |
| 新增未使用生态系统的 Dependabot 配置 | 删除该条目 |

### 5. Good/Base/Bad Cases

- Good: `github-actions` 和 `uv` 都按月检查。
- Base: 手动升级单个依赖后保持 Dependabot 配置不变。
- Bad: 为没有 npm、Docker 或 pip requirements 文件的项目添加对应 Dependabot 生态系统。

### 6. Tests Required

- `.github/dependabot.yml` 改动：检查 YAML 缩进、`package-ecosystem` 名称和 `directory` 路径。
- uv 依赖更新：运行 `uv sync --locked --all-extras --dev`。
- GitHub Actions 更新：确认 `.github/workflows/*.yml` 仍引用有效 action。

### 7. Wrong vs Correct

#### Wrong

```yaml
- package-ecosystem: "npm"
  directory: "/"
```

#### Correct

```yaml
- package-ecosystem: "uv"
  directory: "/"
```

## 必需模式

- 函数签名保持类型标注。
- 外部命令调用使用参数列表。
- 配置名称必须先校验再用于文件路径。
- 写入 `state.json` 和配置文件时，失败必须显式暴露。
- 修改服务命令行、状态字段、命令参数或依赖前，先搜索相关引用。
- 新增复杂逻辑时拆成可测试函数，由 Typer 命令函数调用。
- Python 源码改动后运行 `uv run ruff check src`。
- Python 源码改动后运行 `uv run ty check src`。
- Python 源码改动后运行 `uv run pytest`。

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
