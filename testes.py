import os
import random

from comerciante import Comerciante, Exportavel
from jogo import ARQUIVO_SAVE, Jogo
from mundo import Inimigo, Mercadoria, Planeta, criar_galaxia
from naves import BlindagemMixin, Cargueiro, Fragata, Nave


def da_erro(funcao):
    try:
        funcao()
    except Exception:
        return True
    return False


def lutar(jogo, planeta):
    jogo.escolher_planeta(planeta)
    while jogo.planeta_atual() is not None:
        jogo.turno_batalha("atacar")


def jogo_forte():
    jogo = Jogo(Comerciante("Forte", Cargueiro()))
    jogo.jogador.nave.aumentar_ataque(200)
    jogo.jogador.nave.aumentar_vida_max(500)
    return jogo


def test_mundo():
    sucata = Mercadoria("Sucata", 10)
    assert sucata.get_nome() == "Sucata"
    assert sucata.get_valor() == 10
    assert da_erro(lambda: Mercadoria("Nada", 0))

    inimigo = Inimigo("Drone", 30, 5)
    inimigo.receber_dano(12)
    assert inimigo.get_vida() == 18
    assert inimigo.esta_vivo()
    assert inimigo.copiar().get_vida() == 30
    inimigo.receber_dano(100)
    assert inimigo.get_vida() == 0
    assert not inimigo.esta_vivo()

    galaxia = criar_galaxia()
    assert len(galaxia) == 5
    assert galaxia[0].get_risco() == "baixo"
    assert not galaxia[0].eh_final()
    assert galaxia[-1].eh_final()

    inimigos = galaxia[0].criar_inimigos()
    inimigos[0].receber_dano(5)
    assert galaxia[0].criar_inimigos()[0].get_vida() == 30

    mercadoria, qtd = galaxia[0].get_loot()[0]
    assert mercadoria.get_nome() == "Sucata"
    assert qtd == 4

    assert da_erro(lambda: Planeta("Teste", "extremo", [], []))


def test_naves():
    assert da_erro(lambda: Nave())

    cargueiro = Cargueiro()
    fragata = Fragata()
    assert cargueiro.capacidade() == 20
    assert fragata.capacidade() == 12
    assert cargueiro.get_vida() == 160
    assert cargueiro.get_ataque() == 15
    assert isinstance(fragata, BlindagemMixin)
    assert not isinstance(cargueiro, BlindagemMixin)

    sucata = Mercadoria("Sucata", 10)
    cargueiro.adicionar_carga(sucata, 10)
    assert cargueiro.quantidade("Sucata") == 10
    assert len(cargueiro.remover_carga("Sucata", 4)) == 4
    assert cargueiro.listar_carga() == {"Sucata": 6}
    assert da_erro(lambda: cargueiro.remover_carga("Sucata", 50))
    assert da_erro(lambda: fragata.adicionar_carga(sucata, 21))

    assert cargueiro.receber_dano(40) == 40
    assert cargueiro.get_vida() == 120
    cargueiro.reparar(1000)
    assert cargueiro.get_vida() == 160

    assert fragata.receber_dano(20) == 15
    assert fragata.get_vida() == 85

    fragata.receber_dano(1000)
    assert not fragata.esta_viva()

    cargueiro.aumentar_ataque(5)
    cargueiro.aumentar_vida_max(20)
    cargueiro.aumentar_carga(5)
    assert cargueiro.get_ataque() == 20
    assert cargueiro.get_vida_max() == 180
    assert cargueiro.capacidade_total() == 25
    assert cargueiro.espaco_livre() == 19


