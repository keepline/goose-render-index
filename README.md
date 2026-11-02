# goose-render-index

抓大鹅 **2026** 渲染图统计清单的静态站。只展示名称与数量，**不托管本地 PNG**。

## Online

- **GitHub Pages:** https://keepline.github.io/goose-render-index/
- Repo: https://github.com/keepline/goose-render-index

## What’s on the page

- 年度汇总：`monthly_items`、有内容月份 `/12`、`outside_items`、进度条
- 当月焦点 chips（当前为 11 月：小魔女鹅、驯鹿鹅）
- 月份总览表 + 可展开的各月条目
- 月度外分组（如 元气森林、毛绒玩具）
- `generated_at` 时间戳

数据文件：[`data/2026.json`](./data/2026.json)

## Refresh JSON (local)

在放有 `01_Jan`…`12_Dec` 等目录的 **Output/2026** 根上跑导出脚本，再提交 JSON：

```bash
python3 scripts/export_index.py --root "/path/to/Output/2026"
# optional: --year 2026  --out-dir ./data
git add data/2026.json
git commit -m "chore: refresh 2026 render index"
git push
```

规则与 `SPEC.md` 一致：只统计**直接子文件夹**；`01_`–`12_` 前缀算月度，其它顶层文件夹算月度外；忽略文件。

PNG / 渲染产物请留在本机（例如 Rayu-Working 上的 Output 目录），不要推到本仓库。

## Publish

本仓库用 GitHub Actions（`.github/workflows/pages.yml`）从 `main` 根目录发布静态站。推送到 `main` 后 Actions 会部署 Pages。

若 Actions 尚未启用 Pages，也可在仓库 **Settings → Pages** 选择 Deploy from a branch：`main` / `/ (root)`。

## Spec

见 [`SPEC.md`](./SPEC.md)。
