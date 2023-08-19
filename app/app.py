import pandas as pd
import numpy as np

from backend.ledger import Ledger, Account


class App:
    def __init__(self):
        pass        


class DataOrganizer:
    def __init__(self, input_data: pd.DataFrame):
        self.input_data = input_data

    def prepare_data(self, account_name="all"):
        df = self.input_data
        if account_name != "all":
            df = df[df['Account Name']==account_name]
        df = df.drop(['Account Name'], axis=1)
        df = df[df['subcategory']!='EXCLUDED']
        groupby_cols = [col for col in df.columns if col != 'Amount']
        df = df.groupby(groupby_cols).aggregate('sum').reset_index()
        pivot_table = self._pivot_dataframe(df)
        summary_table = self._generate_summary_table(pivot_table)
        return summary_table

    def _pivot_dataframe(self, df: pd.DataFrame):
        df['Month'] = df['Month'].astype(str)
        pivot_table = pd.pivot_table(df, values='Amount', index=['main_category', 'subcategory', 'budget_item'],
                           columns=['Month'], aggfunc=np.sum).replace(np.nan, 0, regex=True).reset_index()
        return pivot_table
    
    def _generate_summary_table(self, pivot_table: pd.DataFrame):
        self.orig_category_columns = ['main_category', 'subcategory', 'budget_item']
        main_category_lines = pivot_table
        main_category_lines['Category'] = main_category_lines['main_category']
        main_category_lines = self._aggregate_summary_components(main_category_lines)

        subcategory_lines = pivot_table
        subcategory_lines['Category'] = subcategory_lines['main_category'] + "/" + subcategory_lines['subcategory']
        subcategory_lines = self._aggregate_summary_components(subcategory_lines)

        budget_item_lines = pivot_table
        budget_item_lines['Category'] = budget_item_lines['main_category'] + "/" + budget_item_lines['subcategory'] + "/" + budget_item_lines['budget_item']
        budget_item_lines = self._aggregate_summary_components(budget_item_lines)

        summary_table = pd.concat([main_category_lines, subcategory_lines, budget_item_lines]).sort_values(by='Category')
        return summary_table
    

    def _aggregate_summary_components(self, df: pd.DataFrame):
        df = df.drop(self.orig_category_columns, axis=1)
        df = df.groupby(['Category']).aggregate('sum').reset_index()
        return df

        

    def _create_main_category_lines(self, df: pd.DataFrame):
        df['Category'] = df['main_category']
        df.groupby(['Category']).aggregate('sum').reset_index()
        return df
    
    def _create_main_category_lines(self, df: pd.DataFrame):
        df['Category'] = df['main_category']
        df.groupby(['Category']).aggregate('sum').reset_index()
        return df



ledger = Ledger()
ledger.collect_data()

data_organizer = DataOrganizer(ledger.aggregated_data)

table = data_organizer.prepare_data()
table_b = data_organizer.prepare_data(account_name='')
table_f = data_organizer.prepare_data(account_name='')

#print(table)


from dash import Dash, dash_table, html
import pandas as pd

app = Dash(__name__)

#app.layout = dash_table.DataTable(ledger.aggregated_data.to_dict('records'), [{"name": i, "id": i} for i in ledger.aggregated_data.columns])
#app.layout = dash_table.DataTable(table.to_dict('records'), [{"name": i, "id": i} for i in table.columns])

app.layout = html.Div([dash_table.DataTable(table.to_dict('records'), [{"name": i, "id": i} for i in table.columns]),
                       dash_table.DataTable(table_b.to_dict('records'), [{"name": i, "id": i} for i in table.columns]),
                       dash_table.DataTable(table_f.to_dict('records'), [{"name": i, "id": i} for i in table.columns])])

if __name__ == '__main__':
    app.run(debug=True)

