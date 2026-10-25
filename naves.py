from abc import ABC, abstractmethod

from mundo import Mercadoria

COMBUSTIVEL_MAX = 100.0
CAPACIDADE_CARGUEIRO = 20
CAPACIDADE_FRAGATA = 12
REDUCAO_BLINDAGEM = 0.4  # a blindagem corta 40% das perdas em combate


class Nave(ABC):
    """Classe abstrata: não existe "uma nave qualquer", só Cargueiro ou Fragata."""

    __combustivel: float
    __carga: list  # List[Mercadoria] -> agregação (uma entrada por unidade)

    def __init__(self):
        self.__combustivel = COMBUSTIVEL_MAX
        self.__carga = []

    @abstractmethod
    def capacidade(self):
        """Quantas unidades de mercadoria cabem no porão."""
        pass

    def get_combustivel(self):
        return self.__combustivel

    def get_carga(self):
        return list(self.__carga)

    def gastar_combustivel(self, qtd: float):
        if qtd < 0:
            raise Exception("Quantidade de combustível inválida")
        if qtd > self.__combustivel:
            raise Exception(
                f"Combustível insuficiente: precisa de {qtd}, tem {self.__combustivel}"
            )
        self.__combustivel -= qtd

    def abastecer(self, qtd: float):
        if qtd <= 0:
            raise Exception("Quantidade de combustível inválida")
        if self.__combustivel + qtd > COMBUSTIVEL_MAX:
            raise Exception(f"O tanque comporta no máximo {COMBUSTIVEL_MAX}")
        self.__combustivel += qtd

    def adicionar_carga(self, m: Mercadoria, qtd: int):
        if qtd <= 0:
            raise Exception("Quantidade inválida")
        if len(self.__carga) + qtd > self.capacidade():
            livre = self.capacidade() - len(self.__carga)
            raise Exception(f"Porão cheio: só cabem mais {livre} unidades")
        for _ in range(qtd):
            self.__carga.append(m)

    def remover_carga(self, nome: str, qtd: int):
        """Remove `qtd` unidades da mercadoria `nome` e devolve o objeto Mercadoria."""
        if qtd <= 0:
            raise Exception("Quantidade inválida")
        if self.quantidade(nome) < qtd:
            raise Exception(f"Você não tem {qtd}x {nome} no porão")
        removida = None
        for _ in range(qtd):
            for m in self.__carga:
                if m.get_nome() == nome:
                    self.__carga.remove(m)
                    removida = m
                    break
        return removida

    def quantidade(self, nome: str):
        return sum(1 for m in self.__carga if m.get_nome() == nome)

    def __str__(self):
        tipos = {}
        for m in self.__carga:
            tipos[m.get_nome()] = tipos.get(m.get_nome(), 0) + 1
        porao = ", ".join(f"{q}x {n}" for n, q in tipos.items()) or "vazio"
        return (
            f"{type(self).__name__} | combustível {self.__combustivel:.0f}/{COMBUSTIVEL_MAX:.0f} "
            f"| porão {len(self.__carga)}/{self.capacidade()} ({porao})"
        )


class BlindagemMixin:
    """Mixin: só métodos, nenhum atributo. Pode ser "encaixado" em qualquer nave."""

    def reduzir_perda(self, valor: float):
        return valor * (1 - REDUCAO_BLINDAGEM)


class Cargueiro(Nave):
    """Porão grande, sem blindagem."""

    def capacidade(self):
        return CAPACIDADE_CARGUEIRO


class Fragata(BlindagemMixin, Nave):
    """Porão menor, mas a blindagem reduz o que se perde em combate."""

    def capacidade(self):
        return CAPACIDADE_FRAGATA


if __name__ == "__main__":
    sucata = Mercadoria("Sucata", 10)

    cargueiro = Cargueiro()
    cargueiro.adicionar_carga(sucata, 5)
    cargueiro.gastar_combustivel(30)
    print(cargueiro)

    fragata = Fragata()
    print(fragata)
    print("Perda de 100 com blindagem:", fragata.reduzir_perda(100))
    print("MRO da Fragata:", [c.__name__ for c in Fragata.__mro__])

    try:
        Nave()
    except TypeError as erro:
        print("Erro esperado (classe abstrata):", erro)

    try:
        fragata.adicionar_carga(sucata, 13)
    except Exception as erro:
        print("Erro esperado:", erro)
