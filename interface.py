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