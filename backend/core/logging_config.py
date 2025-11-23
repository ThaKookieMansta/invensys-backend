import logging
import queue
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from pathlib import Path
from core.config import Settings

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "invensys.log"
LOG_LEVEL = Settings.LOG_LEVEL

# Shared queue for Async Logging
log_queue = queue.Queue(-1)

# File handler with rotation
file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5
)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
file_handler.setFormatter(formatter)

# Queue handler + Listener for Async Logging
queue_handler = QueueHandler(log_queue)
listener = QueueListener(log_queue, file_handler)
listener.start()

# Global Logger
logger = logging.getLogger("invensys")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
logger.addHandler(queue_handler)

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.ERROR)