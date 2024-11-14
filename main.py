import pandas as pd
import plotly.graph_objects as go

from graph import GasGraph
from graph import Kruskal
import fiona 

import geopandas as gpd
fiona.drvsupport.supported_drivers['libkml'] = 'rw' 
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'

import zipfile
import os  # Importing os to check for file existence
print(gpd.io.file.fiona)
kmz_path ="gasoduto.kmz"
# Check if the KMZ file exists before trying to open it
if os.path.exists(kmz_path):
    with zipfile.ZipFile(kmz_path, 'r') as kmz:
        kmz.extract('doc.kml', path='.')
        kml_path = './doc.kml'
else:
    print(f"Error: The file {kmz_path} does not exist.")

gdf = gpd.read_file(kml_path, driver='LIBKML')
gdf.head()

##################

import plotly.graph_objects as go
import plotly.express as px

# Carregar seu GeoDataFrame (gdf)
# gdf = gpd.read_file('seu_arquivo.geojson')  # Exemplo de como carregar o GeoDataFrame

# Criar um layout com estilo OpenStreetMap
layout = go.Layout(
    mapbox_style="open-street-map",
    mapbox_zoom=10,  # Zoom inicial
    mapbox_center={"lat": gdf.geometry.centroid.y.mean(), "lon": gdf.geometry.centroid.x.mean()}
)

# Lista para armazenar os dados das geometries (pontos, polígonos e linhas)
fig_data = []

# Loop pelas geometrias no GeoDataFrame
for _, row in gdf.iterrows():
    geom_type = row.geometry.geom_type
    name = row['Name']
    
    if geom_type == 'Point':  # Adiciona pontos
        fig_data.append(go.Scattermapbox(
            lat=[row.geometry.y],
            lon=[row.geometry.x],
            mode='markers',
            marker=go.scattermapbox.Marker(size=8, color='red'),
            text=name,
            name=name
        ))
    
    elif geom_type in ['Polygon', 'MultiPolygon']:  # Adiciona polígonos
        # Para polígonos, extrai as coordenadas de cada anel (exterior + interiores)
        coords = []
        for ring in row.geometry.geoms[0].coords:
            coords.append((ring[1], ring[0]))  # Convertendo de (lon, lat) para (lat, lon)
        
        fig_data.append(go.Scattermapbox(
            lat=[coord[0] for coord in coords],
            lon=[coord[1] for coord in coords],
            mode='lines',
            line=go.scattermapbox.Line(color='blue', width=2),
            fill='toself',
            name=name
        ))
    
    elif geom_type == 'MultiLineString' or geom_type == 'MultiLineString Z':  # Adiciona multilinhas
        for line in row.geometry.geoms:
            coords = [(point[1], point[0]) for point in line.coords]  # Ignora a coordenada Z
            fig_data.append(go.Scattermapbox(
                lat=[coord[0] for coord in coords],
                lon=[coord[1] for coord in coords],
                mode='lines',
                line=go.scattermapbox.Line(color='blue', width=2),
                name=name
            ))

# Criar a figura com os dados
fig = go.Figure(data=fig_data, layout=layout)

# Exibir o mapa
fig.show()


################





# # Cria um mapa centralizado (use coordenadas médias do seu conjunto de dados para a localização inicial)
# m = folium.Map(location=[-15.7801, -47.9292], zoom_start=4)  # Exemplo: centro do Brasil

# # Adiciona os pontos ou formas do GeoDataFrame ao mapa
# for _, row in gdf.iterrows():
#     geom_type = row.geometry.geom_type
#     if geom_type == 'Point':  # Adiciona pontos
#         folium.Marker([row.geometry.y, row.geometry.x], popup=row['Name']).add_to(m)
#     elif geom_type in ['Polygon', 'MultiPolygon']:  # Adiciona polígonos
#         folium.GeoJson(row.geometry, name=row['Name']).add_to(m)
#     elif geom_type == 'MultiLineString' or geom_type == 'MultiLineString Z':  # Adiciona multilinhas
#         # Extrai coordenadas para cada linha na MultiLineString
#         for line in row.geometry.geoms:
#             coords = [(point[1], point[0]) for point in line.coords]  # Ignora a coordenada Z para visualização
#             folium.PolyLine(coords, color="blue", weight=2.5, opacity=1).add_to(m)

# # Exibe o mapa (você pode salvar como HTML)
# m.save("mapa_kml.html")
# m


######### 
gas_points_raw = pd.read_excel(open("./atualizado.xlsx", "rb"), decimal=',')
gas_points = gas_points_raw.rename(str.lower,axis='columns')
gas_points = gas_points.rename(columns={"latitude": "lat", "longitude": "lon"})
print(gas_points.head())

gas_points['name'] = gas_points['name'].str.strip()
gas_points['id'] = gas_points['id'].str.strip()
gas_points.dropna()

print(gas_points.head())

mst = Kruskal(gas_points)

listaVizinhos = []
for u,v, w in mst:
    listaVizinhos.append([gas_points.iloc[u]['id'], gas_points.iloc[v]['id'], w])

vizinhos = pd.DataFrame(listaVizinhos, columns=['De', 'Para', 'Custo'])
    
grafo = GasGraph(cityGates=gas_points, vizinhos=vizinhos)


import plotly
import plotly.express as px

fig = px.scatter_map(gas_points, lat="lat", lon="lon", color="type", zoom=3, text="name", size=[2] * len(gas_points))
fig.update_layout(map_style="open-street-map", map_zoom=4, map_center_lat = -33,
    margin={"r":0,"t":0,"l":0,"b":0}, clickmode='event')

for i in range(len(grafo.Mvizinhos)):
    for j in range(i, len(grafo.Mvizinhos)):
        if grafo.Mvizinhos[i][j] >= 0:
            origem = grafo.cityGates.iloc[i]
            destino = grafo.cityGates.iloc[j]
            fig.add_trace(go.Scattermap(lon=[origem.lon, destino.lon], lat=[origem.lat, destino.lat], mode='lines', showlegend = False, line=dict(color='#ffffff')))



# # fig.update_traces(cluster=dict(enabled=True))
# lastSelected = {}
# app.layout = html.Div(
#                    [html.H3('Mapa Gas'), dcc.Graph(figure=fig, id='mapa'), html.Div(id='selected'), html.Div(id='click')]
#                  )
plotly.offline.plot(fig)
fig.show()
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


# if __name__ == '__main__':
#     app.run_server(debug=True)



