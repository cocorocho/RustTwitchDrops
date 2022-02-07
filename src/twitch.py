from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException, \
    ElementNotInteractableException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from threading import Thread
from time import sleep
import json

from facepunch import Facepunch
from checks import Checks
from utils import print_with_time


class Twitch(Checks, Facepunch):
    TWITCH_URL = "https://twitch.tv"
    DROP_ROUND = 14
    STREAM_CONFIG = {
        "video-muted": {"default": True},
        "mature": True,
        "video-quality": {"default": "160p30"}
    }

    def __init__(self):
        super().__init__()
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--log-level=3")
            self.driver = webdriver.Chrome("./driver/chromedriver.exe", options=options)
        except WebDriverException:
            print_with_time("Latest version of chrome needs to be installed")
            exit(1)
        
        self.currently_watching = None
        self.driver.get(self.TWITCH_URL)
        
        # Wait for user to login
        self.wait_for_userlogin()

        # Wait a minute for Weak Password warning by twitch
        sleep(30)
        self.check_weak_password_warning()

        # Get drop names, streamer names, stream urls etc.
        self.streams = self.get_drop_data()

        # Check claimed drops
        self.check_claimed_drops()

        # Apply config
        self.apply_config()

    def apply_config(self) -> None:
        for k, v in self.STREAM_CONFIG.items():
            script = f"""window.localStorage.setItem({json.dumps(k, separators=(',', ':'))}, '{json.dumps(v, separators=(',', ':'))}');"""
            self.driver.execute_script(script)

    def wait_for_userlogin(self) -> None:
        """
        Wait for user to login to twitch
        """
        def loop():
            while not self.user_is_logged_in:
                print_with_time("Waiting for user to login")
                sleep(5)
            
        t = Thread(target=loop)
        t.start()
        t.join()

    def toggle_sidebar(self) -> None:
        """
        Toggle twitch user sidebar, this is needed for progress bar
        """
        element = self.driver.find_element("xpath", "//button[@data-a-target='user-menu-toggle']")
        element.click()

    @property
    def sidebar_is_visible(self) -> bool:
        """
        Check if sidebar is visible, sidebar needs to be active to check progress
        """
        try:
            self.driver.find_element("xpath", "//a[@href='/inventory']")
            return True
        except NoSuchElementException:
            return False

    def go_to_inventory(self) -> None:
        """
        Navigate to inventory
        """
        self.driver.get(f"{self.TWITCH_URL}/drops/inventory")

    def claim_drops(self) -> None:
        """
        Claim drops
        """
        self.go_to_inventory()
        sleep(60)
        try:
            claim_buttons = WebDriverWait(self.driver, 60).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//button[@data-test-selector='DropsCampaignInProgressRewardPresentation-claim-button']")
                )
            )
            claim_attempts = 0
            while claim_attempts < 5:
                for element in claim_buttons:
                    try:
                        element.click()
                        sleep(5)
                    except (ElementNotInteractableException, StaleElementReferenceException):
                        claim_attempts += 1

        except TimeoutException:
            print_with_time("Nothing to claim")
        finally:
            sleep(5)
            self.check_claimed_drops()

    def mute_stream(self) -> None:
        """
        Mutes the stream
        """
        try:
            element = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[@data-a-target='player-mute-unmute-button']")
                )
            )
            sleep(2)
            element.click()
        except (TimeoutException, NoSuchElementException):
            print_with_time("Mute button not found")

    def go_to_channel(self, streamer) -> None:
        """
        Navigate to channel

        :param Streamer streamer: Streamer object
        """
        self.driver.get(streamer.stream_url)
        self.currently_watching = streamer

    def print_stats(self) -> None:
        """
        Print current channel and drop progress
        """
        if self.currently_watching:
            print_with_time(f"Currently watching {self.currently_watching.name} -> Drop Progress {self.current_progress}%")
        else:
            print_with_time(f"Currently not watching anyone")

    def get_drops(self) -> None:
        """
        Start getting drops!
        """
        while self.streams:
            if self.currently_watching:            
                if self.current_progress == 100:
                    self.go_to_inventory()
                    self.claim_drops()
                    self.currently_watching = None

                if not self.currently_watching.is_online:
                    self.currently_watching = None
            else:
                for stream in self.streams:
                    if stream.is_online:
                        self.go_to_channel(stream)
                        break
            
            self.current_progress = self.get_progress()

            if self.progress_stalling(self.current_progress):
                self.streams.remove(self.currently_watching)
                self.currently_watching = None
            self.print_stats()
            sleep(30)
