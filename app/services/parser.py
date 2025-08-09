from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
import re

def text_or_none(el) -> Optional[str]:
    if not el:
        return None
    t = el.get_text(strip=True)
    return t or None

def parse_case_page(html: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    
    # Initialize result structure
    result = {
        "parties": {"petitioner": None, "respondent": None},
        "filing_date": None,
        "next_hearing_date": None,
        "orders": [],
        "most_recent_order": None,
        "case_found": False
    }
    
    # Check if we have actual case data
    tables = soup.find_all('table')
    
    if not tables:
        return result
    
    result["case_found"] = True
    
    # Try to parse case information from tables
    for table in tables:
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)
                
                if 'petitioner' in label:
                    result["parties"]["petitioner"] = value
                elif 'respondent' in label:
                    result["parties"]["respondent"] = value
                elif 'filing' in label or 'date' in label:
                    if not result["filing_date"]:
                        result["filing_date"] = value
                elif 'next' in label or 'hearing' in label:
                    result["next_hearing_date"] = value
    
    # Look for PDF links
    pdf_links = soup.find_all('a', href=re.compile(r'\.pdf', re.I))
    for link in pdf_links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        if href:
            if not href.startswith('http'):
                href = cfg.get('base_url', '') + href
            
            result["orders"].append({
                "date": "",  # Extract from context if possible
                "title": text or "Order/Judgment",
                "pdf_url": href
            })
    
    if result["orders"]:
        result["most_recent_order"] = result["orders"]
    
    return result
