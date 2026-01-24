"""
Configuration Management Module

This module provides centralized configuration management for the LLM Government
Consulting System. It handles environment variables, validation, and provides
type-safe configuration access across the application.

Author: LLM Government Consulting Team
Date: January 24, 2026
Version: 2.0.0 (Professional Refactor)
"""

import os
from dataclasses import dataclass
from datetime import timedelta
from typing import List, Optional
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database configuration settings.
    
    Attributes:
        url: Database connection URL
        track_modifications: SQLAlchemy track modifications flag
        pool_size: Connection pool size
        pool_timeout: Connection timeout in seconds
        pool_recycle: Connection recycle time in seconds
    """
    url: str
    track_modifications: bool = False
    pool_size: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class SecurityConfig:
    """Security and authentication configuration.
    
    Attributes:
        secret_key: Flask secret key for session management
        jwt_secret_key: JWT token encryption key
        jwt_access_token_expires: JWT token expiration time
        password_min_length: Minimum password length
        rate_limit: API rate limit per user
    """
    secret_key: str
    jwt_secret_key: str
    jwt_access_token_expires: timedelta
    password_min_length: int = 8
    rate_limit: str = "100/hour"


@dataclass
class LLMConfig:
    """LLM (Large Language Model) API configuration.
    
    Attributes:
        api_key: OpenAI/Anthropic API key
        model: Default model to use
        temperature: Model temperature (0.0 to 1.0)
        max_tokens: Maximum tokens per request
        timeout: API request timeout in seconds
        retry_attempts: Number of retry attempts for failed requests
    """
    api_key: Optional[str]
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 60
    retry_attempts: int = 3


@dataclass
class CORSConfig:
    """Cross-Origin Resource Sharing configuration.
    
    Attributes:
        origins: List of allowed origins
        methods: List of allowed HTTP methods
        allow_headers: List of allowed headers
    """
    origins: List[str]
    methods: List[str] = None
    allow_headers: List[str] = None
    
    def __post_init__(self):
        if self.methods is None:
            self.methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        if self.allow_headers is None:
            self.allow_headers = ["Content-Type", "Authorization"]


@dataclass
class LoggingConfig:
    """Logging configuration.
    
    Attributes:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format: Log message format
        file_path: Path to log file
        max_bytes: Maximum log file size in bytes
        backup_count: Number of backup log files to keep
    """
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/app.log"
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5


class Config:
    """Main configuration class for the application.
    
    This class loads and validates all configuration settings from environment
    variables and provides type-safe access to configuration values.
    
    Environment Variables:
        DATABASE_URL: Database connection URL
        SECRET_KEY: Flask secret key
        JWT_SECRET_KEY: JWT encryption key
        LLM_API_KEY: OpenAI/Anthropic API key
        CORS_ORIGINS: Comma-separated list of allowed origins
        LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        ENVIRONMENT: Application environment (development, staging, production)
    
    Example:
        >>> config = Config()
        >>> print(config.database.url)
        >>> print(config.security.jwt_secret_key)
    """
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.debug = self.environment == 'development'
        
        # Initialize sub-configurations
        self.database = self._load_database_config()
        self.security = self._load_security_config()
        self.llm = self._load_llm_config()
        self.cors = self._load_cors_config()
        self.logging = self._load_logging_config()
        
        # Application settings
        self.app_name = "LLM Government Consulting System"
        self.app_version = "2.0.0"
        self.host = os.getenv('HOST', '0.0.0.0')
        self.port = int(os.getenv('PORT', 5000))
        
        # Validate configuration
        self._validate()
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration from environment."""
        return DatabaseConfig(
            url=os.getenv(
                'DATABASE_URL',
                'sqlite:///llm_consulting.db'  # Default to SQLite for development
            )
        )
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration from environment."""
        return SecurityConfig(
            secret_key=os.getenv(
                'SECRET_KEY',
                'dev-secret-key-CHANGE-IN-PRODUCTION'  # Default for development
            ),
            jwt_secret_key=os.getenv(
                'JWT_SECRET_KEY',
                'dev-jwt-secret-CHANGE-IN-PRODUCTION'  # Default for development
            ),
            jwt_access_token_expires=timedelta(
                hours=int(os.getenv('JWT_EXPIRES_HOURS', 24))
            )
        )
    
    def _load_llm_config(self) -> LLMConfig:
        """Load LLM API configuration from environment."""
        return LLMConfig(
            api_key=os.getenv('LLM_API_KEY'),  # Required in production
            model=os.getenv('LLM_MODEL', 'gpt-4'),
            temperature=float(os.getenv('LLM_TEMPERATURE', 0.7)),
            max_tokens=int(os.getenv('LLM_MAX_TOKENS', 4000))
        )
    
    def _load_cors_config(self) -> CORSConfig:
        """Load CORS configuration from environment."""
        origins_str = os.getenv('CORS_ORIGINS', 'http://localhost:3000')
        origins = [origin.strip() for origin in origins_str.split(',')]
        return CORSConfig(origins=origins)
    
    def _load_logging_config(self) -> LoggingConfig:
        """Load logging configuration from environment."""
        return LoggingConfig(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            file_path=os.getenv('LOG_FILE', 'logs/app.log')
        )
    
    def _validate(self) -> None:
        """Validate configuration settings.
        
        Raises:
            ValueError: If required configuration is missing in production
            RuntimeError: If configuration values are invalid
        """
        # In production, ensure critical secrets are set
        if self.environment == 'production':
            if 'dev-secret-key' in self.security.secret_key.lower():
                raise ValueError(
                    "Production environment detected with default SECRET_KEY. "
                    "Please set a secure SECRET_KEY environment variable."
                )
            
            if 'dev-jwt-secret' in self.security.jwt_secret_key.lower():
                raise ValueError(
                    "Production environment detected with default JWT_SECRET_KEY. "
                    "Please set a secure JWT_SECRET_KEY environment variable."
                )
            
            if not self.llm.api_key:
                raise ValueError(
                    "Production environment requires LLM_API_KEY to be set."
                )
        
        # Validate database URL format
        if not self.database.url:
            raise ValueError("DATABASE_URL cannot be empty")
        
        # Validate LLM temperature range
        if not 0.0 <= self.llm.temperature <= 2.0:
            raise ValueError(
                f"LLM temperature must be between 0.0 and 2.0, "
                f"got {self.llm.temperature}"
            )
        
        # Create log directory if it doesn't exist
        log_dir = Path(self.logging.file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    def get_database_uri(self) -> str:
        """Get the database URI.
        
        Returns:
            str: Database connection URI
        """
        return self.database.url
    
    def is_development(self) -> bool:
        """Check if running in development mode.
        
        Returns:
            bool: True if in development mode
        """
        return self.environment == 'development'
    
    def is_production(self) -> bool:
        """Check if running in production mode.
        
        Returns:
            bool: True if in production mode
        """
        return self.environment == 'production'
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return (
            f"Config(environment={self.environment}, "
            f"app_name='{self.app_name}', "
            f"version={self.app_version})"
        )


# Global configuration instance
config = Config()


if __name__ == "__main__":
    # Test configuration loading
    print("=" * 60)
    print("Configuration Test")
    print("=" * 60)
    print(f"Environment: {config.environment}")
    print(f"Debug Mode: {config.debug}")
    print(f"Database URL: {config.database.url}")
    print(f"JWT Expires: {config.security.jwt_access_token_expires}")
    print(f"LLM Model: {config.llm.model}")
    print(f"CORS Origins: {config.cors.origins}")
    print(f"Log Level: {config.logging.level}")
    print("=" * 60)
    print("✅ Configuration loaded successfully!")
