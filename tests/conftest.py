import copy
from pathlib import Path
import pytest

LOREM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do "
    "eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut "
    "enim ad minim veniam, quis nostrud exercitation ullamco laboris "
    "nisi ut aliquip ex ea commodo consequat."
)
__ISSUE_DICT = {
    "page": {
        "size": "demitab",
        "bg": None
    },
    "header": {
        "title": "Muckraker",
        "subtitle": "A vintage gazette generator for creative projects",
        "no": "№ 22",
        "date": "April 1, 2024",
        "cost": "Price 1 c.p.",
        "title_font": 10
    },
    "body": LOREM
}


@pytest.fixture
def issue_dict():
    return copy.deepcopy(__ISSUE_DICT)


@pytest.fixture
def good_image():
    path = Path(__file__).parent / "media" / "rufino-train.png"
    return open(path.resolve(), "rb")


@pytest.fixture
def thick_image():
    path = Path(__file__).parent / "media" / "nasa-hubble.jpg"
    return open(path.resolve(), "rb")
