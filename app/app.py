from dash import Dash, dash_table, html, dcc

from backend.ledger import Ledger, Account
from backend.organizer import DataOrganizer


class App:
    def __init__(self):
        pass

    def run(self):
        self.ledger = Ledger()
        self.ledger.collect_data()
        self.data_organizer = DataOrganizer(self.ledger.aggregated_data)
        self.data_organizer.reorganize_data()
        self._display_data()

    def _display_data(self):
        app = Dash(__name__)

        app_visual_content = [dcc.Dropdown(["monthly", "accumulated monthly"], "monthly", id='calc_type')]
        display_columns = [{"name": i, "id": i} for i in self.data_organizer.accounts_data_cost_breakdown["all"].columns]
        for key, account_data in self.data_organizer.accounts_data_cost_breakdown.items():
            if key == "all":
                app_visual_content.append(html.H3(children='Summary', style={'textAlign':'left'}))
            else:
                app_visual_content.append(html.H3(children=f'Account Name: {key}', style={'textAlign':'left'}))            
            #app_visual_content.append(dash_table.DataTable(account_data.to_dict('records'), display_columns))
            app_visual_content.append(dash_table.DataTable(data=account_data.to_dict('records'),
                                                           columns=display_columns,
                                                           style_cell={'textAlign':'right'},
                                                           style_cell_conditional=[
                                                               {
                                                                   'if': {'column_id': 'Category'},
                                                                   'textAlign': 'left'
                                                                   }
                                                            ]))

        app.layout = html.Div(app_visual_content)

        app.run(debug=True)


if __name__ == '__main__':
    app = App()
    app.run()
