# Bootstrap Task: Fill Project Development Guidelines

**You (the AI) are running this task. The developer does not read this file.**

The developer just ran `trellis init` on this project for the first time.
`.trellis/` now exists with empty spec scaffolding, and this bootstrap task
exists under `.trellis/tasks/`. When they want to work on it, they should start
this task from a session that provides Trellis session identity.

**Your job**: help them populate `.trellis/spec/` with the team's real
coding conventions. Every future AI session — this project's
`trellis-implement` and `trellis-check` sub-agents — auto-loads spec files
listed in per-task jsonl manifests. Empty spec = sub-agents write generic
code. Real spec = sub-agents match the team's actual patterns.

Don't dump instructions. Open with a short greeting, figure out if the repo
has any existing convention docs (CLAUDE.md, .cursorrules, etc.), and drive
the rest conversationally.

---

## Status (update the checkboxes as you complete each item)

- [x] Fill backend guidelines
- [x] Add code examples

---

## Confirmed Requirements

- SPEC 使用中文编写。
- 项目目标是实现一个运行在 Windows 上的 Python CLI 应用。
- 背景：`sing-box` 在 Windows 上缺少类似 Linux 服务管理的使用体验。
- CLI 需要支持安装和卸载 `sing-box` Windows 服务。
- CLI 需要支持启动、停止、重启等 `sing-box` 服务管理操作。
- CLI 需要支持管理 `sing-box` 配置。
- CLI 不负责下载或升级 `sing-box.exe`。
- `sing install` 默认使用 `PATH` 中可解析到的 `sing-box.exe`。
- `sing install --bin <path>` 支持指定自定义 `sing-box.exe` 路径。
- `sing install` 只负责注册 Windows 服务并开启自启，不负责指定或写入 `sing-box` 配置。
- Windows 服务注册和控制使用系统内置 `sc.exe`。
- 调用 `sc.exe` 时使用参数列表，不用 shell 字符串拼接。
- Windows 服务名固定为 `sing-box`。
- 第一版不支持通过 `--name` 管理多个 `sing-box` 服务实例。
- 配置管理使用命名 URL 条目模型。
- `sing add <name> <url>` 添加一个配置来源。
- `sing remove <name>` 删除指定名称的配置来源。
- `sing update <name>` 更新指定名称对应的配置内容。
- `sing list` 列出已添加的配置来源。
- 配置 URL 返回完整的 `sing-box` JSON 配置文件，不处理代理订阅格式转换。
- `sing add` 和 `sing update` 不主动调用 `sing-box check` 校验配置；配置有效性由 `sing start <name>` 启动时的 `sing-box` 行为暴露。
- `sing start <name>` 使用 `<name>` 对应的本地配置启动 `sing-box` 服务。
- `sing start <name>` 在服务已运行时失败，并提示使用 `sing restart <name>`；不做隐式重启。
- `sing restart <name>` 停止当前服务后，再使用 `<name>` 对应配置启动。
- `sing stop` 停止服务，不需要配置名。
- `sing start <name>` 和 `sing restart <name>` 启动前，使用 `sc.exe config sing-box binPath= "<sing-box.exe> run -c <config-path>"` 更新服务命令行。
- Windows 服务自启时沿用最后一次 `sing start <name>` 或 `sing restart <name>` 写入的配置。
- 第三方 CLI 框架使用 `typer`。
- 第三方 HTTP 客户端使用 `httpx` 下载配置 URL。
- 不使用 `pywin32` 管理 Windows 服务；服务管理统一通过 `sc.exe`。
- 本地配置和索引存放在 `typer.get_app_dir()` 返回的应用目录中。
- `typer.get_app_dir()` 的应用名使用 `sing-cli`。
- 本地数据目录包含 `state.json` 和 `configs/` 子目录。
- `state.json` 顶层包含 `bin`、`active`、`configs` 字段。
- `configs/<name>.json` 保存 `<name>` 对应 URL 下载到的完整 `sing-box` JSON 配置。
- 配置名称用于文件名，只允许字母、数字、下划线、短横线和点。
- `active` 表示最后一次成功写入 Windows 服务命令行并启动的配置名。
- `sing start <name>` 和 `sing restart <name>` 成功启动后，将 `active` 设为 `<name>`。
- `sing stop` 不清空 `active`。
- `sing remove <name>` 删除 active 配置时失败，避免状态和服务命令行不一致。
- `sing list` 标出 active 配置。

