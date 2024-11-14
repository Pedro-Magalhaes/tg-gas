import pandas as pd

from graph import GasGraph, Kruskal


gas_points_raw = pd.read_excel(open("./atualizado.xlsx", "rb"), decimal=',')
gas_points = gas_points_raw.rename(str.lower,axis='columns')
gas_points = gas_points.rename(columns={"latitude": "lat", "longitude": "lon"})

gas_points['name'] = gas_points['name'].str.strip()
gas_points['id'] = gas_points['id'].str.strip()
gas_points.dropna()
gas_points = gas_points.sort_values(by=['id'], ascending=True)

gas_points = gas_points.drop_duplicates(['id'])


mst = Kruskal(gas_points)
# print(len(mst))
listaVizinhos = []
for u,v, w in mst:
    listaVizinhos.append([gas_points.iloc[u]['id'], gas_points.iloc[v]['id'], w])


vizinhos = pd.DataFrame(listaVizinhos, columns=['De', 'Para', 'Custo'])

grafo = GasGraph(cityGates=gas_points, vizinhos=vizinhos)

entradas = gas_points.loc[gas_points["type"] == "entry"]
caminhos = grafo.ObtemCaminhos(entradas['id'])
# caminhos = grafo.ObtemCaminhos(['I0001'])
# print(caminhos.iloc[0]['N1301'])
caminhos.to_csv(
    path_or_buf="distancias.csv", index=False, decimal=",", encoding="Windows-1252"
)

# print(grafo.dfs('I0001', 'N1301'))
# grafo.NeighbourHoodCsv('bli')