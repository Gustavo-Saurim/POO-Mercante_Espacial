from comerciante import CUSTO_REPARO, UPGRADES, Comerciante
from jogo import ARQUIVO_SAVE, PLANETAS_PARA_FINAL, Jogo
from naves import (
    CAPACIDADE_CARGUEIRO,
    CAPACIDADE_FRAGATA,
    REDUCAO_BLINDAGEM,
    Cargueiro,
    Fragata,
)

NOMES_UPGRADES = {
    "ataque": "Ataque",
    "casco": "Casco (vida máxima)",
    "carga": "Porão (capacidade)",
}


def ler_inteiro(mensagem, minimo, maximo):
    while True:
        try:
            valor = int(input(mensagem))
        except ValueError:
            print("Digite um número válido.")
            continue
        if minimo <= valor <= maximo:
            return valor
        print(f"Escolha um número entre {minimo} e {maximo}.")


def confirmar(pergunta):
    while True:
        resposta = input(f"{pergunta} (s/n): ").strip().lower()
        if resposta in ("s", "n"):
            return resposta == "s"
        print("Responda com s ou n.")


def escolher_opcao(titulo, opcoes, voltar=None):
    print(f"\n=== {titulo} ===")
    for numero, texto in enumerate(opcoes, start=1):
        print(f"{numero} - {texto}")
    if voltar:
        print(f"0 - {voltar}")
    return ler_inteiro("Escolha: ", 0 if voltar else 1, len(opcoes))


def novo_jogo():
    nome = ""
    while not nome:
        nome = input("Nome do comandante: ").strip()
    opcao = escolher_opcao(
        "Escolha sua nave",
        [
            f"Cargueiro - porão de {CAPACIDADE_CARGUEIRO} unidades, sem blindagem",
            f"Fragata - porão de {CAPACIDADE_FRAGATA} unidades, "
            f"blindagem de {REDUCAO_BLINDAGEM:.0%}",
        ],
    )
    nave = Cargueiro() if opcao == 1 else Fragata()
    print(
        f"\nBem-vindo, {nome}! Conquiste {PLANETAS_PARA_FINAL} planetas "
        "para liberar o planeta final."
    )
    return Jogo(Comerciante(nome, nave))


def menu_inicial():
    while True:
        opcao = escolher_opcao(
            "Mercante Espacial", ["Novo jogo", "Carregar jogo"], voltar="Sair"
        )
        if opcao == 0:
            return None
        if opcao == 1:
            return novo_jogo()
        try:
            return Jogo.carregar()
        except Exception as erro:
            print(f"Erro: {erro}")


def descrever_planeta(planeta):
    loot = ", ".join(f"{qtd}x {m.get_nome()}" for m, qtd in planeta.get_loot())
    return (
        f"{planeta.get_nome()} | risco {planeta.get_risco()} | "
        f"{len(planeta.criar_inimigos())} inimigos | loot: {loot or 'nenhum'}"
    )


def mostrar_bloqueio(jogo):
    if jogo.final_liberado():
        return
    normais = [p for p in jogo.get_planetas() if not p.eh_final()]
    disponiveis = [p for p in jogo.planetas_disponiveis() if not p.eh_final()]
    faltam = PLANETAS_PARA_FINAL - (len(normais) - len(disponiveis))
    final = next(p for p in jogo.get_planetas() if p.eh_final())
    print(f"\n{final.get_nome()} está bloqueado: conquiste mais {faltam} planeta(s).")


def escolher_e_batalhar(jogo):
    planetas = jogo.planetas_disponiveis()
    mostrar_bloqueio(jogo)
    opcao = escolher_opcao(
        "Mapa da galáxia",
        [descrever_planeta(p) for p in planetas],
        voltar="Voltar",
    )
    if opcao == 0:
        return
    jogo.escolher_planeta(planetas[opcao - 1])
    batalhar(jogo)
    if jogo.verificar_fim() is None:
        print("\nVocê segue para o comércio.")
        comercio(jogo)


def batalhar(jogo):
    nave = jogo.jogador.nave
    print(f"\nVocê chegou a {jogo.planeta_atual().get_nome()}!")
    while jogo.planeta_atual() is not None and jogo.verificar_fim() is None:
        print(
            f"\nSua nave: vida {nave.get_vida()}/{nave.get_vida_max()} "
            f"| ataque {nave.get_ataque()}"
        )
        print(f"Inimigo: {jogo.inimigo_atual()}")
        opcao = escolher_opcao("Sua ação", ["Atacar", "Defender"])
        try:
            mensagens = jogo.turno_batalha("atacar" if opcao == 1 else "defender")
        except Exception as erro:
            print(f"Erro: {erro}")
            continue
        for mensagem in mensagens:
            print(mensagem)


