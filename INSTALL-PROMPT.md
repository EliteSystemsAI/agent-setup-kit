# Set up my agent team

Set up this kit for me. Start in the kit folder. Read `README.md`, `docs/herdr.md`, `docs/memory.md`, `docs/writing.md` and `docs/start.md`.

1. Use the team tools and private folder I gave you. If I gave no tool list, detect my available tools and tell me which ones you will use. Ask only if you cannot tell which tools or staff Notion page to use. Default to `~/.agent-setup`. Keep distinct teams in separate folders.
2. Run `python3 scripts/install.py --tools codex claude-code hermes`, using my actual tool list and adding `--root` if needed. Use `cursor` for Cursor. Rerun this command to upgrade an existing install. Keep its work notes and current memory connection.
3. Reuse the installed `memory.json` if it points to the staff-approved brain. Otherwise use `docs/memory.md` to connect every runtime to the same staff Notion page. Use a token already supplied by my secret manager. If it is missing, give me the setup command to run in my terminal with the hidden prompt. Never ask me to paste a token in chat. Run the memory check from the installed work folder.
4. Set up the Herdr layout in my dedicated team session. If Herdr is unavailable, use its official install guide and the install method allowed on my machine. From a Herdr shell, run `python3 scripts/team.py layout --start --ceo-tool codex --coo-tool claude-code` with my chosen tools. It starts launchers in new panes and leaves existing panes alone. If you cannot control my terminal, give me that command to run there. Never start a second agent in an occupied role.
5. Verify the CEO and COO loaded the same active memory, the COO can add a worker tab, and the installed Codex, Claude Code, Cursor and Hermes instructions specify the required memory and writing rules. If using remote Hermes, follow `docs/plugins/Hermes.md` on its host. Keep Linear and other optional connections off unless requested.
6. Run `python3 scripts/install.py --check` from the kit with the same `--root` if used. Tell me the work folder and what is ready. Flag any blocked access or runtime sign-in in one line. The CEO can take the first goal after Herdr and Team Memory are ready.

For a dry test, use a temporary work folder and run only the local install and check. Use no network, credentials or active Herdr session.
