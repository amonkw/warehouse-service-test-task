from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    POSTGRES_HOST: str = Field(..., alias="postgres_host")
    POSTGRES_PORT: str = Field(..., alias="postgres_port")
    POSTGRES_DB: str = Field(..., alias="postgres_db")
    POSTGRES_USER: str = Field(..., alias="postgres_user")
    POSTGRES_PASSWORD: str = Field(..., alias="postgres_password")
    ECHO_SQL: bool = Field(default=True, alias="echo_sql")
    IS_AUTOTEST: bool = Field(default=False, alias="is_autotest")

    # Kafka settings
    APP_MODE: str = "webhook_only"  # Режим работы (kafka | webhook_only)
    KAFKA_BOOTSTRAP_SERVERS: str = Field(..., alias="kafka_bootstrap_servers")
    KAFKA_TOPIC: str = Field(..., alias="kafka_topic")
    KAFKA_GROUP_ID: str = Field(..., alias="kafka_group_id")

    # Redis
    REDIS_HOST: str = Field(default="localhost", alias="redis_host")
    REDIS_PORT: int = Field(default=6379, alias="redis_port")
    REDIS_DB: int = Field(default=0, alias="redis_db")
    CACHE_TTL_SECONDS: int = Field(default=300, alias="cache_ttl_seconds")

    # App settings
    APP_HOST: str = Field(default="0.0.0.0", alias="app_host")
    APP_PORT: int = Field(default=8000, alias="app_port")
    DEBUG: bool = Field(default=False, alias="debug")
    PROJECT_VERSION: str = Field(default="1.0.0", alias="project_version")
    OPENAPI_VERSION: str = Field(default="1.0.0", alias="openapi_version")
    PROJECT_NAME: str = Field(..., alias="project_name")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def test_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}_autotest"
        )

    class Config:
        env_file = ".env.example"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
