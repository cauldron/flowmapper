import logging
from typing import List


def stop_console_logging(logger_name: str) -> None:
    """
    Stop a named stdlib logger from writing to the console.
    
    This function removes all StreamHandler instances from the specified logger
    while preserving other types of handlers (like FileHandler).
    
    Args:
        logger_name: Name of the logger to stop console logging for
        
    Example:
        >>> import logging
        >>> logger = logging.getLogger("my_app")
        >>> logger.addHandler(logging.StreamHandler())  # Console handler
        >>> logger.addHandler(logging.FileHandler("app.log"))  # File handler
        >>> 
        >>> # Stop console logging
        >>> stop_console_logging("my_app")
        >>> 
        >>> # Now logs only go to file, not console
        >>> logger.info("This goes to file only")
    """
    logger = logging.getLogger(logger_name)
    
    # Remove all StreamHandler instances (console handlers)
    handlers_to_remove = []
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handlers_to_remove.append(handler)
    
    for handler in handlers_to_remove:
        logger.removeHandler(handler)


def start_console_logging(logger_name: str, level: int = logging.INFO) -> None:
    """
    Start console logging for a named stdlib logger.
    
    This function adds a StreamHandler to the specified logger if one doesn't
    already exist.
    
    Args:
        logger_name: Name of the logger to start console logging for
        level: Logging level for the console handler (default: INFO)
        
    Example:
        >>> import logging
        >>> logger = logging.getLogger("my_app")
        >>> 
        >>> # Start console logging
        >>> start_console_logging("my_app")
        >>> 
        >>> # Now logs go to console
        >>> logger.info("This goes to console")
    """
    logger = logging.getLogger(logger_name)
    
    # Check if a StreamHandler already exists
    has_stream_handler = any(
        isinstance(handler, logging.StreamHandler) for handler in logger.handlers
    )
    
    if not has_stream_handler:
        # Create and add a new StreamHandler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # Create a simple formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)


def toggle_console_logging(logger_name: str, enable: bool = True, level: int = logging.INFO) -> None:
    """
    Toggle console logging for a named stdlib logger.
    
    Args:
        logger_name: Name of the logger to toggle console logging for
        enable: True to enable console logging, False to disable (default: True)
        level: Logging level for the console handler when enabling (default: INFO)
        
    Example:
        >>> import logging
        >>> logger = logging.getLogger("my_app")
        >>> 
        >>> # Enable console logging
        >>> toggle_console_logging("my_app", enable=True)
        >>> logger.info("This goes to console")
        >>> 
        >>> # Disable console logging
        >>> toggle_console_logging("my_app", enable=False)
        >>> logger.info("This doesn't go to console")
    """
    if enable:
        start_console_logging(logger_name, level)
    else:
        stop_console_logging(logger_name)


def get_console_handlers(logger_name: str) -> List[logging.Handler]:
    """
    Get all console handlers (StreamHandler) for a named logger.
    
    Args:
        logger_name: Name of the logger to inspect
        
    Returns:
        List of StreamHandler instances attached to the logger
        
    Example:
        >>> import logging
        >>> logger = logging.getLogger("my_app")
        >>> logger.addHandler(logging.StreamHandler())
        >>> 
        >>> handlers = get_console_handlers("my_app")
        >>> print(f"Found {len(handlers)} console handlers")
    """
    logger = logging.getLogger(logger_name)
    
    return [
        handler for handler in logger.handlers 
        if isinstance(handler, logging.StreamHandler)
    ]


def has_console_logging(logger_name: str) -> bool:
    """
    Check if a named logger has console logging enabled.
    
    Args:
        logger_name: Name of the logger to check
        
    Returns:
        True if the logger has console handlers, False otherwise
        
    Example:
        >>> import logging
        >>> logger = logging.getLogger("my_app")
        >>> 
        >>> print(has_console_logging("my_app"))  # False
        >>> 
        >>> logger.addHandler(logging.StreamHandler())
        >>> print(has_console_logging("my_app"))  # True
    """
    return len(get_console_handlers(logger_name)) > 0


