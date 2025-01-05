import re
import pandas as pd

from graph import GasGraph, Kruskal

# base_tratada = "./base_tratada_tgs.xlsx"
base_tratada = "./df_TGN.xlsx"
# base_tratada = "./atualizado.xlsx"  #df2_TGN

volumeProperty = 'demand22a24'
typeProperty = 'type'

df = pd.read_excel(open(base_tratada, "rb"), decimal=',')  # Leitura do arquivo
gas_points = (
    df.rename(str.lower, axis='columns')  # Renomear colunas para minúsculas
    .rename(columns={"latitude": "lat", "longitude": "lon"})  # Renomear colunas específicas
    .assign(  # Aplicar transformações nas colunas
        name=lambda df: df['name'].str.strip(),
        id=lambda df: df['id'].str.strip(),
        lat=lambda df: df['lat'].astype(float),
        lon=lambda df: df['lon'].astype(float),
        volumeProperty= lambda df: df[volumeProperty].astype(float)
    )
    .loc[:, ['id', 'name', 'lat', 'lon', typeProperty, volumeProperty]]  # Selecionar colunas
    .dropna()  # Remover linhas com valores ausentes
    .drop_duplicates(['id'])  # Remover duplicatas com base em 'id'
    .sort_values(by=['id'], ascending=True)  # Ordenar pelos 'id'
)

mst = Kruskal(gas_points)
listaVizinhos = []
for u,v, w in mst:
    listaVizinhos.append([gas_points.iloc[u]['id'], gas_points.iloc[v]['id'], w])


vizinhos = pd.DataFrame(listaVizinhos, columns=['De', 'Para', 'Custo'])

grafo = GasGraph(cityGates=gas_points, vizinhos=vizinhos)

# entradas = gas_points[(gas_points[volumeProperty] >= 0) & (gas_points[typeProperty] != 'exit')]
entradas = gas_points[(gas_points[typeProperty] == 'entry')]

caminhos = grafo.ObtemCaminhos(entradas['id'])

ids = entradas['id'].unique()

# Regex que pega o id no dentro do nome gerado no caminho <name>(<id>)
escaped_ids = [re.escape(str(id_)) for id_ in ids]
pattern = r'.*\((' + '|'.join(escaped_ids) + r')\)'

# Seleciona as colunas de entrada a serem removidas
cols_to_remove = caminhos.filter(regex=pattern).columns
# Remove as entradas dos caminhos
caminhos = caminhos.drop(columns=cols_to_remove)
caminhos.to_csv(
    path_or_buf="distancias_tgn.csv", index=False, decimal=",", encoding="Windows-1252"
)
