# Court-Data Fetcher & Mini-Dashboard (Delhi High Court)

A FastAPI + Playwright app to fetch Delhi High Court case metadata and latest orders/judgments.

- Tech: FastAPI, Playwright (Chromium), BeautifulSoup, SQLModel (SQLite), Jinja2, Bootstrap
- CAPTCHA strategy: Manual entry (we show the live captcha image; user types it)
- Storage: SQLite (logs each query and raw HTML)

## Task Overview
- Input: Case Type, Case Number, Filing Year
- Output: Parties, filing date, next hearing date, latest order/judgment PDF link(s)

## Court Chosen
- Delhi High Court (https://delhihighcourt.nic.in/)

## Setup (high level)
1. Create venv
2. Install deps
3. Run dev server
4. Use the UI to fetch case details

More details and full instructions will be added as we progress.
