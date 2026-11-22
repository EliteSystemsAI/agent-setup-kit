#!/usr/bin/env python3
"""Set up, read, or propose a fact in Notion."""

import argparse
import getpass
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlencode, urlsplit
from urllib.request import Request, urlopen
from uuid import UUID


VERSION = "2026-03-11"
DATABASE = "Agent Memory"
VIEWS = {"Inbox": "Proposed", "Active facts": "Active"}
FIELDS = {
    "Name": {"title": {}},
    "Fact": {"rich_text": {}},
    "Source": {"rich_text": {}},
    "State": {"select": {"options": [{"name": state} for state in ("Proposed", "Active", "Retired")]}},
    "Added": {"created_time": {}},
}
NEWEST = [{"property": "Added", "direction": "descending"}]


def page_id(value):
    try:
        return str(UUID(value))
    except ValueError:
        path = urlsplit(value).path.rstrip("/")
        match = re.search(r"([0-9a-fA-F]{32}|[0-9a-fA-F-]{36})$", path)
        if not match:
            raise ValueError("Use a Notion page link or page ID.") from None
        return str(UUID(match[0]))


def notion_client():
    token = os.environ.get("NOTION_TOKEN")
    if not token and sys.stdin.isatty():
        token = getpass.getpass("Notion token (hidden): ")
    if not token:
        raise ValueError("Set NOTION_TOKEN in this shell or use the hidden prompt in your terminal.")

    def request(path, body=None, params=None):
        url = f"https://api.notion.com/v1/{path}"
        if params:
            url += "?" + urlencode(params)
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": VERSION,
            "Content-Type": "application/json",
        }
        for attempt in range(3):
            try:
                with urlopen(Request(url, data=data, headers=headers), timeout=30) as response:
                    return json.load(response)
            except HTTPError as error:
                if error.code != 429 or attempt == 2:
                    raise ValueError(f"Notion returned HTTP {error.code}. See docs/memory.md.") from None
                delay = error.headers.get("Retry-After", "1")
                time.sleep(min(10, int(delay)) if delay.isdecimal() else 1)
            except (URLError, TimeoutError):
                raise ValueError("Could not reach Notion. Check your network and try again.") from None

    return request


def collect(request, path, body=None, params=None):
    options = dict((params if body is None else body) or {})
    while True:
        result = request(path, params=options) if body is None else request(path, options)
        yield from result["results"]
        if not result["has_more"]:
            return
        options["start_cursor"] = result["next_cursor"]


def state_filter(state):
    return {"property": "State", "select": {"equals": state}}


def rich_text(value):
    return [{"type": "text", "text": {"content": value}}]


def check_schema(request, source_id):
    properties = request(f"data_sources/{source_id}")["properties"]
    for name, spec in FIELDS.items():
        if properties.get(name, {}).get("type") not in spec:
            raise ValueError(f"Agent Memory needs the {name} field. See docs/memory.md.")
    states = {option["name"] for option in properties["State"]["select"]["options"]}
    if not {"Proposed", "Active", "Retired"} <= states:
        raise ValueError("Agent Memory needs Proposed, Active, and Retired states.")
    return properties["State"]["id"]


def find_or_create_database(request, parent):
    children = collect(request, f"blocks/{parent}/children", params={})
    matches = [
        child["id"] for child in children
        if child["type"] == "child_database" and child["child_database"]["title"] == DATABASE
    ]
    if len(matches) > 1:
        raise ValueError("This page has more than one Agent Memory database. Pick a new parent page.")
    if matches:
        return request(f"databases/{matches[0]}")
    return request("databases", {
        "parent": {"type": "page_id", "page_id": parent},
        "title": rich_text(DATABASE),
        "initial_data_source": {"properties": FIELDS},
    })


def read_config(root):
    path = root / "memory.json"
    if not path.is_file():
        raise ValueError("Memory is not linked. See docs/memory.md.")
    return json.loads(path.read_text(encoding="utf-8"))


