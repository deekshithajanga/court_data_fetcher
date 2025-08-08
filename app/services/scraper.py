import base64
import uuid
from typing import Any, Dict

import yaml
from playwright.async_api import Browser, Page, async_playwright

from app.config import get_settings


class Scraper:
    def __init__(self) -> None:
        self.settings = get_settings()
        with open(self.settings.court_config, "r", encoding="utf-8") as f:
            self.cfg: Dict[str, Any] = yaml.safe_load(f)
        self._pw = None
        self._browser: Browser | None = None
        self._sessions: dict[str, Page] = {}

    async def start(self) -> None:
        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(headless=self.settings.headless)

    async def stop(self) -> None:
        for page in list(self._sessions.values()):
            try:
                await page.context.close()
            except Exception:
                pass
        self._sessions.clear()
        if self._browser:
            await self._browser.close()
        if self._pw:
            await self._pw.stop()

    async def new_captcha_session(self) -> dict[str, str]:
        if not self._browser:
            raise RuntimeError("Scraper browser not started")

        url: str = self.cfg["case_status_url"]
        captcha_selector: str = self.cfg["selectors"]["captcha_img"]

        context = await self._browser.new_context()
        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded")

        locator = page.locator(captcha_selector)
        await locator.wait_for()
        png_bytes = await locator.screenshot()
        data_url = "data:image/png;base64," + base64.b64encode(png_bytes).decode("ascii")

        session_id = str(uuid.uuid4())
        self._sessions[session_id] = page
        return {"session_id": session_id, "image_data_url": data_url}

    async def search_case(
        self,
        session_id: str,
        case_type: str,
        case_number: str,
        filing_year: int,
        captcha_text: str,
    ) -> dict[str, str]:
        page = self._sessions.get(session_id)
        if page is None:
            raise RuntimeError("Invalid or expired session_id. Click 'Get/Refresh Captcha' and try again.")

        s = self.cfg["selectors"]

        # Case type may be a select or free-text input
        case_type_select = s.get("case_type_select")
        case_type_input = s.get("case_type_input")
        if case_type_select:
            # Prefer selecting by label; adjust to value if needed
            try:
                await page.select_option(case_type_select, label=case_type)
            except Exception:
                await page.select_option(case_type_select, value=case_type)
        elif case_type_input:
            await page.fill(case_type_input, case_type)

        await page.fill(s["case_number_input"], str(case_number))
        await page.fill(s["case_year_input"], str(filing_year))

        if s.get("captcha_input"):
            await page.fill(s["captcha_input"], captcha_text)

        await page.click(s["submit_button"])

        marker = s.get("result_marker")
        if marker:
            await page.wait_for_selector(marker, timeout=15000)

        html = await page.content()
        current_url = page.url

        # Close this session to avoid leaks
        try:
            await page.context.close()
        finally:
            self._sessions.pop(session_id, None)

        return {"url": current_url, "html": html}