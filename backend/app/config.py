from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql://user:password@localhost:5432/carbon_footprint"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    # Local dev: allow any port on localhost, 127.0.0.1, and LAN IPs. Set empty in production.
    cors_origin_regex: str = r"http://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}):\d+"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
