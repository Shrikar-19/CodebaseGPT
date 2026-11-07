from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "CodebaseGPT"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    class Config:
        env_file = ".env"


settings = Settings()