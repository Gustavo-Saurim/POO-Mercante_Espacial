import math
import os
import random
import tkinter as tk
from tkinter import messagebox, simpledialog

from comerciante import CUSTO_REPARO, UPGRADES, Comerciante
from jogo import MULTIPLICADOR_DEFESA, PLANETAS_PARA_FINAL, Jogo
from naves import (
    CAPACIDADE_CARGUEIRO,
    CAPACIDADE_FRAGATA,
    REDUCAO_BLINDAGEM,
    Cargueiro,
    Fragata,
)

LARGURA = 960
ALTURA = 600
PASTA_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
ESCALA_TEMPO = 1.0
ALEATORIO = random.Random()

COR_PAINEL = "#0b1030"
COR_BORDA = "#4aa3ff"
COR_TEXTO = "#ffffff"
COR_DESTAQUE = "#ffcc33"
COR_SUCESSO = "#5dff8f"
COR_ERRO = "#ff5d5d"
COR_BOTAO = "#16224f"
COR_BOTAO_HOVER = "#2a3f8f"
COR_BOTAO_OFF = "#2b2b3a"
COR_RISCO = {
    "baixo": "#5dff8f",
    "medio": "#ffcc33",
    "alto": "#ff8a3d",
    "final": "#e04dff",
}

FONTE = ("Arial", 12)
FONTE_NEGRITO = ("Arial", 12, "bold")
FONTE_PEQUENA = ("Arial", 10)
FONTE_TITULO = ("Arial", 36, "bold")
FONTE_SUBTITULO = ("Arial", 22, "bold")

SPRITE_INIMIGO = {
    "Drone Sucateiro": "drone",
    "Saqueador Novato": "drone",
    "Pirata Espacial": "pirata",
    "Caçador de Recompensas": "pirata",
    "Mineradora Rebelde": "pirata",
    "Predador das Dunas": "pirata",
    "Caçador de Elite": "guardiao",
    "Fragata Sombria": "guardiao",
    "Guardião Antigo": "guardiao",
    "Sentinela do Vazio": "sentinela",
    "Senhor do Vazio": "chefao",
}

POSICOES_PLANETAS = {
    "Terra Nova": (150, 300),
    "Ferrum": (330, 190),
    "Aridia": (500, 330),
    "Nexus": (690, 200),
    "Coração do Vazio": (820, 360),
}

NOMES_UPGRADES = {
    "ataque": "Ataque",
    "casco": "Casco (vida máxima)",
    "carga": "Porão (capacidade)",
}

ATRASOS_EXPLOSAO = [90, 90, 110, 140, 180, 230]

TAMANHOS = {
    "fundos/espaco.png": (960, 600),
    "fundos/batalha.png": (960, 600),
    "naves/cargueiro.png": (192, 192),
    "naves/fragata.png": (192, 192),
    "inimigos/drone.png": (192, 192),
    "inimigos/pirata.png": (192, 192),
    "inimigos/guardiao.png": (192, 192),
    "inimigos/sentinela.png": (192, 192),
    "inimigos/chefao.png": (288, 288),
    "planetas/baixo.png": (128, 128),
    "planetas/medio.png": (128, 128),
    "planetas/alto.png": (128, 128),
    "planetas/final.png": (128, 128),
    "efeitos/explosao.gif": (128, 128),
    "efeitos/escudo.gif": (224, 224),
    "ui/moeda.gif": (48, 48),
}


def planetas_conquistados(jogo):
    normais = [p for p in jogo.get_planetas() if not p.eh_final()]
    disponiveis = [p for p in jogo.planetas_disponiveis() if not p.eh_final()]
    return len(normais) - len(disponiveis)


def texto_bloqueio(jogo):
    if jogo.final_liberado():
        return ""
    faltam = PLANETAS_PARA_FINAL - planetas_conquistados(jogo)
    final = next(p for p in jogo.get_planetas() if p.eh_final())
    return f"{final.get_nome()} está bloqueado: conquiste mais {faltam} planeta(s)."


def descrever_planeta(planeta):
    inimigos = ", ".join(i.get_nome() for i in planeta.criar_inimigos())
    loot = ", ".join(
        f"{qtd}x {m.get_nome()} ({m.get_valor()})" for m, qtd in planeta.get_loot()
    )
    return (
        f"{planeta.get_nome()}  |  risco {planeta.get_risco()}\n"
        f"Inimigos: {inimigos}\n"
        f"Loot: {loot or 'nenhum (planeta final)'}"
    )


def exportar_historico(jogo):
    try:
        jogo.jogador.to_csv()
        jogo.jogador.to_txt()
    except Exception as erro:
        messagebox.showerror("Erro", str(erro))
        return
    messagebox.showinfo(
        "Exportar", "Histórico exportado em historico.csv e historico.txt."
    )


