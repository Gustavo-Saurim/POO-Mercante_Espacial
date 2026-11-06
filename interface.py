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

class TelaMapa(Tela):
    def __init__(self, app):
        super().__init__(app)
        self.titulo("Mapa da galáxia")
        bloqueio = texto_bloqueio(self.jogo)
        if bloqueio:
            self.texto(bloqueio)
        tk.Label(self).pack()
        for planeta in self.jogo.planetas_disponiveis():
            self.botao(
                descrever_planeta(planeta),
                lambda p=planeta: self.ir(p),
                largura=85,
            )
        tk.Label(self).pack()
        self.botao("Voltar", lambda: app.mostrar(TelaPrincipal))
 
    def ir(self, planeta):
        try:
            self.jogo.escolher_planeta(planeta)
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))
            return
        self.app.mostrar(TelaBatalha)

class TelaBatalha(Tela):
    def __init__(self, app):
        super().__init__(app)
        self.titulo(f"Batalha em {self.jogo.planeta_atual().get_nome()}")
        self.rotulo_nave = self.texto("")
        self.rotulo_inimigo = self.texto("")
        acoes = tk.Frame(self)
        acoes.pack(pady=8)
        self.atacar = self.botao(
            "Atacar", lambda: self.agir("atacar"), largura=20, pai=acoes
        )
        self.atacar.pack(side="left", padx=6)
        self.defender = self.botao(
            "Defender", lambda: self.agir("defender"), largura=20, pai=acoes
        )
        self.defender.pack(side="left", padx=6)
        self.log = tk.Text(self, height=16, width=95, font=FONTE_LOG, state="disabled")
        self.log.pack(pady=8)
        self.continuar = self.botao(
            "Continuar", self.continuar_jogo, largura=20
        )
        self.continuar.config(state="disabled")
        self.escrever(f"Você chegou a {self.jogo.planeta_atual().get_nome()}!")
        self.atualizar()
 
    def atualizar(self):
        nave = self.jogo.jogador.nave
        self.rotulo_nave.config(
            text=f"Sua nave: vida {nave.get_vida()}/{nave.get_vida_max()} "
            f"| ataque {nave.get_ataque()}"
        )
        inimigo = self.jogo.inimigo_atual()
        self.rotulo_inimigo.config(text=f"Inimigo: {inimigo}" if inimigo else "")
 
    def escrever(self, texto):
        self.log.config(state="normal")
        self.log.insert("end", texto + "\n")
        self.log.see("end")
        self.log.config(state="disabled")
 
    def agir(self, acao):
        try:
            mensagens = self.jogo.turno_batalha(acao)
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))
            return
        for mensagem in mensagens:
            self.escrever(mensagem)
        self.atualizar()
        if self.jogo.planeta_atual() is None or self.jogo.verificar_fim() is not None:
            self.encerrar()
 
    def encerrar(self):
        self.atacar.config(state="disabled")
        self.defender.config(state="disabled")
        self.continuar.config(state="normal")
        if self.jogo.verificar_fim() is None:
            self.escrever("Você segue para o comércio.")
 
    def continuar_jogo(self):
        if self.jogo.verificar_fim() is not None:
            self.app.mostrar(TelaFim)
        else:
            self.app.mostrar(TelaComercio)

class TelaComercio(Tela):
    def __init__(self, app, mensagem=""):
        super().__init__(app)
        jogador = self.jogo.jogador
        self.titulo("Comércio")
        self.texto(f"Créditos: {jogador.get_creditos()}")
        self.texto(f"Nave: {jogador.nave}")
        self.texto(mensagem, fg=COR_SUCESSO)
 
        self.botao("Vender toda a carga", self.vender_tudo)
        self.texto("Carga:")
        carga = jogador.nave.listar_carga()
        if not carga:
            self.texto("Seu porão está vazio.")
        valores = {m.get_nome(): m.get_valor() for m in jogador.nave.get_carga()}
        for nome, qtd in carga.items():
            linha = tk.Frame(self)
            linha.pack(anchor="w")
            tk.Label(
                linha,
                text=f"{nome} - {qtd} un. a {valores[nome]} créditos cada",
                font=FONTE,
                width=50,
                anchor="w",
            ).pack(side="left")
            tk.Button(
                linha,
                text="Vender...",
                font=FONTE,
                command=lambda n=nome, q=qtd: self.vender_item(n, q),
            ).pack(side="left")
 
        self.texto("Melhorias:")
        for tipo in UPGRADES:
            self.botao(
                f"{NOMES_UPGRADES[tipo]} +{UPGRADES[tipo][1]} - "
                f"{jogador.custo_upgrade(tipo)} créditos",
                lambda t=tipo: self.melhorar(t),
            )
        self.botao(
            f"Reparar a nave ({CUSTO_REPARO} créditos por ponto de vida)",
            self.reparar,
        )
        self.botao("Voltar ao menu", lambda: app.mostrar(TelaPrincipal))
 
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
        vitoria = self.jogo.verificar_fim() == "vitoria"
        self.titulo("VITÓRIA" if vitoria else "DERROTA")
        self.texto(
            "Você derrotou o chefão do Coração do Vazio e salvou a galáxia!"
            if vitoria
            else "Sua nave foi destruída e a missão chegou ao fim."
        )
        self.texto(f"Créditos finais: {self.jogo.jogador.get_creditos()}")
        tk.Label(self).pack()
        self.botao("Exportar histórico", lambda: exportar_historico(self.jogo))
        self.botao("Voltar ao menu inicial", self.voltar)
 
    def voltar(self):
        self.app.jogo = None
        self.app.mostrar(TelaMenu)

def main():
    App().mainloop()

if __name__ == "__main__":
    main()