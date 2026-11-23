# Agent Setup Kit

Use three kinds of chat to run a project. The **CEO** talks to you. The **COO** runs the work and writes one outbox. A **worker** does one job and reports to the COO.

## Set it up

1. Clone this kit. Open it in Codex, Claude Code, Cursor or Hermes with terminal access. Use Python 3.9 or newer.
2. Paste [INSTALL-PROMPT.md](INSTALL-PROMPT.md) into a fresh chat. Use a staff-approved Notion Team Memory page. Enter credentials in your terminal or approved secret manager.
3. Open `SETUP.md` in the private work folder. Set up the [Herdr layout](docs/herdr.md) and launch a CEO and COO. The COO adds one worker tab per job. Each command-line launcher checks the same Notion brain before starting the agent.

You can also run this command from a terminal in the kit folder.

```sh
python3 scripts/install.py --tools codex claude-code hermes
```

Use any of `claude-code`, `codex`, `cursor` and `hermes`. Add `--notion-page` and the shared Notion parent page to connect memory in the same run. [Set up Notion](docs/memory.md) shows how to use the connection. The work folder defaults to `~/.agent-setup`. Pass `--root` for a separate team.

To upgrade, pull the latest kit and rerun the installer with your tools and the same work folder. It updates kit scripts, guides and role prompts, and keeps a copy of each replaced file under `.kit-backup/`. It preserves team handoffs, worker jobs and the existing Notion connection. It updates only the marked team rules in existing project instruction files.

## When you work

- [Start work and send reports](docs/start.md)
- [Swap tools or accounts](docs/swap-accounts.md)
- [Use shared memory in Notion](docs/memory.md)
- [Write Linear updates and documentation](docs/writing.md)

Linear and gbrain connections are optional. Each has its own guide in [docs/plugins](docs/plugins).
