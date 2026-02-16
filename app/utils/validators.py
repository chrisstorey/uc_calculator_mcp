"""Validation utilities."""
import re


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_username(username: str) -> bool:
    """Validate username format."""
    if len(username) < 3 or len(username) > 20:
        return False
    pattern = r"^[a-zA-Z0-9_-]+$"
    return re.match(pattern, username) is not None


def validate_password(password: str) -> bool:
    """Validate password strength."""
    if len(password) < 8:
        return False
    has_upper = re.search(r"[A-Z]", password)
    has_lower = re.search(r"[a-z]", password)
    has_digit = re.search(r"\d", password)
    return bool(has_upper and has_lower and has_digit)
