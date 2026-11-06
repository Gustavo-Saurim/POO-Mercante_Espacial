import tkinter as tk
from tkinter import messagebox, simpledialog

from comerciante import CUSTO_REPARO, UPGRADES, Comerciante
from jogo import ARQUIVO_SAVE, PLANETAS_PARA_FINAL, Jogo
from naves import (
    CAPACIDADE_CARGUEIRO,
    CAPACIDADE_FRAGATA,
    REDUCAO_BLINDAGEM,
    Cargueiro,
    Fragata,
)

FONTE = ("Arial", 11)
FONTE_TITULO = ("Arial", 20, "bold")
FONTE_LOG = ("Courier", 10)
COR_SUCESSO = "#0a6b2d"

NOMES_UPGRADES = {
    "ataque": "Ataque",
    "casco": "Casco (vida máxima)",
    "carga": "Porão (capacidade)",
}

def descrever_planeta(planeta):
    loot = ", ".join(f"{qtd}x {m.get_nome()}" for m, qtd in planeta.get_loot())
    return (
        f"{planeta.get_nome()} | risco {planeta.get_risco()} | "
        f"{len(planeta.criar_inimigos())} inimigos | loot: {loot or 'nenhum'}"
    )

def texto_bloqueio(jogo):
    if jogo.final_liberado():
        return ""
    normais = [p for p in jogo.get_planetas() if not p.eh_final()]
    disponiveis = [p for p in jogo.planetas_disponiveis() if not p.eh_final()]
    faltam = PLANETAS_PARA_FINAL - (len(normais) - len(disponiveis))
    final = next(p for p in jogo.get_planetas() if p.eh_final())
    return f"{final.get_nome()} esta bloqueado: conquiste mais {faltam} planeta(s)."

def exportar_historico(jogo):
    try:
        jogo.jogador.to_csv()
        jogo.jogador.to_txt()
    except Exception as erro:
        messagebox.showerror("Erro", str(erro))
        return
    messagebox.showinfo("Exportar", "Historico exportado em historico.csv e historico.txt.")

class Tela(tk,Frame):
    def __int__(self, app):
        super().__init__(app, padx=20, pady=20)
        self.app = app

    @property
    def jogo(self):
        return self.app.jogo

    def titulo(self, texto):
        tk.Label(self, text=texto, font=FONTE_TITULO).pack(pady=(0, 12))

    def texto(self, texto, **opcoes):
        rotulo = tk.Label(
            self, text=texto, font=FONTE, justify="left", wraplength=820, **opcoes
        )
        rotulo.pack(anchor="w", pady=2)
        return rotulo

    def botao(self, texto, comando, largura=50, pai=None):
        botao = tk.Button(
            pai or self, text=texto, command=comando, font=FONTE, width=largura
        )
        botao.pack(pady=3)
        return botao

class App(tk.Tk):
    def __int__(self):
        super().__init__()
        self.title("Mercante Espacial")
        self.geometry("900x720")
        self.jogo = None
        self.tela = None
        self.mostrar(TelaMenu)
    def mostrar(self, classe_tela, *args):
        if self.tela is not None:
            self.tela.destroy()
        self.tela = classe_tela(self, *args)
        self.tela.pack(fill="both", expand=True)

class TelaMenu(Tela):
    def __init__(self, app):
        super().__init__(app)
        self.titulo("Mercante Espacial")
        self.botao("Novo jogo", lambda: app.mostrar(TelaNovoJogo))
        self.botao("Carregar jogo", self.carregar)
        self.botao("Sair", app.destroy)

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
        self.titulo("Novo jogo")
        self.texto("Nome do comandante:")
        self.nome = tk.StringVar()
        tk.Entry(self, textvariable=self.nome, font=FONTE, width=30).pack(
            anchor="w", pady=(0, 10)
        )
        self.texto("Escolha sua nave:")
        self.nave = tk.IntVar(value=1)
        opcoes = [
            (
                1,
                f"Cargueiro - porão de {CAPACIDADE_CARGUEIRO} unidades, "
                f"{Cargueiro().get_vida()} de vida inicial, sem blindagem",
            ),
            (
                2,
                f"Fragata - porão de {CAPACIDADE_FRAGATA} unidades, "
                f"blindagem de {REDUCAO_BLINDAGEM:.0%}",
            ),
        ]
        for valor, texto in opcoes:
            tk.Radiobutton(
                self, text=texto, variable=self.nave, value=valor, font=FONTE
            ).pack(anchor="w")
        tk.Label(self).pack()
        self.botao("Começar", self.comecar)
        self.botao("Voltar", lambda: app.mostrar(TelaMenu))

    def comecar(self):
        nome = self.nome.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "Digite o nome do comandante.")
            return
        nave = Cargueiro() if self.nave.get() == 1 else Fragata()
        self.app.jogo = Jogo(Comerciante(nome, nave))
        messagebox.showinfo(
            "Bem-vindo",
            f"Bem-vindo, {nome}! Conquiste {PLANETAS_PARA_FINAL} planetas "
            "para liberar o planeta final.",
        )
        self.app.mostrar(TelaPrincipal)


class TelaPrincipal(Tela):
    def __init__(self, app):
        super().__init__(app)
        self.titulo("Menu principal")
        self.texto(str(self.jogo))
        tk.Label(self).pack()
        self.botao("Escolher planeta e batalhar", lambda: app.mostrar(TelaMapa))
        self.botao("Comércio", lambda: app.mostrar(TelaComercio))
        self.botao("Status da nave", self.status)
        self.botao("Exportar histórico", lambda: exportar_historico(self.jogo))
        self.botao("Salvar jogo", self.salvar)
        self.botao("Sair", self.sair)

    def status(self):
        messagebox.showinfo("Status da nave", str(self.jogo))

    def salvar(self):
        try:
            self.jogo.salvar()
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))
            return
        messagebox.showinfo("Salvar", f"Jogo salvo em {ARQUIVO_SAVE}.")

    def sair(self):
        if messagebox.askyesno(
            "Sair", "Deseja sair? O progresso não salvo será perdido."
        ):
            self.app.jogo = None
            self.app.mostrar(TelaMenu)