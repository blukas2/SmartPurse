import os
import pandas as pd
import numpy as np
from pandas import DataFrame
import json

from globals.settings import DATA_ROOT_FOLDER

class App:
    def __init__(self):
        pass        

class Ledger:
    def __init__(self):
        self.account_names = os.listdir(DATA_ROOT_FOLDER)

    def collect_data(self):
        self._load_accounts()
        self._collect_all_data()
        self._aggregate_data()
    
    def _load_accounts(self):
        self.accounts = [Account(account_name) for account_name in self.account_names]
        for account in self.accounts:
            account.load()

    def _collect_all_data(self):
        dataframes = [account.data for account in self.accounts]
        self.content = pd.concat(dataframes)

    def _aggregate_data(self):
        self.aggregated_data = (self.content
                                .groupby([
                                    'Year', 'Month', 'Account Name', 'main_category', 'subcategory', 'budget_item'
                                ])['Amount'].aggregate('sum'))



class Account:
    def __init__(self, folder_name: str):
        self.account_name = folder_name
        self.root_path = f"{DATA_ROOT_FOLDER}/{folder_name}"
        self.config_folder = f"{self.root_path}/Config"
        self.data_folder = f"{self.root_path}/Data"

    def load(self):
        self._load_configs()
        self._load_data()
        self._assign_categories()        

    def _load_configs(self):
        with open(f"{self.config_folder}/column_mapping.json", encoding="utf-8") as file:
            self.column_mapping = json.load(file)
        with open(f"{self.config_folder}/categories.json") as file:
            self.categories = json.load(file)

    def _load_data(self):
        data_files = os.listdir(self.data_folder)
        counter = 0
        for filename in data_files:
            df = self._load_data_from_single_file(filename)
            if counter == 0:
                self.data = df
            else:
                self.data = self._merge_tables(self.data, df)
            counter += 1

    def _load_data_from_single_file(self, filename: str):
        df = pd.read_csv(f"{self.data_folder}/{filename}", sep=";", encoding="UTF-16 LE", on_bad_lines='warn')
        df = df[list(self.column_mapping.keys())]
        df = df.rename(columns=self.column_mapping)
        df = df.replace(np.nan, None, regex=True)        
        df['Date'] = pd.to_datetime(df['Date'], format="%d.%m.%Y").dt.date
        df['Year'] = pd.DatetimeIndex(df['Date']).year
        df['Month'] = pd.DatetimeIndex(df['Date']).month
        df['Amount'] = df['Amount'].str.replace('.','', regex=False)
        df['Amount'] = df['Amount'].str.replace(',','.', regex=False)
        df['Amount'] = df['Amount'].astype(float)
        df['Account Name'] = self.account_name
        return df
    
    def _merge_tables(self, left_table: DataFrame, right_table: DataFrame):
        key_columns = ['Date', 'Transaction ID']
        not_key_columns = [col for col in left_table.columns if col not in key_columns]
        merged_table = pd.merge(left_table, right_table, how='left', on=key_columns, suffixes=("_left", "_right"))
        for column in not_key_columns:
            merged_table[column] = merged_table[column + '_left'].combine_first(merged_table[column + '_right'])
            merged_table = merged_table.drop([column + '_left', column + '_right'], axis=1)
        return merged_table
    
    def _assign_categories(self):
        categorizer = Categorizer(self.categories)
        records = self.data.to_dict(orient='records')
        categorized_records = []
        for record in records:
            categorized_records.append(categorizer.categorize(record))
        self.data = pd.DataFrame.from_records(categorized_records)


class Categorizer:
    def __init__(self, categories: dict):
        self.categories = categories
    
    def categorize(self, record : dict):
        self.record = record
        record_identified = False
        self._select_main_category()
        for subcategory_name, subcategory_content  in self.valid_categories.items():
            if record_identified:
                break
            for lineitem_name, lineitem_content in subcategory_content.items():
                if record_identified:
                    break
                if not isinstance(lineitem_content, dict) or len(lineitem_content)>1:
                    raise ValueError(f"Invalid lineitem_content for item: '{lineitem_name}'")
                self._set_categories_for_single_record(subcategory_name, lineitem_name, lineitem_content)
        return self.record
    
    def _set_categories_for_single_record(self, subcategory_name: str, lineitem_name: str, lineitem_content: dict):
        record_identified = self._identify_record(lineitem_content)
        if record_identified:
            self.record['main_category'] = self.main_category
            self.record['subcategory'] = subcategory_name
            self.record['budget_item'] = lineitem_name
        else:
            self.record['main_category'] = self.main_category
            self.record['subcategory'] = "OTHER"
            self.record['budget_item'] = "Other"
    
    def _identify_record(self, lineitem_content: dict) -> bool:
        lineitem_content_key = list(lineitem_content.keys())[0]
        if lineitem_content_key in ['AND', 'OR']:
            record_identified = self._check_for_lineitem_with_complex_statement(lineitem_content, lineitem_content_key)
        else:
            record_identified = self._check_for_lineitem(field_name = lineitem_content_key,
                                                         allowed_values = lineitem_content[lineitem_content_key])
        return record_identified
    
    def _check_for_lineitem_with_complex_statement(self, lineitem_content: dict, lineitem_content_key: str) -> bool:
        field_value_statements = lineitem_content[lineitem_content_key]                    
        field_value_checks = [self._check_for_lineitem(field_name=key, allowed_values=value) for key, value in field_value_statements.items()]                    
        if lineitem_content_key == 'AND':
            record_identified = all(field_value_checks)
        else:
            record_identified = any(field_value_checks)
        return record_identified

    def _check_for_lineitem(self, field_name, allowed_values):
        if field_name not in self.record:
            record_identified = False
        else:            
            actual_value = self.record[field_name]
            if actual_value is None:
                record_identified = False
            else:
                record_identified = any([(allowed_value in actual_value) for allowed_value in allowed_values])
        return record_identified

    def _select_main_category(self):
        if self.record['Amount']>0:
            self._get_main_category('INCOME')
        else:
            self._get_main_category('EXPENDITURE')

    def _get_main_category(self, category_name: str):
        self.valid_categories = self.categories[category_name]
        self.main_category = category_name


ledger = Ledger()

ledger.collect_data()
print(ledger.aggregated_data)


#print(os.listdir(DATA_ROOT_FOLDER))
