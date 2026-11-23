# Set up Herdr

Use one Herdr workspace with the tabs in this order.

```text
Agent Team
  01 CEO
    02 COO
      03 Worker · one job per tab
```

The tab order shows the roles. The inbox, outbox and job handoffs control who assigns work and where results go.

1. Install Herdr from [the Herdr quick start](https://herdr.dev/tui/docs/quick-start/). Install and sign in to your agent tools on this machine.
2. Open `herdr --session agent-team` in your terminal. Use a new session name for each team. Open a shell in that Herdr session.
3. In that shell, go to the installed work folder. Run `python3 scripts/team.py layout --start --ceo-tool codex --coo-tool claude-code`, using your chosen tools. The script creates the CEO and COO tabs and starts their launchers. It keeps existing panes and prints a launch command for each existing tab. Omit `--start` to create tabs only.
4. Use the printed command in its named tab if you need to start the agent manually. The tool can be `codex`, `claude-code`, `cursor` or `hermes`. The launcher checks Team Memory before the agent starts. If the terminal has no token, enter it at the hidden prompt.
5. The COO creates `workers/<job>/TASK.md` and `HANDOFF.md` from the templates, then runs `python3 scripts/team.py worker <job> --tool hermes --start` in Herdr, with the selected tool. Give the job one owner at a time.

For an IDE-only Cursor seat, open the installed work folder and use the messages in its `START.md`. The installed Cursor project rule applies to each chat in that folder.

To switch tools, save the handoff first. Start the replacement from the same folder and use the same job ID. [Swap tools or accounts](swap-accounts.md) has the full sequence.
