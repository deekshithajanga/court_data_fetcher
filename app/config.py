from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Court-Data Fetcher"
    database_url: str = Field(default="sqlite:///./court_data.db", alias="DATABASE_URL")
    headless: bool = Field(default=True, alias="HEADLESS")
    court_config_path: str = Field(default="app/courts/delhi_high_court.yml", alias="COURT_CONFIG")


settings = Settings()
