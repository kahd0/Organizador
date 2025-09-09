from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QDateEdit, QTextEdit, QMessageBox, QTableWidget, QTableWidgetItem,
    QComboBox, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, QDate
from pathlib import Path
import json
import shutil
import traceback

import config
from storage import carregar_atividades
from paths import requisito_dir, activity_folder_name, is_requisito_dir
from ui.windows.editar_movimentacao import EditarMovimentacaoWindow
from utils.fs import safe_remove_dir_if_empty, open_folder
from datetime import date
from send2trash import send2trash


class ControleAtividadesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controle de Atividades")
        self.setMinimumSize(1100, 600)
        self.layout = QVBoxLayout(self)

        # Toolbar (busca + atualizar)
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Buscar:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ID, nome ou requisito...")
        self.search_input.textChanged.connect(self.on_search)
        toolbar.addWidget(self.search_input)

        btn_refresh = QPushButton("Atualizar")
        btn_refresh.clicked.connect(self.load_table)
        toolbar.addWidget(btn_refresh)

        toolbar.addStretch()
        self.layout.addLayout(toolbar)

        # Tabela
        self.table = QTableWidget(0, 11)
        headers = [
            "Tipo", "ID", "Nome", "Requisito", "Prazo",
            "Última Movimentação", "Data", "Editar", "Finalizar", "Salvar", "Caminho"
        ]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)

        self.table.setColumnHidden(10, True)  # caminho oculto

        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        self.layout.addWidget(self.table)

        self.row_activity = {}
        self.row_modified = {}

        # manter referências das janelas de editar para evitar GC
        self._editar_windows = []

        self.load_table()

    def load_table(self):
        try:
            self.table.setRowCount(0)
            self.row_activity.clear()
            self.row_modified.clear()
            self._editar_windows.clear()
            atividades = carregar_atividades()
            for at in atividades:
                self._insert_row(at)
        except Exception:
            traceback.print_exc()
            QMessageBox.warning(self, "Erro", "Falha ao carregar atividades. Veja o console para detalhes.")

    def on_search(self, text: str):
        q = (text or "").strip().lower()
        for row in range(self.table.rowCount()):
            at = self.row_activity.get(row)
            if at is None:
                self.table.setRowHidden(row, False)
                continue
            hay = f"{at.get('id','')} {at.get('nome','')} {at.get('requisito','')}".lower()
            self.table.setRowHidden(row, q != "" and (q not in hay))

    def _insert_row(self, atividade: dict):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.row_activity[row] = atividade
        self.row_modified[row] = False

        # --- Tipo ---
        tipo_cb = QComboBox()
        tipos_disponiveis = ["Atendimento", "Providência", "Outro"]
        tipo_cb.addItems(tipos_disponiveis)
        atual_tipo = atividade.get("tipo") or tipos_disponiveis[0]
        if atual_tipo not in tipos_disponiveis:
            tipo_cb.addItem(atual_tipo)
        tipo_cb.setCurrentText(atual_tipo)
        tipo_cb.currentTextChanged.connect(lambda _=None, r=row: self._mark_modified(r))
        self.table.setCellWidget(row, 0, tipo_cb)

        # --- ID ---
        id_le = QLineEdit(str(atividade.get("id", "")))
        id_le.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        id_le.textChanged.connect(lambda _=None, r=row: self._mark_modified(r))
        self.table.setCellWidget(row, 1, id_le)

        # --- Nome ---
        nome_le = QLineEdit(atividade.get("nome", ""))
        nome_le.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        nome_le.textChanged.connect(lambda _=None, r=row: self._mark_modified(r))
        self.table.setCellWidget(row, 2, nome_le)

        # --- Requisito ---
        req_le = QLineEdit(str(atividade.get("requisito") or ""))
        req_le.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        req_le.textChanged.connect(lambda _=None, r=row: self._mark_modified(r))
        self.table.setCellWidget(row, 3, req_le)

        # --- Prazo ---
        prazo_de = QDateEdit()
        prazo_de.setCalendarPopup(True)
        qdate = QDate.fromString(atividade.get("prazo", ""), "yyyy-MM-dd")
        prazo_de.setDate(qdate if qdate.isValid() else QDate.currentDate())
        prazo_de.dateChanged.connect(lambda _=None, r=row: self._mark_modified(r))
        self.table.setCellWidget(row, 4, prazo_de)

        # --- Última Movimentação ---
        ultima = atividade.get("historico", [{}])[0] if atividade.get("historico") else {}
        mov_te = QTextEdit()
        mov_te.setPlainText(ultima.get("Descricao", ""))
        mov_te.setReadOnly(True)
        mov_te.setFixedHeight(60)
        self.table.setCellWidget(row, 5, mov_te)

        # --- Data ---
        data_lbl = QLabel(ultima.get("Data", ""))
        data_lbl.setAlignment(Qt.AlignCenter)
        self.table.setCellWidget(row, 6, data_lbl)

        # --- Editar ---
        editar_btn = QPushButton("Editar")
        editar_btn.clicked.connect(lambda _=None, r=row: self._open_editar(r))
        self.table.setCellWidget(row, 7, editar_btn)

        # --- Finalizar ---
        finalizar_btn = QPushButton("Finalizar")
        def finalizar_clicked(_=None, r=row):
            self._finalizar_linha(r)
        finalizar_btn.clicked.connect(finalizar_clicked)
        self.table.setCellWidget(row, 8, finalizar_btn)

        # --- Salvar ---
        salvar_btn = QPushButton("Salvar")
        salvar_btn.setEnabled(False)
        salvar_btn.clicked.connect(lambda _=None, r=row: self._salvar_linha(r))
        self.table.setCellWidget(row, 9, salvar_btn)

        # --- Caminho (oculto) ---
        caminho_item = QTableWidgetItem(str(atividade.get("caminho", "")))
        caminho_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.table.setItem(row, 10, caminho_item)

    def _mark_modified(self, row: int):
        self.row_modified[row] = True
        salvar_btn = self.table.cellWidget(row, 9)
        if salvar_btn:
            salvar_btn.setEnabled(True)

    def _open_editar(self, row: int):
        atividade = self.row_activity.get(row)
        if not atividade:
            return

        def callback_salvar(atualizada: dict):
            # Atualiza em memória e na UI, mas não força o botão "Salvar" da linha
            self.row_activity[row] = atualizada
            mov = atualizada.get("historico", [{}])[0] if atualizada.get("historico") else {}
            mov_widget = self.table.cellWidget(row, 5)
            if isinstance(mov_widget, QTextEdit):
                mov_widget.setPlainText(mov.get("Descricao", ""))
            data_widget = self.table.cellWidget(row, 6)
            if isinstance(data_widget, QLabel):
                data_widget.setText(mov.get("Data", ""))
            # se quiser forçar rechecagem de estado dos campos, pode-se comparar valores e ajustar salvar_btn
            # mas, como a movimentação já foi persistida no arquivo, não habilitamos "Salvar" automaticamente.
            # isso evita que o usuário precise clicar em salvar só por uma movimentação já gravada.

            # atualiza caminho na tabela caso a edição tenha alterado o caminho (raro aqui)
            caminho_item = self.table.item(row, 10)
            if caminho_item:
                caminho_item.setText(atualizada.get("caminho", caminho_item.text()))

        # Cria janela de edição e mantém referência para evitar GC
        janela = EditarMovimentacaoWindow(atividade, callback_salvar)
        janela.exec()  # bloqueia até fechar

    def _finalizar_linha(self, row: int):
      atividade = self.row_activity.get(row)
      if not atividade:
          return

      resposta = QMessageBox.question(
          self,
          "Finalizar Atividade",
          f"Tem certeza que deseja finalizar a atividade '{atividade['nome']}'?",
          QMessageBox.Yes | QMessageBox.No
      )
      if resposta != QMessageBox.Yes:
          return

      try:
          pasta_origem = Path(atividade.get("caminho", ""))
          if not pasta_origem.exists():
              QMessageBox.warning(self, "Erro", "Pasta da atividade não encontrada.")
              return

          # Formata nome do ZIP
          tipo = atividade.get("tipo", "")
          id_ = atividade.get("id", "")
          nome = atividade.get("nome", "").replace(" ", "_")
          requisito = atividade.get("requisito", "")
          data_finalizada = date.today().isoformat()
          if requisito:
              nome_zip = f"Requisito_{requisito}_{tipo}_{id_}_{nome}_{data_finalizada}.zip"
          else:
              nome_zip = f"{tipo}_{id_}_{nome}_{data_finalizada}.zip"

          pasta_destino = Path(config.PASTA_FINALIZADAS)
          pasta_destino.mkdir(parents=True, exist_ok=True)
          zip_path = pasta_destino / nome_zip

          # Cria ZIP
          shutil.make_archive(str(zip_path.with_suffix("")), 'zip', root_dir=str(pasta_origem))

          # Move para lixeira
          send2trash(str(pasta_origem))

          QMessageBox.information(self, "Finalizado", f"Atividade finalizada com sucesso!\nArquivo: {zip_path}")

          # Remove linha da tabela e registros internos
          self.table.removeRow(row)
          self.row_activity.pop(row, None)
          self.row_modified.pop(row, None)

          # Reindexa rows posteriores
          new_row_activity = {}
          new_row_modified = {}
          for i, r in enumerate(sorted(self.row_activity.keys())):
              new_row_activity[i] = self.row_activity[r]
              new_row_modified[i] = self.row_modified[r]
          self.row_activity = new_row_activity
          self.row_modified = new_row_modified

      except Exception as e:
          QMessageBox.warning(self, "Erro", f"Não foi possível finalizar a atividade:\n{e}")


    def _salvar_linha(self, row: int):
        try:
            atividade = self.row_activity.get(row)
            if atividade is None:
                return

            tipo_widget = self.table.cellWidget(row, 0)
            novo_tipo = tipo_widget.currentText() if isinstance(tipo_widget, QComboBox) else atividade.get("tipo")

            id_widget = self.table.cellWidget(row, 1)
            novo_id = id_widget.text().strip() if isinstance(id_widget, QLineEdit) else str(atividade.get("id", "")).strip()

            nome_widget = self.table.cellWidget(row, 2)
            novo_nome = nome_widget.text().strip() if isinstance(nome_widget, QLineEdit) else atividade.get("nome", "")

            req_widget = self.table.cellWidget(row, 3)
            novo_requisito = req_widget.text().strip() or None if isinstance(req_widget, QLineEdit) else atividade.get("requisito")

            prazo_widget = self.table.cellWidget(row, 4)
            nova_prazo = prazo_widget.date().toPython().isoformat() if isinstance(prazo_widget, QDateEdit) else atividade.get("prazo")

            if not novo_id:
                QMessageBox.warning(self, "Erro", "O campo ID não pode estar vazio.")
                return

            caminho_atual_text = self.table.item(row, 10).text() if self.table.item(row, 10) else ""
            pasta_atual = Path(caminho_atual_text).resolve()
            if not pasta_atual.exists():
                # apenas avisar; continuamos criando destino
                pass

            pasta_base_nova = requisito_dir(config.PASTA_ATIVIDADES, novo_requisito)
            pasta_base_nova.mkdir(parents=True, exist_ok=True)
            nova_pasta = (pasta_base_nova / activity_folder_name(novo_tipo, novo_id)).resolve()

            if nova_pasta.exists() and nova_pasta != pasta_atual:
                QMessageBox.warning(self, "Erro", f"A pasta destino já existe:\n{nova_pasta}\nOperação cancelada para evitar sobrescrita.")
                return

            nova_pasta.parent.mkdir(parents=True, exist_ok=True)

            if nova_pasta != pasta_atual:
                if pasta_atual.exists():
                    shutil.move(str(pasta_atual), str(nova_pasta))
                else:
                    nova_pasta.mkdir(parents=True, exist_ok=True)

                pasta_antiga_requisito = pasta_atual.parent if is_requisito_dir(pasta_atual.parent) else None
                if pasta_antiga_requisito and pasta_antiga_requisito.exists():
                    safe_remove_dir_if_empty(pasta_antiga_requisito)

            atividade["tipo"] = novo_tipo
            atividade["id"] = novo_id
            atividade["nome"] = novo_nome
            atividade["requisito"] = novo_requisito
            atividade["prazo"] = nova_prazo
            atividade["caminho"] = str(nova_pasta)

            arquivo_json = Path(atividade["caminho"]) / "atividade.json"
            with open(arquivo_json, "w", encoding="utf-8") as f:
                json.dump(atividade, f, ensure_ascii=False, indent=4)

            if self.table.item(row, 10):
                self.table.item(row, 10).setText(str(nova_pasta))
            else:
                self.table.setItem(row, 10, QTableWidgetItem(str(nova_pasta)))

            salvar_btn = self.table.cellWidget(row, 9)
            if salvar_btn:
                salvar_btn.setEnabled(False)
            self.row_modified[row] = False

            QMessageBox.information(self, "Salvar", "Alterações salvas com sucesso.")

        except Exception as e:
            traceback.print_exc()
            QMessageBox.warning(self, "Erro", f"Não foi possível salvar alterações:\n{e}")

    def on_cell_double_clicked(self, row: int, column: int):
        try:
            item = self.table.item(row, 10)
            if item:
                caminho = item.text()
                if caminho:
                    open_folder(caminho)
        except Exception:
            pass