def comercio(jogo):
    jogador = jogo.jogador
    acoes = {
        1: vender_tudo,
        2: vender_item,
        3: melhorar_nave,
        4: reparar_nave,
    }
    while True:
        print(f"\nCréditos: {jogador.get_creditos()}")
        print(f"Nave: {jogador.nave}")
        opcao = escolher_opcao(
            "Comércio",
            [
                "Vender toda a carga",
                "Vender um item",
                "Melhorar a nave",
                f"Reparar a nave ({CUSTO_REPARO} créditos por ponto de vida)",
            ],
            voltar="Voltar ao menu",
        )
        if opcao == 0:
            return
        try:
            acoes[opcao](jogador)
        except Exception as erro:
            print(f"Erro: {erro}")


def vender_tudo(jogador):
    ganho = jogador.vender_tudo()
    if ganho == 0:
        print("Seu porão está vazio.")
    else:
        print(f"Você vendeu toda a carga e recebeu {ganho} créditos.")


def vender_item(jogador):
    carga = jogador.nave.listar_carga()
    if not carga:
        print("Seu porão está vazio.")
        return
    valores = {m.get_nome(): m.get_valor() for m in jogador.nave.get_carga()}
    nomes = list(carga)
    opcao = escolher_opcao(
        "O que vender?",
        [f"{n} - {carga[n]} un. a {valores[n]} créditos cada" for n in nomes],
        voltar="Cancelar",
    )
    if opcao == 0:
        return
    nome = nomes[opcao - 1]
    qtd = ler_inteiro(f"Quantidade (1 a {carga[nome]}): ", 1, carga[nome])
    ganho = jogador.vender(nome, qtd)
    print(f"Você vendeu {qtd}x {nome} e recebeu {ganho} créditos.")


def melhorar_nave(jogador):
    tipos = list(UPGRADES)
    opcao = escolher_opcao(
        "Qual melhoria?",
        [
            f"{NOMES_UPGRADES[t]} +{UPGRADES[t][1]} - {jogador.custo_upgrade(t)} créditos"
            for t in tipos
        ],
        voltar="Cancelar",
    )
    if opcao == 0:
        return
    custo = jogador.comprar_upgrade(tipos[opcao - 1])
    print(f"Melhoria comprada por {custo} créditos.")


def reparar_nave(jogador):
    qtd = jogador.reparar()
    print(f"Você reparou {qtd} pontos de vida.")


def mostrar_status(jogo):
    print(f"\n{jogo}")


def exportar(jogo):
    jogo.jogador.to_csv()
    jogo.jogador.to_txt()
    print("Histórico exportado em historico.csv e historico.txt.")


def salvar(jogo):
    jogo.salvar()
    print(f"Jogo salvo em {ARQUIVO_SAVE}.")


def mostrar_fim(jogo):
    if jogo.verificar_fim() == "vitoria":
        print("\n=== VITÓRIA ===")
        print("Você derrotou o chefão do Coração do Vazio e salvou a galáxia!")
    else:
        print("\n=== DERROTA ===")
        print("Sua nave foi destruída e a missão chegou ao fim.")
    print(f"Créditos finais: {jogo.jogador.get_creditos()}")
    if confirmar("Deseja exportar o histórico?"):
        try:
            exportar(jogo)
        except Exception as erro:
            print(f"Erro: {erro}")


def jogar(jogo):
    acoes = {
        1: escolher_e_batalhar,
        2: comercio,
        3: mostrar_status,
        4: exportar,
        5: salvar,
    }
    while jogo.verificar_fim() is None:
        opcao = escolher_opcao(
            "Menu principal",
            [
                "Escolher planeta e batalhar",
                "Comércio",
                "Status da nave",
                "Exportar histórico",
                "Salvar jogo",
            ],
            voltar="Sair",
        )
        if opcao == 0:
            if confirmar("Deseja sair? O progresso não salvo será perdido"):
                return
            continue
        try:
            acoes[opcao](jogo)
        except Exception as erro:
            print(f"Erro: {erro}")
    mostrar_fim(jogo)


def main():
    print("=== Mercante Espacial ===")
    jogo = menu_inicial()
    if jogo is None:
        print("Até a próxima!")
        return
    jogar(jogo)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nJogo encerrado.")