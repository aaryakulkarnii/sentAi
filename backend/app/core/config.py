"""Application configuration (pydantic-settings)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "development"

    # DEV_MODE = zero-infra: SQLite + in-memory Redis, OpenSearch/Qdrant/Kafka
    # disabled. Lets the whole core run with just `uvicorn`, no Docker.
    DEV_MODE: bool = True

    # Safe dev defaults so the app boots with no .env at all.
    SECRET_KEY: str = "dev-secret-change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]

    # PostgreSQL (used only when DEV_MODE is False)
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "sentinelai"
    POSTGRES_USER: str = "sentinel"
    POSTGRES_PASSWORD: str = "sentinel_dev"

    # SQLite file used in DEV_MODE
    SQLITE_PATH: str = "sentinel_dev.db"

    @property
    def DATABASE_URL(self) -> str:
        if self.DEV_MODE:
            return f"sqlite+aiosqlite:///./{self.SQLITE_PATH}"
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # OpenSearch
    OPENSEARCH_HOST: str = "opensearch"
    OPENSEARCH_PORT: int = 9200

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    # Qdrant
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = ""

    # Kafka – use kafka:29092 inside Docker; localhost:9092 from host
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:29092"
    KAFKA_CONSUMER_GROUP: str = "sentinelai-consumers"

    # LLM – Groq (free-tier, OpenAI-compatible). Set GROQ_API_KEY in .env.
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_MODEL_FAST: str = "llama-3.1-8b-instant"
    # Legacy OpenAI knobs (kept for compatibility; unused when Groq is set)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    # Threat Intel
    ABUSEIPDB_API_KEY: str = ""
    OTX_API_KEY: str = ""
    MALWARE_BAZAAR_API_KEY: str = ""

    # GeoIP (MaxMind GeoLite2 – optional)
    GEOIP_DB_PATH: str = "data/geoip/GeoLite2-City.mmdb"
    GEOIP_ASN_DB_PATH: str = "data/geoip/GeoLite2-ASN.mmdb"
    MAXMIND_LICENSE_KEY: str = ""

    # Detection
    SIGMA_RULES_DIR: str = "data/sigma_rules"
    BEHAVIORAL_BRUTE_FORCE_THRESHOLD: int = 10
    BEHAVIORAL_BRUTE_FORCE_WINDOW: int = 300
    BEHAVIORAL_PASSWORD_SPRAY_THRESHOLD: int = 5
    BEHAVIORAL_PASSWORD_SPRAY_WINDOW: int = 300
    BEHAVIORAL_PORT_SCAN_THRESHOLD: int = 20
    BEHAVIORAL_PORT_SCAN_WINDOW: int = 120
    ALERT_DEDUP_WINDOW: int = 3600

    # Correlation (Tier 2)
    CORRELATION_WINDOW: int = 1800  # seconds: alerts within this window may group
    CORRELATION_MIN_ALERTS: int = 2  # alerts sharing an entity before an incident forms

    # AWS
    S3_BUCKET_REPORTS: str = "sentinelai-reports"
    AWS_REGION: str = "us-east-1"


settings = Settings()