def views(request, database_id):
    records = collect(request, "views", params={"database_id": database_id})
    details = (request(f"views/{record['id']}") for record in records)
    return {view["name"]: view for view in details if view["name"] in VIEWS}


def check_memory(request, config, saved_views=None):
    source_id = config["data_source_id"]
    state_id = unquote(check_schema(request, source_id))
    if saved_views is None:
        saved_views = views(request, config["database_id"])
    for name, state in VIEWS.items():
        view_filter = saved_views.get(name, {}).get("filter") or {}
        clauses = view_filter.get("and", [view_filter])
        clause = clauses[0] if len(clauses) == 1 else {}
        # Notion can return the property ID unescaped in a saved filter.
        property_name = unquote(clause.get("property", ""))
        if property_name not in ("State", state_id) or clause.get("select") != {"equals": state}:
            raise ValueError(f"Check the {name} view's State filter in Notion. See docs/memory.md.")
    request(f"data_sources/{source_id}/query", {"filter": state_filter("Active"), "page_size": 1})
    print(f"Notion check passed: {config['url']}")


def setup_memory(root, parent_link):
    parent = page_id(parent_link)
    request = notion_client()
    path = root / "memory.json"
    if path.exists():
        config = read_config(root)
        if config["parent_page_id"] != parent:
            raise ValueError("Memory is linked to another page. Use that page or a new work folder.")
    else:
        database = find_or_create_database(request, parent)
        sources = database["data_sources"]
        if len(sources) != 1:
            raise ValueError("Agent Memory needs one data source.")
        config = {
            "parent_page_id": parent,
            "database_id": database["id"],
            "data_source_id": sources[0]["id"],
            "url": database["url"],
        }
        check_schema(request, config["data_source_id"])
        with path.open("x", encoding="utf-8") as file:
            json.dump(config, file, indent=2)

    saved_views = views(request, config["database_id"])
    for name, state in VIEWS.items():
        if name not in saved_views:
            created = request("views", {
                "database_id": config["database_id"],
                "data_source_id": config["data_source_id"],
                "name": name,
                "type": "table",
                "filter": state_filter(state),
                "sorts": NEWEST,
            })
            saved_views[name] = request(f"views/{created['id']}")
    check_memory(request, config, saved_views)


def context(request, source_id):
    rows = collect(request, f"data_sources/{source_id}/query", {
        "filter": state_filter("Active"),
        "sorts": NEWEST,
    })
    facts = []
    for row in rows:
        fields = row["properties"]
        facts.append({
            "name": "".join(item["plain_text"] for item in fields["Name"]["title"]),
            "fact": "".join(item["plain_text"] for item in fields["Fact"]["rich_text"]),
            "source": "".join(item["plain_text"] for item in fields["Source"]["rich_text"]),
            "url": row["url"],
        })
    print(json.dumps(facts, ensure_ascii=False, indent=2))


def propose(request, source_id):
    fact = json.load(sys.stdin)
    values = {}
    for key in ("name", "fact", "source"):
        value = fact.get(key) if isinstance(fact, dict) else None
        if not isinstance(value, str) or not 1 <= len(value.strip()) <= 2000:
            raise ValueError(f"Give {key} as text of 1 to 2,000 characters.")
        values[key] = rich_text(value.strip())
    row = request("pages", {
        "parent": {"type": "data_source_id", "data_source_id": source_id},
        "properties": {
            "Name": {"title": values["name"]},
            "Fact": {"rich_text": values["fact"]},
            "Source": {"rich_text": values["source"]},
            "State": {"select": {"name": "Proposed"}},
        },
    })
    print(f"Sent to Inbox: {row['url']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("setup").add_argument("page")
    commands.add_parser("check")
    commands.add_parser("context")
    commands.add_parser("propose")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    os.umask(0o077)

    if args.command == "setup":
        setup_memory(root, args.page)
        return
    config = read_config(root)
    request = notion_client()
    source_id = config["data_source_id"]
    if args.command == "check":
        check_memory(request, config)
    elif args.command == "context":
        context(request, source_id)
    elif args.command == "propose":
        propose(request, source_id)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(str(error))
