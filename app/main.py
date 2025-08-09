import asyncio
import sys
import os

if sys.platform == "win32" or os.name == 'nt':
    try:
        # Try ProactorEventLoop first
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except:
        # Fallback to SelectorEventLoop
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import json
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlencode
import yaml
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from sqlmodel import Session
from app.config import settings
from app.db.session import init_db, get_session
from app.db.models import QueryLog, RawResponse
from app.services.scraper import Scraper
from app.services.parser import parse_case_page

app = FastAPI(title=settings.app_name)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

with open(settings.court_config_path, "r", encoding="utf-8") as f:
    COURT_CFG: Dict[str, Any] = yaml.safe_load(f)

scraper = Scraper(headless=settings.headless, court_cfg=COURT_CFG)

@app.on_event("startup")
async def on_startup() -> None:
    init_db()
    # DON'T start scraper here - start it lazily when needed

@app.on_event("shutdown")
async def on_shutdown() -> None:
    await scraper.stop()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "court_name": COURT_CFG.get("court_name", "Court")}
    )

@app.get("/captcha/new")
async def new_captcha():
    try:
        # Start scraper if not already started (lazy initialization)
        if not scraper.browser:
            await scraper.start()
        
        sid, data_url = await scraper.new_captcha_session()
        return JSONResponse({"session_id": sid, "image_data_url": data_url})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/search", response_class=HTMLResponse)
async def search(
    request: Request,
    case_type: str = Form(...),
    case_number: str = Form(...),
    filing_year: str = Form(...),
    captcha_text: str = Form(...),
    session_id: str = Form(...),
    db: Session = Depends(get_session),
):
    qlog = QueryLog(case_type=case_type, case_number=case_number, filing_year=filing_year)
    db.add(qlog)
    db.commit()
    db.refresh(qlog)

    try:
        final_url, html = await scraper.submit_case_search(
            session_id=session_id,
            case_type=case_type,
            case_number=case_number,
            filing_year=filing_year,
            captcha_text=captcha_text,
        )

        raw = RawResponse(query_id=qlog.id, url=final_url, raw_html=html)
        db.add(raw)
        data = parse_case_page(html, COURT_CFG)
        db.commit()

        return templates.TemplateResponse(
            "result.html",
            {"request": request, "data": data, "error": None},
        )

    except Exception as e:
        qlog.status = "ERROR"
        qlog.error_message = str(e)
        db.add(qlog)
        db.commit()

        return templates.TemplateResponse(
            "index.html",
            {"request": request, "court_name": COURT_CFG.get("court_name", "Court"), "error": str(e)},
            status_code=400,
        )

@app.get("/download")
async def download(url: str):
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
            resp = await client.get(url)
            resp.raise_for_status()

            return Response(
                content=resp.content,
                media_type=resp.headers.get("content-type", "application/pdf"),
                headers={"Content-Disposition": "attachment; filename=order.pdf"},
            )

    except Exception:
        return RedirectResponse(url)
