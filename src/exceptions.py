from utils import print_with_time

from constants import USER_DEFINED_STREAMS_FILENAME


class UserDefinedStreamsLoadException(Exception):
    def __init__(self, *args: object) -> None:
        print_with_time(f"Error reading {USER_DEFINED_STREAMS_FILENAME}")
        print_with_time("Probably due to all drops are claimed")
        print_with_time("If file is empty and you have more drops to claim, add streams to file")
        print_with_time("Check https://github.com/cocorocho/RustTwitchDrops for more info")
