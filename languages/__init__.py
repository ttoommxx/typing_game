"""collection of languages with their translation rules"""

from languages import python


def format_config(path):
    if path.endswith(".py"):
        return {"tab_size": python.tab_size}
    else:
        return {"tab_size": 4}
