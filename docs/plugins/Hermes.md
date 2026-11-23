# Hermes

Use a Hermes profile that has access to the team's own files and Notion connection.

1. On the Hermes host, install the kit in a private work folder with `--tools hermes`. Connect it to the same Notion parent page used by Codex and Claude Code. Use a staff-approved connection scoped to that page. Run `python3 scripts/memory.py check` on the host and compare the database link with the other tools.
2. Set the Hermes working directory to that work folder. Hermes reads the installed `AGENTS.md` there. If this runtime uses a higher-priority `.hermes.md`, add the marked team rules to that file too. [Hermes context files](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files)
3. Give every unattended job the work folder and the team's `NOTION_TOKEN` from its runtime secret store. In the job's instructions, require `python3 scripts/memory.py context` before work and a sourced proposal for each new lasting fact at close. For an interactive Hermes session, use `python3 scripts/team.py launch hermes worker --job <job>`.
4. Test the same harmless memory fact across Hermes, Codex and Claude Code. Check that a proposal from Hermes reaches the shared Inbox and that the other tools can search it after a human activates it.
5. Send one result to the COO or its handoff. Start a schedule after the test passes. Give the job access only to the files and tools it needs.
