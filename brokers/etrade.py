import webbrowser
import json
import logging
import requests
from rauth import OAuth1Service, OAuth1Session

import common.config as config

log = logging.getLogger(__name__)


def oauth():
    """Allows user authorization for the sample application with OAuth 1"""
    etrade = OAuth1Service(
        name="etrade",
        consumer_key=config.etrade_api_key,
        consumer_secret=config.etrade_api_secret,
        request_token_url="https://api.etrade.com/oauth/request_token",
        access_token_url="https://api.etrade.com/oauth/access_token",
        authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
        base_url="https://api.etrade.com")

    menu_items = {"1": "Sandbox Consumer Key",
                  "2": "Live Consumer Key",
                  "3": "Exit"}
    while True:
        print("")
        options = menu_items.keys()
        for entry in options:
            print(entry + ")\t" + menu_items[entry])
        selection = input("Please select Consumer Key Type: ")
        if selection == "1":
            base_url = config.etrade_sandbox_url
            break
        elif selection == "2":
            base_url = config.etrade_consumer_url
            break
        elif selection == "3":
            break
        else:
            print("Unknown Option Selected!")
    print("")

    # # Step 1: Get OAuth 1 request token and secret
    # request_token, request_token_secret = etrade.get_request_token(
    #     params={"oauth_callback": "oob", "format": "json"})

    # # Step 2: Go through the authentication flow. Login to E*TRADE.
    # # After you login, the page will provide a text code to enter.
    # authorize_url = etrade.authorize_url.format(etrade.consumer_key, request_token)
    # webbrowser.open(authorize_url)
    # print(f'Go to this url if on headless: {authorize_url}')
    # text_code = input("Please accept agreement and enter text code from browser: ")

    # # Step 3: Exchange the authorized request token for an authenticated OAuth 1 session
    # # response = etrade.get_access_token(
    # #     request_token,
    # #     request_token_secret,
    # #     params={"oauth_verifier": text_code}
    # # )
    # # print("Oauth: " + response[0])
    # # print("Oauth: " + response[1])
    # # print("Oauth: " + response[0].encode().decode('utf8'))

    # # session = etrade.get_auth_session(oauth_token, oauth_token_secret)
    # # print(session)
    # session = etrade.get_auth_session(request_token,
    #                               request_token_secret,
    #                               params={"oauth_verifier": text_code})
    # print(session.__dict__)

    info_to_serialize =  {
        'consumer_key': config.etrade_api_key,
        'consumer_secret': config.etrade_api_secret,
        'access_token': '', 
        'access_token_secret': ''
    }
    session = OAuth1Session(**info_to_serialize)

    main_menu(session, base_url)


def main_menu(session, base_url):
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
            print(get_accounts(session, base_url))
        elif selection == "3":
            log.debug('Quitting...')
            break
        else:
            print("Unknown Option Selected!")

def get_accounts(session, base_url):
    url = base_url + '/v1/accounts/list.json'
    response = session.get(url)
    if response is not None and response.status_code == 200:
        parsed = json.loads(response.text)
        log.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
        data = response.json()

    return response