import logging

from penstock.brokers.etrade import EtradeInterface
import penstock.common.config as config

logging.getLogger('dicttoxml').setLevel(logging.CRITICAL)
# logging.getLogger('urllib3').setLevel(logging.CRITICAL)

if __name__ == '__main__':
    base_url = ''
    account_id = ''
    consumer_key = ''
    if config.etrade_env == 'live':
        base_url = config.etrade_consumer_url
        account_id = config.etrade_consumer_account_id
        consumer_key = config.etrade_consumer_key
        consumer_secret = config.etrade_consumer_secret
    else: 
        base_url = config.etrade_sandbox_url
        account_id = config.etrade_sandbox_account_id
        consumer_key = config.etrade_sandbox_key
        consumer_secret = config.etrade_sandbox_secret

    etrade = EtradeInterface(
        config.etrade_token_file_name,
        base_url,
        consumer_key,
        consumer_secret,
        account_id,
        config.etrade_account_type,
        config.etrade_institution_type
    )
    etrade.get_session(config.etrade_token_file_name)
    print(etrade.list_accounts())
    print(etrade.get_account_balance())
    print(etrade.preview_order(
        symbol='WKHS',
        order_type='EQ',
        order_action='BUY',
        quantity=1
    ))