class Imagens:
    def __init__(self):
        self.cache = {}

    def imagem(self, nome, zoom=1):
        chave = (nome, zoom)
        if chave not in self.cache:
            self.cache[chave] = self.__ler(nome, zoom)
        return self.cache[chave]

    def quadros(self, nome, zoom=1):
        chave = ("quadros", nome, zoom)
        if chave not in self.cache:
            self.cache[chave] = self.__ler_quadros(nome, zoom)
        return self.cache[chave]

    def __caminho(self, nome):
        return os.path.join(PASTA_ASSETS, *nome.split("/"))

    def __ampliar(self, imagem, zoom):
        return imagem.zoom(zoom) if zoom > 1 else imagem

    def __substituto(self, nome, zoom):
        largura, altura = TAMANHOS.get(nome, (64, 64))
        imagem = tk.PhotoImage(width=largura, height=altura)
        imagem.put("#101030" if nome.startswith("fundos") else "#4a4a7a", to=(0, 0, largura, altura))
        return self.__ampliar(imagem, zoom)

    def __ler(self, nome, zoom):
        try:
            imagem = tk.PhotoImage(file=self.__caminho(nome))
        except tk.TclError:
            return self.__substituto(nome, zoom)
        return self.__ampliar(imagem, zoom)

    def __ler_quadros(self, nome, zoom):
        quadros = []
        while True:
            try:
                quadro = tk.PhotoImage(
                    file=self.__caminho(nome), format=f"gif -index {len(quadros)}"
                )
            except tk.TclError:
                break
            quadros.append(self.__ampliar(quadro, zoom))
        return quadros or [self.__substituto(nome, zoom)]


class Sprite:
    def __init__(self, tela, imagem, x, y, amplitude=5, periodo=2.4, fase=0.0):
        self.canvas = tela.canvas
        self.x = x
        self.y = y
        self.amplitude = amplitude
        self.periodo = periodo
        self.fase = fase
        self.tempo = 0.0
        self.tremor = 0
        self.piscar = 0
        self.seguidores = []
        self.item = self.canvas.create_image(x, y, image=imagem)
        tela.sprites.append(self)

    def atualizar(self, dt):
        self.tempo += dt
        dy = self.amplitude * math.sin(2 * math.pi * self.tempo / self.periodo + self.fase)
        dx = 0
        if self.tremor > 0:
            dx = ALEATORIO.randint(-7, 7)
            self.tremor -= 1
        for item in [self.item] + self.seguidores:
            self.canvas.coords(item, self.x + dx, self.y + dy)
        if self.piscar > 0:
            self.piscar -= 1
            estado = "hidden" if self.piscar % 4 < 2 and self.piscar > 0 else "normal"
            self.canvas.itemconfigure(self.item, state=estado)

    def esconder(self):
        self.canvas.itemconfigure(self.item, state="hidden")
        self.piscar = 0


class Animacao:
    def __init__(self, tela, x, y, quadros, atrasos, repetir=False, ao_fim=None):
        self.tela = tela
        self.canvas = tela.canvas
        self.quadros = quadros
        self.atrasos = atrasos
        self.repetir = repetir
        self.ao_fim = ao_fim
        self.ativa = True
        self.item = self.canvas.create_image(x, y, image=quadros[0])
        self.__passo(0)

    def __passo(self, indice):
        if not self.ativa or not self.tela.ativa:
            return
        if indice >= len(self.quadros):
            if self.repetir:
                indice = 0
            else:
                self.parar()
                if self.ao_fim:
                    self.ao_fim()
                return
        self.canvas.itemconfigure(self.item, image=self.quadros[indice])
        self.tela.agendar(self.atrasos[indice % len(self.atrasos)], self.__passo, indice + 1)

    def parar(self):
        self.ativa = False
        self.canvas.delete(self.item)


class BotaoCanvas:
    def __init__(self, tela, x, y, texto, comando, largura=260, altura=44, fonte=FONTE_NEGRITO):
        self.tela = tela
        self.canvas = tela.canvas
        self.comando = comando
        self.ativo = True
        self.texto = texto
        self.retangulo = self.canvas.create_rectangle(
            x - largura / 2, y - altura / 2, x + largura / 2, y + altura / 2,
            fill=COR_BOTAO, outline=COR_BORDA, width=2,
        )
        self.rotulo = self.canvas.create_text(
            x, y, text=texto, fill=COR_TEXTO, font=fonte, width=largura - 16, justify="center"
        )
        for item in (self.retangulo, self.rotulo):
            self.canvas.tag_bind(item, "<Enter>", self.__entrar)
            self.canvas.tag_bind(item, "<Leave>", self.__sair)
            self.canvas.tag_bind(item, "<Button-1>", self.__clicar)
        tela.botoes.append(self)

    def __entrar(self, evento):
        if self.ativo:
            self.canvas.itemconfigure(self.retangulo, fill=COR_BOTAO_HOVER)
            self.canvas.config(cursor="hand2")

    def __sair(self, evento):
        if self.ativo:
            self.canvas.itemconfigure(self.retangulo, fill=COR_BOTAO)
        self.canvas.config(cursor="")

    def __clicar(self, evento):
        if self.ativo:
            self.comando()

    def definir_ativo(self, ativo):
        self.ativo = ativo
        self.canvas.itemconfigure(self.retangulo, fill=COR_BOTAO if ativo else COR_BOTAO_OFF)
        self.canvas.itemconfigure(self.rotulo, fill=COR_TEXTO if ativo else "#8a8aa0")

    def definir_visivel(self, visivel):
        estado = "normal" if visivel else "hidden"
        self.canvas.itemconfigure(self.retangulo, state=estado)
        self.canvas.itemconfigure(self.rotulo, state=estado)
        self.ativo = visivel


