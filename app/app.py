import copy
import pandas as pd
from pandas import DataFrame
from dash import Dash, dash_table, html, dcc, callback, Input, Output

from typing import Any

import plotly.graph_objects as go

from globals.logger import setup_logging, get_logger
from backend.ledger import Ledger
from backend.organizer import DataOrganizer
from backend.transcript_viewer import TranscriptViewer
from backend.chart_data_provider import ChartDataProvider

setup_logging()
logger = get_logger(__name__)

logger.info("Starting SmartPurse application")
ledger = Ledger()
ledger.collect_data()
data_organizer = DataOrganizer(ledger.aggregated_data)
data_organizer.reorganize_data()
transcript_viewer = TranscriptViewer(ledger.accounts)
chart_data_provider = ChartDataProvider(data_organizer)


app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Tabs(id='tabs-example-1', value='tab-summary', children=[
        dcc.Tab(label='Summary', value='tab-summary'),
        dcc.Tab(label='Charts', value='tab-charts'),
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
            dcc.Tabs(id='summary-sub-tabs', value='sub-tab-monthly', children=[
                dcc.Tab(label='Monthly', value='sub-tab-monthly'),
                dcc.Tab(label='Yearly', value='sub-tab-yearly'),
            ]),
            html.Div(id='summary-sub-tab-content')
        ])
    elif tab == 'tab-charts':
        return _render_charts_tab()
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
                dcc.Dropdown(transcript_viewer.subcategories, None, id='transcript_subcategory', style={"width": "10%"}),
                html.H4("Budget Item: "),
                dcc.Dropdown(transcript_viewer.budget_items, None, id='transcript_budget_item', style={"width": "10%"})
                ], style={"display":"flex"}
            ),
            html.Div(id='transcript_table')
        ])


@callback(
    Output('summary-sub-tab-content', 'children'),
    Input('summary-sub-tabs', 'value')
)
def render_summary_sub_tab(sub_tab):
    if sub_tab == 'sub-tab-monthly':
        return html.Div([
            html.Div([
                html.H4("Year: "),
                dcc.Dropdown(transcript_viewer.years, max(transcript_viewer.years), id='summary_year', style={"width": "10%"}),
                html.H4("Calculation type: "),
                dcc.Dropdown(["monthly", "accumulated monthly", "YTD%"], "monthly", id='calc_type')
            ], style={"display":"flex"}),
            html.Div(id='summary_tables')
        ])
    elif sub_tab == 'sub-tab-yearly':
        return html.Div([
            html.Div([
                html.H4("Calculation type: "),
                dcc.Dropdown(["Yearly", "YoY%", "% of total income"], "Yearly", id='yearly_calc_type')
            ], style={"display":"flex"}),
            html.Div(id='yearly_summary_tables')
        ])


@callback(
    Output(component_id='summary_tables', component_property='children'),
    Input(component_id='summary_year', component_property='value'),
    Input(component_id='calc_type', component_property='value')       
)
def render_calculation_type(year: int, calculation_type: str) -> list:
    if calculation_type == "monthly":
        tables_to_render = _select_year(year, data_organizer.accounts_data_cost_breakdown)
    elif calculation_type == "accumulated monthly":
        tables_to_render = _select_year(year, data_organizer.accounts_data_cost_breakdown_acc)
    elif calculation_type == "YTD%":
        tables_to_render = _select_year(year, data_organizer.accounts_data_cost_breakdown_ytd)
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


@callback(
    Output(component_id='yearly_summary_tables', component_property='children'),
    Input(component_id='yearly_calc_type', component_property='value')
)
def render_yearly_calculation_type(calculation_type: str) -> list:
    if calculation_type == "Yearly":
        tables_to_render = data_organizer.accounts_data_yearly_breakdown
    elif calculation_type == "YoY%":
        tables_to_render = data_organizer.accounts_data_yearly_breakdown_yoy
    elif calculation_type == "% of total income":
        tables_to_render = data_organizer.accounts_data_yearly_breakdown_pct_of_income
    else:
        raise ValueError(f"Invalid calculation type {calculation_type}")
    return _render_tables(tables_to_render)


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
    Input(component_id='transcript_subcategory', component_property='value'),
    Input(component_id='transcript_budget_item', component_property='value')
)
def render_transcript(account_name: str, year: int, month: int, main_category: str,
                      subcategory: str, budget_item: str) -> list:    
    df_to_render = transcript_viewer.account_data
    df_to_render = filter_transcript_df(df_to_render, "Account Name", account_name)
    df_to_render = filter_transcript_df(df_to_render, "Year", year)
    df_to_render = filter_transcript_df(df_to_render, "Month", month)
    df_to_render = filter_transcript_df(df_to_render, "main_category", main_category)
    df_to_render = filter_transcript_df(df_to_render, "subcategory", subcategory)
    df_to_render = filter_transcript_df(df_to_render, "budget_item", budget_item)

    display_columns = [{"name": i, "id": i} for i in df_to_render.columns]
    rendered_table = dash_table.DataTable(data=df_to_render.to_dict('records'),
                                                    columns=display_columns,
                                                    style_cell={'textAlign':'left'})
    return rendered_table

