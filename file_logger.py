import logging
import structlog
from pathlib import Path
from typing import Optional


def configure_file_logger(
    logger_name: str,
    log_file_path: str | Path,
    log_level: int = logging.INFO,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    encoding: str = "utf-8",
) -> structlog.BoundLogger:
    """
    Configure a structlog logger to log messages only to a file.
    
    Args:
        logger_name: Name of the logger
        log_file_path: Path to the log file
        log_level: Logging level (default: INFO)
        log_format: Format string for log messages
        encoding: File encoding (default: utf-8)
        
    Returns:
        structlog.BoundLogger: Configured structlog logger
        
    Example:
        >>> logger = configure_file_logger("my_app", "logs/app.log")
        >>> logger.info("Application started")
        >>> logger.error("An error occurred", error_code=500)
    """
    # Convert path to Path object if it's a string
    log_file_path = Path(log_file_path)
    
    # Create log directory if it doesn't exist
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get the standard library logger
    std_logger = logging.getLogger(logger_name)
    std_logger.setLevel(log_level)
    
    # Remove only FileHandler handlers to avoid duplicates while preserving other handlers
    for handler in std_logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            std_logger.removeHandler(handler)
    
    # Create a simple file handler
    file_handler = logging.FileHandler(
        filename=log_file_path,
        encoding=encoding,
    )
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    std_logger.addHandler(file_handler)
    
    # Prevent propagation to root logger to avoid console output
    std_logger.propagate = False
    
    # Get the structlog logger
    logger = structlog.get_logger(logger_name)
    
    return logger


def configure_structured_file_logger(
    logger_name: str,
    log_file_path: str | Path,
    log_level: int = logging.INFO,
    encoding: str = "utf-8",
    include_timestamp: bool = True,
    include_logger_name: bool = True,
    include_level: bool = True,
) -> structlog.BoundLogger:
    """
    Configure a structlog logger with structured logging to a file.
    
    Args:
        logger_name: Name of the logger
        log_file_path: Path to the log file
        log_level: Logging level (default: INFO)
        encoding: File encoding (default: utf-8)
        include_timestamp: Whether to include timestamp in logs (default: True)
        include_logger_name: Whether to include logger name in logs (default: True)
        include_level: Whether to include log level in logs (default: True)
        
    Returns:
        structlog.BoundLogger: Configured structlog logger with structured logging
        
    Example:
        >>> logger = configure_structured_file_logger("my_app", "logs/app.json")
        >>> logger.info("User logged in", user_id=123, ip="192.168.1.1")
    """
    import json
    
    # Convert path to Path object if it's a string
    log_file_path = Path(log_file_path)
    
    # Create log directory if it doesn't exist
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get the standard library logger
    std_logger = logging.getLogger(logger_name)
    std_logger.setLevel(log_level)
    
    # Remove only FileHandler handlers to avoid duplicates while preserving other handlers
    for handler in std_logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            std_logger.removeHandler(handler)
    
    # Create a simple file handler
    file_handler = logging.FileHandler(
        filename=log_file_path,
        encoding=encoding,
    )
    
    # Create JSON formatter for structured logging
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                "message": record.getMessage(),
            }
            
            if include_timestamp:
                log_entry["timestamp"] = self.formatTime(record)
            
            if include_logger_name:
                log_entry["logger"] = record.name
            
            if include_level:
                log_entry["level"] = record.levelname
            
            # Add any extra fields from structlog
            if hasattr(record, "structlog"):
                log_entry.update(record.structlog)
            
            return json.dumps(log_entry)
    
    formatter = JSONFormatter()
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    std_logger.addHandler(file_handler)
    
    # Prevent propagation to root logger to avoid console output
    std_logger.propagate = False
    
    # Get the structlog logger
    logger = structlog.get_logger(logger_name)
    
    return logger


def get_file_logger(
    logger_name: str,
    log_file_path: str | Path,
    structured: bool = False,
    **kwargs
) -> structlog.BoundLogger:
    """
    Convenience function to get a file logger with either standard or structured logging.
    
    Args:
        logger_name: Name of the logger
        log_file_path: Path to the log file
        structured: Whether to use structured (JSON) logging (default: False)
        **kwargs: Additional arguments passed to the configuration function
        
    Returns:
        structlog.BoundLogger: Configured structlog logger
        
    Example:
        >>> # Standard logging
        >>> logger = get_file_logger("app", "logs/app.log")
        >>> 
        >>> # Structured logging
        >>> logger = get_file_logger("app", "logs/app.json", structured=True)
    """
    if structured:
        return configure_structured_file_logger(logger_name, log_file_path, **kwargs)
    else:
        return configure_file_logger(logger_name, log_file_path, **kwargs)


