import json
from pathlib import Path


default_settings = {
    "video-muted": { "default": True },
    "mature": True,
    "video-quality": { "default": "160p30" }
}

def load_settings(settings) -> dict:
    settings_file = Path("config.json")

    if not settings_file.is_file():
        create_settings_file()


    with open(settings_file) as config_file:
        conf = json.loads(config_file.read())
        settings |= conf

    return settings


def create_settings_file(file: Path):
    file.touch()

    with open(file, "w") as f:
        f.write(default_settings)


settings = default_settings

# Load user defined settings
settings = load_settings(settings)        
