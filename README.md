# Instagram Content Planner

A small, local-first command-line tool for drafting Instagram captions and keeping a simple posting plan. It does **not** log in to Instagram, scrape Instagram, or generate fake likes, views, or followers. Nothing is posted for you.

## Requirements

- Python 3.10 or newer
- No third-party packages

## Get started

```bash
python main.py new
```

Enter a title, write the caption (finish with a line containing only `.`), add optional hashtags, and optionally note a planned date or time. The draft is saved locally in `~/.instagram-content-planner/drafts.json`.

```bash
python main.py list              # list your drafts
python main.py show 1a2b3c4d     # view a draft by ID
python main.py delete 1a2b3c4d   # delete a draft by ID
```

The planner checks the 2,200-character caption limit and the 30-hashtag maximum. Hashtags can be entered with or without `#` and separated by spaces or commas.

## Choose a different data location

Set `IG_PLANNER_DATA` to a JSON file path before running the app. For example:

```bash
IG_PLANNER_DATA=./my-drafts.json python main.py list
```

Drafts may contain unpublished ideas, so keep the local JSON file private and back it up if needed. The tool works entirely on your computer and does not ask for your Instagram password.