def stop_all_console_logging() -> None:
    """
    Stop console logging for all loggers in the application.
    
    This function removes all StreamHandler instances from all loggers,
    including the root logger.
    
    Example:
        >>> import logging
        >>> 
        >>> # Configure multiple loggers with console output
        >>> logger1 = logging.getLogger("app1")
        >>> logger1.addHandler(logging.StreamHandler())
        >>> 
        >>> logger2 = logging.getLogger("app2")
        >>> logger2.addHandler(logging.StreamHandler())
        >>> 
        >>> # Stop all console logging
        >>> stop_all_console_logging()
        >>> 
        >>> # Now no logs go to console
        >>> logger1.info("No console output")
        >>> logger2.info("No console output")
    """
    # Get all existing loggers
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    
    # Also include the root logger
    loggers.append(logging.getLogger())
    
    # Stop console logging for each logger
    for logger in loggers:
        stop_console_logging(logger.name if logger.name else "root")


def configure_logger_without_console(
    logger_name: str,
    level: int = logging.INFO,
    handlers: List[logging.Handler] = None
) -> logging.Logger:
    """
    Configure a logger without any console output.
    
    This function creates a logger with the specified handlers but ensures
    no console output is possible.
    
    Args:
        logger_name: Name of the logger to configure
        level: Logging level for the logger (default: INFO)
        handlers: List of handlers to add to the logger (default: None)
        
    Returns:
        Configured logger without console output
        
    Example:
        >>> import logging
        >>> from logging.handlers import FileHandler
        >>> 
        >>> # Create a file handler
        >>> file_handler = FileHandler("app.log")
        >>> 
        >>> # Configure logger with only file output
        >>> logger = configure_logger_without_console("my_app", handlers=[file_handler])
        >>> 
        >>> # This goes to file only, not console
        >>> logger.info("File only output")
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # Remove all existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add specified handlers
    if handlers:
        for handler in handlers:
            logger.addHandler(handler)
    
    # Ensure no console output by setting propagate to False
    # This prevents logs from bubbling up to parent loggers (like root)
    logger.propagate = False
    
    return logger


# Example usage and testing
if __name__ == "__main__":
    # Example 1: Basic console logging control
    print("=== Example 1: Basic Console Logging Control ===")
    
    logger = logging.getLogger("test_app")
    logger.setLevel(logging.INFO)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    print("Before stopping console logging:")
    logger.info("This should appear in console")
    
    # Stop console logging
    stop_console_logging("test_app")
    print("After stopping console logging:")
    logger.info("This should NOT appear in console")
    
    # Example 2: Toggle console logging
    print("\n=== Example 2: Toggle Console Logging ===")
    
    logger2 = logging.getLogger("toggle_app")
    logger2.setLevel(logging.INFO)
    
    # Enable console logging
    toggle_console_logging("toggle_app", enable=True)
    print("Console logging enabled:")
    logger2.info("This should appear in console")
    
    # Disable console logging
    toggle_console_logging("toggle_app", enable=False)
    print("Console logging disabled:")
    logger2.info("This should NOT appear in console")
    
    # Example 3: Check console logging status
    print("\n=== Example 3: Check Console Logging Status ===")
    
    logger3 = logging.getLogger("status_app")
    print(f"Has console logging: {has_console_logging('status_app')}")  # False
    
    start_console_logging("status_app")
    print(f"Has console logging: {has_console_logging('status_app')}")  # True
    
    console_handlers = get_console_handlers("status_app")
    print(f"Number of console handlers: {len(console_handlers)}")
    
    # Example 4: Configure logger without console
    print("\n=== Example 4: Configure Logger Without Console ===")
    
    from logging.handlers import FileHandler
    
    # Create a file handler
    file_handler = FileHandler("test_output.log")
    file_handler.setFormatter(formatter)
    
    # Configure logger with only file output
    file_only_logger = configure_logger_without_console(
        "file_only_app", 
        handlers=[file_handler]
    )
    
    print("File-only logger configured:")
    file_only_logger.info("This goes to file only")
    
    print("\nAll examples completed!")
    print("Check 'test_output.log' for file output.") 