from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if not (_ROOT / "data").exists():
    _ROOT = Path(__file__).resolve().parent.parent.parent
_DATA_DIR = _ROOT / "data"


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

    # Set to true on 512MB Render free tier to prevent OOM
    DISABLE_LOCAL_EMBEDDINGS: bool = False

    DATABASE_URL: str | None = None

    @property
    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        if self.DEV_MODE:
            return f"sqlite+aiosqlite:///./{self.SQLITE_PATH}"
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"



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
    GEOIP_DB_PATH: str = str(_DATA_DIR / "geoip/GeoLite2-City.mmdb")
    GEOIP_ASN_DB_PATH: str = str(_DATA_DIR / "geoip/GeoLite2-ASN.mmdb")
    MAXMIND_LICENSE_KEY: str = ""

    # Detection
    SIGMA_RULES_DIR: str = str(_DATA_DIR / "sigma_rules")
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
