from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit, QDateEdit, 
    QPushButton, QHBoxLayout, QListWidget, QListWidgetItem, QMessageBox
)
from PySide6.QtCore import QDate
from pathlib import Path
import json


class EditarMovimentacaoWindow(QDialog):
    def __init__(self, atividade: dict, callback_salvar):
        super().__init__()
        self.setWindowTitle("Editar Movimentação")
        self.setMinimumWidth(500)

        self.atividade = atividade
        self.callback_salvar = callback_salvar

        # --- Layout principal ---
        layout = QVBoxLayout(self)

        # Histórico
        layout.addWidget(QLabel("Histórico (mais novo → mais velho):"))
        self.hist_list = QListWidget()
        layout.addWidget(self.hist_list)
        self._carregar_historico()

        # Nova movimentação
        self.desc_label = QLabel("Nova descrição:")
        self.desc_input = QTextEdit()
        self.desc_input.setFixedHeight(60)

        self.data_label = QLabel("Data:")
        self.data_input = QDateEdit()
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())

        layout.addWidget(self.desc_label)
        layout.addWidget(self.desc_input)
        layout.addWidget(self.data_label)
        layout.addWidget(self.data_input)

        # Botões
        btn_layout = QHBoxLayout()
        self.salvar_btn = QPushButton("Adicionar e Salvar")
        self.cancelar_btn = QPushButton("Cancelar")
        btn_layout.addWidget(self.salvar_btn)
        btn_layout.addWidget(self.cancelar_btn)
        layout.addLayout(btn_layout)

        # Conexões
        self.salvar_btn.clicked.connect(self._salvar)
        self.cancelar_btn.clicked.connect(self.reject)

    def _carregar_historico(self):
        """Carrega o histórico existente da atividade no QListWidget"""
        self.hist_list.clear()
        historico = self.atividade.get("historico", [])
        for mov in historico:  # assume-se já em ordem [mais novo → mais velho]
            data = mov.get("Data", "")
            desc = mov.get("Descricao", "")
            self.hist_list.addItem(QListWidgetItem(f"{data} - {desc}"))

    def _salvar(self):
        """Adiciona nova movimentação, persiste no JSON e notifica callback"""
        descricao = self.desc_input.toPlainText().strip()
        data = self.data_input.date().toPython().isoformat()

        if not descricao:
            QMessageBox.information(self, "Aviso", "Digite uma descrição antes de salvar.")
            return

        nova = {"Data": data, "Descricao": descricao}
        self.atividade.setdefault("historico", []).insert(0, nova)  # mais novo no topo

        # Atualiza lista visual
        self.hist_list.insertItem(0, QListWidgetItem(f"{data} - {descricao}"))
        self.desc_input.clear()

        # Persistência no JSON
        try:
            caminho_str = self.atividade.get("caminho", "")
            if not caminho_str:
                raise ValueError("Caminho da atividade não definido (atividade['caminho'] vazio).")

            pasta = Path(caminho_str)
            pasta.mkdir(parents=True, exist_ok=True)
            arquivo = pasta / "atividade.json"

            with open(arquivo, "w", encoding="utf-8") as f:
                json.dump(self.atividade, f, ensure_ascii=False, indent=4)

        except Exception as e:
            QMessageBox.warning(self, "Erro ao salvar", f"Não foi possível salvar o histórico:\n{e}")
        finally:
            # Notifica UI principal (mesmo em falha de disco, para atualizar memória)
            try:
                self.callback_salvar(self.atividade)
            except Exception:
                pass

        # Fecha diálogo com sucesso
        self.accept()
