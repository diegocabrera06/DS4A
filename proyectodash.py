"""
This app creates a simple sidebar layout using inline style arguments and the
dbc.Nav component.

dcc.Location is used to track the current location, and a callback uses the
current location to render the appropriate page content. The active prop of
each NavLink is set automatically according to the current pathname. To use
this feature you must install dash-bootstrap-components >= 0.11.0.

For more details on building multi-page Dash applications, check out the Dash
documentation: https://dash.plot.ly/urls
"""  
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from sklearn import datasets
from sklearn.cluster import KMeans
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import plotly.express as px

#Base de datos 1
db_travelers= pd.read_csv("1. Tablero cifras investigación viajeros.csv")

db_turistaNal=db_travelers[db_travelers["Tema"]=="Turistas Nacionales"]

db_turistaNal.isna().sum()

df_distEtariaTNal=db_turistaNal[db_turistaNal['Subtema']=="Distribucion Etaria"]
df_distEtariaTNal=df_distEtariaTNal.drop(['Tema', 'Subtema'], axis = 1)
df_distEtariaTNal.drop(df_distEtariaTNal[df_distEtariaTNal['Mes'] =='Total'].index, inplace=True)

figtravel = px.bar(df_distEtariaTNal,x='item',y='Viajeros', color='Mes',
             labels={
                     "item": "Edad",
                     "Viajeros": "Numero de turistas nacionales",
                     "Ano": "Ano"
                 })
figtravel.show()




#Base de datos 2
df_indicadores_turismo = pd.read_csv("2. Base de Indicadores de Turismo.csv")

def normalize_column_names(df):
    
    df2 = df.copy()
    original_names = list(df2.columns)
    normalized_names = [x.upper() for x in original_names]
    
    df2.columns = normalized_names
    
    return df2

df_indicadores_turismo = normalize_column_names(df_indicadores_turismo)

df_airbnb_homeway = df_indicadores_turismo[df_indicadores_turismo["TEMA"] == "Airbnb & Homeaway"]
df_airbnb_homeway = df_airbnb_homeway.drop(["TEMA","VARIABLE","CLASE","FUENTE"], axis=1)
df_airbnb_homeway['VALOR'] = df_airbnb_homeway['VALOR'].astype(float)

df_bigdata = df_indicadores_turismo[df_indicadores_turismo["TEMA"] == "Big Data"]
df_bigdata = df_bigdata[df_bigdata["VARIABLE"] == "Capacidad aerea"]
df_bigdata['VALOR'] = df_bigdata['VALOR'].astype(float)
df_bigdata = df_bigdata.drop(["TEMA","FUENTE"], axis=1)

fig = px.bar(df_bigdata, x="SUBTEMA", y="VALOR", color="SUBTEMA", facet_col="ANO")

external_stylesheets = [dbc.themes.CERULEAN]

workspace_user = os.getenv('JUPYTERHUB_USER')  # Get DS4A Workspace user name
request_path_prefix = None
if workspace_user:
    request_path_prefix = '/user/' + workspace_user + '/proxy/8050/'

app = dash.Dash(__name__,
                requests_pathname_prefix=request_path_prefix,
                external_stylesheets=external_stylesheets)

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Instituto Distrital de Turismo", className="display-4"),
        html.Hr(),
        html.P(
            "Sistema de información turística de Bogotá", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Turistas Nacionales", href="/", active="exact"),
                dbc.NavLink("Turistas Internacionales", href="/page-1", active="exact"),
                dbc.NavLink("Indicadores", href="/page-2", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])

def render_page_content(pathname):
    if pathname == "/":
        return html.Div(children = [
    html.H1(
    children = 'Número de viajeros por distribución etaria',
    style = {
      'textAlign': 'center',
    }
  ),
    dcc.Graph(
    id = 'graph-airbnb',
    figure = figtravel
  )
])
    elif pathname == "/page-1":
        return html.Div(children = [
    html.H1(
    children = 'Capacidad aérea por país (total asientos)',
    style = {
      'textAlign': 'center',
    }
  ),
    dcc.Graph(
    id = 'graph-airbnb',
    figure = fig
  )
])
    elif pathname == "/page-2":
        return html.Div([
    html.H1(
    children = 'Promedio mensual propiedades Airbnb & Homeaway',
    style = {
      'textAlign': 'center',
    }
  ),
    dcc.Graph(id = 'graph-with-slider'),
    dcc.RadioItems(
    id = 'year-radio',
    value = df_airbnb_homeway['ANO'].min(),
    options=[{
        'label': v,
        'value': v
    } for v in df_airbnb_homeway['ANO'].unique()],
    labelStyle={'display': 'inline-block', 'margin-right': '10px'}
  )
])

    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
)

@app.callback(Output('graph-with-slider', 'figure'),[Input('year-radio', 'value')])

def update_figure(selected_year):
    filtered_df = df_airbnb_homeway[df_airbnb_homeway['ANO'] == selected_year]

    fig2 = px.bar(filtered_df, x = "SUBTEMA", y = "VALOR")

    fig2.update_layout(transition_duration = 500)

    return fig2

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port="8050", debug=True)