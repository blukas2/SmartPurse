import os
import pandas as pd
import json

from globals.settings import DATA_ROOT_FOLDER

class App:
    def __init__(self):
        self.accounts = os.listdir(DATA_ROOT_FOLDER)



class Account:
    def __init__(self, folder_name: str):
        self.root_path = f"{DATA_ROOT_FOLDER}/{folder_name}"
        self.config_folder = f"{self.root_path}/Config"
        self.data_folder = f"{self.root_path}/Data"

    def load(self):
        self._load_configs()
        self._load_data()
        #print(self.data.shape[0])
        print(self.data)
        print(self.data['Amount'].min())
        print(self.data['Amount'].max())

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
                self.data = pd.merge(self.data, df, how='left', on=['Date', 'Transaction ID'])

    def _load_data_from_single_file(self, filename: str):
        df = pd.read_csv(f"{self.data_folder}/{filename}", sep=";", encoding="UTF-16 LE", on_bad_lines='warn')
        df = df[list(self.column_mapping.keys())]
        df = df.rename(columns=self.column_mapping)
        df['Date'] = pd.to_datetime(df['Date'], format="%d.%m.%Y").dt.date
        df['Amount'] = df['Amount'].str.replace('.','', regex=False)
        df['Amount'] = df['Amount'].str.replace(',','.', regex=False)
        df['Amount'] = df['Amount'].astype(float)
        return df
    
    def _assign_categories(self):
        pass


account = Account("xx")
account.load()



#print(os.listdir(DATA_ROOT_FOLDER))
