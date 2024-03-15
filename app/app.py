import copy
import pandas as pd
from pandas import DataFrame
from dash import Dash, dash_table, html, dcc, callback, Input, Output

from typing import Any

from backend.ledger import Ledger
from backend.organizer import DataOrganizer
from backend.transcript_viewer import TranscriptViewer


ledger = Ledger()
ledger.collect_data()
data_organizer = DataOrganizer(ledger.aggregated_data)
data_organizer.reorganize_data()
transcript_viewer = TranscriptViewer(ledger.accounts)


app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Tabs(id='tabs-example-1', value='tab-summary', children=[
        dcc.Tab(label='Summary', value='tab-summary'),
        dcc.Tab(label='Transcript', value='tab-transcript'),
    ]),
    html.Div(id='tabs-example-content-1')
])

@callback(
    Output('tabs-example-content-1', 'children'),
    Input('tabs-example-1', 'value')
)
def render_content(tab):
    if tab == 'tab-summary':
        return html.Div([
            html.Div([
                html.H4("Year: "),
                dcc.Dropdown(transcript_viewer.years, max(transcript_viewer.years), id='summary_year', style={"width": "10%"}),
                html.H4("Calculation type: "),
                dcc.Dropdown(["monthly", "accumulated monthly"], "monthly", id='calc_type')
            ], style={"display":"flex"}),
            #dcc.Dropdown(["monthly", "accumulated monthly"], "monthly", id='calc_type'),
            html.Div(id='summary_tables')
        ])
    elif tab == 'tab-transcript':

        return html.Div([
            html.Div([
                html.H4("Account name: "),
                dcc.Dropdown(transcript_viewer.account_names, transcript_viewer.account_names[0], id='account_name',
                             style={"width": "10%"}),
                html.H4("Year: "),
                dcc.Dropdown(transcript_viewer.years, max(transcript_viewer.years), id='transcript_year', style={"width": "10%"}),
                html.H4("Month: "),
                dcc.Dropdown(transcript_viewer.months, transcript_viewer.default_month, id='transcript_month', style={"width": "10%"}),
                html.H4("Main Category: "),
                dcc.Dropdown(transcript_viewer.main_categories, None, id='transcript_main_category', style={"width": "10%"}),
                html.H4("Subcategory: "),
                dcc.Dropdown(transcript_viewer.subcategories, None, id='transcript_subcategory', style={"width": "10%"})
                ], style={"display":"flex"}
            ),
            html.Div(id='transcript_table')
        ])


@callback(
    Output(component_id='summary_tables', component_property='children'),
    Input(component_id='summary_year', component_property='value'),
    Input(component_id='calc_type', component_property='value')       
)
def render_calculation_type(year: int, calculation_type: str) -> list:
    if calculation_type == "monthly":
        tables_to_render = _select_year(year, data_organizer.accounts_data_cost_breakdown)
        #rendered_tables = _render_tables(data_organizer.accounts_data_cost_breakdown)
    elif calculation_type == "accumulated monthly":
        tables_to_render = _select_year(year, data_organizer.accounts_data_cost_breakdown_acc)
        #rendered_tables = _render_tables(data_organizer.accounts_data_cost_breakdown_acc)
    else:
        raise ValueError(f"Invalid calculation type {calculation_type}")
    rendered_tables = _render_tables(tables_to_render)
    return rendered_tables

def _select_year(year: int, tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    copied_tables = copy.copy(tables)    
    for key, table in copied_tables.items():
        selected_cols = [col for col in list(table.columns) 
                         if str(year) == col[:4] or col == "Category"]
        copied_tables[key] = table[selected_cols]
    return copied_tables



def _render_tables(tables: dict[str, pd.DataFrame]) -> list:
    rendered_tables = []
    display_columns = [{"name": i, "id": i} for i in tables["all"].columns]
    for key, account_data in tables.items():
        if key == "all":
            rendered_tables.append(html.H3(children='Summary', style={'textAlign':'left'}))
        else:
            rendered_tables.append(html.H3(children=f'Account Name: {key}', style={'textAlign':'left'}))            
        rendered_tables.append(dash_table.DataTable(data=account_data.to_dict('records'),
                                                    columns=display_columns,
                                                    style_cell={'textAlign':'right'},
                                                    style_cell_conditional=[
                                                        {
                                                            'if': {'column_id': 'Category'},
                                                            'textAlign': 'left'
                                                        }
                                                        ]))
    return rendered_tables


@callback(
    Output(component_id='transcript_table', component_property='children'),
    Input(component_id='account_name', component_property='value'),
    Input(component_id='transcript_year', component_property='value'),
    Input(component_id='transcript_month', component_property='value'),
    Input(component_id='transcript_main_category', component_property='value'),
    Input(component_id='transcript_subcategory', component_property='value')
)
def render_transcript(account_name: str, year: int, month: int, main_category: str, subcategory: str) -> list:    
    df_to_render = transcript_viewer.account_data
    df_to_render = filter_transcript_df(df_to_render, "Account Name", account_name)
    df_to_render = filter_transcript_df(df_to_render, "Year", year)
    df_to_render = filter_transcript_df(df_to_render, "Month", month)
    df_to_render = filter_transcript_df(df_to_render, "main_category", main_category)
    df_to_render = filter_transcript_df(df_to_render, "subcategory", subcategory)

    display_columns = [{"name": i, "id": i} for i in df_to_render.columns]
    rendered_table = dash_table.DataTable(data=df_to_render.to_dict('records'),
                                                    columns=display_columns,
                                                    style_cell={'textAlign':'left'})
    return rendered_table

def filter_transcript_df(df: DataFrame, column_name: str, filter_value: Any) -> DataFrame:
    if filter_value is not None:
        df = df[df[column_name]==filter_value]
    return df


if __name__ == '__main__':
    app.run(debug=True)
