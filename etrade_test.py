from brokers.etrade import EtradeInterface
import common.config as config

if __name__ == '__main__':
    etrade = EtradeInterface(
        config.etrade_token_file_name,
        config.etrade_base_url,
        config.etrade_account_id,
        config.etrade_account_type,
        config.etrade_institution_type
    )
    print(etrade.list_accounts())
    print(etrade.get_account_balance())
