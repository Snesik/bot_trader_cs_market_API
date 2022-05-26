from utils import read_yaml, bild_href


class Inventory:
    def __init__(self):
        self.steam_id = read_yaml('config.yaml')['steam_id']


class InvItem:
    """Класс предмета из инвентаря, добавляются все действия информация из:
        БД + Sell + Offerts + Количество в наличие
    """

    def __init__(self, name: str, id, class_id, sell_bd, instanse_id):
        self.name = name
        self.id = [str(id)]
        self.class_id = class_id
        self.sell_bd = sell_bd
        self.instanse_id = instanse_id
        self.href = bild_href(name)

    def __str__(self):
        return self.name


class Offert:
    """Передаем 1 экземляр из списка, полученого от API"""

    def __init__(self, data):
        self.id = [asset['assetid'] for asset in data['items']]
        self.partner = data['partner']
        self.message = data['tradeoffermessage']

    def __str__(self):
        return str(self.partner)
