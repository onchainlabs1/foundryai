import os
from typing import Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./aims.db"
    
    # Security
    SECRET_KEY: str  # Required: Set via environment variable
    FRONTEND_ORIGIN: str = "http://localhost:3001"
    
    # Organization seeding
    ORG_NAME: Optional[str] = None
    ORG_API_KEY: Optional[str] = None
    
    # S3/R2 Configuration
    S3_ENDPOINT: Optional[str] = None
    S3_REGION: str = "auto"
    S3_BUCKET: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_FORCE_PATH_STYLE: bool = True
    S3_URL_EXP_MIN: int = 15  # presigned URL expiry in minutes
    
    # Feature Flags
    EVIDENCE_LOCAL_STORAGE: bool = True
    RATE_LIMIT: int = 60  # requests per minute
    FEATURE_LLM_REFINE: bool = False  # LLM refinement feature flag
    ENABLE_PDF_EXPORT: bool = True  # PDF export via WeasyPrint
    
    # Templates & Compliance Suite
    TEMPLATES_DIR: str = "assets/templates"

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    @property
    def use_s3(self) -> bool:
        """Check if S3 is configured and should be used."""
        return (
            not self.EVIDENCE_LOCAL_STORAGE
            and self.S3_ENDPOINT
            and self.S3_BUCKET
            and self.S3_ACCESS_KEY
            and self.S3_SECRET_KEY
        )


settings = Settings()

