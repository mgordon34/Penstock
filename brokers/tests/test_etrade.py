from brokers.etrade import EtradeInterface
import common.config as config

def dict_contains(superset, subset): 
    for item in subset:
        print(item)
        if type(subset[item]) == list:
            if not dict_contains(superset[item][0], subset[item][0]):
                return False
        elif type(subset[item]) == dict:
            if not dict_contains(superset[item], subset[item]):
                return False
        else:
            if item not in superset or subset[item] != superset[item]:
                print(f'mismatch for {item}: expected: {subset[item]}, actual: {superset[item]}')
                return False
    return True

class TestEtrade:
    etrade = None

    @classmethod
    def setup_class(cls):
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

        TestEtrade.etrade = EtradeInterface(
            config.etrade_token_file_name,
            base_url,
            consumer_key,
            consumer_secret,
            account_id,
            config.etrade_account_type,
            config.etrade_institution_type
        )

    def test_preview(self):
        expected_preview = {
            'PreviewOrderResponse': {
                'orderType': 'EQ',
                'optionLevelCd': 2,
                'Order': [{
                    'orderTerm': 'GOOD_FOR_DAY',
                    'priceType': 'MARKET',
                    'Instrument': [{
                        'symbolDescription': 'WORKHORSE GROUP INC COM NEW',
                        'orderAction': 'BUY',
                        'quantityType': 'QUANTITY',
                        'quantity': 1,
                        'Product': {
                            'symbol': 'WKHS',
                            'securityType': 'EQ',
                        }
                    }]
                }]
            }
        }
        preview_response = self.etrade.preview_order(
            symbol='WKHS',
            order_type='EQ',
            order_action='BUY',
            quantity=1
        )
        assert(dict_contains(preview_response, expected_preview))