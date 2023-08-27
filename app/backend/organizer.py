import pandas as pd
import numpy as np


class DataOrganizer:
    def __init__(self, input_data: pd.DataFrame):
        self.input_data = input_data

    def reorganize_data(self):
        self._reorganize_data_for_cost_breakdown()
        self._calculate_monthly_accumulated()

    def _reorganize_data_for_cost_breakdown(self):
        self.accounts_data_cost_breakdown = {"all": self._prepare_data(account_name="all")}
        account_names = self.input_data['Account Name'].unique().tolist()
        for account_name in account_names:
            self.accounts_data_cost_breakdown[account_name] = self._prepare_data(account_name=account_name)

    def _prepare_data(self, account_name="all"):
        df = self._prepare_data_for_pivot(account_name=account_name)
        pivot_table = self._pivot_dataframe(df)
        summary_table = self._compile_summary_table(pivot_table)
        return summary_table
    
    def _prepare_data_for_pivot(self, account_name = "all"):
        df = self.input_data
        if account_name != "all":
            df = df[df['Account Name']==account_name]
        df = df.drop(['Account Name'], axis=1)
        df = df[df['subcategory']!='EXCLUDED']
        groupby_cols = [col for col in df.columns if col != 'Amount']
        df = df.groupby(groupby_cols).aggregate('sum').reset_index()
        return df

    def _pivot_dataframe(self, df: pd.DataFrame):
        df['Month'] = df['Month'].astype(str)
        pivot_table = pd.pivot_table(df, values='Amount', index=['main_category', 'subcategory', 'budget_item'],
                           columns=['Month'], aggfunc=np.sum).replace(np.nan, 0, regex=True).reset_index()
        return pivot_table
    
    def _compile_summary_table(self, pivot_table: pd.DataFrame):        
        self.orig_category_columns = ['main_category', 'subcategory', 'budget_item']
        summary_income = self._generate_summary_table(pivot_table, main_category='INCOME')
        summary_expenditure = self._generate_summary_table(pivot_table, main_category='EXPENDITURE')
        balance_line = self._calculate_balance(pivot_table)
        summary_table = pd.concat([summary_income, summary_expenditure, balance_line])
        return summary_table

    def _generate_summary_table(self, pivot_table: pd.DataFrame, main_category: str):
        main_category_lines = pivot_table[pivot_table['main_category']==main_category].copy()
        main_category_lines['Category'] = main_category_lines['main_category']
        main_category_lines = self._aggregate_summary_components(main_category_lines)

        subcategory_and_budget_item_lines = self._generate_subcategory_and_budget_item_lines(pivot_table, main_category=main_category, others=False)
        subcategory_and_budget_item_lines_others = self._generate_subcategory_and_budget_item_lines(pivot_table, main_category=main_category, others=True)

        summary_table = pd.concat([main_category_lines, subcategory_and_budget_item_lines, subcategory_and_budget_item_lines_others])
        return summary_table
    
    def _generate_subcategory_and_budget_item_lines(self, pivot_table: pd.DataFrame, main_category: str, others: bool = False):
        if others:
            others_condition = (pivot_table['subcategory']=='OTHER')
        else:
            others_condition = (pivot_table['subcategory']!='OTHER')

        subcategory_lines = pivot_table[(pivot_table['main_category']==main_category) & others_condition].copy()
        subcategory_lines['Category'] = subcategory_lines['main_category'] + "/" + subcategory_lines['subcategory']
        subcategory_lines = self._aggregate_summary_components(subcategory_lines)

        budget_item_lines = pivot_table[(pivot_table['main_category']==main_category) & others_condition].copy()
        budget_item_lines['Category'] = budget_item_lines['main_category'] + "/" + budget_item_lines['subcategory'] + "/" + budget_item_lines['budget_item']
        budget_item_lines = self._aggregate_summary_components(budget_item_lines)

        subcategory_and_budget_item_lines = pd.concat([subcategory_lines, budget_item_lines]).sort_values(by='Category')
        return subcategory_and_budget_item_lines
    
    def _calculate_balance(self, pivot_table: pd.DataFrame):
        balance_line = pivot_table
        balance_line['Category'] = 'BALANCE'
        balance_line = self._aggregate_summary_components(balance_line)
        return balance_line

    def _aggregate_summary_components(self, df: pd.DataFrame):
        df = df.drop(self.orig_category_columns, axis=1)
        df = df.groupby(['Category']).aggregate('sum').reset_index()
        for column in df.columns:
            if column != 'Category':
                df[column] = df[column].round(decimals=2)
        return df

    def _create_main_category_lines(self, df: pd.DataFrame):
        df['Category'] = df['main_category']
        df.groupby(['Category']).aggregate('sum').reset_index()
        return df
    
    def _create_main_category_lines(self, df: pd.DataFrame):
        df['Category'] = df['main_category']
        df.groupby(['Category']).aggregate('sum').reset_index()
        return df
    
    def _calculate_monthly_accumulated(self):
        self.accounts_data_cost_breakdown_acc = {account_name: data.copy() for account_name, data in self.accounts_data_cost_breakdown.items()}
        for account_name, data in self.accounts_data_cost_breakdown_acc.items():
            self.accounts_data_cost_breakdown_acc[account_name] = self._calulate_accomulated_monthly_values_in_df(data)

    def _calulate_accomulated_monthly_values_in_df(self, df: pd.DataFrame):
        for column in df.columns:
            if column != 'Category':
                year, month, day = self._split_date_string_to_components(column)
                if month != '01':
                    previous_month = ('0' + str(int(month)-1))[-2:]
                    previous_column = f"{year}-{previous_month}-{day}"
                    df[column] = df[column] + df[previous_column]
        return df

    def _split_date_string_to_components(self, date: str):
        """:param date: date string in the format of '2020-02-01'"""
        year = date[0:4]
        month = date[5:7]
        day = date[8:10]
        return year, month, day