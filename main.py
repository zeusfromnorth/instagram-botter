#!/usr/bin/env python3
"""A tiny, local-first Instagram content draft planner.

This tool does not log in to Instagram, scrape the site, or automate likes,
views, follows, or posts. Drafts stay on your computer.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MAX_CAPTION_LENGTH = 2_200
MAX_HASHTAGS = 30
DEFAULT_DATA_FILE = Path.home() / ".instagram-content-planner" / "drafts.json"


def data_file() -> Path:
    """Return the draft file path, with an environment-variable override."""
    override = os.environ.get("IG_PLANNER_DATA")
    return Path(override).expanduser() if override else DEFAULT_DATA_FILE


def load_drafts(path: Path | None = None) -> list[dict[str, Any]]:
    path = path or data_file()
    if not path.exists():
        return []
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read drafts from {path}: {exc}") from exc
    if not isinstance(content, list) or not all(isinstance(item, dict) for item in content):
        raise ValueError(f"Draft file has an unexpected format: {path}")
    return content


def save_drafts(drafts: list[dict[str, Any]], path: Path | None = None) -> None:
    path = path or data_file()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(drafts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Could not save drafts to {path}: {exc}") from exc


def normalize_hashtags(raw: str) -> list[str]:
    tags: list[str] = []
    for part in raw.replace(",", " ").split():
        tag = part.lstrip("#").strip()
        if tag and tag not in tags:
            tags.append(tag)
    if len(tags) > MAX_HASHTAGS:
        raise ValueError(f"Use no more than {MAX_HASHTAGS} hashtags (you entered {len(tags)}).")
    return tags


def create_draft(title: str, caption: str, hashtags: list[str], planned_for: str = "") -> dict[str, Any]:
    title = title.strip()
    caption = caption.strip()
    if not title:
        raise ValueError("A draft title cannot be empty.")
    if len(caption) > MAX_CAPTION_LENGTH:
        raise ValueError(f"Caption is {len(caption)} characters; the limit is {MAX_CAPTION_LENGTH}.")
    if len(hashtags) > MAX_HASHTAGS:
        raise ValueError(f"Use no more than {MAX_HASHTAGS} hashtags.")
    return {
        "id": uuid.uuid4().hex[:8],
        "title": title,
        "caption": caption,
        "hashtags": hashtags,
        "planned_for": planned_for.strip(),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def render_draft(draft: dict[str, Any]) -> str:
    tags = " ".join(f"#{tag}" for tag in draft.get("hashtags", []))
    caption = draft.get("caption", "")
    if tags:
        caption = f"{caption}\n\n{tags}" if caption else tags
    planned = draft.get("planned_for") or "Not scheduled"
    return textwrap.dedent(f"""\
        {draft.get('title', 'Untitled')}  [{draft.get('id', '?')}]
        Planned for: {planned}
        Caption ({len(draft.get('caption', ''))}/{MAX_CAPTION_LENGTH} characters):
        {caption or '(empty)'}
    """)


def prompt_new_draft() -> dict[str, Any]:
    print("Create a local draft (nothing will be posted to Instagram).\n")
    title = input("Draft title: ").strip()
    print("Caption (finish by entering a line containing only .):")
    lines: list[str] = []
    while True:
        line = input()
        if line == ".":
            break
        lines.append(line)
    caption = "\n".join(lines).strip()
    hashtags = normalize_hashtags(input("Hashtags (space or comma separated, without # is fine): "))
    planned_for = input("Plan date/time (optional, e.g. 2026-10-04 18:30): ").strip()
    return create_draft(title, caption, hashtags, planned_for)


def run(args: argparse.Namespace) -> int:
    path = data_file()
    try:
        if args.command == "new":
            draft = prompt_new_draft()
            drafts = load_drafts(path)
            drafts.append(draft)
            save_drafts(drafts, path)
            print(f"\nSaved draft {draft['id']} to {path}\n")
            print(render_draft(draft))
        elif args.command == "list":
            drafts = load_drafts(path)
            if not drafts:
                print("No drafts yet. Run `python main.py new` to make one.")
            else:
                for draft in drafts:
                    print(f"{draft.get('id', '?')}  {draft.get('planned_for') or 'Unscheduled':20}  {draft.get('title', 'Untitled')}")
        elif args.command == "show":
            draft = next((item for item in load_drafts(path) if item.get("id") == args.id), None)
            if draft is None:
                print(f"No draft found with ID {args.id!r}.", file=sys.stderr)
                return 1
            print(render_draft(draft))
        elif args.command == "delete":
            drafts = load_drafts(path)
            remaining = [item for item in drafts if item.get("id") != args.id]
            if len(remaining) == len(drafts):
                print(f"No draft found with ID {args.id!r}.", file=sys.stderr)
                return 1
            save_drafts(remaining, path)
            print(f"Deleted draft {args.id}.")
        return 0
    except (ValueError, EOFError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Plan Instagram captions locally; this tool never accesses or posts to Instagram."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("new", help="create a caption draft interactively")
    subparsers.add_parser("list", help="list saved drafts")
    show_parser = subparsers.add_parser("show", help="display a draft")
    show_parser.add_argument("id", help="draft ID shown by the list command")
    delete_parser = subparsers.add_parser("delete", help="delete a draft")
    delete_parser.add_argument("id", help="draft ID shown by the list command")
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
