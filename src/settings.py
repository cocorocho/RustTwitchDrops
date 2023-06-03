import json
from pathlib import Path


def load_settings(settings) -> dict:
    file_name = "config.json"

    if Path(file_name).is_file():
        with open(file_name) as config_file:
            conf = json.loads(config_file.read())
            settings |= conf

    return settings

default_settings = {
    "video-muted": True,
    "mature": True,
    "video-quality": "160p30"
}

settings = default_settings

# Load user defined settings
settings = load_settings(settings)        
