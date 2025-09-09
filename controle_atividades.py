from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QDateEdit, QTextEdit, QMessageBox, QScrollArea, QFrame
from PySide6.QtCore import Qt, QDate
from pathlib import Path
import json
import subprocess
from atividades import carregar_atividades
import config

class EditarMovimentacaoWindow(QWidget):
    def __init__(self, atividade, callback_salvar):
        super().__init__()
        self.setWindowTitle("Editar Movimentação")
        self.atividade = atividade
        self.callback_salvar = callback_salvar
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.desc_label = QLabel("Descrição:")
        self.desc_input = QTextEdit()
        self.data_label = QLabel("Data:")
        self.data_input = QDateEdit()
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())

        self.salvar_btn = QPushButton("Salvar")
        self.cancelar_btn = QPushButton("Cancelar")

        self.layout.addWidget(self.desc_label)
        self.layout.addWidget(self.desc_input)
        self.layout.addWidget(self.data_label)
        self.layout.addWidget(self.data_input)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.salvar_btn)
        btn_layout.addWidget(self.cancelar_btn)
        self.layout.addLayout(btn_layout)

        self.salvar_btn.clicked.connect(self.salvar)
        self.cancelar_btn.clicked.connect(self.close)

    def salvar(self):
        descricao = self.desc_input.toPlainText().strip()
        data = self.data_input.date().toPython().isoformat()
        if descricao:
            self.atividade["historico"].insert(0, {"Data": data, "Descricao": descricao})
            self.callback_salvar(self.atividade)
        self.close()


class ControleAtividadesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controle de Atividades")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container.setLayout(self.container_layout)
        self.scroll.setWidget(self.container)
        self.layout.addWidget(self.scroll)

        self.setMinimumWidth(1100)
        self.setMinimumHeight(600)

        # Cabeçalho das colunas
        header_frame = QFrame()
        header_layout = QHBoxLayout()
        header_frame.setLayout(header_layout)

        header_layout.addWidget(QLabel("ID"))
        header_layout.addWidget(QLabel("Nome"))
        header_layout.addWidget(QLabel("Requisito"))
        header_layout.addWidget(QLabel("Prazo"))
        header_layout.addWidget(QLabel("Última Movimentação"))
        header_layout.addWidget(QLabel("Data"))
        header_layout.addWidget(QLabel("Editar"))
        header_layout.addWidget(QLabel("Finalizar"))
        header_layout.addWidget(QLabel("Salvar"))

        # Definir larguras fixas para alinhar
        for i in range(header_layout.count()):
            widget = header_layout.itemAt(i).widget()
            if isinstance(widget, QLabel):
                widget.setFixedWidth(120)

        self.container_layout.addWidget(header_frame)

        self.carregar_atividades()


    def carregar_atividades(self):
        self.container_layout.setAlignment(Qt.AlignTop)
        # limpa atividades antigas
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.atividades = carregar_atividades()
        for at in self.atividades:
            self.adicionar_atividade_widget(at)

    def adicionar_atividade_widget(self, atividade):
        frame = QFrame()
        layout = QHBoxLayout()
        frame.setLayout(layout)

        # Campos editáveis (converter para str se necessário)
        id_input = QLineEdit(str(atividade["id"]))
        nome_input = QLineEdit(atividade["nome"])
        requisito_input = QLineEdit(str(atividade.get("requisito") or ""))
        prazo_input = QDateEdit()
        prazo_input.setCalendarPopup(True)
        prazo_input.setDate(QDate.fromString(atividade["prazo"], "yyyy-MM-dd"))

        # Última movimentação
        ultima = atividade["historico"][0] if atividade.get("historico") else {"Data": "", "Descricao": ""}
        descricao_text = QTextEdit()
        descricao_text.setPlainText(ultima["Descricao"])
        descricao_text.setReadOnly(True)
        descricao_text.setFixedWidth(200)
        descricao_text.setFixedHeight(40)  # ajustável para mais linhas se necessário

        data_label = QLabel(ultima["Data"])
        data_label.setFixedWidth(70)

        # Botões
        editar_btn = QPushButton("Editar")
        finalizar_btn = QPushButton("Finalizar")
        salvar_btn = QPushButton("Salvar")
        salvar_btn.setEnabled(False)  # habilitar somente se houver alterações

        # Adiciona widgets ao layout
        layout.addWidget(id_input)
        layout.addWidget(nome_input)
        layout.addWidget(requisito_input)
        layout.addWidget(prazo_input)
        layout.addWidget(descricao_text)
        layout.addWidget(data_label)
        layout.addWidget(editar_btn)
        layout.addWidget(finalizar_btn)
        layout.addWidget(salvar_btn)

        # Ajuste de largura
        id_input.setFixedWidth(70)
        nome_input.setFixedWidth(180)
        requisito_input.setFixedWidth(70)
        prazo_input.setFixedWidth(100)
        editar_btn.setFixedWidth(80)
        finalizar_btn.setFixedWidth(80)
        salvar_btn.setFixedWidth(80)

        self.container_layout.addWidget(frame)

        # Conectar sinais para detectar alterações
        def atualizar_salvar():
            salvar_btn.setEnabled(True)

        id_input.textChanged.connect(atualizar_salvar)
        nome_input.textChanged.connect(atualizar_salvar)
        requisito_input.textChanged.connect(atualizar_salvar)
        prazo_input.dateChanged.connect(atualizar_salvar)

        # Editar movimentação
        def abrir_editar():
            def callback_salvar(atualizada):
                ultima_mov = atualizada["historico"][0]
                descricao_text.setPlainText(ultima_mov["Descricao"])
                data_label.setText(ultima_mov["Data"])
                salvar_btn.setEnabled(True)

            janela = EditarMovimentacaoWindow(atividade, callback_salvar)
            janela.show()

        editar_btn.clicked.connect(abrir_editar)

        # Salvar alterações nos campos principais
        def salvar_alteracoes():
            try:
                novo_id = id_input.text().strip()
                novo_nome = nome_input.text().strip()
                novo_requisito = requisito_input.text().strip() or None
                nova_data = prazo_input.date().toPython().isoformat()

                mudou_id = novo_id != str(atividade["id"])
                mudou_nome = novo_nome != atividade["nome"]
                mudou_requisito = novo_requisito != str(atividade.get("requisito") or "")
                mudou_prazo = nova_data != atividade["prazo"]

                if not (mudou_id or mudou_nome or mudou_requisito or mudou_prazo):
                    QMessageBox.information(self, "Salvar", "Nenhuma alteração detectada.")
                    return

                pasta_atual = Path(atividade["caminho"])
                pasta_base = config.PASTA_ATIVIDADES

                if novo_requisito:
                    pasta_base = pasta_base / f"Requisito {novo_requisito}"
                    pasta_base.mkdir(parents=True, exist_ok=True)

                nova_pasta = pasta_base / f"{atividade['tipo']} - {novo_id}"
                if nova_pasta != pasta_atual:
                    pasta_atual.rename(nova_pasta)

                atividade["id"] = novo_id
                atividade["nome"] = novo_nome
                atividade["requisito"] = novo_requisito
                atividade["prazo"] = nova_data
                atividade["caminho"] = str(nova_pasta)

                arquivo_json = nova_pasta / "atividade.json"
                with open(arquivo_json, "w", encoding="utf-8") as f:
                    json.dump(atividade, f, ensure_ascii=False, indent=4)

                QMessageBox.information(self, "Salvar", "Alterações salvas com sucesso.")
                salvar_btn.setEnabled(False)
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Não foi possível salvar alterações:\n{e}")

        salvar_btn.clicked.connect(salvar_alteracoes)
