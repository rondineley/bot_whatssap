import customtkinter as ctk
import tkinter.filedialog as filedialog
from tkcalendar import Calendar
from datetime import datetime
import openpyxl
import webbrowser
import pyautogui
from urllib.parse import quote
import os
from time import sleep

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Painel de Mensagens Futurista")
        self.geometry("1280x720")
        self.caminho_planilha = None
        self.clientes = []
        self.anotacoes = {}

        # Layout
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=15)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        self.main_area = ctk.CTkFrame(self, corner_radius=15)
        self.main_area.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.criar_sidebar()
        self.criar_main_area()

    def criar_sidebar(self):
        ctk.CTkLabel(self.sidebar, text="📅 Calendário", font=("Segoe UI", 18, "bold")).pack(pady=10)
        self.calendario = Calendar(self.sidebar, selectmode="day", background="#1e1e1e",
                                   foreground="white", selectbackground="#00FFAA", font=("Segoe UI", 12))
        self.calendario.pack(pady=10)

        self.botao_planilha = ctk.CTkButton(self.sidebar, text="📁 Selecionar Planilha", command=self.abrir_planilha)
        self.botao_planilha.pack(pady=20)

        self.botao_abrir_excel = ctk.CTkButton(self.sidebar, text="🧾 Abrir no Excel", command=self.abrir_arquivo_excel)
        self.botao_abrir_excel.pack()

    def criar_main_area(self):
        self.label_planilha = ctk.CTkLabel(self.main_area, text="Nenhuma planilha carregada", font=("Segoe UI", 16))
        self.label_planilha.pack(pady=10)

        self.texto_mensagem = ctk.CTkTextbox(self.main_area, height=100, font=("Segoe UI", 14))
        self.texto_mensagem.pack(padx=20, pady=10, fill="x")

        self.botao_enviar = ctk.CTkButton(self.main_area, text="🚀 Enviar Mensagens", height=40, command=self.enviar_mensagens)
        self.botao_enviar.pack(pady=10)

        self.tree = ctk.CTkFrame(self.main_area)
        self.tree.pack(expand=True, fill="both", padx=20, pady=10)

        self.listagem = ctk.CTkLabel(self.tree, text="Clientes aparecerão aqui após carregar a planilha.", font=("Segoe UI", 12))
        self.listagem.pack(pady=10)

        self.label_status = ctk.CTkLabel(self.main_area, text="", font=("Segoe UI", 14))
        self.label_status.pack(pady=5)

    def abrir_planilha(self):
        self.caminho_planilha = filedialog.askopenfilename(
            title="Selecione a planilha de clientes",
            filetypes=[("Arquivos Excel", "*.xlsx")]
        )
        if self.caminho_planilha:
            nome_arquivo = os.path.basename(self.caminho_planilha)
            self.label_planilha.configure(text=f"Planilha: {nome_arquivo}")
            self.exibir_planilha()

    def abrir_arquivo_excel(self):
        if self.caminho_planilha:
            os.startfile(self.caminho_planilha)

    def exibir_planilha(self):
        try:
            workbook = openpyxl.load_workbook(self.caminho_planilha)
            sheet = workbook.active
            self.clientes.clear()

            for row in sheet.iter_rows(min_row=2):
                nome = row[0].value
                telefone = row[1].value
                vencimento = row[2].value

                if not nome or not telefone:
                    continue

                if isinstance(vencimento, str):
                    try:
                        vencimento = datetime.strptime(vencimento, "%d/%m/%Y")
                    except:
                        pass

                self.clientes.append((nome, telefone, vencimento))

            texto = "\n".join([
                f"{nome} | {telefone} | {vencimento.strftime('%d/%m/%Y') if isinstance(vencimento, datetime) else vencimento}"
                for nome, telefone, vencimento in self.clientes
            ])
            self.listagem.configure(text=texto)

        except Exception as e:
            self.listagem.configure(text=f"Erro: {e}")

    def enviar_mensagens(self):
        if not self.caminho_planilha or not self.clientes:
            return

        mensagem_base = self.texto_mensagem.get("1.0", "end-1c").strip()
        if not mensagem_base:
            return

        erros = []
        enviados = 0

        for idx, (nome, telefone, vencimento) in enumerate(self.clientes):
            try:
                venc_formatado = vencimento.strftime('%d/%m/%Y') if isinstance(vencimento, datetime) else str(vencimento)
                mensagem = mensagem_base.replace("{nome}", nome).replace("{vencimento}", venc_formatado)

                link = f"https://web.whatsapp.com/send?phone={telefone}&text={quote(mensagem)}"
                webbrowser.open(link)
                sleep(8)

                pyautogui.press("enter")
                sleep(5)
                pyautogui.hotkey("ctrl", "w")
                sleep(2)

                enviados += 1

                if vencimento not in self.anotacoes:
                    self.anotacoes[vencimento] = []
                self.anotacoes[vencimento].append(f"{nome} ({telefone})")
                self.calendario.calevent_create(vencimento, f"{nome}", "msg")

            except Exception as e:
                erros.append(f"{nome} ({telefone}): {e}")

        # Mostrar o status final na tela
        if erros:
            texto = f"⚠️ Mensagens enviadas com erros:\n" + "\n".join(erros)
        else:
            texto = f"✅ Todas as {enviados} mensagens foram enviadas com sucesso."

        self.label_status.configure(text=texto)

if __name__ == "__main__":
    app = App()
    app.mainloop()
