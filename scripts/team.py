#!/usr/bin/env python3
"""Create the Herdr team layout and launch agents with Team Memory."""

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from memory import get_token, read_config, require_memory


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = "Agent Team"
TOOLS = {
    "codex": ("codex",),
    "claude-code": ("claude",),
    "cursor": ("cursor-agent",),
    "hermes": ("hermes", "chat", "--query"),
}


def herdr(*args):
    result = subprocess.run(
        ("herdr", *args), capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise ValueError(f"Herdr {' '.join(args[:2])} failed: {result.stderr.strip()}")
    if args[:2] == ("pane", "run"):
        return None
    return json.loads(result.stdout)["result"]


def named(items, label):
    matches = [item for item in items if item.get("label") == label]
    if len(matches) > 1:
        raise ValueError(f"More than one Herdr item is named {label}. Use a dedicated team session.")
    return matches[0] if matches else None


def offer_launch(tab, tool, role, job=None, start_pane=None):
    command = [sys.executable, str(ROOT / "scripts/team.py"), "launch", tool, role]
    if job:
        command.extend(("--job", job))
    shell_command = shlex.join(command)
    if start_pane:
        herdr("pane", "run", start_pane, shell_command)
        print(f"{tab} · launcher sent to the new pane")
    else:
        print(f"{tab} · {shell_command}")


def setup_tools():
    lines = (ROOT / "SETUP.md").read_text(encoding="utf-8").splitlines()
    selected = next((line.removeprefix("Tools: ") for line in lines if line.startswith("Tools: ")), "")
    tools = selected.split(", ")
    if any(tool not in TOOLS for tool in tools):
        raise ValueError("Run the installer again and select the team tools.")
    return tools


def get_workspace():
    if os.environ.get("HERDR_ENV") != "1":
        raise ValueError("Open a shell inside Herdr, then run this command in that shell.")
    workspace = named(herdr("workspace", "list")["workspaces"], WORKSPACE)
    if workspace:
        return workspace["workspace_id"], None
    created = herdr("workspace", "create", "--cwd", str(ROOT), "--label", WORKSPACE, "--no-focus")
    workspace_id = created["workspace"]["workspace_id"]
    herdr("tab", "rename", created["tab"]["tab_id"], "01 CEO")
    return workspace_id, created["root_pane"]["pane_id"]


def ensure_tab(workspace_id, label):
    tabs = herdr("tab", "list", "--workspace", workspace_id)["tabs"]
    if named(tabs, label):
        return None
    created = herdr("tab", "create", "--workspace", workspace_id, "--cwd", str(ROOT),
                    "--label", label, "--no-focus")
    return created["root_pane"]["pane_id"]


def task_path(job):
    if not job or not re.fullmatch(r"[a-z][a-z0-9-]{0,31}", job):
        raise ValueError("Use a job slug with up to 32 lower-case letters, digits or hyphens.")
    return ROOT / "workers" / job / "TASK.md"


def launch(tool, role, job):
    if role == "worker":
        task = task_path(job)
        if not task.is_file():
            raise ValueError("The COO must create this worker's TASK.md before launch.")
    elif job:
        raise ValueError("--job applies to workers.")
    command = TOOLS[tool]
    if not shutil.which(command[0]):
        raise ValueError(f"Install and sign in to {tool} before launch.")
    config = read_config(ROOT)
    token = get_token()
    require_memory(config, token)
    prompt = (
        f"The private team work folder is {ROOT}. Read AGENTS.md and prompts/{role.upper()}.md. "
        "Load active Team Memory, then follow your role and acknowledge readiness."
    )
    if role == "worker":
        prompt += f" Your only job folder is {task.parent}."
    env = {**os.environ, "NOTION_TOKEN": token}
    os.chdir(ROOT)
    os.execvpe(command[0], (*command, prompt), env)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    layout = commands.add_parser("layout")
    layout.add_argument("--ceo-tool", choices=tuple(TOOLS))
    layout.add_argument("--coo-tool", choices=tuple(TOOLS))
    layout.add_argument("--start", action="store_true", help="Start launchers in new panes only.")
    worker = commands.add_parser("worker")
    worker.add_argument("job")
    worker.add_argument("--tool", choices=tuple(TOOLS))
    worker.add_argument("--start", action="store_true", help="Start the launcher in a new pane only.")
    start = commands.add_parser("launch")
    start.add_argument("tool", choices=tuple(TOOLS))
    start.add_argument("role", choices=("ceo", "coo", "worker"))
    start.add_argument("--job")
    args = parser.parse_args()

    if args.action == "launch":
        launch(args.tool, args.role, args.job)
        return
    if args.action == "worker" and not task_path(args.job).is_file():
        raise ValueError("The COO must create this worker's TASK.md before opening its tab.")
    configured = setup_tools()
    workspace_id, new_ceo = get_workspace()
    leadership = (("01 CEO", "ceo"), ("02 COO", "coo"))
    new_panes = {role: ensure_tab(workspace_id, label) for label, role in leadership}
    new_panes["ceo"] = new_ceo or new_panes["ceo"]
    if args.action == "layout":
        role_tools = {"ceo": args.ceo_tool, "coo": args.coo_tool}
        for label, role in leadership:
            tool = role_tools[role] or configured[0]
            offer_launch(label, tool, role, start_pane=new_panes[role] if args.start else None)
    else:
        label = f"03 Worker · {args.job}"
        new_worker = ensure_tab(workspace_id, label)
        offer_launch(label, args.tool or configured[0], "worker", args.job,
                     start_pane=new_worker if args.start else None)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        sys.exit(str(error))
