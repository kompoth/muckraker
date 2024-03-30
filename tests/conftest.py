import pytest

LOREM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do "
    "eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut "
    "enim ad minim veniam, quis nostrud exercitation ullamco laboris "
    "nisi ut aliquip ex ea commodo consequat."
)


@pytest.fixture
def issue():
    return {
        "config": {
            "size": "demitab",
            "bg": None,
            "heading": {
                "title": "Muckraker",
                "subtitle": "Test sample",
                "no": "№ 22",
                "date": "April 1,9999",
                "cost": "Price 1 c.p."
            }
        },
        "body": LOREM
    }
