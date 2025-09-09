from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox, QWidget, QStyle
from PySide6.QtGui import QAction, QIcon, QCursor
from atividades import carregar_atividades
from config import ICONES_STATUS, ConfigWindow
from nova_atividade import NovaAtividadeWindow
from controle_atividades import ControleAtividadesWindow
import sys
import subprocess
import traceback

class TrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "Erro", "Nenhum tray disponível no sistema!")
            sys.exit(1)

        # Janela invisível
        self.window = QWidget()
        self.window.hide()

        # Ícone
        icone = QIcon("icone.ico")
        if icone.isNull():
            icone = QIcon.fromTheme("folder")
        if icone.isNull():
            icone = QApplication.style().standardIcon(QStyle.SP_ComputerIcon)

        # Tray
        self.tray = QSystemTrayIcon(icone, parent=self.app)
        self.tray.setToolTip("Gerenciador de Atividades")
        self.tray.setVisible(True)

        # Menu
        self.menu = QMenu(self.window)

        # Config window
        self.config_window = None

        try:
            self.atualizar_menu()
        except Exception:
            print("Erro ao atualizar menu:", traceback.format_exc())

        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self.on_tray_activated)

    def atualizar_menu(self):
        self.menu.clear()

        # Itens fixos
        self.exit_action = QAction("Sair", self.menu)
        self.exit_action.triggered.connect(self.exit_app)
        self.menu.addAction(self.exit_action)

        self.config_action = QAction("Configurações", self.menu)
        self.config_action.triggered.connect(self.open_config)
        self.menu.addAction(self.config_action)

        self.menu.addSeparator()

        # Lista de atividades da pasta atual configurada
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
        atualizar.triggered.connect(self.atualizar_menu)  # chama recarregando as atividades
        self.menu.addAction(atualizar)

        nova = QAction("Nova", self.menu)
        nova.triggered.connect(self.nova_atividade)
        self.menu.addAction(nova)

    def criar_acao_atividade(self, atividade):
        tipo = atividade.get("tipo", "") or ""
        prefixo = tipo[:2].upper() if tipo else ""
        nome_menu = f"{ICONES_STATUS.get(atividade.get('status',''), '')} {prefixo} {atividade.get('id','')}".strip()
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
            subprocess.Popen(["explorer", caminho])
        except Exception as e:
            QMessageBox.warning(self.window, "Erro", f"Não foi possível abrir a pasta: {e}")

    def open_config(self):
        if self.config_window is None:
            self.config_window = ConfigWindow()
        self.config_window.show()
        self.config_window.raise_()
        self.config_window.activateWindow()

    def exit_app(self):
        try:
            self.tray.hide()
        except Exception:
            pass
        self.app.quit()

    def nova_atividade(self):
        self.nova_window = NovaAtividadeWindow()
        self.nova_window.show()

    def abrir_gerenciamento(self):
        self.gerenciamento_window = ControleAtividadesWindow()
        self.gerenciamento_window.show()
        self.gerenciamento_window.raise_()
        self.gerenciamento_window.activateWindow()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.abrir_gerenciamento()
            return

        if reason in (QSystemTrayIcon.Context, QSystemTrayIcon.Trigger):
            self.menu.popup(QCursor.pos())

    def run(self):
        sys.exit(self.app.exec())
