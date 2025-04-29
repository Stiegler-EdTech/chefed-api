import logging
from enum import Enum
import colorlog
from apiflask import APIFlask
from colorama import init, Fore, Style

common_log_color='cyan'

class Response_(dict):
    """Helper to create a standardized API response.
    This class extends the built-in dict to provide a convenient way to create API responses.
    """
    def __init__(self, data: dict, message: str = "", code: int = 200):
        super().__init__(data=data, message=message, code=code)

    def NotFound():
        """
        Returns a 404 Not Found response.
        """
        return Response_(data={}, message="Not Found", code=404)

class LogLevel(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4

def setup_logger(logger: logging.Logger):
    handler = logging.StreamHandler()
    
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s[%(levelname)s]%(reset)s %(cyan)s%(message)s",
        log_colors={
            'DEBUG':    'blue',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'bold_red',
        }
    )
    
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)

  # Remove default handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    
class Loggin:
    COLOR_MAP = {
        LogLevel.DEBUG: Fore.BLUE,
        LogLevel.INFO: Fore.GREEN,
        LogLevel.WARNING: Fore.YELLOW,
        LogLevel.ERROR: Fore.RED,
    }

    def log(self, level: LogLevel, message: str):
        """Extensible logging method."""
        self.logger = logging.getLogger(__name__)
        setup_logger(self.logger)
        
        self.logger.log(level.value, f"{message} [builtin-logger referenced]")  # Use the logger's log method to handle the level
        logging.basicConfig(level=logging.INFO, force=True)
        logging.log(level.value, f"{message} [builtin-logger logging]")  # Use the logger's log method to handle the level
        
        level_color = self.COLOR_MAP.get(level, Fore.WHITE)
        message_color=Fore.CYAN
        print(f"{level_color}{level.name}:{Style.RESET_ALL}{message_color} {message}{Style.RESET_ALL} [Loggin]")

    def info(self, message: str):
        self.log(LogLevel.INFO, message)

    def warning(self, message: str):
        self.log(LogLevel.WARNING, message)

    def debug_(self, message: str):
        self.log(LogLevel.DEBUG, message)

    def error(self, message: str):
        self.log(LogLevel.ERROR, message)


class FlaskLoggin(Loggin):
    def __init__(self, app:APIFlask):
        self.app = app
        setup_logger(app.logger)

    def log(self, level: LogLevel, message: str):
        # Use Flask app's logger
        if level == LogLevel.Info:
            self.app.logger.info(message)
        elif level == LogLevel.Warning:
            self.app.logger.warning(message)
        elif level == LogLevel.Error:
            self.app.logger.error(message)
        else:
            self.app.logger.debug(message)

        #todo: the flask logger is outputting to terminal so this would be duplicative
        #super().log(level, message)
        
