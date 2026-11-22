#!/usr/bin/env python3
"""Put the kit in a private work folder."""

import argparse
import os
import sys
import tempfile
from pathlib import Path


KIT = Path(__file__).resolve().parents[1]
STARTERS = {
    "claude-code": ("Claude Code", "Open a terminal in the work folder and run `claude`."),
    "codex": ("Codex", "Open a terminal in the work folder and run `codex`."),
    "cursor": ("Cursor", "Open the work folder in Cursor and start a new Agent chat."),
}
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

    links = []
    for tool in tools:
        name, opening = STARTERS[tool]
        path = f"starters/{tool}.md"
        guide = f"# Start in {name}\n\n{opening}\n\nUse the role messages in [START.md](../START.md).\n"
        write_once(root / path, guide.encode("utf-8"))
        links.append(f"- [{name}]({path})")

    settings = f"# My setup\n\nTools: {', '.join(tools)}\n\n"
    settings += "\n".join(links) + "\n\nAll add-ons start off.\n"
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=root, delete=False) as file:
        temporary = Path(file.name)
        try:
            file.write(settings)
            file.close()
            temporary.replace(root / "SETUP.md")
        finally:
            temporary.unlink(missing_ok=True)


def check(root):
    for name in ("SETUP.md", *(target for _, target in COPIES)):
        path = root / name
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"Missing or empty: {path}")
    if not (root / "workers").is_dir():
        raise ValueError(f"Missing worker folder: {root / 'workers'}")

    settings = (root / "SETUP.md").read_text(encoding="utf-8").splitlines()
    tools = next((line[len("Tools: "):] for line in settings if line.startswith("Tools: ")), "")
    for tool in tools.split(", "):
        if tool not in STARTERS:
            raise ValueError("Pick your tools again with --tools.")
        path = root / "starters" / f"{tool}.md"
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"Missing or empty: {path}. Run the installer with --tools to add it.")

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
    parser.add_argument("--tools", nargs="+", choices=tuple(STARTERS))
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
        install(root, tuple(dict.fromkeys(args.tools)))
    check(root)
    if args.notion_page and not args.check:
        from memory import setup_memory

        setup_memory(root, args.notion_page)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(str(error))