class Barra:
    def __init__(self, canvas, x, y, largura, altura):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        canvas.create_rectangle(x, y, x + largura, y + altura, fill="#1b1b2b", outline="#8aa0d0")
        self.barra = canvas.create_rectangle(x, y, x + largura, y + altura, fill=COR_SUCESSO, width=0)

    def definir(self, fracao):
        fracao = max(0.0, min(1.0, fracao))
        cor = COR_SUCESSO if fracao > 0.5 else COR_DESTAQUE if fracao > 0.25 else COR_ERRO
        self.canvas.coords(
            self.barra, self.x, self.y, self.x + self.largura * fracao, self.y + self.altura
        )
        self.canvas.itemconfigure(self.barra, fill=cor)


class Tela(tk.Frame):
    def __init__(self, app, fundo="fundos/espaco.png"):
        super().__init__(app, width=LARGURA, height=ALTURA)
        self.app = app
        self.imagens = app.imagens
        self.ativa = True
        self.agendados = set()
        self.botoes = []
        self.sprites = []
        self.canvas = tk.Canvas(self, width=LARGURA, height=ALTURA, highlightthickness=0, bd=0)
        self.canvas.pack()
        self.canvas.create_image(0, 0, image=self.imagens.imagem(fundo), anchor="nw")
        self.agendar(40, self.__tick)

    @property
    def jogo(self):
        return self.app.jogo

    def agendar(self, ms, funcao, *args):
        if not self.ativa:
            return None
        identificador = None

        def executar():
            self.agendados.discard(identificador)
            if self.ativa:
                funcao(*args)

        identificador = self.after(max(1, int(ms * ESCALA_TEMPO)), executar)
        self.agendados.add(identificador)
        return identificador

    def destroy(self):
        self.ativa = False
        for identificador in list(self.agendados):
            try:
                self.after_cancel(identificador)
            except tk.TclError:
                pass
        self.agendados.clear()
        super().destroy()

    def __tick(self):
        for sprite in self.sprites:
            sprite.atualizar(0.04)
        self.agendar(40, self.__tick)

    def texto(self, x, y, texto, fonte=FONTE, cor=COR_TEXTO, ancora="center", largura=0):
        return self.canvas.create_text(
            x, y, text=texto, font=fonte, fill=cor, anchor=ancora, width=largura, justify="left" if ancora == "w" else "center"
        )

    def titulo(self, texto, y=70, fonte=FONTE_TITULO, cor=COR_DESTAQUE):
        self.canvas.create_text(LARGURA / 2 + 3, y + 3, text=texto, font=fonte, fill="black")
        return self.canvas.create_text(LARGURA / 2, y, text=texto, font=fonte, fill=cor)

    def painel(self, x1, y1, x2, y2):
        return self.canvas.create_rectangle(x1, y1, x2, y2, fill=COR_PAINEL, outline=COR_BORDA, width=2)

    def botao(self, x, y, texto, comando, largura=260, altura=44, fonte=FONTE_NEGRITO):
        return BotaoCanvas(self, x, y, texto, comando, largura, altura, fonte)

    def moeda(self, x, y):
        return Animacao(self, x, y, self.imagens.quadros("ui/moeda.gif"), [110], repetir=True)

    def sprite(self, nome, x, y, **opcoes):
        return Sprite(self, self.imagens.imagem(nome), x, y, **opcoes)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mercante Espacial")
        self.resizable(False, False)
        self.geometry(f"{LARGURA}x{ALTURA}")
        self.imagens = Imagens()
        self.jogo = None
        self.tela = None
        self.troca_pendente = None
        self.mostrar(TelaMenu)

    def mostrar(self, classe_tela, *args):
        # A troca de tela é feita fora do evento que a pediu (clique, tecla):
        # destruir o canvas dentro do próprio callback de evento pode travar
        # ou derrubar o Tk. Cliques repetidos antes da troca são ignorados.
        if self.troca_pendente is not None:
            return
        self.troca_pendente = self.after_idle(self.__trocar_tela, classe_tela, args)

    def __trocar_tela(self, classe_tela, args):
        self.troca_pendente = None
        if self.tela is not None:
            self.tela.destroy()
            self.tela = None
        self.config(cursor="")
        self.tela = classe_tela(self, *args)
        self.tela.pack()


class TelaMenu(Tela):
    def __init__(self, app):
        super().__init__(app)
        self.titulo("MERCANTE ESPACIAL", 95)
        self.texto(LARGURA / 2, 150, "Aventura e comércio entre as estrelas", ("Arial", 14, "italic"), "#bcd4ff")
        self.sprite("naves/cargueiro.png", 160, 470, fase=0.0)
        self.sprite("naves/fragata.png", 800, 470, fase=2.0)
        self.botao(LARGURA / 2, 270, "Novo jogo", lambda: app.mostrar(TelaNovoJogo), 300, 50)
        self.botao(LARGURA / 2, 340, "Carregar jogo", self.carregar, 300, 50)
        self.botao(LARGURA / 2, 410, "Sair", app.destroy, 300, 50)

    def carregar(self):
        try:
            self.app.jogo = Jogo.carregar()
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))
            return
        self.app.mostrar(TelaPrincipal)


