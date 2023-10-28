import pandas as pd
from pandas import DataFrame

from backend.ledger import Account


class TranscriptViewer:
    def __init__(self, accounts: list[Account]):
        self.account_data = self._read_account_data(accounts)
        self.account_names = list(self.account_data.keys())

    def _read_account_data(self, accounts: list[Account]):
        return {account.account_name: self._add_fields_to_account_data(account.data)
                        for account in accounts}

    def _add_fields_to_account_data(self, account_data: DataFrame) -> DataFrame:
        account_data['Year'] = pd.DatetimeIndex(account_data['Date']).year
        account_data['Month'] = pd.DatetimeIndex(account_data['Date']).month
        account_data = self._rearrange_account_data_columns(account_data)
        return account_data

    def _rearrange_account_data_columns(self, account_data: DataFrame) -> DataFrame:
        first_columns = ['Account Name', 'Year', 'Month']
        new_column_order = first_columns
        for col in account_data.columns:
            if col not in first_columns:
                new_column_order.append(col)
        account_data = account_data[new_column_order]
        return account_data
