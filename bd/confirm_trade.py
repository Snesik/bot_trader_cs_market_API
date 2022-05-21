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
    def __init__(self, _id, data_confid, data_key, price):
        self.id = _id.split('conf')[1]
        self.data_confid = data_confid
        self.data_key = data_key
        self.data_price = price
        self.trade_id = ''

class Tag(enum.Enum):
    CONF = 'conf'
    DETAILS = 'details'
    ALLOW = 'allow'
    CANCEL = 'cancel'


class ConfirmationExecutor:
    CONF_URL = "https://steamcommunity.com/mobileconf"

    def __init__(self, identity_secret: str, my_steam_id: str, session: requests.Session, adnroid, assetid) -> None:
        self._my_steam_id = my_steam_id
        self._identity_secret = identity_secret
        self._session = session
        self._adnroid = adnroid
        self._assetid = assetid

    def send_trade_allow_request(self, trade_offer_id: str):
        confirmations = self._get_confirmations()
        a = self._select_trade_offer_confirmation(confirmations, trade_offer_id)
        for i in confirmations:
            self._send_confirmation(i)
        return confirmations
    def confirm_sell_listing(self) -> dict:
        confirmations = self._get_confirmations()
        confirmation = self._select_sell_listing_confirmation(confirmations)
        self._send_confirmation(confirmation)
        return confirmations[0].data_price
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
            _id = confirmation_div['id']
            data_confid = confirmation_div['data-confid']
            data_key = confirmation_div['data-key']
            try:
                price = re.findall(r'(.+?) pуб', soup.select('#mobileconf_list .mobileconf_list_entry')[0].text)[0]
            except:
                price = 0
            confirmations.append(Confirmation(_id, data_confid, data_key, price))
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
        #android_id = self._adnroid
        android_id = guard.generate_device_id(self._my_steam_id)
        return {'p': android_id,
                'a': self._my_steam_id,
                'k': confirmation_key,
                't': timestamp,
                'm': 'android',
                'tag': tag_string}

    def _select_trade_offer_confirmation(self, confirmations: List[Confirmation], trade_offer_id: str):
        for confirmation in confirmations:
            confirmation_details_page = self._fetch_confirmation_details_page(confirmation)
            confirmation_id = self._get_confirmation_trade_offer_id(confirmation_details_page)
            confirmation.trade_id = confirmation_id

        return 'a'
        #return confirmations
        #raise ConfirmationExpected

    def _select_sell_listing_confirmation(self, confirmations: List[Confirmation]) -> Confirmation:
        for confirmation in confirmations:
            confirmation_details_page = self._fetch_confirmation_details_page(confirmation)
            confirmation_id = self._get_confirmation_sell_listing_id(confirmation_details_page)
            if confirmation_id == self._assetid:
                return confirmation


        #raise ConfirmationExpected



    @staticmethod
    def _get_confirmation_trade_offer_id(confirmation_details_page: str) -> str:
        soup = BeautifulSoup(confirmation_details_page, 'html.parser')
        full_offer_id = soup.select('.tradeoffer')[0]['id']
        for i in soup.select('div.trade_item'):
            class_instan_id = i['data-economy-item'] #classinfo/730/3790926081/188530139
        return full_offer_id.split('_')[1]
