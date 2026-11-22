# Agent Setup Kit

Use three kinds of chat to run a project. The **CEO** talks to you. The **COO** runs the work and writes one outbox. A **worker** does one job and reports to the COO.

## Set it up

1. Open this kit folder in Claude Code, Codex, or Cursor. The agent needs to read files and run terminal commands. You need Python 3.9 or newer.
2. Paste all of [INSTALL-PROMPT.md](INSTALL-PROMPT.md) into a fresh chat. It sets up a private work folder. For Notion, have a page link and a token you can enter in your own terminal.
3. Open `SETUP.md` in the work folder. It links to a starter for each tool you picked. Follow [Start work](docs/start.md) once your chats are open. You can mix tools and accounts.

You can also run this command from a terminal in the kit folder.

```sh
python3 scripts/install.py --tools codex
```

Use any of `claude-code`, `codex`, and `cursor`. List more than one after `--tools` if you mix tools. Add `--notion-page` and your Notion page link to set up memory in the same run. [Set up Notion](docs/memory.md) shows how to get the page link and token. The kit uses your home folder by default. Pass `--root` with a folder path to pick a different spot.

Run the same command with a new list of tools to update `SETUP.md`. Keep your own notes in the handoffs.

## When you work

- [Start work and send reports](docs/start.md)
- [Swap tools or accounts](docs/swap-accounts.md)
- [Use shared memory in Notion](docs/memory.md)

Extra tools start off. Turn on only the ones you want. Each has its own guide in [docs/plugins](docs/plugins).
