from dash import Dash, html, dcc, callback, Output, Input
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import pandas as pd
import sqlalchemy as sa 
import dash
import geopandas as gpd
import plotly.express as px

import spacy
from spacy import displacy
from io import BytesIO
import base64

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
                road TEXT
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

    # Loading data for the dropdowns:
    trinidad_regions_gdf = gpd.GeoDataFrame.from_file("/Users/matthewteelucksingh/Repos/TT_info_classifier/data/tto_adm1/TTO_adm1.shp")

    fig = px.choropleth_mapbox(
        trinidad_regions_gdf, 
        geojson=trinidad_regions_gdf.geometry, 
        locations=trinidad_regions_gdf['ID_1'],
        mapbox_style='open-street-map',
        opacity=0.5,
        zoom=8.5,
        center={'lat': 10.60622, 'lon':  -61.27125},
        labels={'NAME_1': 'Name'}
    )

    nlp = spacy.load('en_core_web_lg')
    doc = nlp(full_content)
    ner_svg = displacy.render(doc, style="ent", jupyter=False, page=True)

    display_content = html.Div([
        dbc.Row(
            html.H1(title),
            style={'padding-bottom': '0.5rem'}
        ),

        dbc.Row([
            dbc.Col(html.P(created_date)),
        ]),

        dbc.Row(html.P(full_content)),

        dbc.Row([
            html.Div(
                children=[
                    html.H4("Selected Region: "),
                    html.H4(id='selected_region_text')
                ]
            ),
            dbc.Button("Save", id="association_save_btn", disabled=True)
        ], style={'padding-left': '1rem'})
    ])

    ner_detected_entities = html.Iframe(
        srcDoc=ner_svg,
        style={'width': '100%', 'height': '80vh', 'border': 'none'}
    )

    classification_input_component = html.Div([
        dcc.Graph(
            id="tt_regions_graph",
            figure=fig,
            style={'height': '800px'}
        )
    ], style={'padding-top': '1rem', 'padding-right': '2rem'})

    return display_content, ner_detected_entities

@dash.callback(
    Output("selected_region_text", "children"), 
    Input("tt_regions_graph", "clickData")
)
def handle_region_select(selected_polygon):

    if selected_polygon is None:
        raise PreventUpdate

    trinidad_regions_gdf = gpd.GeoDataFrame.from_file("/Users/matthewteelucksingh/Repos/TT_info_classifier/data/tto_adm1/TTO_adm1.shp")
    selected_region_id: int = selected_polygon['points'][0]['location']

    region_row = trinidad_regions_gdf[trinidad_regions_gdf['ID_1'] == selected_region_id]['NAME_1'].to_list()[0]

    return region_row

@dash.callback(
    Output("association_save_btn", "disabled"),
    Input("selected_region_text", "children")
)
def enable_save_btn(selected_region):
    if selected_region is None:
        return True
    else:
        return False