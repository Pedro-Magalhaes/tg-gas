from dash import dcc, html, Dash, Output, Input, callback
import pandas as pd
import plotly.graph_objects as go

from graph import GasGraph


app = Dash(__name__)

import pandas as pd
import plotly.graph_objects as go

def teste(a,b,c):
    print(a)

gas_points_raw = pd.read_excel("./malha_TGN_reduzido.xlsx")
gas_points = gas_points_raw.rename(str.lower,axis='columns')
gas_points = gas_points.rename(columns={"id pe": "id", "denominacion pe": "nome", "zona tarifaria": "zona", "latitud": "lat", "longitud": "lon"})
gas_points['nome'] = gas_points['nome'].str.strip()

print(gas_points.head())
vizinhos = pd.read_excel('./lista_vizinhança_corrigida.xlsx')
vizinhos = vizinhos[['De', 'Para']]
vizinhos['De'] = vizinhos['De'].str.strip()
vizinhos['Para'] = vizinhos['Para'].str.strip()
grafo = GasGraph(cityGates=gas_points, vizinhos=vizinhos)


import plotly
import plotly.express as px

fig = px.scatter_map(gas_points, lat="lat", lon="lon", color="tipo", zoom=3, text="nome", size=[2] * len(gas_points))
fig.update_layout(map_style="open-street-map", map_zoom=4, map_center_lat = -33,
    margin={"r":0,"t":0,"l":0,"b":0}, clickmode='event')

for i in range(len(grafo.Mvizinhos)):
    for j in range(i, len(grafo.Mvizinhos)):
        if grafo.Mvizinhos[i][j] >= 0:
            origem = grafo.cityGates.iloc[i]
            destino = grafo.cityGates.iloc[j]
            fig.add_trace(go.Scattermap(lon=[origem.lon, destino.lon], lat=[origem.lat, destino.lat], mode='lines', showlegend = False, line=dict(color='#ffcb03')))



# fig.update_traces(cluster=dict(enabled=True))
lastSelected = {}
app.layout = html.Div(
                   [html.H3('Mapa Gas'), dcc.Graph(figure=fig, id='mapa'), html.Div(id='selected'), html.Div(id='click')]
                 )
plotly.offline.plot(fig)
# @callback( Output('mapa', 'figure'), Input('mapa', 'clickData'))
# def teste(input):
#     global lastSelected
#     global fig
#     print(type(lastSelected))
#     if input != None and lastSelected != None:
#         pointA = lastSelected.get('points')[0]
#         pointB = input.get('points')[0]
#         print(f'Line from {pointA.get('text')} to {pointB.get('text')}')        
#         fig.add_trace(go.Scattergeo(mode='lines', line=dict(width=6, color='red'), lat=[pointA.get('lat'), pointB.get('lat')], lon=[pointA.get('lon'), pointB.get('lon')], opacity=1))
#     lastSelected = input
#     return fig


if __name__ == '__main__':
    app.run_server(debug=True)



