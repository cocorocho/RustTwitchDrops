import time

def get_time():
    """
    Get time in HH:MM format
    """
    return time.strftime("%H:%M")

def print_with_time(text: str) -> str:
    """
    Print to console with time
    """
    print(f"[{get_time()}] {text}")
    