class TelaNovoJogo(Tela):
    def __init__(self, app):
        super().__init__(app)
        self.titulo("Novo jogo", 50, ("Arial", 28, "bold"))
        self.texto(LARGURA / 2, 105, "Nome do comandante", FONTE_NEGRITO)
        self.nome = tk.Entry(self, font=("Arial", 14), width=26, justify="center")
        self.canvas.create_window(LARGURA / 2, 140, window=self.nome)
        self.nome.focus_set()
        self.nome.bind("<Return>", lambda evento: self.comecar())
        self.escolha = 1
        self.cartoes = {}
        naves = [
            (1, "Cargueiro", "naves/cargueiro.png", 270,
             f"Vida {Cargueiro().get_vida()}  |  Porão {CAPACIDADE_CARGUEIRO}",
             "Casco reforçado, sem blindagem"),
            (2, "Fragata", "naves/fragata.png", 690,
             f"Vida {Fragata().get_vida()}  |  Porão {CAPACIDADE_FRAGATA}",
             f"Blindagem: {REDUCAO_BLINDAGEM:.0%} menos dano"),
        ]
        for valor, nome, imagem, x, linha1, linha2 in naves:
            retangulo = self.painel(x - 170, 185, x + 170, 465)
            self.cartoes[valor] = retangulo
            itens = [retangulo]
            itens.append(self.sprite(imagem, x, 285, amplitude=4, fase=valor).item)
            itens.append(self.texto(x, 395, nome, FONTE_SUBTITULO))
            itens.append(self.texto(x, 428, linha1, FONTE))
            itens.append(self.texto(x, 450, linha2, FONTE_PEQUENA, "#bcd4ff"))
            for item in itens:
                self.canvas.tag_bind(item, "<Button-1>", lambda evento, v=valor: self.selecionar(v))
        self.selecionar(1)
        self.botao(365, 540, "Começar", self.comecar, 200, 46)
        self.botao(595, 540, "Voltar", lambda: app.mostrar(TelaMenu), 200, 46)

    def selecionar(self, valor):
        self.escolha = valor
        for chave, retangulo in self.cartoes.items():
            selecionado = chave == valor
            self.canvas.itemconfigure(
                retangulo,
                outline=COR_DESTAQUE if selecionado else COR_BORDA,
                width=4 if selecionado else 2,
            )

    def comecar(self):
        nome = self.nome.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "Digite o nome do comandante.")
            return
        nave = Cargueiro() if self.escolha == 1 else Fragata()
        self.app.jogo = Jogo(Comerciante(nome, nave))
        self.app.mostrar(
            TelaPrincipal,
            f"Bem-vindo, {nome}! Conquiste {PLANETAS_PARA_FINAL} planetas para liberar o planeta final.",
        )


class TelaPrincipal(Tela):
    def __init__(self, app, mensagem=""):
        super().__init__(app)
        jogador = self.jogo.jogador
        nave = jogador.nave
        self.titulo("Menu principal", 42, ("Arial", 28, "bold"))
        self.painel(30, 85, 500, 575)
        self.painel(520, 85, 930, 575)
        self.sprite(f"naves/{type(nave).__name__.lower()}.png", 265, 195)
        self.texto(265, 305, f"{jogador.get_nome()}  -  {type(nave).__name__}", FONTE_SUBTITULO)
        barra = Barra(self.canvas, 80, 335, 370, 22)
        barra.definir(nave.get_vida() / nave.get_vida_max())
        self.texto(265, 346, f"Vida {nave.get_vida()}/{nave.get_vida_max()}", FONTE_NEGRITO)
        self.texto(80, 382, f"Ataque: {nave.get_ataque()}", FONTE, ancora="w")
        self.texto(80, 405, f"Porão: {len(nave.get_carga())}/{nave.capacidade_total()}", FONTE, ancora="w")
        self.moeda(100, 440)
        self.texto(130, 440, f"Créditos: {jogador.get_creditos()}", FONTE_NEGRITO, COR_DESTAQUE, "w")
        self.texto(
            80, 477,
            f"Planetas conquistados: {planetas_conquistados(self.jogo)}/{PLANETAS_PARA_FINAL}",
            FONTE, ancora="w",
        )
        bloqueio = texto_bloqueio(self.jogo)
        self.texto(
            80, 502,
            bloqueio or "O planeta final está liberado!",
            FONTE_PEQUENA, COR_ERRO if bloqueio else COR_SUCESSO, "w", 400,
        )
        if mensagem:
            self.texto(265, 550, mensagem, FONTE_PEQUENA, COR_SUCESSO, largura=430)

        acoes = [
            ("Escolher planeta e batalhar", lambda: app.mostrar(TelaMapa)),
            ("Comércio", lambda: app.mostrar(TelaComercio)),
            ("Status da nave", self.status),
            ("Exportar histórico", lambda: exportar_historico(self.jogo)),
            ("Salvar jogo", self.salvar),
            ("Sair", self.sair),
        ]
        for indice, (texto, comando) in enumerate(acoes):
            self.botao(725, 135 + indice * 75, texto, comando, 340, 50)

    def status(self):
        messagebox.showinfo("Status da nave", str(self.jogo))

    def salvar(self):
        try:
            self.jogo.salvar()
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))
            return
        messagebox.showinfo("Salvar", "Jogo salvo em save.pkl.")

    def sair(self):
        if messagebox.askyesno("Sair", "Deseja sair? O progresso não salvo será perdido."):
            self.app.jogo = None
            self.app.mostrar(TelaMenu)


