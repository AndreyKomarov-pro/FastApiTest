import logging
import time
from enum import Enum

logger = logging.getLogger(__name__)

FAILURE_THRESHOLD = 5
RECOVERY_TIMEOUT = 30


class State(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = FAILURE_THRESHOLD,
        recovery_timeout: int = RECOVERY_TIMEOUT,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = State.CLOSED
        self.failure_count = 0
        self.last_failure_time: float = 0

    def allow_request(self) -> bool:
        if self.state == State.CLOSED:
            return True
        if self.state == State.OPEN:
            if time.monotonic() - self.last_failure_time >= self.recovery_timeout:
                self.state = State.HALF_OPEN
                logger.info("Circuit breaker -> HALF_OPEN")
                return True
            return False
        return True

    def record_success(self) -> None:
        if self.state == State.HALF_OPEN:
            logger.info("Circuit breaker -> CLOSED")
        self.failure_count = 0
        self.state = State.CLOSED

    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.monotonic()
        if self.failure_count >= self.failure_threshold:
            self.state = State.OPEN
            logger.warning(
                "Circuit breaker -> OPEN after %d failures", self.failure_count
            )
