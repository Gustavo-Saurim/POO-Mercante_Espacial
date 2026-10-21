RISCOS = ("baixo", "medio", "alto", "final")
 
 
class Mercadoria:
    def __init__(self, nome, valor):
        if valor <= 0:
            raise Exception("O valor da mercadoria deve ser maior que zero")
        self.__nome = nome
        self.__valor = valor
 
    def get_nome(self):
        return self.__nome
 
    def get_valor(self):
        return self.__valor
 
    def __str__(self):
        return f"{self.__nome} ({self.__valor} créditos)"
 
 
class Inimigo:
    def __init__(self, nome, vida, ataque):
        self.__nome = nome
        self.__vida_max = vida
        self.__vida = vida
        self.__ataque = ataque
 
    def get_nome(self):
        return self.__nome
 
    def get_vida(self):
        return self.__vida
 
    def get_ataque(self):
        return self.__ataque
 
    def receber_dano(self, valor):
        if valor < 0:
            raise Exception("O dano não pode ser negativo")
        self.__vida = max(0, self.__vida - valor)
 
    def esta_vivo(self):
        return self.__vida > 0
 
    def copiar(self):
        return Inimigo(self.__nome, self.__vida_max, self.__ataque)
 
    def __str__(self):
        return (
            f"{self.__nome} | vida {self.__vida}/{self.__vida_max} "
            f"| ataque {self.__ataque}"
        )

class Planeta:
    def __init__(self, nome, posicao, precos):
        self.__nome = nome
        self.__posicao = posicao
        self.__precos = precos
 
    def get_nome(self):
        return self.__nome
 
    def get_preco(self, nome):
        if nome not in self.__precos:
            raise Exception(f"{nome} não é vendida em {self.__nome}")
        return self.__precos[nome]
 
    def distancia_ate(self, outro):
        return abs(self.__posicao - outro.__posicao)
 
    def __str__(self):
        return f"{self.__nome} (posição {self.__posicao})"
 
 
if __name__ == "__main__":
    terra = Planeta("Terra Nova", 0, {"Grãos": 10, "Ferro": 50, "Chips": 200})
    nexus = Planeta("Nexus", 60, {"Grãos": 20, "Ferro": 100, "Chips": 50})
 
    print(terra)
    print(Mercadoria("Ferro"))
    print(terra.get_preco("Ferro"))
    print(terra.distancia_ate(nexus))
 
    try:
        terra.get_preco("Ouro")
    except Exception as erro:
        print("Erro esperado:", erro)