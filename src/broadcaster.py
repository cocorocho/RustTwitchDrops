import logging
from typing import List

import requests
from bs4 import BeautifulSoup


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
    def __init__(self, url: str) -> None:
        self.url = url

    @property
    def is_online(self) -> bool:
        response = session.get(self.url)
        return "isLiveBroadcast" in response.content.decode("utf-8")


def get_broadcasters() -> List[Broadcaster]:
    broadcaster_urls = get_broadcaster_urls()

    return [
        Broadcaster(url) for url in broadcaster_urls
    ]
