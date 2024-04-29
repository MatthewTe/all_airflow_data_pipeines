from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from ag_grid import generate_ag_grid
import dash_ag_grid as dag

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.layout = html.Div([

    html.Div(id='placeholder_container'),

    dbc.Row(
        dcc.Loading(html.Div(
            dag.AgGrid(
                id='raw_data_tbl',
                dashGridOptions={
                    'pagination': True,
                    'rowSelection':'single'
                }
        ), id="raw_data_grid")),
        style={"padding-top": '1rem'}),

    dbc.Row([
        dbc.Col(html.Div(
            id='selected_article_content_parent', 
            style={'padding': '1rem'}
        )),

        dbc.Col(html.Div(id='classification_inputs_parent')),
    ]),

    dbc.Row([
        dbc.Col()
    ])

])

if __name__ == '__main__':
    app.run(debug=True)