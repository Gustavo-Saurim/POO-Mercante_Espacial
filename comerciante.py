import csv
from abc import ABCMeta, abstractmethod

CREDITOS_INICIAIS = 100
CUSTO_REPARO = 2
UPGRADES = {
    "ataque": (100, 8),
    "casco": (80, 30),
    "carga": (60, 5),
}

class Exportavel(metaclass=ABCMeta):
    @abstractmethod
    def to_csv(self, caminho):
        pass

    @abstractmethod
    def to_txt(self, caminho):
        pass

class Comerciante(Exportavel):
    def __init__(self, nome, nave):
        self.__nome = nome
        self.__creditos = CREDITOS_INICIAIS
        self.nave = nave
        self.__niveis = {tipo: 0 for tipo in UPGRADES}
        self.__historico = []

    def get_creditos(self):
        return self.__creditos

    def get_nome(self):
        return self.__nome

    def coletar(self, mercadoria, qtd):
        coletada = min(qtd, self.nave.espaco_livre())
        if coletada > 0:
            self.nave.adicionar_carga(mercadoria, coletada)
            self.__historico.append(("loot", mercadoria.get_nome(), coletada, 0))
        return coletada

    def vender(self, nome, qtd):
        if qtd <= 0:
            raise Exception("A quantidade deve ser maior que zero")
        removidas = self.nave.remover_carga(nome, qtd)
        ganho = sum(m.get_valor() for m in removidas)
        self.__creditos += ganho
        self.__historico.append(("venda", nome, qtd, ganho))
        return ganho

    def vender_tudo(self):
        total = 0
        for nome, qtd in self.nave.listar_carga().items():
            total += self.vender(nome, qtd)
        return total

    def custo_upgrade(self, tipo):
        if tipo not in UPGRADES:
            raise Exception(f"Upgrade inválido: {tipo}")
        custo_base, _ = UPGRADES[tipo]
        return custo_base * (self.__niveis[tipo] + 1)

    def comprar_upgrade(self, tipo):
        custo = self.custo_upgrade(tipo)
        if custo > self.__creditos:
            raise Exception("Créditos insuficientes")
        _, ganho = UPGRADES[tipo]
        if tipo == "ataque":
            self.nave.aumentar_ataque(ganho)
        elif tipo == "casco":
            self.nave.aumentar_vida_max(ganho)
        else:
            self.nave.aumentar_carga(ganho)
        self.__creditos -= custo
        self.__niveis[tipo] += 1
        self.__historico.append(("upgrade", tipo, 1, -custo))
        return custo

    def reparar(self):
        falta = self.nave.get_vida_max() - self.nave.get_vida()
        if falta == 0:
            raise Exception("A nave já está com a vida cheia")
        qtd = min(falta, self.__creditos // CUSTO_REPARO)
        if qtd == 0:
            raise Exception("Créditos insuficientes")
        custo = qtd * CUSTO_REPARO
        self.nave.reparar(qtd)
        self.__creditos -= custo
        self.__historico.append(("reparo", "casco", qtd, -custo))
        return qtd

    def to_csv(self, caminho="historico.csv"):
        with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(["tipo", "descricao", "quantidade", "valor"])
            escritor.writerows(self.__historico)

    def to_txt(self, caminho="historico.txt"):
        with open(caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write(f"Histórico de {self.__nome}\n")
            for tipo, descricao, qtd, valor in self.__historico:
                arquivo.write(f"{tipo}: {descricao} | qtd {qtd} | valor {valor}\n")

    def __str__(self):
        return f"{self.__nome} | {self.__creditos} créditos | {self.nave}"

if __name__ == "__main__":
    from mundo import Mercadoria
    from naves import Cargueiro

    sucata = Mercadoria("Sucata", 10)
    cristal = Mercadoria("Cristal Bruto", 35)

    jogador = Comerciante("Teste", Cargueiro())
    print(jogador.coletar(sucata, 4), jogador.coletar(cristal, 1))
    print(jogador.nave)

    print(jogador.vender("Sucata", 4), jogador.get_creditos())

    print(jogador.custo_upgrade("ataque"))
    print(jogador.comprar_upgrade("ataque"), jogador.get_creditos())
    print(jogador.custo_upgrade("ataque"))

    jogador.nave.receber_dano(30)
    print(jogador.reparar(), jogador.get_creditos(), jogador.nave.get_vida())

    print(jogador.vender_tudo(), jogador.get_creditos())
    print(jogador.coletar(sucata, 100))
    print(jogador)

    jogador.to_csv()
    jogador.to_txt()

    for acao in (
        lambda: jogador.comprar_upgrade("casco"),
        lambda: jogador.comprar_upgrade("laser"),
        lambda: jogador.vender("Ouro", 1),
        lambda: jogador.vender("Sucata", 0),
    ):
        try:
            acao()
        except Exception as erro:
            print("Erro esperado:", erro)