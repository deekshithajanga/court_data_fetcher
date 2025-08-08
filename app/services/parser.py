from typing import Any, Dict, List

from bs4 import BeautifulSoup


class Parser:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def _text(self, soup: BeautifulSoup, selector: str | None) -> str | None:
        if not selector:
            return None
        node = soup.select_one(selector)
        return node.get_text(strip=True) if node else None

    def parse(self, html: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "lxml")
        sels = self.config.get("selectors", {})

        details = {
            "petitioner": self._text(soup, sels.get("petitioner")),
            "respondent": self._text(soup, sels.get("respondent")),
            "filing_date": self._text(soup, sels.get("filing_date")),
            "next_hearing_date": self._text(soup, sels.get("next_hearing_date")),
        }

        orders: List[Dict[str, str]] = []
        rows_sel = sels.get("orders_table_rows")
        if rows_sel:
            link_sel = sels.get("order_link_selector") or "a[href]"
            for row in soup.select(rows_sel):
                a = row.select_one(link_sel)
                if a:
                    orders.append({
                        "title": a.get_text(strip=True),
                        "pdf_url": a.get("href"),
                    })

        return {"details": details, "orders": orders}