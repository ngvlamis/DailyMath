# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

DailyMath generates and serves daily math worksheets at https://dailymath.education. Every night, a Python script generates 52 PDFs from randomized LaTeX problems, and a Jekyll static site displays them. GitHub Pages serves the `gh-pages` branch.

## Key Commands

### Generate Worksheets (PDFs)
```bash
cd WorksheetGenerator/
python DailyMath_Worksheet_Generator.py
```
Requires: Python with `pyyaml`, and a full TeX Live installation (not minimal — needs `pdflatex`).

### Develop the Jekyll Website Locally
```bash
cd WebsiteGenerator/
bundle exec jekyll serve
```
Visit `localhost:4000`. Requires Ruby + Bundler (`gem install bundler`).

### Publish the Website
After running Jekyll, copy output to the repo root for GitHub Pages:
```bash
python regenerate_dailymath_website.py
```

### Full Daily Automation (runs via cron on Raspberry Pi at 2am)
```bash
bash generate_worksheets_and_commit.sh
```
This generates worksheets, commits, and pushes to `gh-pages`.

## Architecture

### Data Flow

1. **`WorksheetGenerator/DailyMath_Worksheet_Generator.py`** reads `WebsiteGenerator/_data/worksheets.yml`, generates random problems for each of 52 worksheet definitions, compiles them via `pdflatex`, and outputs PDFs to `worksheets/`.

2. **Jekyll** (`WebsiteGenerator/`) reads the same `worksheets.yml` via `_data/` and renders HTML using Liquid templates. The `_includes/worksheets.liquid` component generates the accordion UI dynamically.

3. **`regenerate_dailymath_website.py`** copies `WebsiteGenerator/_site/*` to the repo root, where GitHub Pages serves it.

### Branch Strategy
- `main` — source code (scripts, configuration)
- `gh-pages` — generated content (PDFs + static site); what GitHub Pages deploys
- `development` — active development work

### Central Configuration: `worksheets.yml`
`WebsiteGenerator/_data/worksheets.yml` is the single source of truth for all 52 worksheets. Each entry defines the worksheet ID, title, problem type (addition/subtraction/multiplication/mixed), difficulty constraints (term ranges, number of problems), and layout style (horizontal, vertical, fill-in-the-blank). Both the PDF generator and the website template read from this file.

### Worksheet ID Naming Convention
IDs follow a pattern: `{difficulty prefix}{type}{level}` — e.g., `sda1` = simple digit addition level 1, `dds2` = double digit subtraction level 2, `sdm3` = simple digit multiplication level 3.

### LaTeX Pipeline
The Python generator creates `.tex` files in `out/`, calls `pdflatex`, then moves the resulting PDF to `worksheets/` and cleans up `.aux`, `.log`, `.tex` files.