def reset_logger_to_defaults(logger_name: str) -> structlog.BoundLogger:
    """
    Reset a named structlog logger to its default configuration.
    
    This function removes all custom handlers and resets the logger to use
    the default structlog configuration, which typically outputs to console.
    
    Args:
        logger_name: Name of the logger to reset
        
    Returns:
        structlog.BoundLogger: Reset structlog logger
        
    Example:
        >>> # Configure a file logger
        >>> logger = configure_file_logger("my_app", "logs/app.log")
        >>> logger.info("This goes to file")
        >>> 
        >>> # Reset to defaults (console output)
        >>> logger = reset_logger_to_defaults("my_app")
        >>> logger.info("This goes to console")
    """
    # Get the standard library logger
    std_logger = logging.getLogger(logger_name)
    
    # Remove all existing handlers
    for handler in std_logger.handlers[:]:
        std_logger.removeHandler(handler)
    
    # Reset logger level to default (NOTSET)
    std_logger.setLevel(logging.NOTSET)
    
    # Re-enable propagation to parent loggers
    std_logger.propagate = True
    
    # Get the structlog logger (this will use default structlog configuration)
    logger = structlog.get_logger(logger_name)
    
    return logger


def reset_all_loggers_to_defaults() -> None:
    """
    Reset all loggers to their default configuration.
    
    This function removes all custom handlers from all loggers and resets
    them to use the default structlog configuration.
    
    Example:
        >>> # Configure multiple file loggers
        >>> logger1 = configure_file_logger("app1", "logs/app1.log")
        >>> logger2 = configure_file_logger("app2", "logs/app2.log")
        >>> 
        >>> # Reset all loggers to defaults
        >>> reset_all_loggers_to_defaults()
        >>> 
        >>> # Now all loggers will output to console by default
        >>> logger1.info("This goes to console")
        >>> logger2.info("This also goes to console")
    """
    # Get all existing loggers
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    
    # Also include the root logger
    loggers.append(logging.getLogger())
    
    for logger in loggers:
        # Remove all existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Reset logger level to default
        logger.setLevel(logging.NOTSET)
        
        # Re-enable propagation
        logger.propagate = True


def get_logger_info(logger_name: str) -> dict:
    """
    Get information about a logger's current configuration.
    
    Args:
        logger_name: Name of the logger to inspect
        
    Returns:
        dict: Information about the logger's configuration
        
    Example:
        >>> logger = configure_file_logger("my_app", "logs/app.log")
        >>> info = get_logger_info("my_app")
        >>> print(info)
        >>> # Output: {'name': 'my_app', 'level': 20, 'handlers': 1, 'propagate': False}
    """
    std_logger = logging.getLogger(logger_name)
    
    return {
        "name": logger_name,
        "level": std_logger.level,
        "handlers": len(std_logger.handlers),
        "propagate": std_logger.propagate,
        "handler_types": [type(handler).__name__ for handler in std_logger.handlers],
    }


# Example usage and testing
if __name__ == "__main__":
    # Example 1: Standard file logging
    logger1 = configure_file_logger("test_app", "logs/test.log")
    logger1.info("This is a test message")
    logger1.error("This is an error message", error_code=500)
    
    # Example 2: Structured file logging
    logger2 = configure_structured_file_logger("test_app_structured", "logs/test.json")
    logger2.info("User action", user_id=123, action="login", ip="192.168.1.1")
    logger2.error("Database error", error_code=500, table="users", query="SELECT *")
    
    # Example 3: Using convenience function
    logger3 = get_file_logger("convenience_app", "logs/convenience.log")
    logger3.info("Using convenience function")
    
    logger4 = get_file_logger("convenience_structured", "logs/convenience.json", structured=True)
    logger4.info("Structured logging with convenience", event="test", data={"key": "value"})
    
    # Example 4: Demonstrating reset functionality
    print("\n=== Testing Reset Functionality ===")
    
    # Show logger info before reset
    print("Before reset:")
    print(f"test_app logger info: {get_logger_info('test_app')}")
    
    # Reset specific logger
    reset_logger = reset_logger_to_defaults("test_app")
    reset_logger.info("This message goes to console (after reset)")
    
    # Show logger info after reset
    print("After reset:")
    print(f"test_app logger info: {get_logger_info('test_app')}")
    
    # Example 5: Reset all loggers
    print("\n=== Resetting All Loggers ===")
    reset_all_loggers_to_defaults()
    
    # All loggers now use default configuration
    logger1.info("This also goes to console now")
    logger2.info("This also goes to console now")
    
    print("\nLog files created successfully!")
    print("Check the 'logs' directory for the generated log files.")
    print("After reset, all loggers output to console by default.") 