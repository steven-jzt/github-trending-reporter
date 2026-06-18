"""网络重试：应对电脑唤醒后网络尚未就绪的情况"""
import time
from log import get_logger


def with_retry(func, name: str, max_retries: int = 3, delay: float = 10.0):
    """调用 func()，网络失败时等待 delay 秒重试，最多 max_retries 次。"""
    log = get_logger("retry")
    last_err = None

    for attempt in range(1, max_retries + 1):
        try:
            result = func()
            if attempt > 1:
                log.info(f"{name}: 第 {attempt} 次尝试成功")
            return result
        except Exception as e:
            last_err = e
            if attempt < max_retries:
                log.warn(f"{name}: 失败 ({e})，{delay}s 后重试 ({attempt}/{max_retries})")
                time.sleep(delay)
            else:
                log.error(f"{name}: {max_retries} 次重试均失败 ({e})")

    raise last_err  # type: ignore[misc]
