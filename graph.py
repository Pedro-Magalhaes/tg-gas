from math import acos, cos, radians, sin
from typing import List
import pandas as pd

import math

import plotly

# Classe para a estrutura Union-Find (ou Disjoint Set Union - DSU)
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Caminho comprimido
        return self.parent[x]

    def union(self, x, y):
        rootX = self.find(x)
        rootY = self.find(y)
        
        if rootX != rootY:
            # Union por rank (para manter a árvore balanceada)
            if self.rank[rootX] > self.rank[rootY]:
                self.parent[rootY] = rootX
            elif self.rank[rootX] < self.rank[rootY]:
                self.parent[rootX] = rootY
            else:
                self.parent[rootY] = rootX
                self.rank[rootX] += 1

## Distancia calculada com lei geral dos cossenos.
# Pode ter erros de aproximação para distâncias pequenas. Alternativa usar haversine
def CustoEntreNos(lat1, lat2, lng1, lng2):
    if lat1 == lat2 and lng1 == lng2:
        return 0
    lat1Rad = radians(lat1)
    lat2Rad = radians(lat2)
    lng1Rad = radians(lng1)
    lng2Rad = radians(lng2)

    rTerra = 6371

    return (
        acos(
            sin(lat1Rad) * sin(lat2Rad)
            + cos(lat1Rad) * cos(lat2Rad) * cos(lng2Rad - lng1Rad)
        )
        * rTerra
    )

# Função principal do algoritmo de Kruskal
def Kruskal(stations):
    n = len(stations)
    edges = []

    # Cria todas as arestas possíveis (distâncias entre todas as estações)
    for i in range(n):
        for j in range(i + 1, n):
            #origem.lat, destino.lat, origem.lon, destino.lon
            try:
                dist = CustoEntreNos(stations.iloc[i].lat, stations.iloc[j].lat, stations.iloc[i].lon, stations.iloc[j].lon)
            except:
                print('ERROO AO MEDIR DISTANCIA!!!!',stations.iloc[i], stations.iloc[j])
            
            edges.append((dist, i, j))
    
    # Ordena as arestas pela distância
    edges.sort()  # Ordena com base no primeiro elemento da tupla (distância)

    # Inicializa o Union-Find
    uf = UnionFind(n)
    mst = []  # A MST que será retornada

    # Processa as arestas
    for dist, u, v in edges:
        if uf.find(u) != uf.find(v):
            uf.union(u, v)
            mst.append((u, v, dist))

    return mst

class GasGraph(object):
    def __init__(self, vizinhos: pd.DataFrame, cityGates: pd.DataFrame):
        """Recebe a lista com todas as conexões  de vizinhança e os dados dos city gates"""
        self.cityGates = cityGates
        # A matriz de vizinho vai ter o custo entre cada nó. Se for -1 a conexão não existe
        self.Mvizinhos = [
            [-1] * len(self.cityGates) for x in range(len(self.cityGates))
        ]
        self.nameIndex = {k: v for v, k in enumerate(self.cityGates["id"].to_list())}
        for i, val in vizinhos.iterrows():
            indiceOrigem = self.nameIndex[val["De"]]
            indiceDestino = self.nameIndex[val["Para"]]
            origem = self.cityGates.iloc[indiceOrigem]
            destino = self.cityGates.iloc[indiceDestino]
            custo = CustoEntreNos(origem.lat, destino.lat, origem.lon, destino.lon)
            self.Mvizinhos[indiceOrigem][indiceDestino] = custo
            self.Mvizinhos[indiceDestino][indiceOrigem] = custo
        # for i2 in range(len(self.cityGates)):
        #     arestas = 0
        #     for j2 in range(i2,len(self.cityGates)):
        #         if self.Mvizinhos[j2][i2] != -1 or self.Mvizinhos[i2][j2] != -1:
        #             arestas += 1
        #     if arestas == 0:
        #         print(f'Sem arestas! Arestas de {i2} = {arestas}')
        

    
    def dijkstra(self, startNodeName: str):
        size = len(self.cityGates)
        startVertex = self.nameIndex[startNodeName]
        distances = [float("inf")] * size
        distances[startVertex] = 0
        visited = [False] * size
        while(True):
            # Encontrar o vértice não visitado com a menor distância
            min_distance = float("inf")
            u = None
            
            for i in range(size):
                if not visited[i] and distances[i] < min_distance:
                    min_distance = distances[i]
                    u = i

            # Se não encontramos um vértice, isso significa que não há mais vértices
            # acessíveis a partir do nó inicial
            if u is None:
                break

            # Atualizar as distâncias dos vizinhos de u
            for v in range(size):
                if self.Mvizinhos[u][v] != -1 and not visited[v]:  # Se houver aresta
                    alt = distances[u] + self.Mvizinhos[u][v]
                    if alt < distances[v]:
                        distances[v] = alt
            visited[u] = True
        
        #debug
        for i, v in enumerate(visited):
            if v == False:
                print(f'Não visitado <{i}> {self.cityGates.iloc[i]['id']}')
        #debug

        return distances

    def dijkstra2(self, startNodeName: str):
        size = len(self.cityGates)
        startVertex = self.nameIndex[startNodeName]
        distances = [float("inf")] * size
        distances[startVertex] = 0
        visited = [False] * size

        for _ in range(size):
            min_distance = float("inf")
            u = None

            # Heap seria melhor 
            for i in range(size):
                if not visited[i] and distances[i] < min_distance:
                    min_distance = distances[i]
                    u = i

            if u is None:
                break

            visited[u] = True

            for v in range(size):
                if self.Mvizinhos[u][v] != -1 and not visited[v]:
                    alt = distances[u] + self.Mvizinhos[u][v]
                    if alt < distances[v]:
                        distances[v] = alt
        return distances

    def ObtemCaminhos(self, pontosEntrada: List[str]):
        """Monta um dataframe com cada campo de entrada e a distancia para cada um dos outros nós"""
        rowList = []
        
        # Itera sobre cada ponto de entrada na lista
        for ponto in pontosEntrada:
            distancias = self.dijkstra(ponto)  # Obtém as distâncias mínimas a partir do ponto
            
            # Obtém os nomes dos pontos
            chaves = list(self.nameIndex.keys())
            
            # Cria um dicionário para a linha do DataFrame
            d = {"entry": f"{self.cityGates.loc[self.cityGates['id'] == ponto]['name'].item()}({ponto})"}  # Adiciona a chave 'entry' com o nome do ponto
            
            # Adiciona as distâncias para cada ponto na chave correspondente
            for chave, distancia in zip(chaves, distancias):
                gateName = self.cityGates.loc[self.cityGates['id'] == chave]['name'].item()
                d[f"{gateName}({chave})"] = distancia
            
            # Adiciona o dicionário na lista de linhas
            rowList.append(d)
        
        # Cria um DataFrame a partir da lista de dicionários
        df = pd.DataFrame(rowList)
        
        return df

    def dfs(self, origem: str, destino: str):
        """
        Realiza uma busca em profundidade (DFS) do ponto 'origem' até o ponto 'destino', 
        armazenando o caminho e a distância total.
        """
        # Recupera os índices dos pontos de origem e destino
        origem_idx = self.nameIndex[origem]
        destino_idx = self.nameIndex[destino]
        
        # Inicializa as estruturas para armazenar o caminho e a distância
        caminho = []
        distancia_total = 0
        
        # Função auxiliar recursiva para a DFS
        def dfs_recursiva(v, destino_idx, caminho_atual, distancia_atual, visitados):
            # Marca o vértice atual como visitado
            visitados[v] = True
            
            # Adiciona o vértice ao caminho atual
            caminho_atual.append(v)
            
            # Verifica se chegou ao destino
            if v == destino_idx:
                # Se chegou no destino, armazena o caminho e a distância total
                caminho[:] = caminho_atual[:]
                distancia_atual += sum(self.Mvizinhos[caminho_atual[i]][caminho_atual[i + 1]] 
                                    for i in range(len(caminho_atual) - 1))
                return True
            
            # Explora os vizinhos não visitados
            for u in range(len(self.Mvizinhos)):
                if self.Mvizinhos[v][u] != -1 and not visitados[u]:
                    # distancia_total += self.Mvizinhos[v][u]
                    # Recursão para o próximo vértice
                    if dfs_recursiva(u, destino_idx, caminho_atual, distancia_atual, visitados):
                        return True
            
            # Caso o destino não tenha sido encontrado, desfaz a escolha do vértice atual
            caminho_atual.pop()
            visitados[v] = False
            return False

        # Inicializa o vetor de visitados
        visitados = [False] * len(self.Mvizinhos)
        
        # Chama a DFS a partir do ponto de origem
        encontrou_caminho = dfs_recursiva(origem_idx, destino_idx, [], 0, visitados)
        
        # Se encontrou o caminho, calcula a distância total
        if encontrou_caminho:
            return caminho, distancia_total
        else:
            return None, None  # Se não houver caminho, retorna None
            

