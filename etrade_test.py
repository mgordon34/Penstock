from brokers.etrade import EtradeInterface
import common.config as config

if __name__ == '__main__':
    etrade = EtradeInterface(config.etrade_token_file_name, config.etrade_base_url)
    etrade.get_accounts()
