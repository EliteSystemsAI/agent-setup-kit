#!/usr/bin/env python3
"""Put the kit in a private work folder."""

import argparse
import os
import sys
from pathlib import Path


KIT = Path(__file__).resolve().parents[1]
TOOLS = ("claude-code", "codex", "cursor")
COPIES = (
    ("docs/start.md", "START.md"),
    ("docs/swap-accounts.md", "docs/swap-accounts.md"),
    ("docs/memory.md", "docs/memory.md"),
    ("docs/plugins/Hermes.md", "docs/plugins/Hermes.md"),
    ("docs/plugins/gbrain.md", "docs/plugins/gbrain.md"),
    ("docs/plugins/Linear.md", "docs/plugins/Linear.md"),
    ("prompts/CEO.md", "prompts/CEO.md"),
    ("prompts/COO.md", "prompts/COO.md"),
    ("prompts/WORKER.md", "prompts/WORKER.md"),
    ("templates/HANDOFF.md", "templates/HANDOFF.md"),
    ("templates/TASK.md", "templates/TASK.md"),
    ("templates/HANDOFF.md", "ceo/HANDOFF.md"),
    ("templates/HANDOFF.md", "coo/HANDOFF.md"),
    ("templates/INBOX.md", "coo/INBOX.md"),
    ("templates/OUTBOX.md", "coo/OUTBOX.md"),
    ("templates/TRACKER.md", "coo/TRACKER.md"),
    ("scripts/memory.py", "scripts/memory.py"),
)


def write_once(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as file:
            file.write(content)
    except FileExistsError:
        pass


def install(root, tools):
    root.mkdir(parents=True, exist_ok=True)
    (root / "workers").mkdir(exist_ok=True)
    for source, target in COPIES:
        write_once(root / target, (KIT / source).read_bytes())
    settings = "# My setup\n\nTools: " + ", ".join(tools) + "\n\nAll add-ons start off.\n"
    write_once(root / "SETUP.md", settings.encode("utf-8"))


def check(root):
    for name in ("SETUP.md", *(target for _, target in COPIES)):
        path = root / name
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"Missing or empty: {path}")
    if not (root / "workers").is_dir():
        raise ValueError(f"Missing worker folder: {root / 'workers'}")

    for folder in ("ceo", "coo", "templates"):
        path = root / folder / "HANDOFF.md"
        lines = path.read_text(encoding="utf-8").splitlines()
        for heading in ("Goal", "State", "Next", "Log"):
            if f"## {heading}" not in lines:
                raise ValueError(f"Missing {heading} in {path}")
    print(f"Local setup passed: {root}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.home() / ".agent-setup")
    parser.add_argument("--tools", nargs="+", choices=TOOLS)
    parser.add_argument("--notion-page", help="Set up memory under this Notion page")
    parser.add_argument("--check", action="store_true", help="Check local files only")
    args = parser.parse_args()
    if not args.check and not args.tools:
        parser.error("pick tools with --tools")
    root = args.root.expanduser().resolve()
    if root == KIT or KIT in root.parents:
        parser.error("pick a work folder outside this kit")

    os.umask(0o077)
    if not args.check:
        install(root, dict.fromkeys(args.tools))
    check(root)
    if args.notion_page and not args.check:
        from memory import setup_memory

        setup_memory(root, args.notion_page)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(str(error))
