class Heap(object):

    def __init__(self, sourceList=None):
        """cria o Heap, vazio se nenhuma lista for passada ou a partir da lista passada"""
        if sourceList == None:
            self.heapList = []

        else:
            self.heapList = sourceList[:]
            middle = (len(sourceList) // 2) - 1
            for i in range(middle, -1, -1):
                self._tidy_down(i)

    # Tidy down organiza os valores
    def _tidy_down(self, i):
        fe = i * 2 + 1  # Posição do filho a esquerda do elemento i
        fd = fe + 1  # Posição do filho a direita do elemento i
        tam = len(self.heapList)

        while fe < tam:
            aux = fe  # vou pegar o menor dos filhos e colocar em aux pra comparar
            if fd < tam:
                if self.heapList[fd] < self.heapList[fe]:
                    aux = fd
            if self.heapList[aux] < self.heapList[i]:
                self.heapList[aux], self.heapList[i] = (
                    self.heapList[i],
                    self.heapList[aux],
                )
                i = aux
            else:
                break
            fe = i * 2 + 1
            fd = fe + 1

    def pop(self):
        """retira o elemento do topo do heap e retorna-o"""
        if self.heapList == []:
            return None
        self.heapList[0], self.heapList[-1] = self.heapList[-1], self.heapList[0]
        aux = self.heapList.pop()
        self._tidy_down(0)
        return aux

    def _tidy_up(self, i):
        pai = (i - 1) // 2
        if i == 0:
            return
        if self.heapList[i] < self.heapList[pai]:
            self.heapList[i], self.heapList[pai] = self.heapList[pai], self.heapList[i]
            self._tidy_up(pai)
            return
        return

    def push(self, el):
        self.heapList.append(el)
        self._tidy_up(len(self.heapList) - 1)


def heap_sort(lista):
    """Ordena os elementos de uma lista recebida"""
    h = Heap(lista)
    for i in range(len(lista)):
        lista[i] = h.pop()
    return


## --------------------------------------
from abc import ABC, abstractmethod

class ValueInterface(ABC):
    @abstractmethod
    def getValue(self):
        pass


class Item(ValueInterface):
    def __init__(self, value):
        self._value = value

    def getValue(self):
        return self._value


import heapq

class MinHeap:
    def __init__(self):
        self.heap = []

    def insert(self, item: ValueInterface):
        # Inserindo na heap o valor obtido via getValue()
        heapq.heappush(self.heap, (item.getValue(), item))

    def extract_min(self):
        # Remove e retorna o item com o menor valor
        return heapq.heappop(self.heap)[1]

# Exemplo de uso
item1 = Item(10)
item2 = Item(5)
item3 = Item(20)

min_heap = MinHeap()
min_heap.insert(item1)
min_heap.insert(item2)
min_heap.insert(item3)

# print(min_heap.extract_min().getValue())  # Saída: 5
# print(min_heap.extract_min().getValue())  # Saída: 10
# print(min_heap.extract_min().getValue())  # Saída: 20

print(min_heap.extract_min())  # Saída: 5
print(min_heap.extract_min())  # Saída: 10
print(min_heap.extract_min())  # Saída: 20