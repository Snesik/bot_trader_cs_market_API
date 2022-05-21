import urllib.parse
import yaml


def read_yaml(path: str):
    with open(path, 'r') as c:
        return yaml.safe_load(c)


def hash_in_name(href: str) -> str:
    return urllib.parse.unquote(href)


def bild_href(name: str) -> str:
    """создаем href"""
    name = urllib.parse.quote(name)
    ss = f'https://steamcommunity.com/market/listings/730/{name}'
    return ss
