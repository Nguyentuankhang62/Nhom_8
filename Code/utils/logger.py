
import logging
from pathlib import Path


def get_logger(name="UDM_11", log_file="logs/app.log"):
    """Tạo logger ghi thông báo ra console và file."""

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Nếu logger đã có handler thì không thêm handler trùng.
    if logger.handlers:
        return logger

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(
        log_path,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def close_logger(logger):
    """Đóng và gỡ các handler của logger khi không còn sử dụng."""
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
