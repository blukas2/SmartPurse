# -*- coding: utf-8 -*-
"""
Created on Sat Oct  9 22:14:53 2021

@author: Balazs
"""

class dataReader():
    def __init__(self):
        self.data = None
        self.fileType = None
        
    def read_data(self, path, file_type='xls', header=1, sheet_name=0, sep=None):
        if file_type=='xls':
            self.data=pd.read_excel(path, header=header-1, sheet_name=sheet_name)
        if file_type=='csv':
            self.data = pd.read_csv(path, header=header-1, sep=sep)
        self.fileType = file_type
            
    def identify_columns(self, dictionary):
        self.data = self.data[[dictionary['Transaction type'],
                               dictionary['Transaction time'],
                               dictionary['Amount'],
                               dictionary['Counterparty account number'],
                               dictionary['Counterparty account name'],
                               dictionary['Description']]]
        
        inv_dictionary = {v: k for k, v in dictionary.items()}        
        self.data = self.data.rename(inv_dictionary, axis = 'columns')
        
    def convert_data_types(self, ths_separator = ' ', decimal_separator = ','):        
        self.data['Amount'] = self.data['Amount'].str.replace(ths_separator, '')
        self.data['Amount'] = self.data['Amount'].str.replace(decimal_separator, '.')
        self.data = self.data.astype({'Amount': 'float'})        
        self.data['Transaction time'] = pd.to_datetime(self.data['Transaction time'])
        
    def reshape_data(self, dictionary, 
                     ths_separator = ' ', decimal_separator = ',', date_format = '%Y.%m.%d. %H:%M:S'):
        self.identify_columns(dictionary)
        
        if self.fileType=='csv':
            self.convert_data_types(ths_separator=ths_separator, decimal_separator = decimal_separator)
        
########################
data_reader = dataReader()

data_reader.read_data(path ='E:\\Software Engineering\\SmartPurse\\testing things\\2021_input_b_csv2.csv',
                      file_type='csv', sep=';', header=14)


example_dictionary = {
    'Transaction type' : 'Forgalom típusa',
    'Transaction time' : 'Tranzakció időpontja',
    'Amount' : 'Összeg',
    'Counterparty account number' : 'Ellenoldali számlaszám',
    'Counterparty account name' : 'Ellenoldali név',
    'Description' : 'Közlemény'    
    }

data_reader.reshape_data(example_dictionary)

view_data = data_reader.data


class dataClassifier():
    def __init(self, data):
        self.data=data

                

