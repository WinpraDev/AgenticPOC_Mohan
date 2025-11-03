"""
Configuration management for Meta-Agent.
All configuration loaded from environment variables - NO HARDCODED VALUES.
System will fail explicitly if required configuration is missing.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """
    Meta-Agent configuration.
    All values loaded from environment variables (.env file).
    NO fallback values - system fails fast if configuration missing.
    """
    
    # ==================== LLM Configuration ====================
    # REQUIRED: LM Studio must be running, no fallbacks
    llm_base_url: str = Field(..., description="LM Studio API endpoint")
    llm_model_name: str = Field(..., description="Model name in LM Studio")
    llm_api_key: str = Field(..., description="API key for LM Studio")
    llm_temperature: float = Field(..., description="Temperature for code generation")
    llm_max_tokens: int = Field(..., description="Max tokens per response")
    llm_context_length: int = Field(..., description="Context window size")
    
    # ==================== Database Configuration ====================
    # REQUIRED: PostgreSQL connection, no fallbacks
    database_url: str = Field(..., description="PostgreSQL connection string")
    
    # ==================== Meta-Agent Configuration ====================
    meta_agent_log_level: str = Field(default="INFO", description="Logging level")
    meta_agent_max_retries: int = Field(default=3, description="Max retry attempts for errors")
    meta_agent_timeout: int = Field(default=300, description="Timeout for operations (seconds)")
    meta_agent_strict_mode: bool = Field(default=True, description="Fail on any error, no fallbacks")
    
    # ==================== Sandbox Configuration ====================
    docker_timeout: int = Field(default=30, description="Docker execution timeout")
    sandbox_memory_limit: str = Field(default="512m", description="Memory limit for sandbox")
    sandbox_cpu_limit: float = Field(default=1.0, description="CPU limit for sandbox")
    sandbox_image: str = Field(default="python:3.11-slim", description="Docker image for sandbox")
    
    # ==================== Output Configuration ====================
    output_dir: Path = Field(default=Path("./generated_agents"), description="Output directory for generated agents")
    spec_dir: Path = Field(default=Path("./agent_specs"), description="Directory for agent specifications")
    log_dir: Path = Field(default=Path("./logs"), description="Log directory")
    
    @validator('llm_base_url')
    def validate_llm_url(cls, v):
        """Ensure LLM URL is configured"""
        if not v or v == "":
            raise ValueError(
                "LLM_BASE_URL must be configured. "
                "Please set it in .env file. "
                "Example: LLM_BASE_URL=http://localhost:1234/v1"
            )
        return v
    
    @validator('database_url')
    def validate_database_url(cls, v):
        """Ensure database URL is configured"""
        if not v or v == "" or "username:password" in v:
            raise ValueError(
                "DATABASE_URL must be configured with real credentials. "
                "Please set it in .env file. "
                "Example: DATABASE_URL=postgresql://user:pass@localhost:5432/dbname"
            )
        return v
    
    @validator('llm_temperature')
    def validate_temperature(cls, v):
        """Ensure temperature is in valid range"""
        if not 0.0 <= v <= 1.0:
            raise ValueError("LLM_TEMPERATURE must be between 0.0 and 1.0")
        return v
    
    def __init__(self, **kwargs):
        """Initialize settings and create necessary directories"""
        super().__init__(**kwargs)
        
        # Create output directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.spec_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
# This will fail immediately if .env is not configured properly
try:
    settings = Settings()
except Exception as e:
    print("\n" + "="*70)
    print("❌ CONFIGURATION ERROR")
    print("="*70)
    print(f"\nError: {str(e)}\n")
    print("Required actions:")
    print("1. Create .env file in project root")
    print("2. Set all required environment variables")
    print("3. Example .env file:")
    print("""
# LM Studio Configuration
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL_NAME=qwen2.5-coder-7b-instruct-mlx
LLM_API_KEY=lm-studio
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4096
LLM_CONTEXT_LENGTH=8192

# Database Configuration
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/orlando_db

# Meta-Agent Configuration
META_AGENT_STRICT_MODE=true
""")
    print("="*70 + "\n")
    raise SystemExit(1)

