# Shared memory in Notion

Keep facts the team will need again. One row holds one fact. The Inbox holds new facts for a human to check.

Use one staff-approved brain per team. Connect Codex, Claude Code, Cursor and Hermes to that same database. Keep the executive brain and other teams' private content outside this connection. When a second machine joins, install the kit there and use the same parent page instead of making a new one.

## Set it up

1. Make a blank Notion page called Team Memory. Keep it private or share it with your team. Set up the database once and use it for all your chats.
2. Open the [Notion Developer portal](https://www.notion.so/my-integrations). Click **New integration**. Pick your workspace and **Internal**. Name it Agent Memory. If you don't own the workspace, ask its owner to set up the connection and give your team access.
3. Find **Capabilities** in the connection settings. Turn on **Read content**, **Insert content**, and **Update content** for setup. In **Configuration**, copy the API token. Keep it in a place for secrets.
4. Open Team Memory. Click **•••**, then **Add connections**. Pick Agent Memory and confirm. Copy the Team Memory page link.
5. In your own terminal, go to the work folder. Run the setup command. Replace `PAGE_LINK` with the link you copied. Enter the token when the script asks. It hides what you type.

```sh
cd "$HOME/.agent-setup"
python3 scripts/memory.py setup "PAGE_LINK"
```

If you chose another work folder, use its path in the first line. The script makes the database and two views. It saves the link and IDs in `memory.json`. Keep that file in the private work folder so each chat can use the same database. Keep your token out of chats, notes, and Git.

If setup stopped, run the same command again with the same link. On each machine, use `python3 scripts/memory.py check` to check the fields, views, and read access. Compare the printed database link on all machines. If Notion says 401, check the token. For 403, check the boxes in step 3. For 404, check the page link and step 4.

## Database template

| Field | Type | What to put there |
| --- | --- | --- |
| Name | Title | A short name for the fact |
| Fact | Text | One clear fact and when to use it |
| Source | Text | A link or short note that shows where it came from |
| State | Select | Proposed, Active, or Retired |
| Added | Created time | Set by Notion |

- **Inbox** shows rows where State is Proposed.
- **Active facts** shows rows where State is Active.
- Both lists show the newest rows first. For either view, use **Filter → State → Is** to fix its State filter.

Use the page's share settings to pick who can see the facts. Views can hide rows on screen. Anyone with full read access to the database can still see all the rows.

## Read at the start of each chat or scheduled job

1. Read your handoff.
2. From the work folder, run `python3 scripts/memory.py context`. It reads the active facts. Run `python3 scripts/memory.py search "topic"` before asking a question or relying on a past decision.
3. Use facts that fit the job. If you cannot read the facts, tell the COO and fix access before making decisions that depend on them.

Agents with terminal access need `NOTION_TOKEN` supplied by the approved secret store or team launcher. The CLI launcher checks the selected brain before starting an agent. It can ask for a token at a hidden prompt and pass it to that agent process. Use a process secret for unattended jobs. The kit does not save tokens to disk.

## Propose, review, read

1. **Propose.** At task close, check for a new lasting rule, decision or fact. Search for it first. The command also checks for an exact duplicate in the **Inbox** and **Active facts** before it adds a Proposed row. Add a source. Leave out keys, passwords, task logs, and private facts the team should not see. Run this command from the work folder.

   ```sh
   python3 scripts/memory.py propose <<'JSON'
   {"name":"Test command","fact":"Run make test before you send a change for review.","source":"Project guide"}
   JSON
   ```

2. **Review.** Pick a human to check the Inbox. They check the source and fix the words if needed. They set a true, useful fact to Active and a bad or old fact to Retired. If a new fact takes the place of an old one, they retire the old row too.
3. **Read.** Each chat reads active facts when it starts. Read them again after a review if you need the latest facts.

Use a harmless test fact to verify a new team. Propose from one runtime and check the Inbox. Ask the human reviewer to activate it, then run `search` from the other runtimes to confirm they see it. Ask the reviewer to retire it and verify it is gone from active results.

Role prompts and project instruction files require this procedure. Use the dedicated team working directory and the launcher so each supported runtime loads those rules. Notion sharing controls which data the integration can access.
