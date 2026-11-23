#!/usr/bin/env python3
"""Scan a local Output/{year} tree and write data/{year}.json for goose-render-index.

Folder rules (must match SPEC / Obsidian sync):
- Month folders: names starting with 01_ … 12_ (e.g. 01_Jan). Each **direct
  visible child folder** counts as one monthly item.
- Other top-level folders (e.g. 毛绒玩具, 元气森林): their direct child folders
  are outside_items (not in monthly_items).
- Files (README, scripts, etc.) are ignored.
- Pack lists (当月焦点 and month/outside item lists) are sorted by latest
  official PNG mtime in that pack folder, newest first. Temporary files
  whose names contain ``_tmp_`` are ignored. Packs without PNGs sort last,
  then by name.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

MONTH_PREFIX_RE = re.compile(r"^(0[1-9]|1[0-2])_")
TZ_SHANGHAI = timezone(timedelta(hours=8))


def visible_dirs(path: Path) -> list[Path]:
    if not path.is_dir():
        return []
    out = []
    for child in path.iterdir():
        name = child.name
        if name.startswith("."):
            continue
        if child.is_dir():
            out.append(child)
    out.sort(key=lambda p: p.name.casefold())
    return out


def month_number(folder_name: str) -> int | None:
    m = MONTH_PREFIX_RE.match(folder_name)
    return int(m.group(1)) if m else None


def pack_rendered_at(path: Path) -> datetime | None:
    """Latest official PNG mtime in a pack folder, as Asia/Shanghai."""
    if not path.is_dir():
        return None
    times: list[float] = []
    try:
        entries = list(path.iterdir())
    except OSError:
        return None
    for item in entries:
        name = item.name
        if name.startswith(".") or "_tmp_" in name:
            continue
        if not name.lower().endswith(".png"):
            continue
        if not item.is_file():
            continue
        try:
            times.append(item.stat().st_mtime)
        except OSError:
            continue
    if not times:
        return None
    return datetime.fromtimestamp(max(times), tz=TZ_SHANGHAI)


def item_entry(path: Path) -> dict:
    entry: dict = {"name": path.name}
    ts = pack_rendered_at(path)
    if ts is not None:
        entry["rendered_at"] = ts.isoformat(timespec="seconds")
    return entry


def pack_items(path: Path) -> list[dict]:
    """Direct visible child folders, newest official PNG first."""

    def sort_key(folder: Path):
        ts = pack_rendered_at(folder)
        stamp = ts.timestamp() if ts is not None else float("-inf")
        return (-stamp, folder.name.casefold())

    return [item_entry(folder) for folder in sorted(visible_dirs(path), key=sort_key)]


def scan(root: Path, year: int) -> dict:
    months_map: dict[int, dict] = {}
    for n in range(1, 13):
        months_map[n] = {
            "number": n,
            "folder": f"{n:02d}_" + [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
            ][n - 1],
            "items": [],
            "count": 0,
        }

    outside: list[dict] = []

    # Prefer actual folder names found on disk for month labels.
    for child in visible_dirs(root):
        num = month_number(child.name)
        items = pack_items(child)
        if num is not None:
            months_map[num] = {
                "number": num,
                "folder": child.name,
                "items": items,
                "count": len(items),
            }
        else:
            outside.append(
                {
                    "folder": child.name,
                    "items": items,
                    "count": len(items),
                }
            )

    months = [months_map[n] for n in range(1, 13)]
    monthly_items = sum(m["count"] for m in months)
    months_with_content = sum(1 for m in months if m["count"] > 0)
    outside_items = sum(o["count"] for o in outside)

    now = datetime.now(TZ_SHANGHAI)
    # Prefer calendar month in Asia/Shanghai; clamp to 1–12.
    current_month = now.month

    return {
        "title": "抓大鹅渲染图统计清单",
        "year": year,
        "generated_at": now.isoformat(timespec="seconds"),
        "source": str(root),
        "monthly_items": monthly_items,
        "outside_items": outside_items,
        "months_with_content": months_with_content,
        "current_month": current_month,
        "months": months,
        "outside": outside,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export goose render index JSON from a local Output year folder."
    )
    parser.add_argument(
        "--root",
        required=True,
        help="Path to the year folder to scan (e.g. .../Output/2026)",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="Year label for output file (default: infer from root folder name or 2026)",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Directory for data/{year}.json (default: <repo>/data next to this script)",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"--root is not a directory: {root}")

    year = args.year
    if year is None:
        try:
            year = int(root.name)
        except ValueError:
            year = 2026

    if args.out_dir:
        out_dir = Path(args.out_dir).expanduser().resolve()
    else:
        out_dir = Path(__file__).resolve().parent.parent / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{year}.json"

    payload = scan(root, year)
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {out_path}")
    print(
        f"monthly_items={payload['monthly_items']} "
        f"months_with_content={payload['months_with_content']}/12 "
        f"outside_items={payload['outside_items']}"
    )
    current = next((m for m in payload["months"] if m["number"] == payload["current_month"]), None)
    if current:
        names = [
            item["name"] if isinstance(item, dict) else item
            for item in current.get("items") or []
        ]
        print(f"current_month={current['folder']} focus={names}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())