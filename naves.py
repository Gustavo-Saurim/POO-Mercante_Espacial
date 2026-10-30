from abc import ABC, abstractmethod

from mundo import Mercadoria

VIDA_BASE = 100
ATAQUE_BASE = 15
CAPACIDADE_CARGUEIRO = 20
CAPACIDADE_FRAGATA = 12
REDUCAO_BLINDAGEM = 0.4


class Nave(ABC):

    __vida_max: int
    __vida: int
    __ataque: int
    __bonus_carga: int
    __carga: list 

    def __init__(self):
        self.__vida_max = VIDA_BASE
        self.__vida = VIDA_BASE
        self.__ataque = ATAQUE_BASE
        self.__bonus_carga = 0
        self.__carga = []

    @abstractmethod
    def capacidade(self):
        pass

    def get_vida(self):
        return self.__vida

    def get_vida_max(self):
        return self.__vida_max

    def get_ataque(self):
        return self.__ataque

    def get_carga(self):
        return list(self.__carga)

    def esta_viva(self):
        return self.__vida > 0

    def reduzir_dano(self, valor: float):
        return valor

    def receber_dano(self, valor: float):
        if valor < 0:
            raise Exception("O dano não pode ser negativo")
        dano = round(self.reduzir_dano(valor))
        self.__vida = max(0, self.__vida - dano)
        return dano

    def reparar(self, qtd: int):
        if qtd < 0:
            raise Exception("Quantidade de reparo inválida")
        self.__vida = min(self.__vida_max, self.__vida + qtd)

    def aumentar_ataque(self, valor: int):
        self.__ataque += valor

    def aumentar_vida_max(self, valor: int):
        self.__vida_max += valor
        self.__vida += valor

    def aumentar_carga(self, valor: int):
        self.__bonus_carga += valor

    def capacidade_total(self):
        return self.capacidade() + self.__bonus_carga

    def espaco_livre(self):
        return self.capacidade_total() - len(self.__carga)

    def adicionar_carga(self, m: Mercadoria, qtd: int):
        if qtd <= 0:
            raise Exception("Quantidade inválida")
        if qtd > self.espaco_livre():
            raise Exception(f"Porão cheio: só cabem mais {self.espaco_livre()} unidades")
        for _ in range(qtd):
            self.__carga.append(m)

    def remover_carga(self, nome: str, qtd: int):
        if qtd <= 0:
            raise Exception("Quantidade inválida")
        if self.quantidade(nome) < qtd:
            raise Exception(f"Você não tem {qtd}x {nome} no porão")
        removidas = []
        restante = []
        for m in self.__carga:
            if m.get_nome() == nome and len(removidas) < qtd:
                removidas.append(m)
            else:
                restante.append(m)
        self.__carga = restante
        return removidas

    def quantidade(self, nome: str):
        return sum(1 for m in self.__carga if m.get_nome() == nome)

    def listar_carga(self):
        resumo = {}
        for m in self.__carga:
            resumo[m.get_nome()] = resumo.get(m.get_nome(), 0) + 1
        return resumo

    def __str__(self):
        porao = ", ".join(f"{q}x {n}" for n, q in self.listar_carga().items()) or "vazio"
        return (
            f"{type(self).__name__} | vida {self.__vida}/{self.__vida_max} "
            f"| ataque {self.__ataque} "
            f"| porão {len(self.__carga)}/{self.capacidade_total()} ({porao})"
        )


class BlindagemMixin:

    def reduzir_dano(self, valor: float):
        return valor * (1 - REDUCAO_BLINDAGEM)


class Cargueiro(Nave):

    def capacidade(self):
        return CAPACIDADE_CARGUEIRO


class Fragata(BlindagemMixin, Nave):

    def capacidade(self):
        return CAPACIDADE_FRAGATA


if __name__ == "__main__":
    sucata = Mercadoria("Sucata", 10)

    cargueiro = Cargueiro()
    cargueiro.adicionar_carga(sucata, 5)
    print(cargueiro)
    print("Removidas:", len(cargueiro.remover_carga("Sucata", 2)))
    print("Dano sofrido:", cargueiro.receber_dano(40))
    cargueiro.reparar(15)
    cargueiro.aumentar_ataque(5)
    cargueiro.aumentar_vida_max(20)
    cargueiro.aumentar_carga(5)
    print(cargueiro)

    fragata = Fragata()
    print(fragata)
    print("Dano de 100 com blindagem:", fragata.receber_dano(100))
    print("MRO da Fragata:", [c.__name__ for c in Fragata.__mro__])

    try:
        Nave()
    except TypeError as erro:
        print("Erro esperado (classe abstrata):", erro)

    try:
        fragata.adicionar_carga(sucata, 13)
    except Exception as erro:
        print("Erro esperado:", erro)