---

## Spec files to populate


### Backend guidelines

| File | What to document |
|------|------------------|
| `.trellis/spec/backend/directory-structure.md` | Where different file types go (routes, services, utils) |
| `.trellis/spec/backend/database-guidelines.md` | ORM, migrations, query patterns, naming conventions |
| `.trellis/spec/backend/error-handling.md` | How errors are caught, logged, and returned |
| `.trellis/spec/backend/logging-guidelines.md` | Log levels, format, what to log |
| `.trellis/spec/backend/quality-guidelines.md` | Code review standards, testing requirements |


### Thinking guides (already populated)

`.trellis/spec/guides/` contains general thinking guides pre-filled with
best practices. Customize only if something clearly doesn't fit this project.

---

## How to fill the spec

### Step 1: Import from existing convention files first (preferred)

Search the repo for existing convention docs. If any exist, read them and
extract the relevant rules into the matching `.trellis/spec/` files —
usually much faster than documenting from scratch.

| File / Directory | Tool |
|------|------|
| `CLAUDE.md` / `CLAUDE.local.md` | Claude Code |
| `AGENTS.md` | Codex / Claude Code / agent-compatible tools |
| `.cursorrules` | Cursor |
| `.cursor/rules/*.mdc` | Cursor (rules directory) |
| `.windsurfrules` | Windsurf |
| `.clinerules` | Cline |
| `.roomodes` | Roo Code |
| `.github/copilot-instructions.md` | GitHub Copilot |
| `.vscode/settings.json` → `github.copilot.chat.codeGeneration.instructions` | VS Code Copilot |
| `CONVENTIONS.md` / `.aider.conf.yml` | aider |
| `CONTRIBUTING.md` | General project conventions |
| `.editorconfig` | Editor formatting rules |

### Step 2: Analyze the codebase for anything not covered by existing docs

Scan real code to discover patterns. Before writing each spec file:
- Find 2-3 real examples of each pattern in the codebase.
- Reference real file paths (not hypothetical ones).
- Document anti-patterns the team clearly avoids.

### Step 3: Document reality, not ideals

**Critical**: write what the code *actually does*, not what it should do.
Sub-agents match the spec, so aspirational patterns that don't exist in the
codebase will cause sub-agents to write code that looks out of place.

If the team has known tech debt, document the current state — improvement
is a separate conversation, not a bootstrap concern.

---

## Quick explainer of the runtime (share when they ask "why do we need spec at all")

- Every AI coding task spawns two sub-agents: `trellis-implement` (writes
  code) and `trellis-check` (verifies quality).
- Each task has `implement.jsonl` / `check.jsonl` manifests listing which
  spec files to load.
- The platform hook auto-injects those spec files + the task's `prd.md`
  into every sub-agent prompt, so the sub-agent codes/reviews per team
  conventions without anyone pasting them manually.
- Source of truth: `.trellis/spec/`. That's why filling it well now pays
  off forever.

---

## Completion

When the developer confirms the checklist items above are done with real
examples (not placeholders), guide them to run:

```bash
python3 ./.trellis/scripts/task.py finish
python3 ./.trellis/scripts/task.py archive 00-bootstrap-guidelines
```

After archive, every new developer who joins this project will get a
`00-join-<slug>` onboarding task instead of this bootstrap task.

---

## Suggested opening line

"Welcome to Trellis! Your init just set me up to help you fill the project
spec — a one-time setup so every future AI session follows the team's
conventions instead of writing generic code. Before we start, do you have
any existing convention docs (CLAUDE.md, .cursorrules, CONTRIBUTING.md,
etc.) I can pull from, or should I scan the codebase from scratch?"
