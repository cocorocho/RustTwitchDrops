from bs4 import BeautifulSoup
from requests import Session


class Streamer(Session):
    def __init__(self, stream_url: str, streamer_name: str, drop_name: str):
        super().__init__()
        self.name = streamer_name.strip()
        self.drop_name = drop_name.strip()
        self.stream_url = stream_url.strip()
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.27"}

    @property
    def is_online(self) -> bool:
        """
        Check if streamer is currently online on twitch
        """
        response = self.get(self.stream_url)
        return "isLiveBroadcast" in response.content.decode("utf-8")


class Facepunch(Session):
    FACEPUNCH_TWITCH_URL = "https://twitch.facepunch.com"

    def __init__(self):
        super().__init__()
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.27"}

    def get_drop_data(self) -> list:
        """
        Fetch streamer urls from facepunch
        """
        page_data = self.get(self.FACEPUNCH_TWITCH_URL)
        soup = BeautifulSoup(page_data.content, "html.parser")
        drop_tiles = soup.find_all("a", class_="drop-tile")
        streams = []

        for tile in drop_tiles:
            stream_url = tile.get("href")
            try:
                streamer_name = tile.find("span", attrs={"class": "streamer-name"}).text
            except AttributeError:
                # If streamer name doesn't exist, drop is general drop.
                continue
            
            _drop_name = tile.find("span", attrs={"class": "drop-name"}).text
            
            if "LR" in _drop_name.upper():
                _drop_name = "LR"
            elif "JACKET" in _drop_name.upper():
                _drop_name = "JACKET"
            
            drop_name = f"{streamer_name} {_drop_name}"

            streams.append(
                Streamer(
                    stream_url,
                    streamer_name,
                    drop_name
                )
            )

        return streams
