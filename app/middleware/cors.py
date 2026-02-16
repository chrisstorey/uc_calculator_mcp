"""CORS middleware configuration."""
from typing import List


def get_cors_middleware() -> dict:
    """Get CORS middleware configuration."""
    return {
        "allow_origins": ["*"],
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
