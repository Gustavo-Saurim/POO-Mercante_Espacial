class Mercadoria:
    def __init__(self, nome):
        self.__nome = nome

    def get_nome(self):
        return self.__nome

    def __str__(self):
        return self.__nome