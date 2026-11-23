# Team operating rules

1. Work from the private team folder. Use the matching prompt in `prompts/` for the CEO, COO or worker role.
2. At every session start, resume, and provider handoff, run `python3 scripts/memory.py context` from that folder before taking on work. Use the active facts that apply. If Team Memory is unavailable, tell the COO and resolve access before making decisions that depend on it.
3. Before asking for information or relying on a past decision, run `python3 scripts/memory.py search "topic"`. Check the source. Apply the latest instruction for the current scope.
4. Before closing a job, check for a new lasting fact, rule or decision. Search for it and use `python3 scripts/memory.py propose` with the fact and its source if it is new. The [memory guide](docs/memory.md) shows the JSON format. A human reviews proposals. Do not activate or retire rows as an agent.
5. Keep one brain for this team across runtimes. Keep private or client facts within their permitted audience. Leave passwords, tokens and task logs out of memory.
6. Follow [the team writing rules](docs/writing.md) for all AI-authored Linear updates and documentation. Use ASD-STE100 principles for about 80% of the writing. Use natural language where it helps preserve context or tone.
7. The CEO talks to the human. The COO assigns work and verifies results. Workers report to the COO. Record the outcome and evidence in the handoff.
