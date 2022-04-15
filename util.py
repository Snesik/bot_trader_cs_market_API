import urllib.parse
import mysql.connector
import yaml


def read_yaml(path: str):
    with open(path, 'r') as c:
        return yaml.safe_load(c)


config = read_yaml('config.yaml')


# def create_connection(host: str, login: str, passwd: str, bd: str):
#     connection = None
#     try:
#         connection = mysql.connector.connect(
#             host=host,
#             user=login,
#             passwd=passwd,
#             database=bd
#         )
#     except Exception as e:
#         print(f"The error '{e}' occurred")
#     return connection


def hash_in_name(href: str):
    return urllib.parse.unquote(href)


def bild_href(name):
    """создаем href"""
    name = urllib.parse.quote(name)
    ss = f'https://steamcommunity.com/market/listings/730/{name}'
    return ss