def filter_transcript_df(df: DataFrame, column_name: str, filter_value: Any) -> DataFrame:
    if filter_value is not None:
        df = df[df[column_name]==filter_value]
    return df


def _render_charts_tab():
    return html.Div([
        dcc.Tabs(id='charts-sub-tabs', value='charts-sub-tab-basic', children=[
            dcc.Tab(label='Basic', value='charts-sub-tab-basic'),
            dcc.Tab(label='Annual Trend', value='charts-sub-tab-annual-trend'),
        ]),
        html.Div(id='charts-sub-tab-content')
    ])


@callback(
    Output('charts-sub-tab-content', 'children'),
    Input('charts-sub-tabs', 'value')
)
def render_charts_sub_tab(sub_tab):
    if sub_tab == 'charts-sub-tab-basic':
        return _render_basic_charts_tab()
    elif sub_tab == 'charts-sub-tab-annual-trend':
        return _render_annual_trend_tab()


def _render_basic_charts_tab():
    return html.Div([
        html.Div([
            html.H4("Time Granularity: "),
            dcc.Dropdown(
                id='chart-time-granularity',
                options=["Monthly", "Yearly"],
                value="Monthly",
                style={"width": "15%"}
            ),
            html.H4("Calculation Type: "),
            dcc.Dropdown(
                id='chart-calc-type',
                options=["Nominal", "YoY%", "% of total income"],
                value="Nominal",
                style={"width": "15%"}
            ),
        ], style={"display": "flex"}),
        html.Div([
            html.H4("Categories: "),
            dcc.Dropdown(
                id='chart-categories',
                options=chart_data_provider.get_categories(),
                value=[],
                multi=True
            ),
        ]),
        dcc.Graph(id='chart-line-graph')
    ])


def _render_annual_trend_tab():
    available_years = chart_data_provider.get_available_years()
    return html.Div([
        html.Div([
            html.H4("Category: "),
            dcc.Dropdown(
                id='cumulative-chart-category',
                options=chart_data_provider.get_categories(),
                value=None,
                style={"width": "40%"}
            ),
            html.H4("Years: "),
            dcc.Dropdown(
                id='cumulative-chart-years',
                options=available_years,
                value=[max(available_years)] if available_years else [],
                multi=True,
                style={"width": "30%"}
            ),
        ], style={"display": "flex"}),
        dcc.Graph(id='cumulative-chart-graph')
    ])


@callback(
    Output('chart-line-graph', 'figure'),
    Input('chart-time-granularity', 'value'),
    Input('chart-calc-type', 'value'),
    Input('chart-categories', 'value')
)
def update_chart(granularity: str, calc_type: str, selected_categories: list[str]):
    figure = go.Figure()
    if not selected_categories:
        return figure
    df = chart_data_provider.get_chart_data(granularity, calc_type)
    filtered = df[df["Category"].isin(selected_categories)]
    date_columns = ChartDataProvider._get_date_columns(filtered)
    figure = _build_line_chart(filtered, date_columns, calc_type)
    return figure


def _build_line_chart(df: pd.DataFrame, date_columns: list[str], calc_type: str) -> go.Figure:
    figure = go.Figure()
    for _, row in df.iterrows():
        figure.add_trace(go.Scatter(
            x=date_columns,
            y=[row[col] for col in date_columns],
            mode='lines',
            name=row["Category"]
        ))
    y_label = _get_y_axis_label(calc_type)
    figure.update_layout(xaxis_title="Period", yaxis_title=y_label)
    return figure


def _get_y_axis_label(calc_type: str) -> str:
    labels = {
        "Nominal": "Amount",
        "YoY%": "Year-over-Year %",
        "% of total income": "% of Total Income"
    }
    return labels.get(calc_type, "Value")


@callback(
    Output('cumulative-chart-graph', 'figure'),
    Input('cumulative-chart-category', 'value'),
    Input('cumulative-chart-years', 'value')
)
def update_annual_trend_chart(category: str, years: list[int]):
    figure = go.Figure()
    if not category or not years:
        return figure
    cumulative_data = chart_data_provider.get_cumulative_data(category, years)
    return _build_annual_trend_chart(cumulative_data, category)


def _build_annual_trend_chart(cumulative_data: dict, category: str) -> go.Figure:
    figure = go.Figure()
    for year, values in cumulative_data.items():
        figure.add_trace(go.Scatter(
            x=_get_month_labels(len(values)),
            y=values,
            mode='lines+markers',
            name=str(year)
        ))
    figure.update_layout(xaxis_title="Month", yaxis_title="Amount", title=f"Annual Trend: {category}")
    return figure


def _get_month_labels(count: int) -> list[str]:
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return month_names[:count]


if __name__ == '__main__':
    app.run(debug=True)
