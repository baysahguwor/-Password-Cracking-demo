import re
import math

COMMON_WORDS = [
    "password", "admin", "welcome", "letmein", "monkey", "football",
    "qwerty", "abc123", "iloveyou", "master", "dragon", "pass",
    "login", "hello", "sunshine", "princess", "shadow", "superman",
    "michael", "baseball"
]

CHAR_SETS = {
    "lowercase": 26,
    "uppercase": 26,
    "digits": 10,
    "symbols": 32,
}


def analyze_password(password: str) -> dict:
    length = len(password)
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_symbol = bool(re.search(r"[^A-Za-z0-9]", password))
    has_common = any(word in password.lower() for word in COMMON_WORDS)

    score = 0
    if length >= 8:
        score += 1
    if length >= 12:
        score += 1
    if length >= 16:
        score += 1
    if has_upper:
        score += 1
    if has_lower:
        score += 1
    if has_digit:
        score += 1
    if has_symbol:
        score += 2
    if has_common:
        score -= 2

    score = max(0, min(score, 8))

    if score <= 1:
        strength = "Very Weak"
        color = "#FF4444"
    elif score <= 3:
        strength = "Weak"
        color = "#FF8C00"
    elif score <= 5:
        strength = "Moderate"
        color = "#FFD700"
    elif score <= 6:
        strength = "Strong"
        color = "#7CFC00"
    else:
        strength = "Very Strong"
        color = "#00FF88"

    charset_size = 0
    if has_lower:
        charset_size += CHAR_SETS["lowercase"]
    if has_upper:
        charset_size += CHAR_SETS["uppercase"]
    if has_digit:
        charset_size += CHAR_SETS["digits"]
    if has_symbol:
        charset_size += CHAR_SETS["symbols"]
    if charset_size == 0:
        charset_size = 26

    combinations = charset_size ** length
    guesses_per_second = 1_000_000_000  # 1 billion/sec (modern GPU)
    seconds_to_crack = combinations / guesses_per_second

    crack_time_str = _format_time(seconds_to_crack)

    return {
        "length": length,
        "has_upper": has_upper,
        "has_lower": has_lower,
        "has_digit": has_digit,
        "has_symbol": has_symbol,
        "has_common": has_common,
        "score": score,
        "strength": strength,
        "color": color,
        "charset_size": charset_size,
        "combinations": combinations,
        "crack_time_str": crack_time_str,
        "strength_percent": int((score / 8) * 100),
    }


def _format_time(seconds: float) -> str:
    if seconds < 0.001:
        return "Instantly"
    elif seconds < 1:
        return f"{seconds * 1000:.1f} milliseconds"
    elif seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        return f"{seconds / 60:.1f} minutes"
    elif seconds < 86400:
        return f"{seconds / 3600:.1f} hours"
    elif seconds < 2_592_000:
        return f"{seconds / 86400:.1f} days"
    elif seconds < 31_536_000:
        return f"{seconds / 2_592_000:.1f} months"
    elif seconds < 31_536_000_000:
        return f"{seconds / 31_536_000:.1f} years"
    else:
        years = seconds / 31_536_000
        exp = math.log10(years)
        return f"10^{exp:.0f} years"
