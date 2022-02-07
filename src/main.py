import logging
import sys
import os

from chromedriver import ChromeDriverDownloader
from twitch import Twitch

if getattr(sys, 'frozen', False):
    app_path = os.path.dirname(sys.executable)
else:
    app_path = os.path.dirname(os.path.abspath(__file__))

LOGNAME = "log.txt"

logger = logging.getLogger("Logger")
logging.basicConfig(
    filename=LOGNAME,
    filemode="a+",
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s %(levelname)s\t %(message)s"
)

def log_handler(exception_type, exception_value, exception_traceback):
    logger.exception(
        exception_value,
        exc_info=(exception_type, exception_value, exception_traceback)
    )

sys.excepthook = log_handler

if __name__ == "__main__":
    chromedriver = ChromeDriverDownloader()
    chromedriver.download()
    twitch = Twitch()
    twitch.get_drops()
    