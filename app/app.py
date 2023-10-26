import pandas as pd

from dash import Dash, dash_table, html, dcc, callback, Input, Output

from backend.ledger import Ledger
from backend.organizer import DataOrganizer


ledger = Ledger()
ledger.collect_data()
data_organizer = DataOrganizer(ledger.aggregated_data)
data_organizer.reorganize_data()



#def _display_data():
app = Dash(__name__)

app.layout = html.Div([
        dcc.Dropdown(["monthly", "accumulated monthly"], "monthly", id='calc_type'),
                      html.Div(id='show_tables')
        ])


@callback(
    Output(component_id='show_tables', component_property='children'),
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

if __name__ == '__main__':
    app.run(debug=True)
