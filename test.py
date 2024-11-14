import pandas as pd
import plotly.graph_objects as go

def teste(a,b,c):
    print(a)

gas_points_raw = pd.read_excel("./malha_TGN_reduzido.xlsx")
gas_points = gas_points_raw.rename(str.lower,axis='columns')
gas_points = gas_points.rename(columns={"id pe": "id", "denominacion pe": "nome", "zona tarifaria": "zona"})
print(gas_points.head())
# us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")
# us_cities = us_cities.query("State in ['New York', 'Ohio']")
# print(us_cities)
# gas_points = gas_points.query("id in ['N8020']")


import plotly
import plotly.express as px
# print(help(px.scatter_map))
# fig = go.FigureWidget([px.scatter_map(gas_points, lat="latitud", lon="longitud", color="tipo", zoom=3, text="nome", size=[2] * len(gas_points))])
fig = px.scatter_map(gas_points, lat="latitud", lon="longitud", color="tipo", zoom=3, text="nome", size=[2] * len(gas_points))
fig.update_layout(map_style="open-street-map", map_zoom=4, map_center_lat = -33,
    margin={"r":0,"t":0,"l":0,"b":0})

fig.update_traces(cluster=dict(enabled=True))
# plotly.offline.plot(fig, filename='gas.html')
fig.show()