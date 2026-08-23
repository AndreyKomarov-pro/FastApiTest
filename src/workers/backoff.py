from datetime import datetime, timedelta, timezone


def calculate_next_retry(
    attempts: int, base_backoff: int, max_backoff: int,
) -> datetime:
    delay = min(base_backoff * 2 ** attempts, max_backoff)
    return datetime.now(timezone.utc) + timedelta(seconds=delay)