class TelaMapa(Tela):
    def __init__(self, app):
        super().__init__(app)
        jogo = self.jogo
        self.titulo("Mapa da galáxia", 38, ("Arial", 28, "bold"))
        self.texto(
            LARGURA / 2, 78,
            f"Planetas conquistados: {planetas_conquistados(jogo)}/{PLANETAS_PARA_FINAL}",
            FONTE, "#bcd4ff",
        )
        planetas = jogo.get_planetas()
        pontos = [POSICOES_PLANETAS.get(p.get_nome(), (480, 300)) for p in planetas]
        for (x1, y1), (x2, y2) in zip(pontos, pontos[1:]):
            self.canvas.create_line(x1, y1, x2, y2, fill="#5a78c8", width=2, dash=(6, 8))

        self.bloqueio = texto_bloqueio(jogo)
        self.painel(30, 465, 720, 580)
        self.info = self.texto(
            45, 522,
            self.bloqueio or "Passe o mouse sobre um planeta para ver os detalhes. Clique para viajar.",
            FONTE, COR_TEXTO, "w", 660,
        )
        self.botao(830, 522, "Voltar", lambda: app.mostrar(TelaPrincipal), 180, 46)

        disponiveis = jogo.planetas_disponiveis()
        for planeta in planetas:
            x, y = POSICOES_PLANETAS.get(planeta.get_nome(), (480, 300))
            risco = planeta.get_risco()
            imagem = self.imagens.imagem(f"planetas/{risco}.png")
            item = self.canvas.create_image(x, y, image=imagem)
            self.texto(x, y + 82, planeta.get_nome(), FONTE_NEGRITO)
            self.texto(x, y + 100, f"risco {risco}", FONTE_PEQUENA, COR_RISCO[risco])
            if planeta in disponiveis:
                # O anel fica abaixo da imagem e nunca recebe eventos do mouse;
                # se ficasse por cima, mostrá-lo geraria um ciclo infinito de
                # <Enter>/<Leave> na imagem e a janela pararia de responder.
                anel = self.canvas.create_oval(
                    x - 72, y - 72, x + 72, y + 72, outline=COR_DESTAQUE, width=4, state="hidden"
                )
                self.canvas.tag_lower(anel, item)
                self.canvas.tag_bind(item, "<Enter>", lambda e, p=planeta, a=anel: self.entrar(p, a))
                self.canvas.tag_bind(item, "<Leave>", lambda e, a=anel: self.sair(a))
                self.canvas.tag_bind(item, "<Button-1>", lambda e, p=planeta: self.ir(p))
            elif planeta.eh_final():
                self.canvas.create_oval(x - 60, y - 60, x + 60, y + 60, fill="black", stipple="gray50", outline="")
                self.texto(x, y, "BLOQUEADO", FONTE_NEGRITO, COR_ERRO)
            else:
                self.texto(x, y, "CONQUISTADO", FONTE_NEGRITO, COR_SUCESSO)

    def entrar(self, planeta, anel):
        self.canvas.itemconfigure(anel, state="disabled")
        self.canvas.itemconfigure(self.info, text=descrever_planeta(planeta))
        self.canvas.config(cursor="hand2")

    def sair(self, anel):
        self.canvas.itemconfigure(anel, state="hidden")
        self.canvas.itemconfigure(
            self.info,
            text=self.bloqueio or "Passe o mouse sobre um planeta para ver os detalhes. Clique para viajar.",
        )
        self.canvas.config(cursor="")

    def ir(self, planeta):
        if self.jogo.planeta_atual() is not None:
            return
        try:
            self.jogo.escolher_planeta(planeta)
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))
            return
        self.app.mostrar(TelaBatalha)


