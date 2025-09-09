from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox, QWidget, QStyle
from PySide6.QtGui import QAction, QIcon, QCursor
from atividades import carregar_atividades
from config import ICONES_STATUS
import sys
import subprocess
import traceback

class TrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)

        # Evita que app termine sozinho quando a janela "invisível" for fechada
        self.app.setQuitOnLastWindowClosed(False)

        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "Erro", "Nenhum tray disponível no sistema!")
            sys.exit(1)

        # Janela invisível que mantém o app vivo e serve como parent para menus/dialogs
        self.window = QWidget()
        self.window.hide()

        # Escolha de ícone: tenta .ico local -> tema -> fallback do estilo
        icone = QIcon("icone.ico")
        if icone.isNull():
            icone = QIcon.fromTheme("folder")
        if icone.isNull():
            icone = QApplication.style().standardIcon(QStyle.SP_ComputerIcon)

        # Cria o tray
        self.tray = QSystemTrayIcon(icone, parent=self.app)
        self.tray.setToolTip("Gerenciador de Atividades")
        self.tray.setVisible(True)

        # Cria menu com parent para evitar GC e preenche
        self.menu = QMenu(self.window)
        try:
            self.atualizar_menu()
        except Exception:
            print("Erro ao atualizar menu:", traceback.format_exc())

        # Associa menu ao tray (comportamento padrão)
        self.tray.setContextMenu(self.menu)

        # Evento do tray
        self.tray.activated.connect(self.on_tray_activated)

    def atualizar_menu(self):
        self.menu.clear()

        # Itens fixos (passando self.menu como parent)
        sair = QAction("Sair", self.menu)
        sair.triggered.connect(self.app.quit)
        self.menu.addAction(sair)

        config = QAction("Configuração", self.menu)
        config.triggered.connect(self.abrir_configuracao)
        self.menu.addAction(config)

        self.menu.addSeparator()

        # Lista de atividades recursiva
        atividades = carregar_atividades()
        if atividades:
            for at in atividades:
                self.menu.addAction(self.criar_acao_atividade(at))
        else:
            vazio = QAction("(nenhuma atividade encontrada)", self.menu)
            vazio.setEnabled(False)
            self.menu.addAction(vazio)

        # Rodapé
        self.menu.addSeparator()

        atualizar = QAction("Atualizar", self.menu)
        atualizar.triggered.connect(self.atualizar_menu)
        self.menu.addAction(atualizar)

        nova = QAction("Nova", self.menu)
        nova.triggered.connect(self.nova_atividade)
        self.menu.addAction(nova)

    def criar_acao_atividade(self, atividade):
        tipo = atividade.get("tipo", "") or ""
        prefixo = tipo[:2].upper() if tipo else ""
        nome_menu = f"{ICONES_STATUS.get(atividade.get('status',''), '')} {prefixo} {atividade.get('id','')}"
        if atividade.get("requisito"):
            nome_menu += f" - {atividade['requisito']}"

        acao = QAction(nome_menu, self.menu)

        def abrir():
            self.abrir_pasta(atividade.get("caminho", ""))

        acao.triggered.connect(abrir)
        return acao

    def abrir_pasta(self, caminho):
        if not caminho:
            QMessageBox.information(self.window, "Abrir pasta", "Caminho inválido.")
            return
        try:
            # Use lista para evitar problemas com espaços/escaping
            subprocess.Popen(["explorer", caminho])
        except Exception as e:
            QMessageBox.warning(self.window, "Erro", f"Não foi possível abrir a pasta: {e}")

    def abrir_configuracao(self):
        QMessageBox.information(self.window, "Configuração", "Janela de configuração (em desenvolvimento)")

    def nova_atividade(self):
        QMessageBox.information(self.window, "Nova Atividade", "Criar nova atividade (em desenvolvimento)")

    def abrir_gerenciamento(self):
        QMessageBox.information(self.window, "Gerenciamento", "Tela de gerenciamento (em desenvolvimento)")

    def on_tray_activated(self, reason):
        # Duplo-clique
        if reason == QSystemTrayIcon.DoubleClick:
            self.abrir_gerenciamento()
            return

        # Clique direito (Context) ou comportamento que chega como Trigger em alguns ambientes
        if reason in (QSystemTrayIcon.Context, QSystemTrayIcon.Trigger):
            # popup() é não-bloqueante e geralmente mais confiável que exec_()
            self.menu.popup(QCursor.pos())

    def run(self):
        sys.exit(self.app.exec())
