import requests
import os
import zipfile
from tqdm import tqdm


class ChromeDriverDownloader:
    CHROMEDRIVERURL = "https://chromedriver.storage.googleapis.com/index.html"
    DRIVER_FOLDER = "./driver"

    def __init__(self):
        try:
            os.mkdir(self.DRIVER_FOLDER)
        except FileExistsError:
            pass
    
    def get_latest_version(self) -> str:
        """
        Get latest stable version of chromedriver
        """
        URL = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
        response = requests.get(URL)
        return response.content.decode()

    def download_chromedriver(self, version: str) -> str:
        """
        Download chromedriver.zip

        :param str version: Version of chromedriver
        """
        DOWNLOAD_URL = f"https://chromedriver.storage.googleapis.com/{version}/chromedriver_win32.zip"
        FILE_NAME = f"./chromedriver_{version}.zip"
        print("Downloading Chromedriver")
        response = requests.get(DOWNLOAD_URL, stream=True)
        file_size = int(response.headers.get("Content-Length", 0))
        progress_bar = tqdm(total=file_size, unit="iB", unit_scale=True)
        with open(os.path.join(self.DRIVER_FOLDER, FILE_NAME), "wb") as file:
            for data in response.iter_content(1024):
                progress_bar.update(len(data))
                file.write(data)
        
        return os.path.join(self.DRIVER_FOLDER, FILE_NAME)

    def unzip_file(self, file_path: str, target_path: str=DRIVER_FOLDER, delete_after: bool=True) -> None:
        """
        Unzip chromedriver

        :param str file_path: File path of chromedriver.zip
        :param str target_path: Path to extract
        :param bool delete_after: Delete zip after extracting
        """
        with zipfile.ZipFile(file_path, "r") as zip:
            zip.extractall(target_path)
        
        if delete_after:
            os.remove(file_path)

    def download(self, force: bool=False) -> None:
        """
        Start downloading chromedriver

        :param bool force: If latest_version of chromedriver already
        """
        if not force and os.path.exists(os.path.join(self.DRIVER_FOLDER, "chromedriver.exe")):
            return
        latest_version = self.get_latest_version()
        zip_path = self.download_chromedriver(latest_version)
        self.unzip_file(zip_path)
        