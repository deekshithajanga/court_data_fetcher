from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class QueryLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    case_type: str
    case_number: str
    filing_year: int

    status: str
    error_message: Optional[str] = None

    raw_responses: List["RawResponse"] = Relationship(back_populates="query")


class RawResponse(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    query_id: int = Field(foreign_key="querylog.id")

    url: str
    raw_html: str

    query: Optional[QueryLog] = Relationship(back_populates="raw_responses")


class OrderLink(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    query_id: int = Field(foreign_key="querylog.id")

    date: Optional[str] = None
    title: Optional[str] = None
    pdf_url: Optional[str] = None