#!/usr/bin/env python3
"""Put the kit in a private work folder."""

import argparse
import hashlib
import os
import sys
import tempfile
from pathlib import Path


KIT = Path(__file__).resolve().parents[1]
STARTERS = {
    "claude-code": ("Claude Code", "Open a terminal in the work folder and run `claude`."),
    "codex": ("Codex", "Open a terminal in the work folder and run `codex`."),
    "cursor": ("Cursor", "Open the work folder in Cursor and start a new Agent chat."),
    "hermes": ("Hermes", "Use the team launcher or set your Hermes job's working directory to this folder."),
}
MANAGED = (
    ("docs/start.md", "START.md"),
    ("docs/swap-accounts.md", "docs/swap-accounts.md"),
    ("docs/memory.md", "docs/memory.md"),
    ("docs/herdr.md", "docs/herdr.md"),
    ("docs/writing.md", "docs/writing.md"),
    ("docs/plugins/Hermes.md", "docs/plugins/Hermes.md"),
    ("docs/plugins/gbrain.md", "docs/plugins/gbrain.md"),
    ("docs/plugins/Linear.md", "docs/plugins/Linear.md"),
    ("prompts/CEO.md", "prompts/CEO.md"),
    ("prompts/COO.md", "prompts/COO.md"),
    ("prompts/WORKER.md", "prompts/WORKER.md"),
    ("scripts/memory.py", "scripts/memory.py"),
    ("scripts/team.py", "scripts/team.py"),
)
INSTRUCTIONS = (
    ("templates/AGENTS.md", "AGENTS.md", ""),
    ("templates/AGENTS.md", "CLAUDE.md", ""),
    ("templates/AGENTS.md", ".cursor/rules/agent-setup.mdc",
     "---\ndescription: Shared team memory and writing rules\nalwaysApply: true\n---\n\n"),
)
WORK_FILES = (
    ("templates/HANDOFF.md", "templates/HANDOFF.md"),
    ("templates/TASK.md", "templates/TASK.md"),
    ("templates/HANDOFF.md", "ceo/HANDOFF.md"),
    ("templates/HANDOFF.md", "coo/HANDOFF.md"),
    ("templates/INBOX.md", "coo/INBOX.md"),
    ("templates/OUTBOX.md", "coo/OUTBOX.md"),
    ("templates/TRACKER.md", "coo/TRACKER.md"),
)


def write_once(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as file:
            file.write(content)
    except FileExistsError:
        pass


def replace_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as file:
        temporary = Path(file.name)
        try:
            file.write(content)
            file.close()
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


def install_instructions(root, source, target, preamble):
    path = root / target
    opening = "<!-- agent-setup-kit:start -->"
    closing = "<!-- agent-setup-kit:end -->"
    block = f"{opening}\n{(KIT / source).read_text(encoding='utf-8').strip()}\n{closing}"
    previous = path.read_text(encoding="utf-8") if path.exists() else ""
    if opening in previous and closing in previous:
        start = previous.index(opening)
        end = previous.index(closing, start) + len(closing)
        content = previous[:start] + block + previous[end:]
    elif previous:
        content = previous.rstrip() + "\n\n" + block + "\n"
    else:
        content = preamble + block + "\n"
    if content != previous:
        replace_file(path, content.encode("utf-8"))


def install(root, tools):
    root.mkdir(parents=True, exist_ok=True)
    (root / "workers").mkdir(exist_ok=True)
    for source, target in WORK_FILES:
        write_once(root / target, (KIT / source).read_bytes())
    for source, target in MANAGED:
        path = root / target
        content = (KIT / source).read_bytes()
        if path.exists():
            current = path.read_bytes()
            if current == content:
                continue
            # Keep the previous copy of an upgraded guide, script or prompt.
            digest = hashlib.sha256(current).hexdigest()[:12]
            backup = root / ".kit-backup" / digest / target
            write_once(backup, current)
        replace_file(path, content)
    for source, target, preamble in INSTRUCTIONS:
        install_instructions(root, source, target, preamble)

    links = []
    for tool in tools:
        name, opening = STARTERS[tool]
        path = f"starters/{tool}.md"
        guide = f"# Start in {name}\n\n{opening}\n\nUse the role messages in [START.md](../START.md).\n"
        write_once(root / path, guide.encode("utf-8"))
        links.append(f"- [{name}]({path})")

    settings = f"# My setup\n\nTools: {', '.join(tools)}\n\n"
    settings += (
        "\n".join(links)
        + "\n\n[Set up Herdr](docs/herdr.md) · [Connect team memory](docs/memory.md)"
        + " · [Writing rules](docs/writing.md)\n"
    )
    replace_file(root / "SETUP.md", settings.encode("utf-8"))


def check(root):
    for name in (
        "SETUP.md", *(target for _, target in MANAGED + WORK_FILES),
        *(target for _, target, _ in INSTRUCTIONS),
    ):
        path = root / name
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"Missing or empty: {path}")
    for _, target, _ in INSTRUCTIONS:
        if "<!-- agent-setup-kit:start -->" not in (root / target).read_text(encoding="utf-8"):
            raise ValueError(f"Missing team rules: {root / target}. Run the installer again.")
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
