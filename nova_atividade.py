from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QComboBox, QDateEdit, QTextEdit, QPushButton, QMessageBox)
from PySide6.QtCore import QDate
from pathlib import Path
import json
import datetime
import config
import subprocess

class NovaAtividadeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nova Atividade")
        self.setMinimumWidth(400)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Tipo
        self.tipo_label = QLabel("Tipo:")
        self.tipo_dropdown = QComboBox()
        self.tipo_dropdown.addItems(["Atendimento", "Providência", "Outro"])
        self.layout.addWidget(self.tipo_label)
        self.layout.addWidget(self.tipo_dropdown)

        # ID
        self.id_label = QLabel("ID:")
        self.id_input = QLineEdit()
        self.layout.addWidget(self.id_label)
        self.layout.addWidget(self.id_input)

        # Nome
        self.nome_label = QLabel("Nome da Atividade:")
        self.nome_input = QLineEdit()
        self.layout.addWidget(self.nome_label)
        self.layout.addWidget(self.nome_input)

        # Requisito
        self.requisito_label = QLabel("Requisito (números):")
        self.requisito_input = QLineEdit()
        self.layout.addWidget(self.requisito_label)
        self.layout.addWidget(self.requisito_input)

        # Prazo
        self.prazo_label = QLabel("Prazo:")
        self.prazo_input = QDateEdit()
        self.prazo_input.setCalendarPopup(True)
        self.prazo_input.setDate(QDate.currentDate())
        self.layout.addWidget(self.prazo_label)
        self.layout.addWidget(self.prazo_input)

        # Última movimentação
        self.mov_label = QLabel("Última Movimentação (opcional):")
        self.mov_input = QTextEdit()
        self.layout.addWidget(self.mov_label)
        self.layout.addWidget(self.mov_input)

        # Data da última movimentação
        self.mov_data_label = QLabel("Data da última movimentação:")
        self.mov_data_input = QDateEdit()
        self.mov_data_input.setCalendarPopup(True)
        self.mov_data_input.setDate(QDate.currentDate())
        self.layout.addWidget(self.mov_data_label)
        self.layout.addWidget(self.mov_data_input)

        # Botões
        self.botao_layout = QHBoxLayout()
        self.criar_btn = QPushButton("Criar")
        self.criar_mais_btn = QPushButton("Criar+")
        self.cancelar_btn = QPushButton("Cancelar")
        self.botao_layout.addWidget(self.criar_btn)
        self.botao_layout.addWidget(self.criar_mais_btn)
        self.botao_layout.addWidget(self.cancelar_btn)
        self.layout.addLayout(self.botao_layout)

        # Conectar sinais
        self.criar_btn.clicked.connect(self.criar)
        self.criar_mais_btn.clicked.connect(self.criar_mais)
        self.cancelar_btn.clicked.connect(self.close)


    def criar_pasta_json(self):
        """Cria pasta na pasta Pendentes com nome correto e salva o JSON"""
        tipo = self.tipo_dropdown.currentText()
        id_ = self.id_input.text().strip()
        nome = self.nome_input.text().strip()
        requisito = self.requisito_input.text().strip() or None
        prazo = self.prazo_input.date().toPython().isoformat()

        historico = []
        if self.mov_input.toPlainText().strip():
            mov_data = self.mov_data_input.date().toPython().isoformat()
            historico.append({"Data": mov_data, "Descricao": self.mov_input.toPlainText().strip()})

        atividade = {
            "status": "Em andamento",
            "requisito": requisito,
            "historico": historico,
            "nome": nome,
            "prazo": prazo,
            "id": id_,
            "tipo": tipo
        }

        # Definir pasta base
        pasta_base = config.PASTA_ATIVIDADES

        # Se houver requisito, cria pasta pai Requisito X
        if requisito:
            pasta_base = pasta_base / f"Requisito - {requisito}"
            pasta_base.mkdir(parents=True, exist_ok=True)

        # Pasta da atividade com nome [Tipo] - [ID]
        pasta_atividade = pasta_base / f"{tipo} - {id_}"
        pasta_atividade.mkdir(parents=True, exist_ok=True)

        # Salvar JSON
        arquivo_json = pasta_atividade / "atividade.json"
        with open(arquivo_json, "w", encoding="utf-8") as f:
            json.dump(atividade, f, ensure_ascii=False, indent=4)

        return pasta_atividade

    def criar(self):
        try:
            pasta = self.criar_pasta_json()
            subprocess.Popen(["explorer", str(pasta)])
            self.close()
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Não foi possível criar a atividade:\n{e}")

    def criar_mais(self):
        try:
            self.criar_pasta_json()
            # limpa campos para nova atividade
            self.tipo_dropdown.setCurrentIndex(0)
            self.id_input.clear()
            self.nome_input.clear()
            self.requisito_input.clear()
            self.prazo_input.setDate(QDate.currentDate())
            self.mov_input.clear()
            self.mov_data_input.setDate(QDate.currentDate())
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Não foi possível criar a atividade:\n{e}")
