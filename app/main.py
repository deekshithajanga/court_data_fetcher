import sys
import asyncio
from typing import Any, Dict

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.db.models import QueryLog, RawResponse
from app.db.session import get_session, init_db
from app.services.parser import Parser
from app.services.scraper import Scraper
from sqlmodel import Session
import yaml

# Windows event loop policy for Playwright
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

settings = get_settings()
app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

scraper = Scraper()
with open(settings.court_config, "r", encoding="utf-8") as f:
    parser = Parser(yaml.safe_load(f))


@app.on_event("startup")
async def on_startup() -> None:
    init_db()
    await scraper.start()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await scraper.stop()


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/captcha/new")
async def captcha_new() -> JSONResponse:
    try:
        data = await scraper.new_captcha_session()
        return JSONResponse(data)
    except Exception as exc:  # surface error for debugging during setup
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/search")
async def search(
    request: Request,
    case_type: str = Form(...),
    case_number: str = Form(...),
    filing_year: int = Form(...),
    session_id: str = Form(...),
    captcha_text: str = Form(...),
    db: Session = Depends(get_session),
):
    # Run scrape
    try:
        scrape_res: Dict[str, str] = await scraper.search_case(
            session_id=session_id,
            case_type=case_type,
            case_number=case_number,
            filing_year=filing_year,
            captcha_text=captcha_text,
        )
        status = "success"
        error_message = None
    except Exception as exc:
        scrape_res = {"url": "", "html": ""}
        status = "error"
        error_message = str(exc)

    # Persist log + raw html
    qlog = QueryLog(
        case_type=case_type,
        case_number=case_number,
        filing_year=filing_year,
        status=status,
        error_message=error_message,
    )
    db.add(qlog)
    db.commit()
    db.refresh(qlog)

    if scrape_res.get("html"):
        db.add(
            RawResponse(query_id=qlog.id, url=scrape_res.get("url", ""), raw_html=scrape_res["html"])  # type: ignore[arg-type]
        )
        db.commit()

    # Parse and render
    result: Dict[str, Any]
    if scrape_res.get("html"):
        result = parser.parse(scrape_res["html"])  # type: ignore[index]
    else:
        result = {"details": {}, "orders": []}

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "result": result,
            "status": status,
            "error": error_message,
        },
    )