class TelaBatalha(Tela):
    def __init__(self, app):
        super().__init__(app, "fundos/batalha.png")
        jogo = self.jogo
        nave = jogo.jogador.nave
        planeta = jogo.planeta_atual()
        self.ocupado = False
        self.fim_batalha = False
        self.carregado = False
        self.linhas = []
        self.escudo = None
        self.sprite_inimigo = None
        self.inimigo = None
        self.vida_inimigo_max = 1

        self.canvas.create_text(
            LARGURA / 2 + 2, 118, text=planeta.get_nome(), font=("Arial", 16, "bold"), fill="black"
        )
        self.canvas.create_text(
            LARGURA / 2, 116, text=planeta.get_nome(), font=("Arial", 16, "bold"), fill=COR_RISCO[planeta.get_risco()]
        )

        self.painel(15, 12, 405, 98)
        self.texto(30, 30, type(nave).__name__, FONTE_NEGRITO, ancora="w")
        self.barra_nave = Barra(self.canvas, 30, 48, 360, 16)
        self.texto_nave = self.texto(30, 78, "", FONTE_PEQUENA, "#bcd4ff", "w")
        self.painel(555, 12, 945, 98)
        self.nome_inimigo = self.texto(570, 30, "", FONTE_NEGRITO, ancora="w")
        self.barra_inimigo = Barra(self.canvas, 570, 48, 360, 16)
        self.texto_inimigo = self.texto(570, 78, "", FONTE_PEQUENA, "#bcd4ff", "w")

        self.sprite_nave = self.sprite(f"naves/{type(nave).__name__.lower()}.png", 190, 300)
        self.anel_carga = self.canvas.create_oval(
            85, 195, 295, 405, outline=COR_DESTAQUE, width=3, state="hidden"
        )
        self.texto_carga = self.texto(
            190, 175, f"ATAQUE CARREGADO x{MULTIPLICADOR_DEFESA}", FONTE_NEGRITO, COR_DESTAQUE
        )
        self.canvas.itemconfigure(self.texto_carga, state="hidden")

        self.painel(20, 450, 620, 585)
        self.botao_atacar = self.botao(780, 482, "Atacar", lambda: self.agir("atacar"), 280, 50)
        self.botao_defender = self.botao(780, 545, "Defender", lambda: self.agir("defender"), 280, 50)
        self.botao_continuar = self.botao(780, 515, "Continuar", self.continuar_jogo, 280, 56)
        self.botao_continuar.definir_visivel(False)

        self.mostrar_inimigo()
        self.atualizar_nave()
        self.escrever(f"Você chegou a {planeta.get_nome()}!")

    def atualizar_nave(self):
        nave = self.jogo.jogador.nave
        self.barra_nave.definir(nave.get_vida() / nave.get_vida_max())
        self.canvas.itemconfigure(
            self.texto_nave,
            text=f"vida {nave.get_vida()}/{nave.get_vida_max()}  |  ataque {nave.get_ataque()}",
        )

    def atualizar_inimigo(self):
        if self.inimigo is None:
            return
        vida = self.inimigo.get_vida()
        self.barra_inimigo.definir(vida / self.vida_inimigo_max)
        self.canvas.itemconfigure(
            self.texto_inimigo,
            text=f"vida {vida}/{self.vida_inimigo_max}  |  ataque {self.inimigo.get_ataque()}",
        )

    def mostrar_inimigo(self):
        if self.sprite_inimigo is not None:
            self.sprites.remove(self.sprite_inimigo)
            self.canvas.delete(self.sprite_inimigo.item)
            self.sprite_inimigo = None
        self.inimigo = self.jogo.inimigo_atual()
        if self.inimigo is None:
            return
        self.vida_inimigo_max = self.inimigo.get_vida()
        chave = SPRITE_INIMIGO.get(self.inimigo.get_nome(), "pirata")
        self.sprite_inimigo = self.sprite(f"inimigos/{chave}.png", 770, 300, fase=1.5)
        self.sprite_inimigo.piscar = 12
        self.canvas.itemconfigure(self.nome_inimigo, text=self.inimigo.get_nome())
        self.atualizar_inimigo()

    def escrever(self, texto):
        self.linhas = (self.linhas + [texto])[-5:]
        self.canvas.delete("log")
        for indice, linha in enumerate(self.linhas):
            self.canvas.create_text(
                35, 470 + indice * 24, text=linha, font=FONTE, fill=COR_TEXTO,
                anchor="w", width=570, tags="log",
            )

    def definir_carga(self, carregado):
        self.carregado = carregado
        estado = "normal" if carregado else "hidden"
        self.canvas.itemconfigure(self.anel_carga, state=estado)
        self.canvas.itemconfigure(self.texto_carga, state=estado)

    def sequencia(self, passos, final):
        if not passos:
            final()
            return
        passos[0](lambda: self.sequencia(passos[1:], final))

    def disparar(self, x_origem, x_destino, y, cor, ao_chegar):
        sinal = 1 if x_destino > x_origem else -1
        item = self.canvas.create_line(
            x_origem, y, x_origem + 50 * sinal, y, fill=cor, width=6, capstyle="round"
        )
        passos = 9
        deslocamento = (x_destino - x_origem) / passos

        def passo(i):
            if not self.ativa:
                return
            if i >= passos:
                self.canvas.delete(item)
                ao_chegar()
                return
            self.canvas.move(item, deslocamento, 0)
            self.agendar(28, passo, i + 1)

        passo(0)

    def numero_flutuante(self, x, y, texto, cor, fonte=("Arial", 22, "bold")):
        sombra = self.canvas.create_text(x + 2, y + 2, text=texto, font=fonte, fill="black")
        item = self.canvas.create_text(x, y, text=texto, font=fonte, fill=cor)

        def passo(i):
            if not self.ativa:
                return
            if i >= 18:
                self.canvas.delete(item)
                self.canvas.delete(sombra)
                return
            self.canvas.move(item, 0, -2)
            self.canvas.move(sombra, 0, -2)
            self.agendar(30, passo, i + 1)

        passo(0)

    def passo_tiro(self, origem, destino, cor):
        def executar(proximo):
            sinal = 1 if destino.x > origem.x else -1
            self.disparar(origem.x + 95 * sinal, destino.x - 95 * sinal, origem.y, cor, proximo)
        return executar

    def passo_dano_inimigo(self, dano, inimigo, carregado):
        def executar(proximo):
            alvo = self.sprite_inimigo
            alvo.tremor = 10
            alvo.piscar = 12
            fonte = ("Arial", 30, "bold") if carregado else ("Arial", 22, "bold")
            self.numero_flutuante(alvo.x, alvo.y - 90, f"-{dano}", "#ff8a3d" if carregado else COR_DESTAQUE, fonte)
            self.atualizar_inimigo()
            self.agendar(450, proximo)
        return executar

    def passo_dano_nave(self, dano):
        def executar(proximo):
            self.sprite_nave.tremor = 10
            self.sprite_nave.piscar = 12
            self.numero_flutuante(self.sprite_nave.x, self.sprite_nave.y - 90, f"-{dano}", COR_ERRO)
            self.atualizar_nave()
            self.agendar(450, proximo)
        return executar

    def passo_explodir(self, sprite, zoom, proximo):
        quadros = self.imagens.quadros("efeitos/explosao.gif", zoom)
        Animacao(self, sprite.x, sprite.y, quadros, ATRASOS_EXPLOSAO, ao_fim=lambda: self.agendar(250, proximo))
        self.agendar(260, sprite.esconder)

    def passo_explodir_inimigo(self, proximo):
        zoom = 2 if self.inimigo.get_nome() == "Senhor do Vazio" else 1
        self.passo_explodir(self.sprite_inimigo, zoom, proximo)

    def passo_explodir_nave(self, proximo):
        self.passo_explodir(self.sprite_nave, 2, proximo)

    def passo_escudo_ligar(self, proximo):
        quadros = self.imagens.quadros("efeitos/escudo.gif")
        self.escudo = Animacao(self, self.sprite_nave.x, self.sprite_nave.y, quadros, [190], repetir=True)
        self.canvas.tag_lower(self.escudo.item, self.sprite_nave.item)
        self.sprite_nave.seguidores.append(self.escudo.item)
        self.definir_carga(True)
        self.agendar(450, proximo)

    def passo_escudo_desligar(self, proximo):
        if self.escudo is not None:
            self.sprite_nave.seguidores.remove(self.escudo.item)
            self.escudo.parar()
            self.escudo = None
        proximo()

    def agir(self, acao):
        if self.ocupado or self.fim_batalha:
            return
        jogo = self.jogo
        nave = jogo.jogador.nave
        inimigo = self.inimigo
        vida_inimigo = inimigo.get_vida()
        vida_nave = nave.get_vida()
        carregado = self.carregado
        try:
            mensagens = jogo.turno_batalha(acao)
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))
            return
        dano_dado = vida_inimigo - inimigo.get_vida()
        dano_recebido = vida_nave - nave.get_vida()
        derrotou = not inimigo.esta_vivo()
        defendendo = acao == "defender"

        self.ocupado = True
        self.botao_atacar.definir_ativo(False)
        self.botao_defender.definir_ativo(False)

        passos = []
        if defendendo:
            passos.append(self.passo_escudo_ligar)
        else:
            self.definir_carga(False)
            passos.append(self.passo_tiro(self.sprite_nave, self.sprite_inimigo, "#4de1ff"))
            passos.append(self.passo_dano_inimigo(dano_dado, inimigo, carregado))
            if derrotou:
                passos.append(self.passo_explodir_inimigo)
        if not derrotou:
            passos.append(self.passo_tiro(self.sprite_inimigo, self.sprite_nave, "#ff5b5b"))
            passos.append(self.passo_dano_nave(dano_recebido))
            if not nave.esta_viva():
                passos.append(self.passo_explodir_nave)
        if defendendo:
            passos.append(self.passo_escudo_desligar)
        self.sequencia(passos, lambda: self.fim_turno(mensagens, derrotou))

    def fim_turno(self, mensagens, derrotou):
        for mensagem in mensagens:
            self.escrever(mensagem)
        self.atualizar_nave()
        self.ocupado = False
        jogo = self.jogo
        fim = jogo.verificar_fim()
        if fim is not None:
            self.encerrar()
            return
        if jogo.planeta_atual() is None:
            self.escrever("Você segue para o comércio.")
            self.encerrar()
            return
        if derrotou:
            self.mostrar_inimigo()
        self.botao_atacar.definir_ativo(True)
        self.botao_defender.definir_ativo(True)

    def encerrar(self):
        self.fim_batalha = True
        self.definir_carga(False)
        self.botao_atacar.definir_visivel(False)
        self.botao_defender.definir_visivel(False)
        self.botao_continuar.definir_visivel(True)

    def continuar_jogo(self):
        if self.jogo.verificar_fim() is not None:
            self.app.mostrar(TelaFim)
        else:
            self.app.mostrar(TelaComercio)


