from dash import Dash, html, dcc, callback, Output, Input
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import pandas as pd
import sqlalchemy as sa 
import dash

from config import INPUT_DATASET

@dash.callback(
    Output("raw_data_tbl", "rowData"), 
    Output("raw_data_tbl", 'columnDefs'),
    Input("placeholder_container", "children")
)
def generate_ag_grid(_) -> dag.AgGrid:

    Raw_Data_Engine: sa.engine.Engine = sa.create_engine(
        f"sqlite:////{INPUT_DATASET}"
    )

    with Raw_Data_Engine.connect() as conn, conn.begin():

        conn.execute(sa.text(
            """ CREATE TABLE IF NOT EXISTS article_labels (
                id TEXT PRIMARY KEY,
                region TEXT,
                municipality TEXT,
                city TEXT,
                road TEXT,
                electorial_district TEXT
            )
            """
        ))

        df_raw_data = pd.read_sql_query(
            sa.text("SELECT * FROM articles"),
            con=conn
        )

        df_labeled_data = pd.read_sql_query(
            sa.text("SELECT * FROM article_labels"),
            con=conn
        )

        df = df_raw_data.join(df_labeled_data, lsuffix='_raw_data', rsuffix='_labeled')
        columnDefs = [
            {'field': 'id_raw_data', 'headerName': 'Id'},
            {'field': 'title', 'headerName': 'Title'},
            {'field': 'content', 'headerName': 'Text Content'},
            {'field':'published_date', 'headerName': 'Published Date'},
            {'field':'region', 'headerName': 'Region'},
            {'field':'municipality', 'headerName': 'Municipality'},
            {'field':'city', 'headerName': 'City'},
            {'field':'road', 'headerName': 'Road'},
            {'field':'electorial_district', 'headerName': 'Electorial District'},
        ]

    return df.to_dict('records'), columnDefs

@dash.callback(
    Output("selected_article_content_parent", "children"),
    Output("classification_inputs_parent", "children"),
    Input("raw_data_tbl", "selectedRows")
)
def edit_specific_cell(row_data: dict): 

    if row_data is None: 
        raise PreventUpdate
    

    title = row_data[0]['title']
    full_content = row_data[0]['content']
    created_date = row_data[0]['published_date']

    selected_region = None
    selected_municipality = None
    selected_city = None
    selected_road = None
    selected_electoral_district = None

    # Loading data for the dropdowns:
    region_options_df = pd.read_csv("../../data/regions_tt.csv")
    region_options_lst: list[str] = region_options_df[region_options_df['TYPE_1'] == 'Region']['NAME_1'].to_list()

    display_content = html.Div([
        dbc.Row(
            html.H1(title),
            style={'padding-bottom': '0.5rem'}
        ),

        dbc.Row([
            dbc.Col(html.P(created_date)),
        ]),

        dbc.Row(html.P(full_content))
    ])

    classification_input_component = html.Div([
        dbc.Row([
            html.H4("Region"),
            dcc.Dropdown(id='text_region_container', options=region_options_lst, value=selected_region)
        ], style={'padding-bottom': '1rem'}),
        dbc.Row([
            html.H4("Municipality"),
            dcc.Dropdown(id='text_municipality_container')
        ], style={'padding-bottom': '1rem'}),
        dbc.Row([
            html.H4("City"),
            dcc.Dropdown(id='text_city_container')
        ], style={'padding-bottom': '1rem'}),
        dbc.Row([
            html.H4("Road"),
            dcc.Dropdown(id='text_road_container')
        ], style={'padding-bottom': '1rem'}),
        dbc.Row([
            html.H4("Electorial District"),
            dcc.Dropdown(id='text_electoral_district_container')
        ], style={'padding-bottom': '1rem'})
    ], style={'padding-top': '1rem', 'padding-right': '2rem'})

    return display_content, classification_input_component


