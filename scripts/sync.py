#!/usr/bin/env python3
"""Sync and symlink curated agent skills globally across coding-agent harnesses."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
from typing import Any

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "manifest.json"
CLONE_ROOT = pathlib.Path.home() / ".agents" / "repos"
STATE_PATH = CLONE_ROOT / ".workspace-skills-state.json"


def run(cmd: list[str], cwd: pathlib.Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def expand(path_str: str) -> pathlib.Path:
    return pathlib.Path(os.path.expanduser(path_str)).resolve()


def load_manifest() -> dict[str, Any]:
    with MANIFEST_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def ensure_repo(entry: dict[str, Any], update: bool) -> pathlib.Path:
    clone_id = entry.get("reuse_clone") or entry["id"]
    dest = CLONE_ROOT / clone_id
    if not dest.exists():
        CLONE_ROOT.mkdir(parents=True, exist_ok=True)
        print(f"[clone] {entry['url']} -> {dest}")
        run(["git", "clone", "--depth", "1", entry["url"], str(dest)])
    elif update and not entry.get("reuse_clone"):
        print(f"[pull]  {dest}")
        run(["git", "-C", str(dest), "pull", "--ff-only"])
    return dest


def discover_skills(entry: dict[str, Any], clone_dir: pathlib.Path) -> list[tuple[pathlib.Path, str]]:
    """Return list of (skill_dir, context_slug) pairs for a manifest repo entry."""
    results: list[tuple[pathlib.Path, str]] = []
    mode = entry["mode"]

    if mode == "glob":
        root = (clone_dir / entry.get("root", ".")).resolve()
        exclude = set(entry.get("exclude_dirs", []))
        for skill_md in sorted(root.rglob("SKILL.md")):
            sdir = skill_md.parent
            rel_parts = sdir.relative_to(clone_dir).parts
            if any(part in exclude for part in rel_parts):
                continue
            context_slug = rel_parts[0] if len(rel_parts) > 1 else entry["id"]
            results.append((sdir, context_slug))
    elif mode == "list":
        for rel in entry.get("paths", []):
            sdir = (clone_dir / rel).resolve()
            if not (sdir / "SKILL.md").exists():
                print(f"[warn]  missing SKILL.md at {sdir}", file=sys.stderr)
                continue
            rel_parts = sdir.relative_to(clone_dir).parts
            context_slug = rel_parts[0] if len(rel_parts) > 1 else entry["id"]
            results.append((sdir, context_slug))
    else:
        raise ValueError(f"Unsupported repo mode: {mode}")

    return results


def load_state() -> dict[str, list[str]]:
    if not STATE_PATH.exists():
        return {}
    try:
        with STATE_PATH.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
            if isinstance(data, dict):
                return {str(k): list(v) for k, v in data.items()}
    except (OSError, json.JSONDecodeError):
        pass
    return {}


def save_state(state: dict[str, list[str]]) -> None:
    CLONE_ROOT.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)
        fh.write("\n")


def clean_managed(targets: list[pathlib.Path] | None = None) -> int:
    state = load_state()
    removed = 0
    keys = [str(t) for t in targets] if targets is not None else list(state.keys())
    for t_str in keys:
        t_dir = pathlib.Path(t_str)
        for name in state.get(t_str, []):
            link = t_dir / name
            if link.is_symlink():
                link.unlink()
                removed += 1
        state.pop(t_str, None)
    save_state(state)
    return removed


def cmd_status(manifest: dict[str, Any]) -> None:
    state = load_state()
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"Clones:   {CLONE_ROOT}")
    if CLONE_ROOT.exists():
        repos = sorted(p.name for p in CLONE_ROOT.iterdir() if p.is_dir() and not p.name.startswith("."))
        print(f"  present ({len(repos)}): {', '.join(repos)}")
    else:
        print("  none cloned yet")

    all_targets = [expand(t) for t in manifest["default_targets"] + manifest.get("extra_targets", [])]
    print("Targets:")
    for t in all_targets:
        managed = len(state.get(str(t), []))
        total = len(list(t.iterdir())) if t.exists() else 0
        if total or managed or str(t) in [str(expand(d)) for d in manifest["default_targets"]]:
            print(f"  {t}: {total} total ({managed} managed)")


def cmd_sync(args: argparse.Namespace, manifest: dict[str, Any]) -> None:
    enabled_groups = {"core", "design"}
    if args.include_partner:
        enabled_groups.add("partner")
    if args.include_personal:
        enabled_groups.add("personal")

    target_strs = list(manifest["default_targets"])
    if args.all_agents:
        target_strs.extend(manifest.get("extra_targets", []))
    if args.target:
        target_strs.extend(args.target)

    # Deduplicate targets while preserving order
    targets: list[pathlib.Path] = []
    seen_t: set[pathlib.Path] = set()
    for t_str in target_strs:
        tp = expand(t_str)
        if tp not in seen_t:
            seen_t.add(tp)
            targets.append(tp)

    # Collect skills in manifest order with deterministic collision resolution
    planned: dict[str, pathlib.Path] = {}
    renamed: list[tuple[str, str]] = []

    for entry in manifest["repos"]:
        if entry.get("group", "core") not in enabled_groups:
            continue
        clone_dir = ensure_repo(entry, update=args.update)
        discovered = discover_skills(entry, clone_dir)

        # Count internal duplicates within this repo entry
        internal_counts: dict[str, int] = {}
        for sdir, _ in discovered:
            base = sdir.name if sdir != clone_dir else entry["id"]
            internal_counts[base] = internal_counts.get(base, 0) + 1

        prefix = entry.get("collision_prefix", entry["id"])
        for sdir, context_slug in discovered:
            base = sdir.name if sdir != clone_dir else entry["id"]
            if base in planned:
                candidate = f"{prefix}-{context_slug}-{base}" if context_slug != base else f"{prefix}-{base}"
                renamed.append((f"{entry['id']}/{sdir.relative_to(clone_dir)}", candidate))
            elif internal_counts[base] > 1:
                candidate = f"{context_slug}-{base}"
                if candidate in planned:
                    candidate = f"{prefix}-{context_slug}-{base}"
                renamed.append((f"{entry['id']}/{sdir.relative_to(clone_dir)}", candidate))
            else:
                candidate = base

            # Final fallback if still colliding
            if candidate in planned:
                rel_slug = "-".join(sdir.relative_to(clone_dir).parts)
                candidate = f"{prefix}-{rel_slug}"
            planned[candidate] = sdir

    state = load_state()
    for t in targets:
        t.mkdir(parents=True, exist_ok=True)
        prev_managed = set(state.get(str(t), []))
        new_managed: list[str] = []

        # Remove stale symlinks previously managed by this tool
        for stale in sorted(prev_managed - set(planned.keys())):
            stale_path = t / stale
            if stale_path.is_symlink():
                stale_path.unlink()

        for name, src in sorted(planned.items()):
            link = t / name
            if link.is_symlink():
                if link.resolve() != src:
                    link.unlink()
                    link.symlink_to(src)
            elif link.exists():
                print(f"[skip]  non-symlink exists at {link}", file=sys.stderr)
                continue
            else:
                link.symlink_to(src)
            new_managed.append(name)

        state[str(t)] = new_managed

    save_state(state)

    print(f"\nSynced {len(planned)} skills into {len(targets)} target dir(s):")
    for t in targets:
        print(f"  - {t}")
    if renamed:
        print(f"Disambiguated {len(renamed)} name collision(s):")
        for src_label, final_name in renamed:
            print(f"  - {src_label} -> {final_name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Install and sync Doniyor's global agent skills.")
    parser.add_argument("--update", action="store_true", help="git pull --ff-only existing clones before linking")
    parser.add_argument("--status", action="store_true", help="show installed repos and target directories")
    parser.add_argument("--clean", action="store_true", help="remove all symlinks managed by this repo")
    parser.add_argument("--all-agents", action="store_true", help="link into all extra agent-specific directories")
    parser.add_argument("--include-partner", action="store_true", help="also link partner-built skills from knowledge-work-plugins")
    parser.add_argument("--include-personal", action="store_true", help="also link doniyor117/no-ai-slop and doniyor117/writing-skill")
    parser.add_argument("--target", action="append", help="additional skill target directory (repeatable)")
    args = parser.parse_args()

    manifest = load_manifest()

    if args.status:
        cmd_status(manifest)
        return 0
    if args.clean:
        removed = clean_managed()
        print(f"Removed {removed} managed symlink(s).")
        return 0

    cmd_sync(args, manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
