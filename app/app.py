import pandas as pd
from dash import Dash, dash_table, html, dcc, callback, Input, Output

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
            dcc.Dropdown(["monthly", "accumulated monthly"], "monthly", id='calc_type'),
            html.Div(id='summary_tables')
        ])
    elif tab == 'tab-transcript':

        return html.Div([
            html.Div([
                html.H4("Account name: "),
                dcc.Dropdown(transcript_viewer.account_names, transcript_viewer.account_names[0], id='account_name',
                             style={"width": "10%"}),
                html.H4("Year: "),
                dcc.Dropdown([2023, 2022], 2022, id='transcript_year', style={"width": "10%"}),
                html.H4("Month: "),
                dcc.Dropdown([1,2,3,4,5], 4, id='transcript_month', style={"width": "10%"})
                ], style={"display":"flex"}
            ),
            html.Div(id='transcript_table')
        ])


@callback(
    Output(component_id='summary_tables', component_property='children'),
    Input(component_id='calc_type', component_property='value')       
)
def render_calculation_type(calculation_type: str) -> list:
    if calculation_type == "monthly":
        rendered_tables = _render_tables(data_organizer.accounts_data_cost_breakdown)
    elif calculation_type == "accumulated monthly":
        rendered_tables = _render_tables(data_organizer.accounts_data_cost_breakdown_acc)
    else:
        raise ValueError(f"Invalid calculation type {calculation_type}")
    return rendered_tables
            
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
    Input(component_id='transcript_month', component_property='value')
)
def render_transcript(account_name: str, year: int, month: int) -> list:
    df_to_render = transcript_viewer.account_data[account_name]
    df_to_render = df_to_render[df_to_render["Year"]==year]
    df_to_render = df_to_render[df_to_render["Month"]==month]
    
    display_columns = [{"name": i, "id": i} for i in df_to_render.columns]
    rendered_table = dash_table.DataTable(data=df_to_render.to_dict('records'),
                                                    columns=display_columns,
                                                    style_cell={'textAlign':'left'})
    return rendered_table


if __name__ == '__main__':
    app.run(debug=True)
