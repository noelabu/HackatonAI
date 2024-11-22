from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    CORS_ENABLED: bool = True
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOWED_ORIGINS: frozenset[str] = frozenset({"*"})
    CORS_ALLOWED_METHODS: frozenset[str] = frozenset({"*"})
    CORS_ALLOWED_HEADERS: frozenset[str] = frozenset({"*"})

    @classmethod
    def parse_env_var(cls, field_name: str, raw_val: str) -> frozenset[str] | str:
        """
        Provides additional parsing for CORS env vars.
        """
        match field_name:
            case (
                "CORS_ALLOWED_ORIGINS"
                | "CORS_ALLOWED_METHODS"
                | "CORS_ALLOWED_HEADERS"
            ):
                return frozenset(raw_val.split(","))

            case _:
                return raw_val


settings = Settings()
