from utils import read_yaml, bild_href


class Inventory:
    def __init__(self):
        self.steam_id = read_yaml('config.yaml')['steam_id']


class Inv_item:
    def __init__(self, name: str, id, class_id, sell_bd, instanse_id):
        self.name = name
        self.id = [id]
        self.class_id = class_id
        self.sell_bd = sell_bd
        self.instanse_id = instanse_id
        self.href = bild_href(name)

    def __str__(self):
        return self.name
