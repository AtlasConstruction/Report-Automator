import logging
import os
from typing import Any, Optional



class Logger:
    """
    A wrapper class for Python's logging module with additional convenience methods.
    """
    
    def start_logger():
        logging.basicConfig(
        filename=os.path.join(os.path.dirname(__file__), '../logs/app.log'),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
)
    @staticmethod
    def log(message: str, level: int = logging.INFO, exc_info: Optional[Any] = None) -> None:
        """
        Log a message with the specified level.
        
        Args:
            message: The message to log
            level: The logging level (default: logging.INFO)
            exc_info: Exception information to include (for error logging)
        """
        logging.log(level, message, exc_info=exc_info)
    
    @staticmethod
    def error(message: str, exc_info: Optional[Any] = None) -> None:
        """
        Log an error message.
        
        Args:
            message: The error message to log
            exc_info: Exception information to include
        """
        logging.error(message, exc_info=exc_info)
    
    @staticmethod
    def info(message: str) -> None:
        """
        Log an informational message.
        
        Args:
            message: The info message to log
        """
        logging.info(message)
    
    @staticmethod
    def warning(message: str) -> None:
        """
        Log a warning message.
        
        Args:
            message: The warning message to log
        """
        logging.warning(message)
    
    @staticmethod
    def debug(message: str) -> None:
        """
        Log a debug message.
        
        Args:
            message: The debug message to log
        """
        logging.debug(message)
    
    @staticmethod
    def critical(message: str, exc_info: Optional[Any] = None) -> None:
        """
        Log a critical message.
        
        Args:
            message: The critical message to log
            exc_info: Exception information to include
        """
        logging.critical(message, exc_info=exc_info)
    
    @staticmethod
    def exception(message: str) -> None:
        """
        Log a message with exception information.
        This should only be called from an exception handler.
        
        Args:
            message: The message to log with exception info
        """
        logging.exception(message)

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get a named logger instance.
        
        Args:
            name: The name of the logger
            
        Returns:
            A configured logger instance
        """
        return logging.getLogger(name)