def test_comerciante():
    sucata = Mercadoria("Sucata", 10)
    cristal = Mercadoria("Cristal Bruto", 35)

    jogador = Comerciante("Teste", Cargueiro())
    assert jogador.get_creditos() == 100
    assert jogador.get_nome() == "Teste"
    assert isinstance(jogador, Exportavel)
    assert da_erro(lambda: Exportavel())

    assert jogador.coletar(sucata, 100) == 20
    assert jogador.coletar(cristal, 1) == 0

    jogador = Comerciante("Teste", Cargueiro())
    jogador.coletar(sucata, 4)
    assert jogador.vender("Sucata", 4) == 40
    assert jogador.get_creditos() == 140
    assert da_erro(lambda: jogador.vender("Ouro", 1))
    assert da_erro(lambda: jogador.vender("Sucata", 0))

    jogador = Comerciante("Teste", Cargueiro())
    jogador.coletar(sucata, 4)
    jogador.coletar(cristal, 1)
    assert jogador.vender_tudo() == 75
    assert jogador.nave.listar_carga() == {}

    jogador = Comerciante("Teste", Cargueiro())
    assert jogador.custo_upgrade("ataque") == 100
    jogador.comprar_upgrade("ataque")
    assert jogador.get_creditos() == 0
    assert jogador.nave.get_ataque() == 23
    assert jogador.custo_upgrade("ataque") == 200
    assert da_erro(lambda: jogador.comprar_upgrade("casco"))
    assert da_erro(lambda: jogador.comprar_upgrade("laser"))

    jogador = Comerciante("Teste", Cargueiro())
    jogador.nave.receber_dano(30)
    assert jogador.reparar() == 30
    assert jogador.nave.get_vida() == 160
    assert jogador.get_creditos() == 40
    assert da_erro(lambda: jogador.reparar())

    jogador = Comerciante("Teste", Cargueiro())
    jogador.coletar(sucata, 4)
    jogador.vender("Sucata", 4)
    jogador.to_csv("teste_historico.csv")
    jogador.to_txt("teste_historico.txt")
    with open("teste_historico.csv", encoding="utf-8") as arquivo:
        assert "venda,Sucata,4,40" in arquivo.read()
    with open("teste_historico.txt", encoding="utf-8") as arquivo:
        assert "venda: Sucata" in arquivo.read()
    os.remove("teste_historico.csv")
    os.remove("teste_historico.txt")


def test_jogo():
    random.seed(1)
    jogo = jogo_forte()
    planetas = jogo.get_planetas()
    assert len(planetas) == 5
    assert len(jogo.planetas_disponiveis()) == 4
    assert not jogo.final_liberado()
    assert jogo.verificar_fim() is None
    assert da_erro(lambda: jogo.escolher_planeta(planetas[-1]))
    assert da_erro(lambda: jogo.turno_batalha("atacar"))

    lutar(jogo, planetas[0])
    assert jogo.jogador.nave.quantidade("Sucata") == 4
    assert len(jogo.planetas_disponiveis()) == 3

    jogo.escolher_planeta(planetas[1])
    assert da_erro(lambda: jogo.salvar())
    assert da_erro(lambda: jogo.escolher_planeta(planetas[2]))
    assert da_erro(lambda: jogo.turno_batalha("fugir"))
    while jogo.planeta_atual() is not None:
        jogo.turno_batalha("atacar")

    lutar(jogo, planetas[2])
    assert jogo.final_liberado()
    assert planetas[-1] in jogo.planetas_disponiveis()

    lutar(jogo, planetas[-1])
    assert jogo.verificar_fim() == "vitoria"

    fraco = Jogo(Comerciante("Fraco", Fragata()))
    fraco.escolher_planeta(fraco.get_planetas()[3])
    while fraco.verificar_fim() is None:
        fraco.turno_batalha("defender")
    assert fraco.verificar_fim() == "derrota"

    jogo_salvo = jogo_forte()
    jogo_salvo.salvar()
    assert Jogo.carregar().jogador.get_creditos() == 100
    os.remove(ARQUIVO_SAVE)
    assert da_erro(lambda: Jogo.carregar())


if __name__ == "__main__":
    for teste in (test_mundo, test_naves, test_comerciante, test_jogo):
        teste()
        print(f"{teste.__name__}: OK")
    print("Todos os testes passaram")
