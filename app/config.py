from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "FoodieLog"
    database_url: str = "sqlite:///./data/foodie.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="FOODIE_",
        extra="ignore",
    )