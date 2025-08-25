"""
Configuration constants for the CBOE Trail Search API
"""
import logging
import os
from pathlib import Path
from typing import List

# API Configuration
API_TITLE = "CBOE Trail Search API"
API_VERSION = "1.0.0"
HOST = os.getenv("API_HOST", "0.0.0.0")
PORT = int(os.getenv("API_PORT", "8000"))

# CORS Configuration
def get_cors_origins() -> List[str]:
    """Get CORS origins from environment variable"""
    origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
    return [origin.strip() for origin in origins_str.split(",")]

ALLOWED_ORIGINS = get_cors_origins()

# Database Configuration
DB_PATH = os.getenv("DATABASE_URL", "trails.db").replace("sqlite:///", "").replace("./", "")

# AI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
OPENAI_MAX_COMPLETION_TOKENS = int(os.getenv("OPENAI_MAX_COMPLETION_TOKENS", "500"))

# Geographic Constants
CHICAGO_LAT = 41.8781
CHICAGO_LNG = -87.6298
DEFAULT_RADIUS_MILES = 37.3  # ~60 km converted to miles

# Search Configuration
MAX_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "20"))
TOP_RESULTS_LIMIT = 100

# Streaming Configuration
WORDS_PER_CHUNK = int(os.getenv("WORDS_PER_CHUNK", "3"))
STREAM_DELAY_MS = int(os.getenv("STREAM_DELAY_MS", "80"))

# Request Limits
MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE_BYTES", "10240"))

# Performance Settings
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(funcName)s:%(lineno)d"

def setup_logging():
    """Setup logging configuration with structured format"""
    import json
    import datetime
    
    class StructuredFormatter(logging.Formatter):
        def format(self, record):
            log_obj = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            if record.exc_info:
                log_obj["exception"] = self.formatException(record.exc_info)
            
            return json.dumps(log_obj)
    
    # Setup handlers with structured logging
    structured_formatter = StructuredFormatter()
    console_formatter = logging.Formatter(LOG_FORMAT)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    
    file_handler = logging.FileHandler("trail_search.log")
    file_handler.setFormatter(structured_formatter)
    
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper()),
        handlers=[console_handler, file_handler]
    )
    
    # Create logger for our application
    logger = logging.getLogger("trail_search")
    return logger
