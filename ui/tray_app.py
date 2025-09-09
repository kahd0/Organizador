import sys
import traceback
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox, QWidget, QStyle
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt

from storage import carregar_atividades
from config import ICONES_STATUS
from ui.gui_utils import show_and_raise
from utils.fs import open_folder

from ui.windows.config_window import ConfigWindow
from ui.windows.nova_atividade import NovaAtividadeWindow
from ui.windows.controle_atividades import ControleAtividadesWindow


class TrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "Erro", "Nenhum tray disponível no sistema!")
            sys.exit(1)

        # Janela invisível (parent para menus)
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

        # Janelas (reuso de instâncias)
        self.config_window: ConfigWindow | None = None
        self.nova_window: NovaAtividadeWindow | None = None
        self.gerenciamento_window: ControleAtividadesWindow | None = None

        try:
            self.atualizar_menu()
        except Exception:
            print("Erro ao atualizar menu:", traceback.format_exc())

        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self.on_tray_activated)

    # ---------- ações de janelas ----------
    def open_config(self):
        if self.config_window is None:
            self.config_window = ConfigWindow()
        show_and_raise(self.config_window)

    def nova_atividade(self):
        if self.nova_window is None:
            self.nova_window = NovaAtividadeWindow()
        show_and_raise(self.nova_window)

    def abrir_gerenciamento(self):
        if self.gerenciamento_window is None:
            self.gerenciamento_window = ControleAtividadesWindow()
        show_and_raise(self.gerenciamento_window)

    # ---------- menu ----------
    def atualizar_menu(self):
        self.menu.clear()

        # Itens fixos (topo)
        ac_gerenciar = QAction("Gerenciar atividades", self.menu)
        ac_gerenciar.triggered.connect(self.abrir_gerenciamento)
        self.menu.addAction(ac_gerenciar)

        ac_nova = QAction("Nova atividade", self.menu)
        ac_nova.triggered.connect(self.nova_atividade)
        self.menu.addAction(ac_nova)

        ac_config = QAction("Configurações", self.menu)
        ac_config.triggered.connect(self.open_config)
        self.menu.addAction(ac_config)

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
        atualizar.triggered.connect(self.atualizar_menu)  # recarrega as atividades
        self.menu.addAction(atualizar)

        self.menu.addSeparator()

        exit_action = QAction("Sair", self.menu)
        exit_action.triggered.connect(self.exit_app)
        self.menu.addAction(exit_action)

    def criar_acao_atividade(self, atividade: dict) -> QAction:
        tipo = (atividade.get("tipo") or "").strip()
        prefixo = tipo[:2].upper() if tipo else ""
        status_icone = ICONES_STATUS.get(atividade.get('status', ''), '')
        nome_menu = f"{status_icone} {prefixo} {atividade.get('id','')}".strip()
        if atividade.get("requisito"):
            nome_menu += f" - {atividade['requisito']}"

        acao = QAction(nome_menu, self.menu)

        def abrir():
            caminho = atividade.get("caminho", "")
            if not caminho:
                QMessageBox.information(self.window, "Abrir pasta", "Caminho inválido.")
                return
            open_folder(caminho)

        acao.triggered.connect(abrir)
        return acao

    # ---------- events ----------
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.abrir_gerenciamento()
            return

        if reason in (QSystemTrayIcon.Context, QSystemTrayIcon.Trigger):
            # abre o menu próximo ao cursor
            self.menu.popup(self.tray.geometry().center())

    def exit_app(self):
        try:
            self.tray.hide()
        except Exception:
            pass
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec())
