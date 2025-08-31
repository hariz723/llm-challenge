import logging
from pathlib import Path
import sys


def setup_logging(log_level: str = "INFO", log_file: str = "src/logs/app.log"):
    """Setup logging configuration with standard formatting"""

    # Create logs directory
    Path("src/logs").mkdir(exist_ok=True)

    class ColoredFormatter(logging.Formatter):
        COLOR_CODES = {
            "INFO": "\033[94m",  # Blue
            "WARNING": "\033[93m",  # Yellow
            "ERROR": "\033[91m",  # Red
            "CRITICAL": "\033[91m",  # Red
            "DEBUG": "\033[92m",  # Green
            "RESET": "\033[0m",
        }

        def format(self, record):
            levelname = record.levelname
            if levelname in self.COLOR_CODES:
                levelname_color = (
                    self.COLOR_CODES[levelname] + levelname + self.COLOR_CODES["RESET"]
                )
                record.levelname = levelname_color
            return super().format(record)

    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"
    )
    console_formatter = ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s")

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # File handler with detailed formatting
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(logging.DEBUG)  # Log all levels to file

    # Console handler with simpler formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)  # Only INFO and above to console

    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Configure third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)  # Reduce uvicorn logging
    logging.getLogger("uvicorn.access").setLevel(
        logging.WARNING
    )  # Reduce uvicorn access logging

    # No return, just configure the root logger


# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)