if __name__ == "__main__":
    base_tratada = "./base_tratada_tgs.xlsx"

    gas_points_raw = pd.read_excel(open(base_tratada, "rb"), decimal=',') # Excel com os citygates
    gas_points = gas_points_raw.rename(str.lower,axis='columns')
    gas_points = gas_points.rename(columns={"latitude": "lat", "longitude": "lon"}) # Uso lat e lon no código

    gas_points['name'] = gas_points['name'].str.strip()
    gas_points['id'] = gas_points['id'].str.strip()
    gas_points = gas_points.sort_values(by=['id'], ascending=True)
    gas_points = gas_points.drop_duplicates(['id'])  # deleta as linhas com Id duplicado mantendo apenas uma

    minSpanTree = Kruskal(gas_points) # Obtém a arvore geradora minima. Pode ser demorado!!!! Se ficar demorado pode ser mais facik abrir o csv 
    listaVizinhos = []

    for u,v, w in minSpanTree: # Mapeia de indice numérico para Id 
        listaVizinhos.append([gas_points.iloc[u]['id'], gas_points.iloc[v]['id'], w])
    


    vizinhos = pd.DataFrame(listaVizinhos, columns=['De', 'Para', 'Custo']) # transforma em dataframe
    vizinhos.to_csv( #exporta csv
        path_or_buf="vizinhos_mst.csv", index=False, decimal=",", encoding="Windows-1252"
    )

    grafo = GasGraph(cityGates=gas_points, vizinhos=vizinhos)


    import plotly.graph_objects as go
    import plotly.express as px

    fig = px.scatter_map(gas_points, lat="lat", lon="lon", color="type", zoom=3, text="id", size=[2] * len(gas_points))
    fig.update_layout(map_style="open-street-map", map_zoom=4, map_center_lat = -33,
        margin={"r":0,"t":0,"l":0,"b":0}, clickmode='event')

    lineColor = '#ffffff' # Branco
    for i in range(len(grafo.Mvizinhos)):
        for j in range(i, len(grafo.Mvizinhos)):
            if grafo.Mvizinhos[i][j] >= 0:
                origem = grafo.cityGates.iloc[i]
                destino = grafo.cityGates.iloc[j]
                fig.add_trace(go.Scattermap(lon=[origem.lon, destino.lon], lat=[origem.lat, destino.lat], mode='lines', showlegend = False, line=dict(color=lineColor)))
    fig.show()

    plotly.offline.plot(fig, filename="tgs_mst.html", )