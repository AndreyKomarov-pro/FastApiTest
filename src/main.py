import logging

from src.application import get_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s request_id=%(request_id)s — %(message)s",
    defaults={"request_id": "-"},
)

app = get_app()
