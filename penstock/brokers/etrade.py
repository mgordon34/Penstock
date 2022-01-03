from dicttoxml import dicttoxml
import json
import logging
import random
from rauth import OAuth1Service, OAuth1Session
import webbrowser

from requests.sessions import to_native_string

import common.config as config

log = logging.getLogger(__name__)

class EtradeInterface(object):
    def __init__(self, base_url, consumer_key, consumer_secret,
                 account_id, account_type, institution_type):
        self.base_url = base_url
        self.account_id = account_id
        self.account_type = account_type
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.institution_type = institution_type

    def get_session(self, token_file_name):
        try:
            with open(token_file_name) as token_file:
                token_data = json.load(token_file)
                self.session = OAuth1Session(
                    consumer_key=self.consumer_key,
                    consumer_secret=self.consumer_secret,
                    **token_data
                )
                if not self.list_accounts():
                    self.oauth(token_file_name)

        except FileNotFoundError:
            log.debug('No token file found, running oauth...')
            self.oauth(token_file_name)

    def oauth(self, token_file_name):
        etrade = OAuth1Service(
            name="etrade",
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            request_token_url="https://api.etrade.com/oauth/request_token",
            access_token_url="https://api.etrade.com/oauth/access_token",
            authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
            base_url="https://api.etrade.com")

        # Step 1: Get OAuth 1 request token and secret
        request_token, request_token_secret = etrade.get_request_token(
            params={"oauth_callback": "oob", "format": "json"})

        # Step 2: Go through the authentication flow. Login to E*TRADE.
        # After you login, the page will provide a text code to enter.
        authorize_url = etrade.authorize_url.format(etrade.consumer_key, request_token)
        webbrowser.open(authorize_url)
        print(f'Go to this url if on headless: {authorize_url}')
        text_code = input("Please accept agreement and enter text code from browser: ")

        # Step 3: Exchange the authorized request token for an authenticated OAuth 1 session
        response = etrade.get_access_token(
            request_token,
            request_token_secret,
            params={"oauth_verifier": text_code}
        )
        access_tokens = {
            'access_token': response[0],
            'access_token_secret': response[1]
        }

        with open(token_file_name, 'w') as token_file:
            json.dump(access_tokens, token_file)

        self.session = OAuth1Session(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            **access_tokens
        )

    def main_menu(self):
        menu_items = {"1": "Market Quotes",
                    "2": "Account List",
                    "3": "Exit"}

        while True:
            print("")
            options = menu_items.keys()
            for entry in options:
                print(entry + ")\t" + menu_items[entry])
            selection = input("Please select an option: ")
            if selection == "1":
                log.debug('Market')
            elif selection == "2":
                log.debug('Accounts')
                print(self.get_accounts())
            elif selection == "3":
                log.debug('Quitting...')
                break
            else:
                print("Unknown Option Selected!")

    def list_accounts(self):
        data = None

        url = self.base_url + '/v1/accounts/list.json'
        headers = {'consumerkey': self.consumer_key}
        response = self.session.get(url)
        if response is not None and response.status_code == 200:
            data = response.json()

        return data

    def get_account_balance(self):
        data = None

        url = self.base_url + f'/v1/accounts/{self.account_id}/balance.json'
        params = {
            'instType': self.institution_type,
            'realTimeNAV': 'true'
        }
        headers = {'consumerkey': self.consumer_key}
        response = self.session.get(url, header_auth=True, params=params, headers=headers)
        # response = self.session.get(url + f'?instType={self.institution_type}&realTimeNAV=true', header_auth=True)
        if response is not None and response.status_code == 200:
            data = response.json()['BalanceResponse']['Computed']
        return {
            'account_balance': data['RealTimeValues']['totalAccountValue'],
            'settled_cash': data['settledCashForInvestment']
        }

    def preview_order(
        self,
        symbol,
        order_type, # 'EQ'
        order_action, # 'BUY'
        quantity,
        all_or_none=False,
        price_type='MARKET',
        order_term='GOOD_FOR_DAY',
        market_session='REGULAR',
        stop_price='',
        limit_price='',
        stop_limit_price='',
        quantity_type='QUANTITY'
    ):
        data = None

        url = self.base_url + f'/v1/accounts/{self.account_id}/orders/preview.json'
        headers = {
            'consumerkey': self.consumer_key,
            'Content-Type': 'application/xml'
        }
        body = {
            'orderType': order_type,
            'clientOrderId': random.randint(1000000000,9999999999),
            'Order': {
                'allOrNone': 'false',
                'priceType': price_type,
                'orderTerm': order_term,
                'marketSession': market_session,
                'stopPrice': stop_price,
                'limitPrice': limit_price,
                'Instrument': {
                    'Product': {
                        'securityType': order_type,
                        'symbol': symbol
                    },
                    'orderAction': order_action,
                    'quantityType': quantity_type,
                    'quantity': quantity
                }
            }
        }
        body_xml = to_native_string(dicttoxml(body, custom_root='PreviewOrderRequest'))

        response = self.session.post(url, header_auth=True, headers=headers, data=body_xml)

        if response is not None and response.status_code == 200:
            data = response.json()
        else:
            print(f'problem found: {response.text}')

        return data

    def place_order(self, order_detail):
        return f'place order TBD'