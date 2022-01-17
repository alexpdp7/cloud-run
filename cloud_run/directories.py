import pathlib
import appdirs


APPNAME = "cloud_run"
APPAUTHOR = "alexpdp7"


def get_cache_dir():
    cache_dir = pathlib.Path(appdirs.user_cache_dir(APPNAME, APPAUTHOR))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_data_dir():
    data_dir = pathlib.Path(appdirs.user_data_dir(APPNAME, APPAUTHOR))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir
