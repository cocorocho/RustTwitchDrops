import os
import json
import string
import random
from sys import exit
from time import sleep

import undetected_chromedriver as uc
from selenium.common.exceptions import (
    WebDriverException, NoSuchElementException, ElementNotInteractableException,
    StaleElementReferenceException, TimeoutException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from checks import Checks
from utils import print_with_time
from broadcaster import get_broadcasters
from settings import settings

from constants import CLIENT_ID, USER_DEFINED_STREAMS_FILENAME
from exceptions import UserDefinedStreamsLoadException
from twitchlogin import TwitchLogin


class Twitch(Checks):
    ###################################
    #### RUST TWICH DROPS ROUND 23 ####
    ###################################
    TWITCH_URL = "https://twitch.tv"

    def __init__(self):
        super().__init__()
        try:
            self.cookies_file = "./cookies.pkl"
            self.device_id = "".join(
                random.choice(string.ascii_letters + string.digits) for _ in range(32)
            )
            agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            self.twitch_login = TwitchLogin(CLIENT_ID, self.device_id, None, agent)
            self.login()
            cookies = self.twitch_login.load_cookies(self.cookies_file)

            options = uc.ChromeOptions()
            options.add_argument('--log-level=3')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--lang=en')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            self.driver = uc.Chrome(driver_executable_path="./driver/chromedriver.exe", options=options, use_subprocess=True)
            self.driver.get('https://www.twitch.tv/robots.txt')

            for cookie in cookies:
                self.driver.add_cookie(cookie)

            self.driver.get('https://www.twitch.tv/settings/profile')
        except WebDriverException:
            print_with_time("Latest version of chrome needs to be installed")
            exit(1)
        
        self.currently_watching = None
        self.driver.get(self.TWITCH_URL)

        # Apply config
        self.apply_config()
        
        # Wait 30 secs for Weak Password warning by twitch
        # sleep(30)
        # self.check_weak_password_warning()

        # Get drop names, streamer names, stream urls etc.
        self.streams = get_broadcasters()

        # Check claimed drops
        self.claim_drops()

    def login(self):
        if not os.path.isfile(self.cookies_file):
            if self.twitch_login.login_flow():
                self.twitch_login.save_cookies(self.cookies_file)
            else:
                print("login failed, try again")
                raise Exception("login failed, try again")
        else:
            self.twitch_login.load_cookies(self.cookies_file)
            self.twitch_login.set_token(self.twitch_login.get_auth_token())

    def apply_config(self) -> None:
        """
        Apply config to driver
        """
        print_with_time("Applying config")
        
        for k, v in settings.items():
            script = f"""window.localStorage.setItem({json.dumps(k, separators=(',', ':'))}, '{json.dumps(v, separators=(',', ':'))}');"""
            self.driver.execute_script(script)

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
        print_with_time("Checking and claiming drops in inventory")

        self.go_to_inventory()
        sleep(10)
        try:
            claim_buttons = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//button[@class='ScCoreButton-sc-ocjdkq-0 ScCoreButtonPrimary-sc-ocjdkq-1 dNGoHt hdAxZi']")
                )
            )
            claim_attempts = 0
            while claim_attempts < 5:
                for element in claim_buttons:
                    try:
                        self.driver.execute_script("arguments[0].click();", element)

                        if self.currently_watching:
                            self.claim_drop_for_broadcaster(self.currently_watching)

                        sleep(5)
                        print_with_time("Claimed a drop!")
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
        self.driver.get(streamer.url)
        self.driver.switch_to.window(self.driver.current_window_handle)
        self.currently_watching = streamer

    def print_stats(self) -> None:
        """
        Print current channel and drop progress
        """
        if self.currently_watching:
            msg = f"Currently watching {str(self.currently_watching)}"

            if str(self.current_progress).isnumeric():
                msg += f"-> Drop Progress {self.current_progress}%"

            print_with_time(msg)
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

                elif not self.currently_watching.is_online:
                    self.currently_watching = None
            else:
                for stream in self.streams:
                    if stream.is_online:
                        self.go_to_channel(stream)
                        break
            
            self.current_progress = self.get_progress()

            if self.currently_watching and self.progress_stalling(self.current_progress):
                self.currently_watching = None

            self.print_stats()
            sleep(15)

        print_with_time("=" * 20)
        print_with_time("All drops are claimed!")
        print_with_time("=" * 20)
        self.driver.close()
        
    def claim_drop_for_broadcaster(self, broadcaster) -> None:
        if settings.get("use_user_defined_broadcasters", False):
            print_with_time(f"Updating drop data for {str(broadcaster)}")
            with open(USER_DEFINED_STREAMS_FILENAME) as f:
                try:
                    data = json.load(f)
                except json.decoder.JSONDecodeError:
                    raise UserDefinedStreamsLoadException()
                    
                broadcaster_data_index = self.find_streamer_data_index(data, broadcaster)
                self.update_broadcaster_drop_data(data, broadcaster_data_index, broadcaster)

                # Update file
                with open(USER_DEFINED_STREAMS_FILENAME, "w") as f:
                    json.dump(data, f)
                return
        
        for stream in self.streams:
            if stream is broadcaster:
                self.streams.remove(stream)
                break

    def find_streamer_data_index(self, data, broadcaster) -> int:
        for i, row in enumerate(data):
            url = row.get("url") if isinstance(row, dict) else row

            if url == broadcaster.url:
                return i

    def update_broadcaster_drop_data(self, data, index, broadcaster) -> None:
        broadcaster_data = data[index]

        if isinstance(broadcaster_data, dict):
            num_drops = broadcaster_data.get("num_drops", None)

            try:
                num_drops = int(num_drops)
                num_drops -= 1

                if num_drops == 0:
                    data.pop(index)
                    self.streams.remove(broadcaster)
                    return
                
                broadcaster_data["num_drops"] = num_drops
            except TypeError:
                data.pop(index)
                self.streams.remove(broadcaster)
            finally:
                return
        
        # Plain url
        self.streams.remove(broadcaster)
        data.pop(index)
