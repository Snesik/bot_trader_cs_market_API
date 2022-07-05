import time
import requests
from utils import read_yaml


class ApiCs:
    """Обращениея по API"""
    v1 = 'https://market.csgo.com/api'
    v2 = 'https://market.csgo.com/api/v2'

    def __init__(self):
        self.config = read_yaml('config.yaml')
        self.cs_api = self.config['cs']
        self.steam_api = self.config['steam']

    """Запросы через api"""

    def my_inventory(self):
        """Предметы для продаже в моем инвенторе"""
        result = requests.get(f'{self.v2}/my-inventory/?key={self.cs_api}').json()
        if result['success']:
            return result['items']
        else:
            raise 'Не удалось получить инвентарь, через API CS'

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
        result = requests.get(f'{self.v2}/ping/?key={self.cs_api}').json()
        for key, value in result.items():
            if value or value == 'pong':
                pass
            else:
                raise print(f'{key} нет доступа: ответ {value}')
        return True

    def balance(self):
        """Баланс"""
        return requests.get(f'{self.v2}/get-money/?key={self.cs_api}').json()

    def remove_all_from_sale(self):
        """Снятие сразу всех предметов с продажи."""
        return requests.get(f'{self.v2}/remove-all-from-sale?key={self.cs_api}').json()

    def sell(self, id_item: str, price: float):
        """Выставить лот на продажу"""
        data = requests.get(f'{self.v2}/add-to-sale?key={self.cs_api}&id={id_item}&price={price}&cur=RUB').json()
        return data
        # if data['success']:
        #     cursor = self.connect_bd.cursor()
        #     cursor.execute('UPDATE market_cs SET id_item = %s, status = "sale" where id_market = %s',
        #                    [data['item_id'], id_item])
        #     self.connect_bd.commit()
        #     cursor.close()
        # else:
        #     print(f'{id_item} Failed')

    def all_order_item(self, classid: str, instanceid: str):
        """Все ордера на продажу"""
        return requests.get(f'{self.v1}/SellOffers/{classid}_{instanceid}/?key={self.cs_api}').json()

    def search_item_by_name(self, hash_name: str):
        """Поиск предмета по hash имени"""
        return requests.get(f'{self.v2}/search-item-by-hash-name?key={self.cs_api}&hash_name={hash_name}').json()

    def search_item_by_name_5(self, data):
        """Поиск предмета по hash имени макс. 5"""
        a = {}
        data1 = ''
        for i in data:
            data1 += f'&list_hash_name[]=' + i.name
            if data.index(i) % 5 == 0:
                a.update(requests.get(f'{self.v2}/search-list-items-by-hash-name-all?'
                                      f'key={self.cs_api}&extended=1{data1}').json()['data'])
                data1 = ''
                time.sleep(0.25)
        for i in data:
            if i.name in a:
                i.sell_orders = [float(item['price']) / 100 for item in a[i.name]]
            else:
                i.sell_orders = [float(i.avg_result * 0.4 + i.avg_result)]
        return data

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
        return requests.post(f'{self.v1}/MassInfo/0/0/0/1?key={self.cs_api}', data=items).json()

    def item_info(self, classid: str, instanceid: str):
        return requests.get(f'{self.v1}/ItemInfo/{classid}_{instanceid}/ru/?key={self.cs_api}').json()
