# Start work

Open each chat in the same work folder, or give each chat the full path. By default it is `~/.agent-setup`. You can use two tools or two accounts if both can read and write that folder.

1. Open the chat you will talk to. Start it with `Read <work folder>/prompts/CEO.md and follow it. The work folder is <work folder>.`
2. Open a second chat for the work. Start it with `Read <work folder>/prompts/COO.md and follow it. The work folder is <work folder>.`
3. Give your goal to the CEO. Say what done looks like. The CEO writes it to `coo/INBOX.md`. Ask the COO chat to check its inbox if it is idle.
4. The COO makes one folder per worker in `workers/`, using `templates/TASK.md` and `templates/HANDOFF.md`. The COO gives each worker the full path to its own folder and asks it to read `prompts/WORKER.md`. Use a new chat or a child agent that can use the same files. If your tool cannot start one, the COO gives you the start message to paste into a fresh chat.
5. The worker writes its result in its own `HANDOFF.md` and tells only the COO. The COO reads it, checks the result, and writes one update in `coo/OUTBOX.md`. Ask the CEO to read the outbox when you want an update.

In Claude Code or Codex, use one terminal per chat. A terminal multiplexer can keep them open in one window. In Cursor, use separate agent chats with file and terminal access. If a chat asks to trust a folder or allow a command, read the request before you pick.

## Who writes what

| File | Who writes it |
| --- | --- |
| `ceo/HANDOFF.md` | CEO |
| `coo/INBOX.md` | CEO |
| `coo/HANDOFF.md`, `coo/TRACKER.md`, `coo/OUTBOX.md` | COO |
| `workers/<job>/TASK.md` | COO |
| `workers/<job>/HANDOFF.md` | That job's worker |

Keep one live chat per role or job. Write down work as it changes. Keep these files in a private folder. Keep keys and passwords out of all work notes.

## Try it once

Ask the CEO to have a worker check that the four handoff headings exist. Let the COO see the worker's result and write it to the outbox. Ask the CEO to read the outbox. Check that the same result made it back to you.
