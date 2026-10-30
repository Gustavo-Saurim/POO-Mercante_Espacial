
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
        return Inimigo(
            self.__nome,
            self.__vida_max,
            self.__ataque
        )

    def __str__(self):
        return (
            f"{self.__nome} | vida {self.__vida}/{self.__vida_max} "
            f"| ataque {self.__ataque}"
        )


class Planeta:
    def __init__(self, nome, risco, inimigos, loot):
        if risco not in RISCOS:
            raise Exception(f"Risco inválido: {risco}")

        self.__nome = nome
        self.__risco = risco
        self.__inimigos = inimigos
        self.__loot = loot

    def get_nome(self):
        return self.__nome

    def get_risco(self):
        return self.__risco

    def eh_final(self):
        return self.__risco == "final"

    def criar_inimigos(self):
        return [
            inimigo.copiar()
            for inimigo in self.__inimigos
        ]

    def get_loot(self):
        return list(self.__loot)

    def __str__(self):
        return (
            f"{self.__nome} | risco {self.__risco} "
            f"| {len(self.__inimigos)} inimigos"
        )


def criar_galaxia():
    sucata = Mercadoria("Sucata", 15)
    cristal = Mercadoria("Cristal Bruto", 50)
    liga = Mercadoria("Liga Estelar", 135)
    nucleo = Mercadoria("Núcleo de Plasma", 300)

    return [
        Planeta(
            "Terra Nova",
            "baixo",
            [
                Inimigo("Drone Sucateiro", 30, 5),
                Inimigo("Saqueador Novato", 40, 7)
            ],
            [
                (sucata, 4),
                (cristal, 1)
            ]
        ),

        Planeta(
            "Ferrum",
            "medio",
            [
                Inimigo("Pirata Espacial", 60, 10),
                Inimigo("Caçador de Recompensas", 70, 12)
            ],
            [
                (cristal, 3),
                (liga, 1)
            ]
        ),

        Planeta(
            "Aridia",
            "medio",
            [
                Inimigo("Mineradora Rebelde", 65, 11),
                Inimigo("Predador das Dunas", 75, 13)
            ],
            [
                (cristal, 2),
                (liga, 2)
            ]
        ),

        Planeta(
            "Nexus",
            "alto",
            [
                Inimigo("Caçador de Elite", 85, 15),
                Inimigo("Fragata Sombria", 102, 19),
                Inimigo("Guardião Antigo", 128, 21)
            ],
            [
                (liga, 3),
                (nucleo, 2)
            ]
        ),

        Planeta(
            "Coração do Vazio",
            "final",
            [
                Inimigo("Sentinela do Vazio", 119, 20),
                Inimigo("Senhor do Vazio", 212, 26)
            ],
            []
        )
    ]


if __name__ == "__main__":
    galaxia = criar_galaxia()

    for planeta in galaxia:
        print(planeta)

    terra_nova = galaxia[0]

    inimigos = terra_nova.criar_inimigos()

    print(inimigos[0])

    inimigos[0].receber_dano(12)

    print(inimigos[0])

    print(terra_nova.criar_inimigos()[0])

    for mercadoria, qtd in terra_nova.get_loot():
        print(f"{qtd}x {mercadoria}")

    print(galaxia[-1].eh_final())

    try:
        Planeta("Teste", "extremo", [], [])

    except Exception as erro:
        print("Erro esperado:", erro)
