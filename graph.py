from math import acos, cos, radians, sin
from typing import List
import pandas as pd


## Distancia calculada com lei geral dos cossenos.
# Pode ter erros de aproximação para distâncias pequenas. Alternativa usar haversine
def CustoEntreNos(lat1, lat2, lng1, lng2):
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


class GasGraph(object):
    def __init__(self, vizinhos: pd.DataFrame, cityGates: pd.DataFrame):
        """Recebe a lista com todas as conexões  de vizinhança e os dados dos city gates"""
        self.cityGates = cityGates
        # A matriz de vizinho vai ter o custo entre cada nó. Se for -1 a conexão não existe
        self.Mvizinhos = [
            [-1] * len(self.cityGates) for x in range(len(self.cityGates))
        ]
        self.nameIndex = {k: v for v, k in enumerate(self.cityGates["nome"].to_list())}
        for i, val in vizinhos.iterrows():
            indiceOrigem = self.nameIndex[val["De"]]
            indiceDestino = self.nameIndex[val["Para"]]
            origem = self.cityGates.iloc[indiceOrigem]
            destino = self.cityGates.iloc[indiceDestino]
            custo = CustoEntreNos(origem.lat, destino.lat, origem.lon, destino.lon)
            self.Mvizinhos[indiceOrigem][indiceDestino] = custo
            self.Mvizinhos[indiceDestino][indiceOrigem] = custo

    def dijkstra(self, startNodeName: str):
        size = len(self.cityGates)
        startVertex = self.nameIndex[startNodeName]
        distances = [float("inf")] * size
        distances[startVertex] = 0
        visited = [False] * size

        for _ in range(size):
            min_distance = float("inf")
            u = None
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
        for i, ponto in enumerate(pontosEntrada):
            distancias = self.dijkstra(ponto)
            # Adiciona o Id ao nome do ponto ficando <Nome>#<Id>
            chaves = list(
                map(
                    lambda x: f"{x}#{self.cityGates.iloc[self.nameIndex[x]].id}",
                    list(self.nameIndex.keys()),
                )
            )
            d = dict(zip(["Inyección"] + chaves, [ponto] + distancias))
            rowList.append(d)
        return pd.DataFrame(rowList)


if __name__ == "__main__":
    print("Iniciando...")
    vizinhos = pd.read_excel("./lista_vizinhança_corrigida.xlsx")
    vizinhos = vizinhos[["De", "Para"]]
    vizinhos["De"] = vizinhos["De"].str.strip()
    vizinhos["Para"] = vizinhos["Para"].str.strip()

    cityGates = pd.read_excel("./malha_TGN_reduzido.xlsx")
    gas_points = cityGates.rename(str.lower, axis="columns")
    gas_points = gas_points.rename(
        columns={
            "id pe": "id",
            "denominacion pe": "nome",
            "zona tarifaria": "zona",
            "latitud": "lat",
            "longitud": "lon",
        }
    )
    gas_points["nome"] = gas_points["nome"].str.strip()
    g = GasGraph(vizinhos, gas_points)
    # print(g.dijkstra('Campo Duran'))
    gas_points
    entradas = gas_points.loc[gas_points["tipo"] == "Inyección"]

    caminhos = g.ObtemCaminhos(entradas)
    caminhos.to_csv(
        path_or_buf="distancias.csv", index=False, decimal=",", encoding="Windows-1252"
    )
