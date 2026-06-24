from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FoodieLog"
    database_url: str = "sqlite:///./data/foodie.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_per_minute: int = 0  # 0 = disabled; set to 20 in compose.yaml

    # JWT (Session 11)
    jwt_secret: str = "change-me-in-production"
    jwt_issuer: str = "foodielog"
    jwt_audience: str = "foodielog-clients"
    jwt_expiry_minutes: int = 30

    # Async refresh worker (Session 09)
    api_base_url: str = "http://localhost:8000"
    refresh_max_concurrency: int = 4
    trace_id: str = "foodielog-refresh"
    refresh_user_email: str = "admin@foodielog.com"
    refresh_user_password: str = "admin123"

    # AI assistant (Groq — OpenAI-compatible API)
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="FOODIE_",
        extra="ignore",
    )
