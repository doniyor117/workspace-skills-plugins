# Agent instructions — workspace-skills-plugins

This repository is Doniyor's portable manifest and bootstrapper for global AI coding-agent skills.
When setting up a new machine, container, or agent environment, follow this file directly instead
of re-researching or re-picking skills from scratch.

## Quick bootstrap (do this first)

Run from the repository root:

```bash
./scripts/install.sh
```

What this does:
1. Shallow-clones the curated skill repositories into `~/.agents/repos/`.
2. Symlinks every configured skill into the shared global directories:
   - `~/.agents/skills/` (Codex, Gemini CLI, Cursor, VS Code / GitHub Copilot, OpenCode, Antigravity)
   - `~/.claude/skills/` (Claude Code, Cursor, OpenCode)
3. Resolves name collisions deterministically in `manifest.json` order (earlier entries keep the bare name; later collisions are prefixed).

### Useful flags

- `./scripts/install.sh --update` — pull latest commits (`git pull --ff-only`) in all cloned repos and refresh symlinks.
- `./scripts/install.sh --all-agents` — also symlink into agent-specific global paths (`~/.gemini/skills`, `~/.gemini/antigravity/skills`, `~/.codex/skills`, `~/.cursor/skills`, `~/.copilot/skills`, `~/.config/opencode/skills`).
- `./scripts/install.sh --target <dir>` — add any custom skill directory for the current harness.
- `./scripts/install.sh --include-personal` — also link `doniyor117/no-ai-slop` and `doniyor117/writing-skill`.
- `./scripts/install.sh --include-partner` — also link the 71 `partner-built/` vendor skills from `anthropics/knowledge-work-plugins`.
- `./scripts/install.sh --status` — check cloned repos and linked counts.
- `./scripts/install.sh --clean` — remove symlinks managed by this repo without touching unmanaged skills.

If the current agent harness uses a built-in skill registry instead of filesystem paths, read
`manifest.json` and load only the specific skills the user asks for from `~/.agents/repos/`.

## Source of truth & maintenance rules

- **`manifest.json` is the single source of truth.** Do not hardcode skill lists in scripts.
- To add or remove a skill or repository:
  1. Edit `manifest.json`.
  2. Run `./scripts/install.sh` and verify zero missing paths or unexpected collisions.
  3. Update the summary table in `README.md` so humans stay in sync.
  4. Commit and push.
- **Public repository:** never commit tokens, API keys, `.env` files, private repository URLs, or personal contact details.
- Keep `AGENTS.md` concise (< 8 KiB) so any agent can load it cleanly at session start.
