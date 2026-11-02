# goose-render-index

Static GitHub Pages site for 抓大鹅 2026 render inventory.

## Goal
Public site at https://keepline.github.io/goose-render-index/ showing the same counts/names as the Obsidian note `抓大鹅渲染图统计清单.md`, without hosting PNG assets.

## Data rules (must match Output/2026 sync script)
- Source of truth is local folder scan; committed file is `data/2026.json`.
- Months `01_Jan`…`12_Dec` (prefix `01_`…`12_`): each **direct visible child folder** = 1 monthly item.
- Other top-level folders (e.g. 毛绒玩具, 元气森林): their direct children = outside_items (not in monthly total).
- Do not count files (README, scripts).

## Site requirements
- Single-page static site (HTML+CSS+vanilla JS, no build step preferred; Vite ok if simple).
- Chinese UI. Lead with year summary: monthly_items, months_with_content/12, outside_items, progress bar, current month focus + item chips.
- Year overview table (month → count → status). Expandable month sections listing item names.
- Outside section separately.
- Show `generated_at`. Cream / royal-blue / orange scrapbook palette (see design ref); readable on mobile.
- Load `./data/2026.json` (relative). Works on GitHub Pages project site (`/goose-render-index/`).

## Repo setup
- Enable GitHub Pages from `main` / root (or `/docs`). Prefer root with `index.html`.
- README: how to refresh data (run local exporter → commit `data/2026.json`), link Pages URL.
- Include a small `scripts/export_index.py` that scans a `--root` path with the same rules and writes `data/2026.json` (for Rayu-Working).

## Out of scope
- Do not upload or link local file:/// PNGs.
- Do not rewrite the Obsidian PowerShell sync script in this first PR unless needed for JSON export only as a companion script in this repo.
