class Mercadoria:
    def __init__(self, nome):
        self.__nome = nome

    def get_nome(self):
        return self.__nome

    def __str__(self):
        return self.__nome

class Planeta:
    def init(self,nome,posicao,precos):
        self.nome = nome
        self.posicao = posicao
        self.precos = precos

    def get_nome(self):
        return self.nome

    def get_preco(self,nome):
        if nome not in self.precos:
            raise Exception(f"{nome} não é vendida em {self.nome}")
        return self.precos[nome]

    def distancia_ate(self,outro):
        return abs(self.posicao - outro.posicao)

    def str(self):
        return f"{self.nome} (posicao{self.posicao})"
