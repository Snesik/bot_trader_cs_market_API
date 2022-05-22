import enum
import json
import time
import re

import requests
from bs4 import BeautifulSoup
from typing import List
from steampy import guard
from steampy.exceptions import ConfirmationExpected
from steampy.login import InvalidCredentials


class Confirmation:
    def __init__(self, _id, data_confid, data_key):
        self.id = _id.split('conf')[1]
        self.data_confid = data_confid
        self.data_key = data_key
        self.trade_id = ''
        self.class_instanse_id = []


class Tag(enum.Enum):
    CONF = 'conf'
    DETAILS = 'details'
    ALLOW = 'allow'
    CANCEL = 'cancel'


class ConfirmationExecutor:
    CONF_URL = "https://steamcommunity.com/mobileconf"

    def __init__(self, identity_secret: str, my_steam_id: str, adnroid, requests_session) -> None:
        self._my_steam_id = my_steam_id
        self._identity_secret = identity_secret
        self._session = requests_session
        self._adnroid = adnroid
        # self._all_items = all_items
        # self._offerts = offerts

    def send_trade_allow_request(self):
        confirmations = self._get_confirmations()
        a = self._select_trade_offer_confirmation(confirmations)
        for i in confirmations:
            self._send_confirmation(i)
        return confirmations

    def _send_confirmation(self, confirmation: Confirmation) -> dict:
        tag = Tag.ALLOW
        try:
            params = self._create_confirmation_params(tag.value)
            params['op'] = tag.value,
            params['cid'] = confirmation.data_confid
            params['ck'] = confirmation.data_key
            headers = {'X-Requested-With': 'XMLHttpRequest'}
            return self._session.get(self.CONF_URL + '/ajaxop', params=params, headers=headers).json()
        except:
            pass

    def _get_confirmations(self) -> List[Confirmation]:
        confirmations = []
        confirmations_page = self._fetch_confirmations_page()
        soup = BeautifulSoup(confirmations_page.text, 'html.parser')
        if soup.select('#mobileconf_empty'):
            return confirmations
        for confirmation_div in soup.select('#mobileconf_list .mobileconf_list_entry'):
            _id = confirmation_div['id']  # 'conf11290066175'
            data_confid = confirmation_div['data-confid']  # '11290066175'
            data_key = confirmation_div['data-key']  # '90047898288540428'
            confirmations.append(Confirmation(_id, data_confid, data_key))
        return confirmations

    def _fetch_confirmations_page(self) -> requests.Response:
        tag = Tag.CONF.value
        params = self._create_confirmation_params(tag)
        headers = {'X-Requested-With': 'com.valvesoftware.android.steam.community'}
        response = self._session.get(self.CONF_URL + '/conf', params=params, headers=headers)
        if 'Steam Guard Mobile Authenticator is providing incorrect Steam Guard codes.' in response.text:
            raise InvalidCredentials('Invalid Steam Guard file')
        return response

    def _fetch_confirmation_details_page(self, confirmation: Confirmation) -> str:
        tag = 'details' + confirmation.id
        params = self._create_confirmation_params(tag)
        response = self._session.get(self.CONF_URL + '/details/' + confirmation.id, params=params)
        return response.json()['html']

    def _create_confirmation_params(self, tag_string: str) -> dict:
        timestamp = int(time.time())
        confirmation_key = guard.generate_confirmation_key(self._identity_secret, tag_string, timestamp)
        # android_id = self._adnroid
        android_id = guard.generate_device_id(self._my_steam_id)
        return {'p': android_id,
                'a': self._my_steam_id,
                'k': confirmation_key,
                't': timestamp,
                'm': 'android',
                'tag': tag_string}

    def _select_trade_offer_confirmation(self, confirmations: List[Confirmation]):
        for confirmation in confirmations:
            confirmation_details_page = self._fetch_confirmation_details_page(confirmation)
            confirmation_id = self._get_confirmation_trade_offer_id(confirmation_details_page, confirmation)
            if confirmation_id == 0:
                continue
            confirmation.trade_id = confirmation_id

        return 'a'

    @staticmethod
    def _get_confirmation_trade_offer_id(confirmation_details_page: str, confirmation) -> int | str:
        soup = BeautifulSoup(confirmation_details_page, 'html.parser')
        full_offer_id = soup.select('.tradeoffer')[0]['id']
        # name_trader = soup.select('.trade_no_items_warning')[0].text
        # name_trader = re.findall(r'Пользователь (.+?) не', name_trader)[0]
        if 'Вы не выбрали предметы из инвентаря' in soup.select('div.tradeoffer .trade_no_items_warning')[0].text:
            for i in soup.select('div.trade_item'):
                confirmation.class_instanse_id.append(
                    i['data-economy-item'].split('/')[2] + '_' +
                    i['data-economy-item'].split('/')[3])
        else:
            print(
                'ALARM!!! ' * 5, 'Обнаружен инициирование сделки не нами, сделка: ID',
                full_offer_id.split('_')[1], 'Когда ', time.strftime('%H:%M:%S'),
                'КТО: '
            )
            return 0
        return full_offer_id.split('_')[1]
