from datetime import datetime

def log(message, level="INFO"):
    """
    Logs a message with a timestamp and log level.

    Args:
        message (str): Message to log
        level (str): Log level (e.g., INFO, ERROR, DEBUG)
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{level}] {timestamp} - {message}")
