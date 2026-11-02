#!/usr/bin/env python3
"""Scan a local Output/{year} tree and write data/{year}.json for goose-render-index.

Folder rules (must match SPEC / Obsidian sync):
- Month folders: names starting with 01_ … 12_ (e.g. 01_Jan). Each **direct
  visible child folder** counts as one monthly item.
- Other top-level folders (e.g. 毛绒玩具, 元气森林): their direct child folders
  are outside_items (not in monthly_items).
- Files (README, scripts, etc.) are ignored.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

MONTH_PREFIX_RE = re.compile(r"^(0[1-9]|1[0-2])_")
TZ_SHANGHAI = timezone(timedelta(hours=8))


def visible_dirs(path: Path) -> list[Path]:
    if not path.is_dir():
        return []
    out = []
    for child in sorted(path.iterdir(), key=lambda p: p.name.casefold()):
        name = child.name
        if name.startswith("."):
            continue
        if child.is_dir():
            out.append(child)
    return out


def month_number(folder_name: str) -> int | None:
    m = MONTH_PREFIX_RE.match(folder_name)
    return int(m.group(1)) if m else None


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
        if num is not None:
            items = [d.name for d in visible_dirs(child)]
            months_map[num] = {
                "number": num,
                "folder": child.name,
                "items": items,
                "count": len(items),
            }
        else:
            items = [d.name for d in visible_dirs(child)]
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
