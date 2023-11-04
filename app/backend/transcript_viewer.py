import pandas as pd
from pandas import DataFrame

from backend.ledger import Account


class TranscriptViewer:
    def __init__(self, accounts: list[Account]):
        self.account_data = self._read_account_data(accounts)
        
        self.account_names = self.account_data['Account Name'].unique().tolist()
        self.years = self.account_data['Year'].unique().tolist()
        self.months = self.account_data['Month'].unique().tolist()
        self.default_month = self._get_default_month()
        self.main_categories = self.account_data['main_category'].unique().tolist()
        self.subcategories = self.account_data['subcategory'].unique().tolist()


    def _read_account_data(self, accounts: list[Account]):
        return pd.concat([self._add_fields_to_account_data(account.data) for account in accounts]).reset_index(drop=True)

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
    
    def _get_default_month(self):
        latest_year = max(self.years)
        relevant_df = self.account_data[self.account_data['Year']==latest_year]
        return max(relevant_df['Month'].unique().tolist())
