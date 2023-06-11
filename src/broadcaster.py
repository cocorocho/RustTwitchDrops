import logging
import json
from pathlib import Path
from typing import List, Optional

import requests
from bs4 import BeautifulSoup
from utils import print_with_time

from settings import settings
from exceptions import UserDefinedStreamsLoadException
from constants import USER_DEFINED_STREAMS_FILENAME


logger = logging.getLogger("Logger")

# Session
session = requests.Session()
session_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 OPR/99.0.0.0"}
session.headers.update(session_headers)


def get_broadcaster_urls() -> List[str]:
    url = "https://github.com/cocorocho/RustTwitchDrops"
    
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, features="lxml")
    
        streams_container = soup.find("div", {"id": "user-content-streamers"})
        url_elems = streams_container.find_all("a", {"href": True})

        stream_urls = [url["href"] for url in url_elems]
        return stream_urls
    except Exception as err:
        print("Error getting list of streamers")
        logger.error("Error getting list of streamers")
        logger.error(err)
        exit(1)


class Broadcaster:
    def __init__(self, url: str, num_drops: int=1) -> None:
        self.url = url
        self.num_drops = num_drops

    def __str__(self) -> str:
        return self.url
    
    @property
    def is_online(self) -> bool:
        response = session.get(self.url)
        return "isLiveBroadcast" in response.content.decode("utf-8")
    

def get_user_defined_broadcasters() -> Optional[List[Broadcaster]]:
    """
    Load user defined broadcasters for drops from `user_defined_streams.json`

    If `user_defined_streams.json` has data, it will be used for drops.

    Format for file is list of URLs:

    [
        "https://www.twitch.tv/foo",
        "https://www.twitch.tv/bar",
        "https://www.twitch.tv/baz"
        ...
    ]

    In some cases single stream can have many consecutive drops.
    `url` param is not optional
    In this case use this format:

    [
        {
            "url": "https://www.twitch.tv/foo",
            "num_drops":2
        },
        {
            "url": "https://www.twitch.tv/bar",
            "num_drops": 4
        },
        "https://www.twitch.tv/baz" <<<< you don't have to use object format if num_drops is 1
    ]
    """
    file = Path(USER_DEFINED_STREAMS_FILENAME)
    file.touch(exist_ok=True)
    
    broadcasters = []

    with open(file) as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError:
            raise UserDefinedStreamsLoadException()

        for row in data:
            if isinstance(row, dict):
                broadcasters.append(Broadcaster(**row))
                continue

            broadcasters.append(Broadcaster(row))

    return broadcasters


def get_broadcasters() -> List[Broadcaster]:
    print_with_time("Getting broadcaster list")
    print_with_time("Checking user defined broadcasters")

    user_defined_broadcasters = get_user_defined_broadcasters()

    if user_defined_broadcasters:
        print_with_time("Using userdefined broadcasters for drops")
        settings["use_user_defined_broadcasters"] = True
        return user_defined_broadcasters

    broadcaster_urls = get_broadcaster_urls()

    return [
        Broadcaster(url) for url in broadcaster_urls
    ]
