# -*- coding: utf-8 -*-
"""
Created on Sun Oct 17 09:55:36 2021

@author: Balazs
"""

d = {'category_id' : ['IR0000',
                      'II0000',
                      'ER0000',
                      'EI0000'],
     'category_name' : ['Regular Income',
                        'Irregular Income',
                        'Regular Expenditure',
                        'Irregular Expandiutre']}

transaction_categories = pd.DataFrame(data=d)


transaction_categories.to_csv(RESOURCES_FOLDER+"\\breadDataset.csv", index = False)

transaction_categories_read = pd.read_csv(RESOURCES_FOLDER+"\\breadDataset.csv")