class TelaComercio(Tela):
    def __init__(self, app, mensagem=""):
        super().__init__(app)
        jogador = self.jogo.jogador
        nave = jogador.nave
        self.titulo("Comércio", 40, ("Arial", 28, "bold"))
        self.moeda(740, 40)
        self.texto(770, 40, f"Créditos: {jogador.get_creditos()}", FONTE_NEGRITO, COR_DESTAQUE, "w")

        self.painel(25, 80, 290, 575)
        self.sprite(f"naves/{type(nave).__name__.lower()}.png", 157, 185)
        self.texto(157, 295, type(nave).__name__, FONTE_SUBTITULO)
        barra = Barra(self.canvas, 45, 330, 225, 18)
        barra.definir(nave.get_vida() / nave.get_vida_max())
        self.texto(157, 339, f"Vida {nave.get_vida()}/{nave.get_vida_max()}", FONTE_PEQUENA)
        self.texto(45, 375, f"Ataque: {nave.get_ataque()}", FONTE, ancora="w")
        self.texto(45, 400, f"Porão: {len(nave.get_carga())}/{nave.capacidade_total()}", FONTE, ancora="w")

        self.painel(310, 80, 935, 305)
        self.texto(325, 98, "Carga", FONTE_SUBTITULO, ancora="w")
        carga = nave.listar_carga()
        valores = {m.get_nome(): m.get_valor() for m in nave.get_carga()}
        if not carga:
            self.texto(325, 150, "Seu porão está vazio.", FONTE, "#bcd4ff", "w")
        for indice, (nome, qtd) in enumerate(carga.items()):
            y = 138 + indice * 38
            self.texto(325, y, f"{nome}  x{qtd}   ({valores[nome]} créditos cada)", FONTE, ancora="w")
            self.botao(860, y, "Vender...", lambda n=nome, q=qtd: self.vender_item(n, q), 120, 30, FONTE)
        self.botao(622, 282, "Vender toda a carga", self.vender_tudo, 300, 34)

        self.painel(310, 318, 935, 470)
        self.texto(325, 336, "Melhorias", FONTE_SUBTITULO, ancora="w")
        for indice, tipo in enumerate(UPGRADES):
            texto = (
                f"{NOMES_UPGRADES[tipo]}\n+{UPGRADES[tipo][1]}  -  {jogador.custo_upgrade(tipo)} créditos"
            )
            self.botao(
                425 + indice * 205, 390, texto, lambda t=tipo: self.melhorar(t), 190, 60, FONTE
            )
        self.botao(
            622, 445, f"Reparar a nave ({CUSTO_REPARO} créditos por ponto de vida)",
            self.reparar, 420, 34, FONTE,
        )
        if mensagem:
            self.texto(622, 497, mensagem, FONTE_NEGRITO, COR_SUCESSO, largura=600)
        self.botao(622, 545, "Voltar ao menu", lambda: app.mostrar(TelaPrincipal), 280, 42)

    def agir(self, acao, *args, mensagem):
        try:
            resultado = acao(*args)
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))
            return
        self.app.mostrar(TelaComercio, mensagem(resultado))

    def vender_tudo(self):
        self.agir(
            self.jogo.jogador.vender_tudo,
            mensagem=lambda ganho: "Seu porão está vazio."
            if ganho == 0
            else f"Você vendeu toda a carga e recebeu {ganho} créditos.",
        )

    def vender_item(self, nome, disponivel):
        qtd = simpledialog.askinteger(
            "Vender",
            f"Quantidade de {nome} (1 a {disponivel}):",
            minvalue=1,
            maxvalue=disponivel,
            parent=self,
        )
        if qtd is None:
            return
        self.agir(
            self.jogo.jogador.vender,
            nome,
            qtd,
            mensagem=lambda ganho: f"Você vendeu {qtd}x {nome} e recebeu {ganho} créditos.",
        )

    def melhorar(self, tipo):
        self.agir(
            self.jogo.jogador.comprar_upgrade,
            tipo,
            mensagem=lambda custo: f"Melhoria comprada por {custo} créditos.",
        )

    def reparar(self):
        self.agir(
            self.jogo.jogador.reparar,
            mensagem=lambda qtd: f"Você reparou {qtd} pontos de vida.",
        )


