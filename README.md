# workspace-skills-plugins

My day-to-day global skills and plugins setup for AI coding agents (Claude Code, Codex, Antigravity, Gemini CLI, Cursor, OpenCode, GitHub Copilot).

One command installs the whole curated set in any fresh environment so I don't have to re-research or re-pick skills when switching agents or machines.

## Quick start

```bash
git clone https://github.com/doniyor117/workspace-skills-plugins.git
cd workspace-skills-plugins
./scripts/install.sh
```

Requires `git` and `python3`. Skills are shallow-cloned into `~/.agents/repos/` and symlinked into `~/.agents/skills/` and `~/.claude/skills/`.

### Common commands

| Command | What it does |
| --- | --- |
| `./scripts/install.sh` | Clone missing repos and link all default skills (241 total) |
| `./scripts/install.sh --update` | `git pull --ff-only` all repos and refresh symlinks |
| `./scripts/install.sh --all-agents` | Also link into `~/.gemini/skills`, `~/.gemini/antigravity/skills`, `~/.codex/skills`, `~/.cursor/skills`, `~/.copilot/skills`, `~/.config/opencode/skills` |
| `./scripts/install.sh --include-personal` | Also include `doniyor117/no-ai-slop` and `doniyor117/writing-skill` |
| `./scripts/install.sh --include-partner` | Also include 71 `partner-built/` vendor skills from `anthropics/knowledge-work-plugins` |
| `./scripts/install.sh --status` | Show cloned repos and linked skill counts |
| `./scripts/install.sh --clean` | Remove symlinks managed by this repo |

## Included skill packs

Defined in [`manifest.json`](./manifest.json).

### Core engineering & knowledge work
- **[`doniyor117/matpockock-skills`](https://github.com/doniyor117/matpockock-skills)** (35 skills) — engineering, productivity, and in-progress skills (`deprecated/` and `misc/` excluded). Keeps priority on `code-review`.
- **[`anthropics/knowledge-work-plugins`](https://github.com/anthropics/knowledge-work-plugins)** (181 skills) — all 17 first-party Anthropic plugins (`design`, `engineering`, `data`, `product-management`, `productivity`, `marketing`, `finance`, `legal`, `human-resources`, `sales`, `small-business`, `customer-support`, `operations`, `enterprise-search`, `bio-research`, `cowork-plugin-management`, `pdf-viewer`). Includes 7 design workflow skills (`design-critique`, `design-system`, `design-handoff`, `accessibility-review`, `ux-copy`, `user-research`, `research-synthesis`).

### Curated design & UI skills (25 skills)
- **Anthropic** ([`anthropics/skills`](https://github.com/anthropics/skills) & [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official)) — `frontend-design`, `canvas-design`, `theme-factory`, `web-artifacts-builder`, `algorithmic-art`, `playground`.
- **Google Labs Stitch** ([`google-labs-code/stitch-skills`](https://github.com/google-labs-code/stitch-skills)) — `taste-design`, `design-md`, `site-md`, `extract-design-md`, `manage-design-system`, `code-to-design`, `generate-design`, `react-components`, `react-vite-dashboard`, `shadcn-ui`, `remotion`.
- **OpenAI** ([`openai/skills`](https://github.com/openai/skills)) — `figma`, `figma-use`, `figma-implement-design`, `figma-create-design-system-rules`, `figma-generate-design`, `figma-generate-library`, `figma-code-connect-components`, `imagegen`.

### Optional personal skills (`--include-personal`)
- **[`doniyor117/no-ai-slop`](https://github.com/doniyor117/no-ai-slop)** — anti-slop writing pass.
- **[`doniyor117/writing-skill`](https://github.com/doniyor117/writing-skill)** — personal voice & writing guide.

## For AI agents

See [`AGENTS.md`](./AGENTS.md) for automated setup and maintenance rules.
