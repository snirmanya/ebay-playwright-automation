import time
from typing import Callable, Any

def retry(action: Callable[[], Any], retries: int = 3, delay: float = 1.0) -> Any:
    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            return action()
        except Exception as exc:
            last_exception = exc
            if attempt < retries:
                time.sleep(delay)
    raise last_exception