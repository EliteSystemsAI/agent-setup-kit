# Shared memory in Notion

Keep facts the team will need again. One row holds one fact. The Inbox holds new facts for a human to check.

## Set it up

1. Make a blank Notion page called Team Memory. Keep it private or share it with your team. Set up the database once and use it for all your chats.
2. If you own the workspace, open the [Notion Developer portal](https://app.notion.com/my-integrations). Click **New integration**. Pick your workspace and **Internal**. Name it Agent Memory.
3. Find **Capabilities** in the connection settings. Turn on **Read content**, **Insert content**, and **Update content** for setup. In **Configuration**, copy the API token. Keep it in a place for secrets.
4. Open Team Memory. Click **•••**, then **Add connections**. Pick Agent Memory and confirm. Copy the Team Memory page link.
5. In your own terminal, go to the work folder. Run the setup command. Replace `PAGE_LINK` with the link you copied. Enter the token when the script asks. It hides what you type.

```sh
cd "$HOME/.agent-setup"
python3 scripts/memory.py setup "PAGE_LINK"
```

If you chose another work folder, use its path in the first line. The script makes the database and two views. It saves the link and IDs in `memory.json`. Keep that file in the private work folder so each chat can use the same database. Keep your token out of chats, notes, and Git.

If setup stopped, run the same command again with the same link. Use `python3 scripts/memory.py check` to check the fields, views, and read access. If Notion says 401, check the token. For 403, check the boxes in step 3. For 404, check the page link and step 4.

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

## Read at the start of each chat

1. Read your handoff.
2. From the work folder, run `python3 scripts/memory.py context`. It reads the active facts. You can also open the **Active facts** view if your chat can read Notion that way.
3. Use only facts that fit the job. If you cannot read the facts, say so in your handoff. Ask the COO for help if your job needs a fact before you can go on.

Agents with terminal access need `NOTION_TOKEN` set in their own shell by your secret tool. Use the hidden prompt when you run setup, check, or context by hand. The propose command reads the fact from its input and needs the token in the shell.

## Propose, review, read

1. **Propose.** Check for an old copy first. If the fact is new, add a row with State set to Proposed. Add a source. Leave out keys, passwords, and private facts the team should not see. An agent can run this command from the work folder.

   ```sh
   python3 scripts/memory.py propose <<'JSON'
   {"name":"Test command","fact":"Run make test before you send a change for review.","source":"Project guide"}
   JSON
   ```

2. **Review.** Pick a human to check the Inbox. They check the source and fix the words if needed. They set a true, useful fact to Active and a bad or old fact to Retired. If a new fact takes the place of an old one, they retire the old row too.
3. **Read.** Each chat reads active facts when it starts. Read them again after a review if you need the latest facts.

Try this with one test fact. Check that it lands in the Inbox and stays out of `context`. Set it to Active and check that it shows up. Set it to Retired and check that it goes away.
