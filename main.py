import requests
from util import hash_in_name, create_connection, config


class Config:
    def __init__(self, config):
        self.cs_api = config['cs']
        self.steam_api = config['steam']
        self.connect_bd = create_connection(**config['BD'])
        self.v1 = 'https://market.csgo.com/api'
        self.v2 = 'https://market.csgo.com/api/v2'


class RequestCS(Config):
    """Запросы через api"""

    def my_inventory(self):
        """Предметы для продаже в моем инвенторе"""
        return requests.get(f'{self.v2}/my-inventory/?key={self.cs_api}').json()

    def all_price(self):
        """Цены на все товары"""
        return requests.get(f'{self.v2}/prices/RUB.json').json()

    def all_sell(self):
        """Выставленные на продажу лоты"""
        return requests.get(f'{self.v2}/items?key={self.cs_api}').json()

    def update_inv(self):
        """Обновить информацию об инвенторе, рекомендация проводить после каждой передачи предмета"""
        return requests.get(f'{self.v2}/update-inventory/?key={self.cs_api}').json()

    def test(self):
        """Проверить возможность работы, все должны быть TRUE"""
        return requests.get(f'{self.v2}/test?key={self.cs_api}').json()

    def ping_pong(self):
        """Раз в 3 минуты отправить, что я на сайте"""
        return requests.get(f'{self.v2}/ping/?key={self.cs_api}').json()

    def balance(self):
        """Баланс"""
        return requests.get(f'{self.v2}/get-money/?key={self.cs_api}').json()

    def remove_all_from_sale(self):
        """Снятие сразу всех предметов с продажи."""
        return requests.get(f'{self.v2}/remove-all-from-sale?key={self.cs_api}').json()

    def sell(self, id_item: str, price: float):
        """Выставить лот на продажу"""
        data = requests.get(f'{self.v2}/add-to-sale?key={self.cs_api}&id={id_item}&price={price}&cur=RUB').json()
        if data['success']:
            cursor = self.connect_bd.cursor()
            cursor.execute('UPDATE market_cs SET id_item = %s, status = "sale" where id_market = %s',
                           [data['item_id'], id_item])
            self.connect_bd.commit()
            cursor.close()
        else:
            print(f'{id_item} Failed')

    def all_order_item(self, classid: str, instanceid: str):
        """Все ордера на продажу"""
        return requests.get(f'{self.v1}/SellOffers/{classid}_{instanceid}/?key={self.cs_api}').json()

    def search_item_by_name(self, hash_name):
        """Поиск предмета по hash имени"""
        return requests.get(f'{self.v2}/search-item-by-hash-name?key={self.cs_api}&hash_name={hash_name}').json()

    def search_item_by_name_50(self, hash_name):
        """Поиск предмета по hash имени"""
        # return requests.get(f'{self.v2}/search-item-by-hash-name?key={self.cs_api}&hash_name={hash_name}').json()

    def trade_request_all(self):
        """Все трейды что нужно потвердить приходит LIST( {'appid', 'contextid', 'assetid'(при попадения
         можно найти в инвентаре при нажатии правой кнопкной мыше), 'amount'}"""
        return requests.get(f'{self.v2}/trade-request-give-p2p-all?key={self.cs_api}').json()

    def set_price(self, item_id: str, price: float):
        """Изменить цену лота, ответ dict {'success': True}"""
        return requests.get(f'{self.v2}/set-price?key={self.cs_api}&item_id={item_id}&price={price}&cur=RUB').json()

    def history(self, items):
        """История продаж предметов, макс. 100 post
        Пример:
        a = trader.history({"list": [dd]})"""
        return requests.post(f'{self.v1}/MassInfo/0/0/1/1?key={self.cs_api}', data=items).json()


trader = RequestCS(config)


def bd():
    with trader.connect_bd.cursor() as cn:
        cn.execute('SELECT hash_name from market_cs') #where status = "trade"')
        bd = [hash_in_name(i[0]) for i in cn.fetchall()]
        market = trader.all_price()
        price_lot_we_have = [i for i in market['items'] if i['market_hash_name'] in bd]
        a = trader.my_inventory()

    return price_lot_we_have
bd()
# https://market.csgo.com/api/v2/search-item-by-hash-name?key=[your_secret_key]&hash_name=[market_hash_name]


# my_inventory = requests.get(f'https://market.csgo.com/api/v2/my-inventory/?key={Config.cs_api}').json()
"Все что не продаже"
# all_sell = requests.get(f'https://market.csgo.com/api/v2/items?key={Config.cs_api}').json()
"Обновить информацию об инвенторе, рекомендация проводить после каждой передачи предмета"
# update_inventory = requests.get(f'https://market.csgo.com/api/v2/update-inventory/?key={Config.cs_api}').json()
"Проверить возможность работы все должны быть TRUE"
# test = requests.get(f'https://market.csgo.com/api/v2/test?key={Config.cs_api}').json()
"Раз в 3 минуты отправить, что я на сайте"
# ping_pong = requests.get(f'https://market.csgo.com/api/PingPong/?key={Config.cs_api}').json()
"Выставить на продажу"
# https://market.csgo.com/api/v2/add-to-sale?key=[your_secret_key]&id=[id]&price=[price]&cur=[currency]
"Изменить цену лота"
# https://market.csgo.com/api/v2/set-price?key=[your_secret_key]&item_id=[item_id]&price=[price]&cur=[currency]
# a = Request_cs.my_inventory
"ttps://market.csgo.com/api/MassInfo/[SELL]/[BUY]/[HISTORY]/[INFO]?key=[your_secret_key]"
"list — classid_instanceid,classid_instanceid,classid_instanceid"

# a = trader.my_inventory()
# bd = create_connection(**config['BD'])
# print(trader.ping_pong())
# with trader.connect_bd.cursor() as bd:
#     bd.execute('SELECT * from market_cs')
#     bbb = bd.fetchall()
#     print()
# dd = ['4141781426_188530170']
a = trader.all_price()
# поиск из инвентаря
# [i for i in a['items'] if i['market_hash_name'] == 'StatTrak™ Glock-18 | Moonrise (Well-Worn)']
# ww = trader.ping_pong()
# w = trader.test()
# a = trader.history({"list": [dd]})
# b = trader.trade_request_all()
# a = trader.sell('25222328757', 100)
# www = trader.trade_request_all()
# bbbbb = ''
# sa = trader.sell('25222287403', 10000)
# ss = trader.all_order_item('1704597526', '188530170')
#
# bb = trader.set_price(bbbbb, 11111)
print()
# trader.remove_all_from_sale()
'Sawed-Off | Forest DDPAT (Factory New)'
# b = trader.all_sell()
# print()
# with bd as bdd:
#     print()
# bdd = bd.cursor()
# bdd.execute('SELECT id_market from market_cs')
# we_have = [i[0] for i in bdd.fetchall()]


# add_news = [i for i in a['items'] if i['id'] in we_have]
# for i in a['items']:
#     id_market = i['id']
#     hash_name = bild_hash_name(i['market_hash_name'])
#     class_id = i['classid']
#     instance_id = i['instanceid']
#
#
#     bdd.execute('INSERT INTO market_cs(id_market, hash_name, class_id, instance_id, ) VALUES(%s, %s, %s, %s)',
#                       [id_market, hash_name, class_id, instance_id])
#
#
#
#     print(i['market_hash_name'])
# bd.commit()
#
# bdd.close()
# bd.close()
# # print()
