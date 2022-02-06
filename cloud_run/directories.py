import pathlib
import appdirs


APPNAME = "cloud_run"
APPAUTHOR = "alexpdp7"


def get_cache_dir():
    return _get_dir(appdirs.user_cache_dir)


def get_data_dir():
    return _get_dir(appdirs.user_data_dir)


def get_state_dir():
    return _get_dir(appdirs.user_state_dir)


def _get_dir(d):
    data_dir = pathlib.Path(d(APPNAME, APPAUTHOR))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir
