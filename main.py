from collections import Counter
from sqlalchemy.orm import Session
from bd.models import engine, engine_cs_bd, Items, Price, Status
from bd.confirm_trade import *
from market_cs.requsts_api import ApiCs
from inventory.models import InvItem, Offert
from utils import time_block, read_yaml

from steam.add_session import creation_session_bots


session = Session(bind=engine)
session_cs_bd = Session(bind=engine_cs_bd)
trader = ApiCs()
crede = read_yaml('config.yaml')['config']


def find_instance_id(asset_id):
    head = {'Referer': f"https://steamcommunity.com/profiles/76561198073787208/inventory"}
    all_intem = requests.get('https://steamcommunity.com/inventory/76561198073787208/730/2?l=russian&count=5000',
                             headers=head).json()
    return [item['instanceid'] for item in all_intem['assets']
            if item['assetid'] == asset_id and item['instanceid'] != 0][0]


def add_in_bd(inventory):
    lots_in_bd = [str(i[0]) for i in session.query(Items.id).all()]
    that_we_add_in_bd = [i for i in inventory if not i['id'] in lots_in_bd]
    for i in that_we_add_in_bd:
        if i['instanceid'] == '0':
            result = find_instance_id(i['id'])
            if result is None:
                i['instanceid'] = 0
            else:
                i['instanceid'] = result

        item = Items(id=i['id'],
                     name=i['market_hash_name'],
                     class_id=i['classid'],
                     instance_id=i['instanceid']
                     )
        price = Price(item_id=i['id'])
        if i['tradable'] != 0:
            status = Status(item_id=i['id'], status='hold')
        else:
            status = Status(item_id=i['id'])
        session.add_all([item, price, status])
        session.commit()
        print(i['market_hash_name'])


def we_sell():
    all_lot = []
    result = session.query(Items.class_id).where(Items.id == Status.item_id and Status.status == 'hold').all()
    result = [str(i) for i, in result]
    for class_id in result:
        if class_id not in all_lot:
            all_lot.append(class_id)
    all_lot = Counter(all_lot)
    # {str(only_assetid)[1:-1]}
    a = session.query(Items.id).filter(
        Items.class_id.in_(all_lot) and Items.id == Status.item_id and Status.status == 'b').all()
    all_trader_item = trader.all_sell()


# ПРЕДМЕТЫ ТОРГОВЛИ
def chech_my_price():
    all_price_item = trader.all_price()['items']
    result_bd = session.query(Items.name, Items.id, Items.class_id, Price.sell, Items.instance_id) \
        .where(Items.id == Price.item_id) \
        .all()
    all_inv_item = []
    for one_result in result_bd:
        if len(all_inv_item) == 0:
            all_inv_item.append(InvItem(*one_result))
            continue
        for item in all_inv_item:
            if item.name == one_result[0]:
                if item.id == one_result[1]:
                    break
                else:
                    item.id = item.id + [str(one_result[1])]
                    break
        else:
            all_inv_item.append(InvItem(*one_result))

    for price in all_price_item:
        for item in all_inv_item:
            if price['market_hash_name'] == item.name:
                item.price = float(price['price'])

    request_in_bd = tuple([item.href for item in all_inv_item])
    mysql = f'SELECT ss, avg_result, low_avg FROM cs WHERE ss in {request_in_bd}'
    r = session_cs_bd.execute(mysql)
    result = [row for row in r]
    for i in result:
        for item in all_inv_item:
            if item.href == i[0]:
                item.avg_result = i[1]
                item.low_avg = i[2]
                break
        else:
            print('Лота нету в наших лотах ', i[0])

    return all_inv_item


def add_in_offerts_item(offerts, items):
    for item in items:
        for offert in offerts:
            for asset in offert.id:
                if asset in item.id:
                    offert.config = {asset: str(item.class_id) + '_' + str(item.instanse_id)}



# def proverka_na_otkat():


# def check_price(time_block, items):
#     for item in items:
#         if item.price != item.sell_bd:
#             pass
#         else:


# TIMEBLOCK

ss = trader.ping_pong()
ddd = trader.test()
# trader.remove_all_from_sale()
trader.update_inv()
add_in_bd(trader.my_inventory())
#aa = trader.my_inventory()
# for i in aa:
#     sss = trader.sell(i['id'], 10000000)
#     print(sss)
#     time.sleep(0.25)

print()

# НАДО ДОБАВИТЬ ПРОВЕРКУ ЛОТОВ КОТОРЫЕ ЕСТЬ В НАЛИЧИИ НА класс и инстант из за инв. стим через запрос стима а не ксмаркета

#requests_session = creation_session_bots()['_kornelius_']
items = chech_my_price()
#
# offerts = [Offert(partner) for partner in trader.trade_request_all()['offers']]
# add_in_offerts_item(offerts, items)
fff = trader.search_item_by_name_5(items)

# ConfirmationExecutor(
#     crede['identity_secret'], crede['steam_login_sec'],
#     crede['android'], requests_session, offerts
# ).send_trade_allow_request()
print()
# for item in items:
#     if item.price > item.low_avg:
#         if item.price < item.min_price():





#min_price = Avg_result - (Avg_result*TimeBlock) (плавающее значение)

# Если Sell > Low_Avg True то
#
#         Если Sell < min_price True то                /(мы достигли minPrice)
#
#                 Если CB0 > 5 True то                    /(Нас давят стеком предметов)
#
#                          то продать Sell - 0.01, обновить дату      /(Продаём до победного (до тех пор пока Sell > Low_Avg не будет False))
#
#                 Если false остаёмся в стакане на 2 позиции /(Стек маленький, ждём пока он продаст вещи)
#
#          Если False то продать Sell - 0.01, обновить дату
#
#



# for item in items:
#     b.append(trader.search_item_by_name(item.name)['data'])
#     time.sleep(0.25)
#     b.append(trader.item_info(item.class_id, item.instanse_id))
#     time.sleep(0.25)
# dddd = trader.all_order_item(items[0].class_id, items[0].instanse_id)
# p = trader.all_sell()


# def look_in_cs_market():


# sss =  trader.remove_all_from_sale()
# b = trader.all_price()
# we_sell()
# chech_my_price()
# ww = trader.ping_pong()
# w = trader.test()


# www = trader.update_inv()
# time.sleep(0.5)
# #a = trader.history({"list": [dd]})
# b = trader.all_sell()
# add_in_bd(aa)

# print()
# sell0 = trader.sell('25222288942', 100)
# sell1 = trader.sell('25222330183', 100)
# response = trader.trade_request_all()
# print()
# #sa = trader.sell('25222287403', 10000)
# #ss = trader.all_order_item('1704597526', '188530170')
# #bb = trader.set_price(bbbbb, 11111)
#
#


# print()
#
# add_in_bb()
