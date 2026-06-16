"""结构化日志：同时输出到控制台和 logs/ 目录"""
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Logger:
    def __init__(self, name: str):
        self.name = name
        log_file = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        self._fh = open(str(log_file), "a", encoding="utf-8")

    def _write(self, level: str, msg: str):
        ts = _now()
        line = f"[{ts}] [{level}] [{self.name}] {msg}"
        # 控制台
        try:
            print(line)
        except UnicodeEncodeError:
            print(line.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8", errors="replace"))
        # 文件
        self._fh.write(line + "\n")
        self._fh.flush()

    def info(self, msg: str):
        self._write("INFO", msg)

    def warn(self, msg: str):
        self._write("WARN", msg)

    def error(self, msg: str):
        self._write("ERROR", msg)

    def ok(self, msg: str):
        self._write("OK", msg)

    def close(self):
        if self._fh and not self._fh.closed:
            self._fh.close()


_loggers: dict[str, Logger] = {}


def get_logger(name: str = "main") -> Logger:
    if name not in _loggers:
        _loggers[name] = Logger(name)
    return _loggers[name]
