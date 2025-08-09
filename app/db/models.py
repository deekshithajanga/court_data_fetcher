from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class QueryLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    case_type: str
    case_number: str
    filing_year: str
    status: str = "SUCCESS"
    error_message: Optional[str] = None

    raw_response: "RawResponse" = Relationship(back_populates="query")


class RawResponse(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    query_id: int = Field(foreign_key="querylog.id")
    url: str
    raw_html: str

    query: QueryLog = Relationship(back_populates="raw_response")