class TelaFim(Tela):
    def __init__(self, app):
        super().__init__(app)
        jogador = self.jogo.jogador
        vitoria = self.jogo.verificar_fim() == "vitoria"
        self.titulo("VITÓRIA" if vitoria else "DERROTA", 110, ("Arial", 48, "bold"), COR_DESTAQUE if vitoria else COR_ERRO)
        self.texto(
            LARGURA / 2, 180,
            "Você derrotou o Senhor do Vazio e salvou a galáxia!"
            if vitoria
            else "Sua nave foi destruída e a missão chegou ao fim.",
            ("Arial", 16), COR_TEXTO,
        )
        if vitoria:
            self.sprite(f"naves/{type(jogador.nave).__name__.lower()}.png", 330, 340)
            self.sprite("planetas/baixo.png", 640, 340, amplitude=3)
        else:
            quadros = self.imagens.quadros("efeitos/explosao.gif", 2)
            Animacao(self, LARGURA / 2, 340, quadros, ATRASOS_EXPLOSAO + [600], repetir=True)
        self.moeda(400, 450)
        self.texto(430, 450, f"Créditos finais: {jogador.get_creditos()}", ("Arial", 16, "bold"), COR_DESTAQUE, "w")
        self.botao(330, 535, "Exportar histórico", lambda: exportar_historico(self.jogo), 280, 48)
        self.botao(630, 535, "Voltar ao menu inicial", self.voltar, 280, 48)

    def voltar(self):
        self.app.jogo = None
        self.app.mostrar(TelaMenu)


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
