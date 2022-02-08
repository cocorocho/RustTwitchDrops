from selenium.common.exceptions import  NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep


from utils import print_with_time

class Checks:
    MAX_PROGRESS_REPEAT_COUNT = 5 # Number of times to wait if progress doesn't change
    WAIT_AFTER_NOPROGRESSBAR = 180 # Seconds

    def __init__(self):
        self.current_progress = 0
        self.progress_check_count = 0
        self.last_progress_value = 0
        super().__init__()

    @property
    def user_is_logged_in(self) -> bool:
        """
        Check if user is logged into twitch
        """
        cookies = self.driver.get_cookies()
        for cookie in cookies:
            if cookie.get("name", None) == "name":
                return True
        return False

    def check_claimed_drops(self) -> None:
        """
        Check claimed drops
        """
        self.go_to_inventory()
        root_element = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@data-test-selector='drops-list__wrapper']")
            )
        )
        root_element_html = root_element.text.lower()
        _to_remove = []

        for streamer in self.streams:
            if streamer.name.lower() in root_element_html:
                print_with_time(f"You have already claimed {streamer.name}'s drop")
                _to_remove.append(streamer)

            # CAPTAIN MYKO AND ELLA NAMES WERE WRITTEN RANDOMLY ON TWITCH
            # THIS IS NOT NEEDED IF STREAMER NAMES ARE WRITTEN CORRECTLY
            elif "captain myko" in root_element_html and streamer.name.lower() == "captainmyko":
                _to_remove.append(streamer)
                print_with_time(f"You have already claimed {streamer.name}'s drop")
            elif "ella" in root_element_html and streamer.name.lower() == "ella_playz":
                print_with_time(f"You have already claimed {streamer.name}'s drop")
                _to_remove.append(streamer)
            #############################################################
        
        for i in _to_remove:
            self.streams.remove(i)

    def get_progress(self) -> int:
        """
        Get current drop progress
        """
        if not self.sidebar_is_visible:
            self.toggle_sidebar()
        try:
            parent_element = self.driver.find_element("xpath", "//a[@href='/inventory'][@data-a-target='inventory-dropdown-link']")
            progress_element = parent_element.find_element("xpath", ".//div[@role='progressbar']")
            progress = int(progress_element.get_attribute("aria-valuenow"))
            return progress

        except (TimeoutException, NoSuchElementException):
            # This can occur due to drop progress bar not showing up immediately
            # Wait 5 minutes and reload the page
            print_with_time("Couldn't locate progress bar")
            sleep(self.WAIT_AFTER_NOPROGRESSBAR)
            self.driver.refresh()

        finally:
            self.progress_check_count += 1

    def progress_stalling(self, progress: int) -> bool:
        """
        Check if progress is stalling
        If progress remains same for MAX_PROGRESS_REPEAT_COUNT

        :param int progress: Current progress
        """
        if self.MAX_PROGRESS_REPEAT_COUNT == self.progress_check_count:
            print_with_time(f"Progress is stalling with {self.currently_watching}, changing stream.")
            return True
        elif progress == self.last_progress_value:
            self.last_progress_value += 1
            return False
        else:
            self.progress_check_count = 0
            self.last_progress_value = progress
            return False

    def check_weak_password_warning(self) -> None:
        """
        Check twitch's weak password warning.
        Remind Later will be chosen if warning is present
        """
        try:
            modal = self.driver.find_element("xpath", "//div[@data-a-target='account-checkup-weak-password-warning-modal']")
            button = modal.find_element("xpath", ".//button[@data-a-target='account-checkup-generic-modal-secondary-button']")
            button.click()
            print_with_time("Change password warning dismissed.")

        except (NoSuchElementException):
            pass
