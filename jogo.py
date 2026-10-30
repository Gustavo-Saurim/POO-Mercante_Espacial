import pickle
import random

from comerciante import Comerciante
from mundo import criar_galaxia

PLANETAS_PARA_FINAL = 3
VARIACAO_DANO = 0.2
ARQUIVO_SAVE = "save.pkl"


class Jogo:
    def __init__(self, jogador):
        self.__planetas = criar_galaxia()
        self.jogador = jogador
        self.__vencidos = []
        self.__planeta_atual = None
        self.__inimigos = []
        self.__final_vencido = False

    def get_planetas(self):
        return list(self.__planetas)

    def planeta_atual(self):
        return self.__planeta_atual

    def inimigo_atual(self):
        return self.__inimigos[0] if self.__inimigos else None

    def final_liberado(self):
        return len(self.__vencidos) >= PLANETAS_PARA_FINAL

    def planetas_disponiveis(self):
        return [
            planeta
            for planeta in self.__planetas
            if planeta.get_nome() not in self.__vencidos
            and (not planeta.eh_final() or self.final_liberado())
        ]

    def escolher_planeta(self, planeta):
        if self.verificar_fim() is not None:
            raise Exception("O jogo já terminou")
        if self.__planeta_atual is not None:
            raise Exception("Já existe uma batalha em andamento")
        if planeta not in self.planetas_disponiveis():
            raise Exception(f"{planeta.get_nome()} não está disponível")
        self.__planeta_atual = planeta
        self.__inimigos = planeta.criar_inimigos()

    def turno_batalha(self, acao):
        if self.__planeta_atual is None:
            raise Exception("Não há batalha em andamento")
        if self.verificar_fim() is not None:
            raise Exception("O jogo já terminou")
        if acao not in ("atacar", "defender"):
            raise Exception(f"Ação inválida: {acao}")

        nave = self.jogador.nave
        inimigo = self.__inimigos[0]
        defendendo = acao == "defender"
        mensagens = []

        if defendendo:
            mensagens.append("Você se prepara para defender o próximo ataque")
        else:
            dano = self.__sortear_dano(nave.get_ataque())
            inimigo.receber_dano(dano)
            mensagens.append(
                f"Você causou {dano} de dano a {inimigo.get_nome()} "
                f"(vida {inimigo.get_vida()})"
            )
            if not inimigo.esta_vivo():
                mensagens.append(f"{inimigo.get_nome()} foi derrotado!")
                self.__inimigos.pop(0)
                if not self.__inimigos:
                    mensagens.extend(self.__concluir_planeta())
                return mensagens

        dano = self.__sortear_dano(inimigo.get_ataque())
        if defendendo:
            dano //= 2
        recebido = nave.receber_dano(dano)
        mensagens.append(
            f"{inimigo.get_nome()} causou {recebido} de dano à sua nave "
            f"({nave.get_vida()}/{nave.get_vida_max()})"
        )
        if not nave.esta_viva():
            mensagens.append("Sua nave foi destruída")
        return mensagens

    def verificar_fim(self):
        if not self.jogador.nave.esta_viva():
            return "derrota"
        if self.__final_vencido:
            return "vitoria"
        return None

    def salvar(self):
        if self.__planeta_atual is not None:
            raise Exception("Não é possível salvar durante uma batalha")
        with open(ARQUIVO_SAVE, "wb") as arquivo:
            pickle.dump(self, arquivo)

    @staticmethod
    def carregar():
        try:
            with open(ARQUIVO_SAVE, "rb") as arquivo:
                return pickle.load(arquivo)
        except FileNotFoundError:
            raise Exception("Nenhum jogo salvo encontrado")

    def __concluir_planeta(self):
        planeta = self.__planeta_atual
        self.__planeta_atual = None
        mensagens = [f"Planeta {planeta.get_nome()} conquistado!"]
        if planeta.eh_final():
            self.__final_vencido = True
            mensagens.append("Você venceu o jogo!")
            return mensagens
        self.__vencidos.append(planeta.get_nome())
        for mercadoria, qtd in planeta.get_loot():
            coletada = self.jogador.coletar(mercadoria, qtd)
            linha = f"Loot: {coletada}x {mercadoria.get_nome()}"
            if coletada < qtd:
                linha += f" ({qtd - coletada} descartadas, porão cheio)"
            mensagens.append(linha)
        return mensagens

    def __sortear_dano(self, base):
        minimo = max(1, int(base * (1 - VARIACAO_DANO)))
        maximo = max(minimo, int(base * (1 + VARIACAO_DANO)))
        return random.randint(minimo, maximo)

    def __str__(self):
        return f"Jogo | {len(self.__vencidos)} planetas conquistados | {self.jogador}"


if __name__ == "__main__":
    import os

    from naves import Cargueiro, Fragata

    def lutar(jogo, planeta):
        jogo.escolher_planeta(planeta)
        while jogo.planeta_atual() is not None:
            for linha in jogo.turno_batalha("atacar"):
                print(linha)

    random.seed(7)
    jogo = Jogo(Comerciante("Teste", Cargueiro()))
    jogo.jogador.nave.aumentar_ataque(200)
    jogo.jogador.nave.aumentar_vida_max(500)

    try:
        jogo.escolher_planeta(jogo.get_planetas()[-1])
    except Exception as erro:
        print("Erro esperado:", erro)

    for planeta in jogo.planetas_disponiveis()[:3]:
        lutar(jogo, planeta)

    print(jogo)
    print(jogo.final_liberado())
    jogo.salvar()
    print(Jogo.carregar())
    os.remove(ARQUIVO_SAVE)

    lutar(jogo, jogo.get_planetas()[-1])
    print(jogo.verificar_fim())

    jogo2 = Jogo(Comerciante("Teste2", Fragata()))
    jogo2.escolher_planeta(jogo2.get_planetas()[0])
    print(jogo2.turno_batalha("defender"))
    for acao in (
        lambda: jogo2.salvar(),
        lambda: jogo2.escolher_planeta(jogo2.get_planetas()[1]),
        lambda: jogo2.turno_batalha("fugir"),
        lambda: Jogo.carregar(),
    ):
        try:
            acao()
        except Exception as erro:
            print("Erro esperado:", erro)

    jogo3 = Jogo(Comerciante("Fraco", Fragata()))
    jogo3.escolher_planeta(jogo3.get_planetas()[3])
    while jogo3.verificar_fim() is None:
        jogo3.turno_batalha("defender")
    print(jogo3.verificar_fim())