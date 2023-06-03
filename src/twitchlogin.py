import copy
import logging
import os
import pickle

import browser_cookie3

import requests

from constants import GQLOperations

logger = logging.getLogger(__name__)

class TwitchLogin(object):
    __slots__ = [
        "client_id",
        "device_id",
        "token",
        "login_check_result",
        "session",
        "session",
        "username",
        "password",
        "user_id",
        "email",
        "cookies",
        "shared_cookies"
    ]

    def __init__(self, client_id, device_id, username, user_agent, password=None):
        self.client_id = client_id
        self.device_id = device_id
        self.token = None
        self.login_check_result = False
        self.session = requests.session()
        self.session.headers.update(
            { "Client-ID": self.client_id, "X-Device-Id": self.device_id, "User-Agent": user_agent }
        )
        self.username = username
        self.password = password
        self.user_id = None
        self.email = None

        self.cookies = []
        self.shared_cookies = []

    def login_flow(self):
        logger.info("You'll have to login to Twitch!")

        self.set_token(self.login_flow_backup())
        return self.check_login()

    def set_token(self, new_token):
        self.token = new_token
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def send_login_request(self, json_data):
        #response = self.session.post("https://passport.twitch.tv/protected_login", json=json_data)
        response = self.session.post("https://passport.twitch.tv/login", json=json_data, headers={
                    'Accept': 'application/vnd.twitchtv.v3+json',
                    'Accept-Encoding': 'gzip',
                    'Accept-Language': 'en-US',
                    'Content-Type': 'application/json; charset=UTF-8',
                    'Host': 'passport.twitch.tv'
                },)
        return response.json()

    def login_flow_backup(self, password = None):
        """Backup OAuth login flow in case manual captcha solving is required"""
        print("Chrome Only!")
        print("Please login to twitch with Chrome (NOT INCOGNITO)")
        print("Make sure page is fully loaded after login!")
        input("Press Enter")
        
        logger.info("Loading cookies saved on your computer...")
        twitch_domain = ".twitch.tv"

        cookie_jar = browser_cookie3.chrome(domain_name=twitch_domain)

        cookies_dict = requests.utils.dict_from_cookiejar(cookie_jar)
        self.username = cookies_dict.get("login")
        self.shared_cookies = cookies_dict
        return cookies_dict.get("auth-token")        

    def check_login(self):
        if self.login_check_result:
            return self.login_check_result
        if self.token is None:
            return False

        self.login_check_result = self.__set_user_id()
        return self.login_check_result

    def save_cookies(self, cookies_file):
        # old way saves only 'auth-token' and 'persistent'
        self.cookies = []
        cookies_dict = self.shared_cookies

        for cookie_name, value in cookies_dict.items():
            self.cookies.append({"name": cookie_name, "value": value})
        
        pickle.dump(self.cookies, open(cookies_file, "wb")) 

    def get_cookie_value(self, key):
        for cookie in self.cookies:
            if cookie["name"] == key:
                if cookie["value"] is not None:
                    return cookie["value"]
        return None

    def load_cookies(self, cookies_file):
        if os.path.isfile(cookies_file):
            return pickle.load(open(cookies_file, "rb"))
        else:
            raise Exception("There must be a cookies file!")

    def get_user_id(self):
        persistent = self.get_cookie_value("persistent")
        user_id = (
            int(persistent.split("%")[0]) if persistent is not None else self.user_id
        )
        if user_id is None:
            if self.__set_user_id() is True:
                return self.user_id
        return user_id

    def __set_user_id(self):
        json_data = copy.deepcopy(GQLOperations.ReportMenuItem)
        json_data["variables"] = {"channelLogin": self.username}
        response = self.session.post(GQLOperations.url, json=json_data)

        if response.status_code == 200:
            json_response = response.json()
            if (
                "data" in json_response
                and "user" in json_response["data"]
                and json_response["data"]["user"]["id"] is not None
            ):
                self.user_id = json_response["data"]["user"]["id"]
                return True
        return False

    def get_auth_token(self):
        return self.get_cookie_value("auth-token")
