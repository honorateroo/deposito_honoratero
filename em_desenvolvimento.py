# ULTIMAS ATUALIZAÇÕES:
 
        # BANCO DE DADOS Main 100%
        # SAVE DO PARTES FUNCIONANDO CORRETAMENTE
        # ERRO COMBOBOX COM ROLAGEM DO MOUSE CORRIGIDO

import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # Define a localização para formatação monetária brasileira
import sqlite3
import sys
from docx import Document
import os
from PyQt5.QtWidgets import (QHBoxLayout, QMessageBox, QInputDialog, QFileDialog, QPushButton, QCheckBox, QMessageBox, QFrame, QApplication, QMainWindow, QLabel, QLineEdit, QComboBox, QVBoxLayout, QWidget, QScrollArea, QSpacerItem, QSizePolicy)
from openpyxl import Workbook, load_workbook
import os
import requests
import re
from PyQt5.QtCore import (Qt, QDate)
import qrcode
from xml.etree import ElementTree as ET


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

# Inicializa o layout como None
        self.layout_terceiro_interessado = None

# Configurações da Janela Principal
        self.setWindowTitle("Formulário Jurídico 1.0")
        self.resize(1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #eaeaea;
            }
            QWidget {
                font-family: 'Arial';
                font-size: 17px;
                color: #333;
            }
            QLineEdit, QComboBox {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-family: 'Arial';
                font-size: 17px;
                padding: 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-size: 14px;
                color: #444;
            }
        """)

# Widget central e a Barra de Rolagem
        self.central_widget = QWidget(self)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.central_widget)
        self.setCentralWidget(self.scroll_area)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(20)

# Configuração Inicial dos Campos
        self.setup_initial_fields()

# Lista para armazenar os campos de porcentagem
        self.porcentagem_fields = []
        
# Espaço expansivo para empurrar futuros widgets para baixo
        self.spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addItem(self.spacer)

# Inicialização da conexão com o banco de dados
        self.conn = sqlite3.connect('juridico_geral.db')
        self.cursor = self.conn.cursor()
        
# Criação da tabela se não existir
        self.criar_tabela_juridico_geral()
    def criar_tabela_juridico_geral(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS juridico_geral (
                processo TEXT PRIMARY KEY
            )
        """)
        self.conn.commit()
    def add_column_if_not_exists(self, column_name):
        self.cursor.execute(f"PRAGMA table_info(juridico_geral)")
        columns = [info[1] for info in self.cursor.fetchall()]

        if (column_name not in columns) and column_name:
            self.cursor.execute(f"ALTER TABLE juridico_geral ADD COLUMN {column_name} TEXT")
            self.conn.commit()
    def criar_campo_data(self, label_text, placeholder, layout):
        label = QLabel(label_text, self)
        label.setStyleSheet("font-size: 16px; color: #333;")
        field = QLineEdit(self)
        field.setPlaceholderText(placeholder)
        layout.addWidget(label)
        layout.addWidget(field)
        return label, field
    def criar_campo_combobox(self, label_text, options, layout):
        label = QLabel(label_text, self)
        label.setStyleSheet("font-size: 16px; color: #333;")
        
        combobox = QComboBox(self)
        combobox.addItems(options)
        combobox.setCurrentIndex(0)  # Define o índice atual para 0

        # Sobrescreve o evento de rolagem do mouse para evitar a mudança de seleção
        def wheelEvent(event):
            event.ignore()
        
        combobox.wheelEvent = wheelEvent

        layout.addWidget(label)
        layout.addWidget(combobox)
        return label, combobox
    def criar_campo_checkbox(self, label_text, layout):
        checkbox = QCheckBox(label_text, self)
        checkbox.setStyleSheet("font-size: 16px; color: #333;")
        layout.addWidget(checkbox)
        return checkbox
    def criar_linha_separadora(self, layout):
        linha_separar = QFrame(self)
        linha_separar.setFrameShape(QFrame.HLine)
        linha_separar.setFrameShadow(QFrame.Sunken)
        layout.addWidget(linha_separar)
        return linha_separar
    def criar_campo_completo(self, label_text, layout, campo_placeholder=" ", folhas_placeholder="folhas", situacao_placeholder="situação"):
# Cria o label e o campo principal
        label = QLabel(label_text, self)
        label.setStyleSheet("font-size: 16px; color: #333;")
        campo = QLineEdit(self)
        campo.setPlaceholderText(campo_placeholder)
        layout.addWidget(label)
        layout.addWidget(campo)

# Cria o campo de folhas
        campo_folha = QLineEdit(self)
        campo_folha.setPlaceholderText(folhas_placeholder)
        layout.addWidget(campo_folha)

# Cria o campo de situação
        campo_situacao = QLineEdit(self)
        campo_situacao.setPlaceholderText(situacao_placeholder)
        layout.addWidget(campo_situacao)

# Adiciona a linha separadora
        linha_separar = QFrame(self)
        linha_separar.setFrameShape(QFrame.HLine)
        linha_separar.setFrameShadow(QFrame.Sunken)
        layout.addWidget(linha_separar)

        return label, campo, campo_folha, campo_situacao
    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Erro")
        msg.exec_()
    def show_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Validação")
        msg.exec_()
    def criar_campo_comparativo(self, titulo_texto, link_placeholder, metragem_placeholder, valor_placeholder, layout):
        # LABEL TITULO
        label_titulo = QLabel(titulo_texto, self)
        label_titulo.setStyleSheet("color: #333; font-size: 18px")
        layout.addWidget(label_titulo)

        # CAMPO Link
        link_label = QLabel("Link :", self)
        link_label.setStyleSheet("font-size: 16px; color: #333;")
        link_field = QLineEdit(self)
        link_field.setPlaceholderText(link_placeholder)
        layout.addWidget(link_label)
        layout.addWidget(link_field)

        # CAMPO Metragem
        metragem_label = QLabel("M² :", self)
        metragem_label.setStyleSheet("font-size: 16px; color: #333;")
        metragem_field = QLineEdit(self)
        metragem_field.setPlaceholderText(metragem_placeholder)
        layout.addWidget(metragem_label)
        layout.addWidget(metragem_field)

        # CAMPO Valor
        valor_label = QLabel("Valor :", self)
        valor_label.setStyleSheet("font-size: 16px; color: #333;")
        valor_field = QLineEdit(self)
        valor_field.setPlaceholderText(valor_placeholder)
        layout.addWidget(valor_label)
        layout.addWidget(valor_field)

        # Retorno dos campos criados
        return label_titulo, link_label, link_field, metragem_label, metragem_field, valor_label, valor_field
    def preencher_checkbox_partes(self, tipo_parte):
        processo = self.processo_field.text()
        if processo:
            self.partes_window = PartesWindow(processo)
            # Preenche a checkbox correspondente com base no tipo de parte
            if tipo_parte == "Exequente":
                self.partes_window.checkbox_exequente.setChecked(True)
            elif tipo_parte == "Advogado do Exequente":
                self.partes_window.checkbox_adv_exequente.setChecked(True)
            elif tipo_parte == "Executado":
                self.partes_window.checkbox_executado.setChecked(True)
            elif tipo_parte == "Advogado do Executado":
                self.partes_window.checkbox_adv_executado.setChecked(True)
            elif tipo_parte == "Terceiro Interessado":
                self.partes_window.checkbox_terceiro_interessado.setChecked(True)
            elif tipo_parte == "Proprietario Coproprietario":
                self.partes_window.checkbox_proprietario.setChecked(True)
            elif tipo_parte == "Credor Fiduciário":
                self.partes_window.checkbox_credor_fid.setChecked(True)
            elif tipo_parte == "Credor da Penhora":
                self.partes_window.checkbox_credor_pen.setChecked(True)
            elif tipo_parte == "Credor Hipotecário":
                self.partes_window.checkbox_credor_hip.setChecked(True)
            elif tipo_parte == "Proprietário Registral":
                self.partes_window.checkbox_proprietario_registral.setChecked(True)
            elif tipo_parte == "Proprietário Comprador":
                self.partes_window.checkbox_proiminente_comprador.setChecked(True)
            elif tipo_parte == "Curador Especial":
                self.partes_window.checkbox_curador_esp.setChecked(True)
            else:
                QMessageBox.warning(self, "Erro", "Tipo de parte inválido.")
                return

            self.partes_window.show()
        else:
            QMessageBox.warning(self, "Erro", "Por favor, insira um número de processo válido.")

    def setup_initial_fields(self):

# LABEL TITULO Informações do Processo
        self.label_informacoes_juridicas = QLabel("Informações do Processo", self)
        self.label_informacoes_juridicas.setStyleSheet("color: #333; font-size: 30px")
        self.main_layout.addWidget(self.label_informacoes_juridicas)

# Processo
        self.processo_label, self.processo_field = self.criar_campo_data("Processo :", "processo", self.main_layout)

# Salvar
        self.save_button = QPushButton("Salvar", self)
        self.save_button.clicked.connect(self.save_to_db_dynamic)
        self.main_layout.addWidget(self.save_button)

# Carregar
        self.load_button = QPushButton("Carregar", self)
        self.load_button.clicked.connect(self.load_from_db_dynamic)
        self.main_layout.addWidget(self.load_button)

############################################################################# Partes
        self.label_partes = QLabel("Partes", self)
        self.label_partes.setStyleSheet("color: #333; font-size: 30px")
        self.main_layout.addWidget(self.label_partes)

        # Adicionar Partes
        self.adicionar_partes_button = QPushButton("Adicionar Partes", self)
        self.adicionar_partes_button.clicked.connect(self.open_partes_window)
        self.main_layout.addWidget(self.adicionar_partes_button)


        self.link_processo_label, self.link_processo_field = self.criar_campo_data("Link do processo :", " ", self.main_layout)

# Ação
        self.acao_label, self.acao_field = self.criar_campo_data("Ação :", " ", self.main_layout)

# Vara
        self.vara_label, self.vara_field = self.criar_campo_data("Vara :", " ", self.main_layout)

# Foro
        self.foro_label, self.foro_field = self.criar_campo_data("Foro :", " ", self.main_layout)

# Comarca
        self.comarca_label, self.comarca_field = self.criar_campo_data("Comarca :", " ", self.main_layout)

# E-mail do Cartório
        self.email_cartorio_label, self.email_cartorio_field = self.criar_campo_data("E-mail do Cartório :", " ", self.main_layout)

# Nome do Juíz
        self.nome_juiz_label, self.nome_juiz_field = self.criar_campo_data("Nome do Juíz :", "nome_juiz", self.main_layout)

# Exequente
        self.exequente_label = QLabel("Exequente :", self)
        self.exequente_label.setStyleSheet("font-size: 17px; color: #333;")
        self.exequente_button = QPushButton("Adicionar Exequente", self)
        self.exequente_button.clicked.connect(lambda: self.preencher_checkbox_partes("Exequente"))
        self.main_layout.addWidget(self.exequente_label)
        self.main_layout.addWidget(self.exequente_button)

# Advogado do Exequente
        self.adv_exequente_label = QLabel("Advogado do Exequente :", self)
        self.adv_exequente_label.setStyleSheet("font-size: 17px; color: #333;")
        self.adv_exequente_button = QPushButton("Adicionar Exequente", self)
        self.adv_exequente_button.clicked.connect(lambda: self.preencher_checkbox_partes("Advogado do Exequente"))
        self.main_layout.addWidget(self.adv_exequente_label)
        self.main_layout.addWidget(self.adv_exequente_button)

# Executado
        self.executado_label = QLabel("Executado :", self)
        self.executado_label.setStyleSheet("font-size: 17px; color: #333;")
        self.executado_button = QPushButton("Adicionar Executado", self)
        self.executado_button.clicked.connect(lambda: self.preencher_checkbox_partes("Executado"))
        self.main_layout.addWidget(self.executado_label)
        self.main_layout.addWidget(self.executado_button)

# Advogado do Executado
        self.adv_executado_label = QLabel("Advogado do Executado :", self)
        self.adv_executado_label.setStyleSheet("font-size: 17px; color: #333;")
        self.adv_executado_button = QPushButton("Adicionar Executado", self)
        self.adv_executado_button.clicked.connect(lambda: self.preencher_checkbox_partes("Advogado do Executado"))
        self.main_layout.addWidget(self.adv_executado_label)
        self.main_layout.addWidget(self.adv_executado_button)

# terceiro_interessado
        self.terceiro_interessado_label = QLabel("Terceiro Interessado :", self)
        self.terceiro_interessado_label.setStyleSheet("font-size: 17px; color: #333;")
        self.terceiro_interessado_button = QPushButton("Adicionar Executado", self)
        self.terceiro_interessado_button.clicked.connect(lambda: self.preencher_checkbox_partes("Terceiro Interessado"))
        self.main_layout.addWidget(self.terceiro_interessado_label)
        self.main_layout.addWidget(self.terceiro_interessado_button)

# Sobre o Domínio do Bem
        self.sobre_dominio_bem_label = QLabel("Sobre o Domínio do bem :", self)
        self.sobre_dominio_bem_label.setStyleSheet("font-size: 20px; color: #333;")
        self.main_layout.addWidget(self.sobre_dominio_bem_label)

# O que esta sendo vendido/leiloado ?
        self.oq_leiloado_label, self.oq_leiloado_combobox = self.criar_campo_combobox("O que esta sendo vendido/leiloado ?", ["O Bem", "Direitos ?", "Fração ideal do bem ?"], self.main_layout)
# Proprietarios
        self.proprietarios_label = QLabel("Proprietarios (obrigatoriamente, os donos que constam na matricula e estão sendo executados.):", self)
        self.proprietarios_label.setStyleSheet("font-size: 17px; color: #333;")
        self.proprietarios_button = QPushButton("Adicionar Proprietarios", self)
        self.proprietarios_button.clicked.connect(lambda: self.preencher_checkbox_partes("Proprietario Coproprietario"))
        self.main_layout.addWidget(self.proprietarios_label)
        self.main_layout.addWidget(self.proprietarios_button)


# Credor Fiduciáio
        self.credor_fiduciario_label = QLabel("Credor Fiduciáio:", self)
        self.credor_fiduciario_label.setStyleSheet("font-size: 17px; color: #333;")
        self.credor_fiduciario_button = QPushButton("Adicionar Credor Fiduciáio", self)
        self.credor_fiduciario_button.clicked.connect(lambda: self.preencher_checkbox_partes("Credor Fiduciário"))
        self.main_layout.addWidget(self.credor_fiduciario_label)
        self.main_layout.addWidget(self.credor_fiduciario_button)

# Credor da Penhora
        self.credor_penhora_label = QLabel("Credor da Penhora :", self)
        self.credor_penhora_label.setStyleSheet("font-size: 17px; color: #333;")
        self.credor_penhora_button = QPushButton("Adicionar Credor da Penhora", self)
        self.credor_penhora_button.clicked.connect(lambda: self.preencher_checkbox_partes("Credor da Penhora"))
        self.main_layout.addWidget(self.credor_penhora_label)
        self.main_layout.addWidget(self.credor_penhora_button)

# Credor da Hipotecário
        self.credor_hipotecario_label = QLabel("Credor da Hipotecário :", self)
        self.credor_hipotecario_label.setStyleSheet("font-size: 17px; color: #333;")
        self.credor_hipotecario_button = QPushButton("Adicionar Credor da Hipotecário", self)
        self.credor_hipotecario_button.clicked.connect(lambda: self.preencher_checkbox_partes("Credor Hipotecário"))
        self.main_layout.addWidget(self.credor_hipotecario_label)
        self.main_layout.addWidget(self.credor_hipotecario_button)

# Propietário Registral
        self.proeminente_formal_label = QLabel("Propietário Registral :", self)
        self.proeminente_formal_label.setStyleSheet("font-size: 17px; color: #333;")
        self.proeminente_formal_button = QPushButton("Adicionar Propietário Registral", self)
        self.proeminente_formal_button.clicked.connect(lambda: self.preencher_checkbox_partes("Proprietário Registral"))
        self.main_layout.addWidget(self.proeminente_formal_label)
        self.main_layout.addWidget(self.proeminente_formal_button)

# Propietário Comptrador
        self.proeminente_comprado_label = QLabel("Propietário Comprador :", self)
        self.proeminente_comprado_label.setStyleSheet("font-size: 17px; color: #333;")
        self.proeminente_comprado_button = QPushButton("Adicionar Propietário Comptrador", self)
        self.proeminente_comprado_button.clicked.connect(lambda: self.preencher_checkbox_partes("Proprietário Comprador"))
        self.main_layout.addWidget(self.proeminente_comprado_label)
        self.main_layout.addWidget(self.proeminente_comprado_button)

# Curador Especial
        self.curador_especial_label = QLabel("Curador Especial :", self)
        self.curador_especial_label.setStyleSheet("font-size: 17px; color: #333;")
        self.curador_especial_button = QPushButton("Adicionar Curador Especial", self)
        self.curador_especial_button.clicked.connect(lambda: self.preencher_checkbox_partes("Curador Especial"))
        self.main_layout.addWidget(self.curador_especial_label)
        self.main_layout.addWidget(self.curador_especial_button)

# Há Alienação Fiduciária
        self.ha_alienacao_label, self.ha_alienacao_combobox = self.criar_campo_combobox("Há Alienação Fiduciária ?", [" ", "Sim", "Não"], self.main_layout)

# Há incapaz
        self.ha_incapaz_label, self.combo_ha_incapaz = self.criar_campo_combobox("Há incapaz ?", [" ", "Sim", "Não"], self.main_layout)

# Há Usufutuário
        self.ha_usufrutuario_label, self.ha_usufrutuario_combobox = self.criar_campo_combobox("Há Usufutuário ?", [" ", "Sim", "Não"], self.main_layout)

# Qual a situação da representação processual:
        self.representacao_processual_label, self.representacao_processual_field, self.representacao_processual_field_folhas, self.representacao_processual_field_situacao = self.criar_campo_completo(
            "Qual a situação da representação processual:", self.main_layout)

# Citações
        self.citacoes_label, self.citacoes_field, self.citacoes_field_folhas, self.citacoes_field_situacao = self.criar_campo_completo(
            "Citações:", self.main_layout)

# Sentença e/ou situação que preceda o feito
        self.sentenca_label, self.sentenca_field, self.sentenca_field_folhas, self.sentenca_field_situacao = self.criar_campo_completo(
            "Sentença e/ou situação que preceda o feito:", self.main_layout)

# Transito julgado
        self.transito_julgado_label, self.transito_julgado_field, self.transito_julgado_field_folhas, self.transito_julgado_field_situacao = self.criar_campo_completo(
            "Transito julgado", self.main_layout)

# Inicio do cumprimento de senteça/ Prosseguimento da Execução
        self.cumprimento_sentenca_label, self.cumprimento_sentenca_field, self.cumprimento_sentenca_field_folhas, self.cumprimento_sentenca_field_situacao = self.criar_campo_completo(
            "Inicio do cumprimento de senteça/ Prosseguimento da Execução:", self.main_layout)

# Termo(s) de Penhora
        self.termo_penhora_label, self.termo_penhora_field, self.termo_penhora_field_folhas, self.termo_penhora_field_situacao = self.criar_campo_completo(
            "Termo(s) de Penhora", self.main_layout)

# Depositário
        self.depositario_label, self.depositario_field, self.depositario_field_folhas, self.depositario_field_situacao = self.criar_campo_completo(
            "Depositário", self.main_layout)

# Inicio do cumprimento de senteça/ Prosseguimento da Execução
        self.intimacao_executado_label, self.intimacao_executado_field, self.intimacao_executado_field_folhas, self.intimacao_executado_field_situacao = self.criar_campo_completo(
            "Intimação do Executado", self.main_layout)

# Intimação do Credor(es) Fiduciário(s/Hipotecário(s)
        self.intimacao_credor_label, self.intimacao_credor_field, self.intimacao_credor_field_folhas, self.intimacao_credor_field_situacao = self.criar_campo_completo(
            "Intimação do Credor(es) Fiduciário(s/Hipotecário(s)", self.main_layout)

# Sentençe/ou Decisão
        self.sentenca_label, self.sentenca_field, self.sentenca_field_folhas, self.sentenca_field_situacao = self.criar_campo_completo(
            "Sentençe/ou Decisão", self.main_layout)

# Perfil do Executado
        self.perfil_executado_label = QLabel("Perfil do Executado :", self)
        self.perfil_executado_label.setStyleSheet("font-size: 17px; color: #333;")
        self.main_layout.addWidget(self.perfil_executado_label)

# Ao analisar o processo, foi identificado alguma dificuldade em intimar o réus
        self.dificuldade_initimar_label, self.dificuldade_initimar_field, self.dificuldade_initimar_field_folhas, self.dificuldade_initimar_field_situacao = self.criar_campo_completo(
            "Ao analisar o processo, foi identificado alguma dificuldade em intimar o réus", self.main_layout)

# O réu é combativo, peticiona muito ou recorre com frequencia
        self.reu_combativo_label, self.reu_combativo_field, self.reu_combativo_field_folhas, self.reu_combativo_field_situacao = self.criar_campo_completo(
            "O réu é combativo, peticiona muito ou recorre com frequencia", self.main_layout)

# O réu é combativo, peticiona muito ou recorre com frequencia
        self.embargos_label, self.embargos_field, self.embargos_field_folhas, self.embargos_field_situacao = self.criar_campo_completo(
            "Há embargos / recursos pendentes de serem julgados", self.main_layout)

# Condições do leilão
        self.label_determinacao_condicoes = QLabel("Condições do leilão", self)
        self.label_determinacao_condicoes.setStyleSheet("color: #333; font-size: 30px")
        self.main_layout.addWidget(self.label_determinacao_condicoes)
        self.main_layout.setSpacing(20)  # Espaçamento reduzido

# Despacho sobre as condições do leilão
        self.despacho_nomeacao_label, self.despacho_nomeacao_field = self.criar_campo_data("Despacho de nomeação :", " ", self.main_layout)
        self.despacho_nomeacao_field.setStyleSheet("height: 17px; min-height: 200px; font-size: 16px")

# Despacho sobre as condições do leilão
        self.despacho_condicoes_label, self.despacho_condicoes_field = self.criar_campo_data("Despacho de sobre as condições do leilão :", " ", self.main_layout)
        self.despacho_condicoes_field.setStyleSheet("height: 17px; min-height: 200px; font-size: 16px")

# Datas do leilão
        self.datas_leilao_label = QLabel("Datas do leilão :", self)
        self.datas_leilao_label.setStyleSheet("font-size: 17px; color: #333;")
        self.main_layout.addWidget(self.datas_leilao_label)

        # Primeiro, defina todos os campos necessários
        self.quantas_praca_label, self.quantas_praca_combobox = self.criar_campo_combobox("Quantas Praças", ["2 Praças", "1 Praça", "3 Praças"], self.main_layout)

        self.inicio_ipraca_label, self.inicio_ipraca_field = self.criar_campo_data("Inicio 1ª Praça :", " ", self.main_layout)
        self.fim_ipraca_label, self.fim_ipraca_field = self.criar_campo_data("Fim 1ª Praça :", " ", self.main_layout)

        self.inicio_iipraca_label, self.inicio_iipraca_field = self.criar_campo_data("Inicio 2ª Praça :", " ", self.main_layout)
        self.fim_iipraca_label, self.fim_iipraca_field = self.criar_campo_data("Fim 2ª Praça :", " ", self.main_layout)

        self.inicio_iiipraca_label, self.inicio_iiipraca_field = self.criar_campo_data("Inicio 3ª Praça :", " ", self.main_layout)
        self.fim_iiipraca_label, self.fim_iiipraca_field = self.criar_campo_data("Fim 3ª Praça :", " ", self.main_layout)

        # Depois, conecte a função ao evento e chame a função

        self.atualizar_visibilidade_pracas()

# Conectar os campos à função de atualização
        self.inicio_ipraca_field.textChanged.connect(lambda: self.update_dates(self.inicio_ipraca_field))
        self.fim_ipraca_field.textChanged.connect(lambda: self.update_dates(self.fim_ipraca_field))
        self.inicio_iipraca_field.textChanged.connect(lambda: self.update_dates(self.inicio_iipraca_field))
        self.fim_iipraca_field.textChanged.connect(lambda: self.update_dates(self.fim_iipraca_field))

        # Sobre o pagamento do bem
        self.pagamento_bem_label, self.pagamento_bem_combobox = self.criar_campo_combobox("Sobre o Pagamento do Bem", ["Só a vista", "Permite pagamento parcelado via proposta, somente até abertura do leilão", "Permite lances parcelados"], self.main_layout)

        # Parcelas
        self.parcelas_label, self.parcelas_combobox = self.criar_campo_combobox("Quantas Parcelas", [str(i) for i in range(1, 31)], self.main_layout)
        self.parcelas_label.hide()
        self.parcelas_combobox.hide()
        # Conectando a combobox à função
        self.pagamento_bem_combobox.currentIndexChanged.connect(self.verificar_pagamento_bem)

# Publicação jornal
        self.publicacao_jornal_label, self.publicacao_jornal_combobox = self.criar_campo_combobox("Juíz determinou publicação no jornal", ["Sim", "Não"], self.main_layout)

# Lance parcelado ou só proposta
        self.determinacao_proposta_label, self.determinacao_proposta_field = self.criar_campo_data("Juíz permitiu lance parcelado ou só proposta", " ", self.main_layout)

# O que o juíz diz sobre : :
        self.label_oque_diz_juiz = QLabel("O que o juíz diz sobre :", self)
        self.label_oque_diz_juiz.setStyleSheet("font-size: 17px; color: #333;")
        self.main_layout.addWidget(self.label_oque_diz_juiz)

# IPTU (Dívida ativa e não ativa): ?
        self.sobre_iptu_total_label, self.sobre_iptu_total_combobox = self.criar_campo_combobox("Determinação sobre subrogação dos débitos IPTU", [" ", "Serão sub rogados", "Não serão nub rogados"], self.main_layout)

# Juíz Valor total IPTU 
        self.iptu_total_label, self.iptu_total_field = self.criar_campo_data("Valor total da dívida de IPTU (Dívida ativa e não ativa)", "Dívida ativa e não ativa ", self.main_layout)

# Condominio (Dívida ativa e não ativa): ?
        self.sobre_condominio_total_label, self.sobre_condominio_total_combobox = self.criar_campo_combobox("Determinação sobre subrogação dos débitos condominio", [" ", "Serão sub rogados", "Não serão nub rogados"], self.main_layout)

# Juíz Valor total condominio 
        self.condominio_total_label, self.condominio_total_field = self.criar_campo_data("Valor total das dívidas de Condomínio (Inclui todo débito exequendo condominial)", "Dívida ativa e não ativa ", self.main_layout)


# Demanda processual
        self.debito_exequendo_label, self.debito_exequendo_field = self.criar_campo_data("Débito da Demanda Processual", " ", self.main_layout)

# Data Demanda processual
        self.data_debito_exequendo_label, self.data_debito_exequendo_field = self.criar_campo_data("Data do débito da Demanda Processual", " ", self.main_layout)

# Ultimo Condominio
        self.ultimo_condominio_label, self.ultimo_condominio_field = self.criar_campo_data("Débito do ultimo condomínio", " ", self.main_layout)

# Data Ultimo condomínio
        self.data_ultimo_condominio_label, self.data_ultimo_condominio_field = self.criar_campo_data("Data do débito do ultimo condomínio", " ", self.main_layout)

# Juíz manifestou sobre propter rem ?
        self.manifestacao_propter_label, self.manifestacao_propter_combobox = self.criar_campo_combobox("O juíz se manifestou sobre o  saldo dos débitos Propter Rem que superem o valor da arrematação", [" ", "Sim", "Não"], self.main_layout)
        self.manifestou_oq_label, self.manifestou_oq_field = self.criar_campo_data("Qual a manifestação", " ", self.main_layout)
        self.manifestou_oq_label.hide()
        self.manifestou_oq_field.hide()

# Onde o juiz mandou depositar a comissão
        self.resumo_processo_label, self.resumo_processo_combobox = self.criar_campo_combobox("Onde o juiz mandou depositar a comissão", [" ", "Autos", "Direto para o leiloeiro"], self.main_layout)

# Resumo do processo e observações até aqui
        self.resumo_processo_label, self.resumo_processo_field = self.criar_campo_data("Resumo do processo e observações até aqui", " ", self.main_layout)
        self.resumo_processo_field.setStyleSheet("height: 17px; min-height: 200px; font-size: 16px")

# Ônus e Gravames* vide matrícula do imóvel
        self.onus_label, self.onus_field = self.criar_campo_data("Ônus e Gravames* vide matrícula do imóvel", " ", self.main_layout)
        self.onus_field.setStyleSheet("height: 17px; min-height: 200px; font-size: 16px")

        self.descricao_bem_label, self.descricao_bem_field = self.criar_campo_data("Descrição completa do bem", " ", self.main_layout)
        self.descricao_bem_field.setStyleSheet("height: 17px; min-height: 200px; font-size: 16px")

# Quadrados informativos
        self.frames_layout = QHBoxLayout()
        labels = ["Todas as Partes e Envolvidos", "Intimar pelo DJE (Representados)", "Intimar pela 'AR' (Não representados)", "Varas e Juízes a serem Intimados (por terem penhora gravada na matrícula)"]
        # Adiciona 5 frames ao layout
        for i in range(4):
            # Frame com borda
            frame = QFrame(self)
            frame.setFrameShape(QFrame.Box)
            frame.setStyleSheet("border: 1px solid black;")
            frame.setFixedSize(200, 200)  # Tamanho fixo dos frames

            # Layout vertical para frame e label
            frame_layout = QVBoxLayout(frame)
            
            # Label personalizada para cada frame com base na lista
            label = QLabel(labels[i], self)
            label.setAlignment(Qt.AlignTop | Qt.AlignCenter)  # Alinha no topo e centraliza horizontalmente
            label.setWordWrap(True)  # Permite a quebra de linha dentro da label
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            frame_layout.addWidget(label)
            
            # Adiciona o frame ao layout horizontal
            self.frames_layout.addWidget(frame)

        # Adiciona o layout horizontal ao layout principal
        self.main_layout.addLayout(self.frames_layout)

# Informações do Processo
        self.label_informacoes_do_bem = QLabel("Informações do Bem", self)
        self.label_informacoes_do_bem.setStyleSheet("color: #333; font-size: 30px")
        self.main_layout.addWidget(self.label_informacoes_do_bem)

# Campo "CEP"
        self.cep_bem_label, self.cep_bem_field = self.criar_campo_data("CEP", "Digite o CEP", self.main_layout)

# Buscar endereço
        self.buscar_endereco_button = QPushButton("Buscar Endereço", self)
#        self.buscar_endereco_button.clicked.connect(self.buscar_endereco)
        self.main_layout.addWidget(self.buscar_endereco_button)

# logradouro
        self.logradouro_bem_label, self.logradouro_bem_field = self.criar_campo_data("Logradouro :", " ", self.main_layout)

# numero
        self.num_bem_label, self.num_bem_field = self.criar_campo_data("Número :", " ", self.main_layout)

# Complemento
        self.complemento_bem_label, self.complemento_bem_field = self.criar_campo_data("Complemento :", " ", self.main_layout)

# Bairro
        self.bairro_bem_label, self.bairro_bem_field = self.criar_campo_data("Bairro :", " ", self.main_layout)

# Zona (Região):
        self.combo_zona_label, self.combo_zona_fields = self.criar_campo_combobox("UF", ["Centro", "Zona Norte", "Zona Sul", "Zona Leste", "Zona Oeste"], self.main_layout)

# Cidade
        self.cidade_bem_label, self.cidade_bem_field = self.criar_campo_data("Cidade :", " ", self.main_layout)

# UF
        self.combo_uf_label, self.combo_uf_fields = self.criar_campo_combobox("UF", ["SP", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SE", "TO"], self.main_layout)

# Matricula
        self.matricula_bem_label, self.matricula_bem_field = self.criar_campo_data("Matrícula :", " ", self.main_layout)

# Inscrição Imobiliária
        self.inscricao_imobiliaria_bem_label, self.inscricao_imobiliaria_bem_field = self.criar_campo_data("Inscrição Imobiliária :", " ", self.main_layout)

# Cartório
        self.cartorio_bem_label, self.cartorio_bem_field = self.criar_campo_data("Cartório :", " ", self.main_layout)

# Valor de Avaliação
        self.valor_avaliacao_bem_label, self.valor_avaliacao_bem_field = self.criar_campo_data("Valor de Avaliação :", " ", self.main_layout)

# Valor de Avaliação (Atualizada)
        self.valor_avaliacao_atz_data_bem_label, self.valor_avaliacao_atz_data_bem_field = self.criar_campo_data("Valor de Avaliação (Atualizada) :", "R$ 0,00", self.main_layout)

# Área Útil
        self.area_util_bem_label, self.area_util_bem_field = self.criar_campo_data("Área Útil :", " ", self.main_layout)

# Área Total
        self.area_total_bem_label, self.area_total_bem_field = self.criar_campo_data("Área Total :", " ", self.main_layout)

# Qual a porcentagem de desconto da 2ª Praça
        self.porcentagem_segundapraca_bem_label, self.porcentagem_segundapraca_bem_field = self.criar_campo_data("Porcentagem da 2ª Praça :", " ", self.main_layout)

# Valor do Propter Rem
        self.propter_rem_total_label, self.propter_rem_total_field = self.criar_campo_data("Valor do Propter Rem :", " ", self.main_layout)
        self.propter_rem_total_field.setReadOnly(True)

# Valor da 2ª Praça (Calculado automaticamente)
        self.valor_segunda_praca_bem_label, self.valor_segunda_praca_bem_field = self.criar_campo_data("Valor da 2ª Praça :", "R$ 0,00", self.main_layout)
        self.valor_segunda_praca_bem_field.setReadOnly(True)

# Comparação em Porcentagem
        self.comparacao_percentual_label, self.comparacao_percentual_field = self.criar_campo_data("Comparação Percentual (Propter Rem vs 2ª Praça):", "0%", self.main_layout)
        self.comparacao_percentual_field.setReadOnly(True)

# Caracteristicas do imóvel
        self.label_caracteristicas_do_bem = QLabel("Informações do Bem", self)
        self.main_layout.addWidget(self.label_caracteristicas_do_bem)
        self.checkbox_academia = self.criar_campo_checkbox("Academia", self.main_layout)
        self.checkbox_churrasqueira = self.criar_campo_checkbox("Churrasqueira", self.main_layout)
        self.checkbox_cinema = self.criar_campo_checkbox("Cinema", self.main_layout)
        self.checkbox_espaco_gourmet = self.criar_campo_checkbox("Espaço Gourmet", self.main_layout)
        self.checkbox_jardim = self.criar_campo_checkbox("Jardim", self.main_layout)
        self.checkbox_piscina = self.criar_campo_checkbox("Piscina", self.main_layout)
        self.checkbox_playground = self.criar_campo_checkbox("Playground", self.main_layout)
        self.checkbox_quadra_squash = self.criar_campo_checkbox("Quadra de Squash", self.main_layout)
        self.checkbox_quadra_tenis = self.criar_campo_checkbox("Quadra de Tênis", self.main_layout)
        self.checkbox_quadra_poliesportiva = self.criar_campo_checkbox("Quadra Poliesportiva", self.main_layout)
        self.checkbox_salao_festa = self.criar_campo_checkbox("Salão de Festa", self.main_layout)
        self.checkbox_acesso_deficiente = self.criar_campo_checkbox("Acesso para Deficiente", self.main_layout)
        self.checkbox_bicicletario = self.criar_campo_checkbox("Bicicletário", self.main_layout)
        self.checkbox_coworking = self.criar_campo_checkbox("Coworking", self.main_layout)
        self.checkbox_elevador = self.criar_campo_checkbox("Elevador", self.main_layout)
        self.checkbox_lavanderia = self.criar_campo_checkbox("Lavanderia", self.main_layout)
        self.checkbox_sauna = self.criar_campo_checkbox("Sauna", self.main_layout)
        self.checkbox_spa = self.criar_campo_checkbox("Spa", self.main_layout)
        self.checkbox_condominio_fechado = self.criar_campo_checkbox("Condomínio Fechado", self.main_layout)
        self.checkbox_portao_eletrico = self.criar_campo_checkbox("Portão Elétrico", self.main_layout)
        self.checkbox_portaria = self.criar_campo_checkbox("Portaria", self.main_layout)
        self.manifestacao_propter_combobox.currentIndexChanged.connect(self.mostrar_manifestou_oq)

# Tipo de imóvel'
        self.tipo_imovel_label, self.tipo_imovel_fields = self.criar_campo_combobox("Tipo de imóvel", [" ", "Casa", "Casa em Condomínio", "Apartamento", "Sala Comercial", "Terreno", "Terreno em Condomínio", "Prédio Comercial", "Imóvel Rural", "Vaga de Garagem"], self.main_layout)
        
# Vagas'
        self.vagas_label, self.vagas_fields = self.criar_campo_combobox("Tipo de imóvel", [str(i) for i in range(1, 11)], self.main_layout)


# Banheiros'
        self.banheiros_label, self.banheiros_fields = self.criar_campo_combobox("Banheiros", [str(i) for i in range(1, 11)], self.main_layout)

# Quartos
        self.quartos_label, self.quartos_fields = self.criar_campo_combobox("Quartos", [str(i) for i in range(1, 11)], self.main_layout)

# Suites
        self.suites_label, self.suites_fields = self.criar_campo_combobox("Suítes", [str(i) for i in range(1, 11)], self.main_layout)

# Ocupado?'
        self.ocupado_label, self.ocupado_fields = self.criar_campo_combobox("O imóvel está ocupado ?", [" ", "Sim", "Não"], self.main_layout)

# Qual a finalidade do imóvel ?
        self.combo_finalidade_label, self.combo_finalidade_fields = self.criar_campo_combobox("Qual a finalidade do imóvel", ["Residencial", "Comercial"], self.main_layout)


# Tem condomínio?'
        self.tem_condominio_label, self.combo_tem_condominio = self.criar_campo_combobox("Tem condomínio", [" ", "Sim", "Não"], self.main_layout)


# Condominio Que valor (mensal)
        self.label_valor_condominio, self.lineedit_valor_condominio = self.criar_campo_data("Que valor (mensal)", " ", self.main_layout)
        self.label_valor_condominio.hide()
        self.lineedit_valor_condominio.hide()

#Avaliação
        self.label_comparacao_mercadologica = QLabel("Avaliação mercadológica ", self)
        self.label_comparacao_mercadologica.setStyleSheet("color: #333; font-size: 30px")
        self.main_layout.addWidget(self.label_comparacao_mercadologica)

        # Botão para exibir/ocultar o formulário avaliacao
        self.toggle_form_button = QPushButton("Fazer Avaliação", self)
        self.toggle_form_button.clicked.connect(self.toggle_formulario_avaliacao)
        self.main_layout.addWidget(self.toggle_form_button)

# Frame Formulário
        # Criação do QFrame com borda para o formulário avaliacao (inicialmente oculto)
        self.formulario_avaliacao_frame = QFrame(self)
        self.formulario_avaliacao_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #4CAF50; 
                border-radius: 5px; 
                padding: 10px;
                background-color: #f0f0f0;
            }
            QFrame > QWidget { 
                border: none;
            }
        """)
        self.formulario_avaliacao_frame.hide()

        # Layout para os widgets do formulário avaliacao dentro do QFrame
        self.formulario_avaliacao_layout = QVBoxLayout(self.formulario_avaliacao_frame)

# Campos ao formulário avaliacao

        # Exemplo de uso para criar o primeiro conjunto de campos comparativos:
        self.label_titulo_avaliacao_i, self.link_avaliacao_i_label, self.link_avaliacao_i_field, \
        self.metragem_avaliacao_i_label, self.metragem_avaliacao_i_field, \
        self.valor_avaliacao_i_label, self.valor_avaliacao_i_field = \
        self.criar_campo_comparativo("1º Imóvel", "Link do 1º Imóvel", "M² do 1º Imóvel", "Valor de Avaliação do 1º Imóvel", self.formulario_avaliacao_layout)

        # Exemplo de uso para criar o primeiro conjunto de campos comparativos:
        self.label_titulo_avaliacao_ii, self.link_avaliacao_ii_label, self.link_avaliacao_ii_field, \
        self.metragem_avaliacao_ii_label, self.metragem_avaliacao_ii_field, \
        self.valor_avaliacao_ii_label, self.valor_avaliacao_ii_field = \
        self.criar_campo_comparativo("2º Imóvel", "Link do 2º Imóvel", "M² do 2º Imóvel", "Valor de Avaliação do 2º Imóvel", self.formulario_avaliacao_layout)

        # Exemplo de uso para criar o primeiro conjunto de campos comparativos:
        self.label_titulo_avaliacao_iii, self.link_avaliacao_iii_label, self.link_avaliacao_iii_field, \
        self.metragem_avaliacao_iii_label, self.metragem_avaliacao_iii_field, \
        self.valor_avaliacao_iii_label, self.valor_avaliacao_iii_field = \
        self.criar_campo_comparativo("3º Imóvel", "Link do 3º Imóvel", "M² do 3º Imóvel", "Valor de Avaliação do 3º Imóvel", self.formulario_avaliacao_layout)

# Valor médio do metro quadrado
        self.valor_medio_label, self.valor_medio_field = self.criar_campo_data("Valor Médio do metro quadrado (Avaliado)", "", self.formulario_avaliacao_layout)
        self.valor_medio_field.setReadOnly(True)

# Valor de Mercado
        self.valor_mercado_label, self.valor_mercado_field = self.criar_campo_data("Valor de Mercado :", "", self.formulario_avaliacao_layout)
        self.valor_mercado_field.setReadOnly(True)

# Resultado da Comparação (Porcentagem)
        self.resultado_comparacao_label, self.resultado_comparacao_field = self.criar_campo_data("Resultado da Comparação:", "0%", self.formulario_avaliacao_layout)
        self.resultado_comparacao_field.setReadOnly(True)

# Probabilidade com base na comparação
        self.probabilidade_label, self.probabilidade_field = self.criar_campo_data("Probabilidade:", "Indefinido", self.formulario_avaliacao_layout)
        self.probabilidade_field.setReadOnly(True)

# Adicionando o QFrame ao layout principal
        self.main_layout.addWidget(self.formulario_avaliacao_frame)
        self.formulario_avaliacao_frame.hide()

# Valor da 2ª Praça (Calculado automaticamente)
        self.valor_segunda_praca_bem_label, self.valor_segunda_praca_bem_field_ii = self.criar_campo_data("Valor da 2ª Praça :", "R$ 0,00", self.main_layout)
        self.valor_segunda_praca_bem_field_ii.setReadOnly(True)

# Conexões
        self.iptu_total_field.textChanged.connect(self.update_propter_rem_total)
        self.condominio_total_field.textChanged.connect(self.update_propter_rem_total)
        self.iptu_total_field.textChanged.connect(self.calcular_comparacao_percentual)
        self.propter_rem_total_field.textChanged.connect(self.calcular_comparacao_percentual)
        self.valor_segunda_praca_bem_field.textChanged.connect(self.calcular_comparacao_percentual)
        self.valor_avaliacao_atz_data_bem_field.textChanged.connect(self.calcular_valor_segunda_praca)
        self.porcentagem_segundapraca_bem_field.textChanged.connect(self.calcular_valor_segunda_praca)
        self.valor_segunda_praca_bem_field.textChanged.connect(self.calcular_comparacao)
        self.valor_mercado_field.textChanged.connect(self.calcular_comparacao)
        self.valor_segunda_praca_bem_field.textChanged.connect(self.calcular_comparacao_percentual)
        self.metragem_avaliacao_i_field.textChanged.connect(self.update_valor_medio)
        self.valor_avaliacao_ii_field.textChanged.connect(self.update_valor_medio)
        self.metragem_avaliacao_ii_field.textChanged.connect(self.update_valor_medio)
        self.valor_avaliacao_ii_field.textChanged.connect(self.update_valor_medio)
        self.metragem_avaliacao_iii_field.textChanged.connect(self.update_valor_medio)
        self.valor_avaliacao_iii_field.textChanged.connect(self.update_valor_medio)
        self.area_total_bem_field.textChanged.connect(self.update_valor_mercado)
        self.valor_medio_field.textChanged.connect(self.update_valor_mercado)
        self.iptu_total_field.textChanged.connect(self.update_valor_segunda_praca)
        self.condominio_total_field.textChanged.connect(self.update_valor_segunda_praca)
        self.valor_segunda_praca_bem_field.textChanged.connect(self.update_valor_segunda_praca)
        self.pagamento_bem_combobox.currentIndexChanged.connect(self.verificar_pagamento_bem)
        self.combo_tem_condominio.currentIndexChanged.connect(self.update_condominio_visibility)
        self.quantas_praca_combobox.currentIndexChanged.connect(self.atualizar_visibilidade_pracas)
        self.combo_ha_incapaz.currentIndexChanged.connect(self.validar_porcentagem)
        self.porcentagem_segundapraca_bem_field.editingFinished.connect(self.validar_porcentagem)
        self.valor_real_segunda_praca_label = None
        self.valor_real_segunda_praca_field = None
    def mostrar_manifestou_oq(self):
        if self.manifestacao_propter_combobox.currentText() == "Sim":
                self.manifestou_oq_label.show()
                self.manifestou_oq_field.show()
        else:
                self.manifestou_oq_label.hide()
                self.manifestou_oq_field.hide()
    def buscar_endereco(self):
        cep = self.cep_bem_field.text()
        if cep:
            try:
                response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
                data = response.json()

                if "erro" not in data:
                    self.logradouro_bem_field.setText(data.get("logradouro", ""))
                    self.bairro_bem_field.setText(data.get("bairro", ""))
                    self.cidade_bem_field.setText(data.get("localidade", ""))
                    self.combo_uf_fields.setCurrentText(data.get("uf", ""))
                else:
                    QMessageBox.warning(self, "Erro", "CEP não encontrado.")
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao buscar CEP: {str(e)}")
        else:
            QMessageBox.warning(self, "Aviso", "Por favor, insira um CEP válido.")
    def update_propter_rem_total(self):
        iptu_total = self.convert_to_float(self.iptu_total_field.text())
        condominio_total = self.convert_to_float(self.condominio_total_field.text())

        if iptu_total is not None and condominio_total is not None:
            propter_rem_total = iptu_total + condominio_total
            self.propter_rem_total_field.setText(f"R$ {propter_rem_total:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
    def calcular_comparacao_percentual(self):
        try:
            valor_propter_rem = float(self.propter_rem_total_field.text().replace("R$", "").replace(".", "").replace(",", ".").strip())
            valor_segunda_praca = float(self.valor_segunda_praca_bem_field.text().replace("R$", "").replace(".", "").replace(",", ".").strip())
            
            if valor_segunda_praca == 0:
                porcentagem = 0
            else:
                porcentagem = (valor_propter_rem / valor_segunda_praca) * 100

            porcentagem_formatada = f"{porcentagem:.2f}%"



            # Definir a cor do texto com base na porcentagem
            if porcentagem > 100:
                self.comparacao_percentual_field.setStyleSheet("color: red;")
            else:
                self.comparacao_percentual_field.setStyleSheet("color: green;")

            self.comparacao_percentual_field.setText(porcentagem_formatada)

        except ValueError:
            self.comparacao_percentual_field.setText("")   
    def convert_to_float(self, value):
        try:
            return float(value.replace('.', '').replace(',', '.'))
        except ValueError:
            return None
    def calcular_valor_segunda_praca(self):
        try:
                # Substitui os pontos (separador de milhar) por nada e a vírgula (separador decimal) por ponto
                valor_avaliacao = float(self.valor_avaliacao_atz_data_bem_field.text().replace('R$', '').replace('.', '').replace(',', '.').strip())
                porcentagem = float(self.porcentagem_segundapraca_bem_field.text().strip()) / 100.0
                valor_segunda_praca = valor_avaliacao * porcentagem
                self.valor_segunda_praca_bem_field.setText(f"R$ {valor_segunda_praca:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
                self.valor_segunda_praca_bem_field_ii.setText(f"R$ {valor_segunda_praca:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        except ValueError:
                # Limpa o campo se houver erro na conversão
                self.valor_segunda_praca_bem_field_ii.clear()
                self.valor_segunda_praca_bem_field_ii.clear()
    def formatar_para_moeda(self):
        texto = self.valor_avaliacao_atz_data_bem_field.text().replace('R$', '').replace('.', '').replace(',', '')
        if texto.isdigit():
                valor_formatado = "R$ {:,.2f}".format(int(texto) / 100)
                # Corrige a formatação para o padrão brasileiro
                valor_formatado = valor_formatado.replace(',', 'X').replace('.', ',').replace('X', '.')
                self.valor_avaliacao_atz_data_bem_field.blockSignals(True)
                self.valor_avaliacao_atz_data_bem_field.setText(valor_formatado)
                self.valor_avaliacao_atz_data_bem_field.blockSignals(False)
    def validar_porcentagem(self):
        ha_incapaz = self.combo_ha_incapaz.currentText()
        porcentagem_text = self.porcentagem_segundapraca_bem_field.text()
        
        if ha_incapaz == "Sim":
            if porcentagem_text.isdigit():
                porcentagem = int(porcentagem_text)
                if 80 <= porcentagem <= 100:
                    QMessageBox.information(self, "Porcentagem válida", "Porcentagem válida")
                else:
                    self.porcentagem_segundapraca_bem_field.clear()
                    QMessageBox.warning(self, "Valor incorreto", "Valor incorreto, como há incapaz, só é possível de 80 a 100!")
            else:
                if porcentagem_text:  # se não for vazio
                    self.porcentagem_segundapraca_bem_field.clear()
                    QMessageBox.warning(self, "Valor incorreto", "Valor incorreto, como há incapaz, só é possível de 80 a 100!")
    def update_dates(self, source_field):
        source_text = source_field.text()
        if not source_text:
            return

        source_date = QDate.fromString(source_text, "dd/MM/yy")
        if not source_date.isValid():
            return

        # Verifica qual campo foi alterado e atualiza os outros
        if source_field == self.inicio_ipraca_field:
            fim_ipraca_date = source_date.addDays(3)
            inicio_iipraca_date = fim_ipraca_date
            fim_iipraca_date = fim_ipraca_date.addDays(20)
            self.fim_ipraca_field.setText(fim_ipraca_date.toString("dd/MM/yy"))
            self.inicio_iipraca_field.setText(inicio_iipraca_date.toString("dd/MM/yy"))
            self.fim_iipraca_field.setText(fim_iipraca_date.toString("dd/MM/yy"))

        elif source_field == self.fim_ipraca_field:
            inicio_ipraca_date = source_date.addDays(-3)
            inicio_iipraca_date = source_date
            fim_iipraca_date = source_date.addDays(20)
            self.inicio_ipraca_field.setText(inicio_ipraca_date.toString("dd/MM/yy"))
            self.inicio_iipraca_field.setText(inicio_iipraca_date.toString("dd/MM/yy"))
            self.fim_iipraca_field.setText(fim_iipraca_date.toString("dd/MM/yy"))

        elif source_field == self.inicio_iipraca_field:
            fim_ipraca_date = source_date
            inicio_ipraca_date = fim_ipraca_date.addDays(-3)
            fim_iipraca_date = fim_ipraca_date.addDays(20)
            self.inicio_ipraca_field.setText(inicio_ipraca_date.toString("dd/MM/yy"))
            self.fim_ipraca_field.setText(fim_ipraca_date.toString("dd/MM/yy"))
            self.fim_iipraca_field.setText(fim_iipraca_date.toString("dd/MM/yy"))

        elif source_field == self.fim_iipraca_field:
            inicio_iipraca_date = source_date.addDays(-20)
            fim_ipraca_date = inicio_iipraca_date
            inicio_ipraca_date = fim_ipraca_date.addDays(-3)
            self.inicio_ipraca_field.setText(inicio_ipraca_date.toString("dd/MM/yy"))
            self.fim_ipraca_field.setText(fim_ipraca_date.toString("dd/MM/yy"))
            self.inicio_iipraca_field.setText(inicio_iipraca_date.toString("dd/MM/yy"))
    def atualizar_visibilidade_pracas(self):
        # Obter o valor selecionado na combobox
        valor = self.quantas_praca_combobox.currentText()

        # Ocultar todos os campos inicialmente
        self.inicio_ipraca_label.hide()
        self.inicio_ipraca_field.hide()
        self.fim_ipraca_label.hide()
        self.fim_ipraca_field.hide()
        self.inicio_iipraca_label.hide()
        self.inicio_iipraca_field.hide()
        self.fim_iipraca_label.hide()
        self.fim_iipraca_field.hide()
        self.inicio_iiipraca_label.hide()
        self.inicio_iiipraca_field.hide()
        self.fim_iiipraca_label.hide()
        self.fim_iiipraca_field.hide()

        # Mostrar os campos de acordo com a seleção
        if valor == "1 Praça":
                # Exibe apenas a primeira praça
                self.inicio_ipraca_label.show()
                self.inicio_ipraca_field.show()
                self.fim_ipraca_label.show()
                self.fim_ipraca_field.show()

        elif valor == "2 Praças":
                # Exibe a primeira e segunda praça
                self.inicio_ipraca_label.show()
                self.inicio_ipraca_field.show()
                self.fim_ipraca_label.show()
                self.fim_ipraca_field.show()
                self.inicio_iipraca_label.show()
                self.inicio_iipraca_field.show()
                self.fim_iipraca_label.show()
                self.fim_iipraca_field.show()

        elif valor == "3 Praças":
                # Exibe todas as praças
                self.inicio_ipraca_label.show()
                self.inicio_ipraca_field.show()
                self.fim_ipraca_label.show()
                self.fim_ipraca_field.show()
                self.inicio_iipraca_label.show()
                self.inicio_iipraca_field.show()
                self.fim_iipraca_label.show()
                self.fim_iipraca_field.show()
                self.inicio_iiipraca_label.show()
                self.inicio_iiipraca_field.show()
                self.fim_iiipraca_label.show()
                self.fim_iiipraca_field.show()
    def update_condominio_visibility(self):
        index = self.main_layout.indexOf(self.combo_tem_condominio) + 1
        self.main_layout.insertWidget(index, self.label_valor_condominio)
        self.main_layout.insertWidget(index + 1, self.lineedit_valor_condominio)

        if self.combo_tem_condominio.currentText().strip() == "Sim":
            self.label_valor_condominio.show()
            self.lineedit_valor_condominio.show()
        else:
            self.label_valor_condominio.hide()
            self.lineedit_valor_condominio.hide()
    def toggle_formulario_avaliacao(self):
        if self.formulario_avaliacao_frame.isVisible():
            self.formulario_avaliacao_frame.hide()
            self.toggle_form_button.setText("Mostrar Formulário avaliacao")
        else:
            self.formulario_avaliacao_frame.show()
            self.toggle_form_button.setText("Ocultar Formulário avaliacao")
    def open_partes_window(self):
        processo = self.processo_field.text()
        if processo:
            self.partes_window = PartesWindow(processo)
            self.partes_window.show()
        else:
            QMessageBox.warning(self, "Erro", "Por favor, insira um número de processo válido.")
    def update_valor_medio(self):
        try:
            metragem01 = float(self.metragem_avaliacao_i_field.text() or 0)
            valor01 = float(self.metragem_avaliacao_i_field.text() or 0)
            metragem02 = float(self.metragem_avaliacao_ii_field.text() or 0)
            valor02 = float(self.valor_avaliacao_ii_field.text() or 0)
            metragem03 = float(self.metragem_avaliacao_iii_field.text() or 0)
            valor03 = float(self.valor_avaliacao_iii_field.text() or 0)

            sqm01 = valor01 / metragem01 if metragem01 else 0
            sqm02 = valor02 / metragem02 if metragem02 else 0
            sqm03 = valor03 / metragem03 if metragem03 else 0

            valor_medio = (sqm01 + sqm02 + sqm03) / 3 if (metragem01 or metragem02 or metragem03) else 0

            self.valor_medio_field.setText(f"{valor_medio:.2f}")

        except ValueError:
            self.valor_medio_field.setText("Erro")
    def update_valor_mercado(self):
        try:
            valor_medio = float(self.valor_medio_field.text() or 0)
            area_total = float(self.area_total_bem_field.text() or 0)

            valor_mercado = valor_medio * area_total

            self.valor_mercado_field.setText(f"{valor_mercado:.2f}")

        except ValueError:
            self.valor_mercado_field.setText("Erro")
    def calcular_comparacao(self):
        try:
            # Leitura dos valores como strings
            valor_segunda_praca_text = self.valor_segunda_praca_bem_field.text().replace('R$', '').replace('.', '').replace(',', '').strip()
            valor_mercado_text = self.valor_mercado_field.text().replace('R$', '').replace('.', '').replace(',', '').strip()
            valor_propter_rem_text = self.propter_rem_total_field.text().replace('R$', '').replace('.', '').replace(',', '').strip()

            # Verificar se os campos estão vazios ou formatados incorretamente
            if not valor_segunda_praca_text or not valor_mercado_text or not valor_propter_rem_text:
                self.resultado_comparacao_field.setText("0%")
                self.probabilidade_field.setText("Indefinido")
                return

            # Conversão para inteiros
            valor_segunda_praca = int(valor_segunda_praca_text)
            valor_mercado = int(valor_mercado_text)
            valor_propter_rem = int(valor_propter_rem_text)

            # Verificar qual valor é maior entre valor_segunda_praca e valor_propter_rem
            valor_comparacao = max(valor_segunda_praca, valor_propter_rem)

            # Verificar se o valor de mercado é 0 para evitar divisão por zero
            if valor_mercado == 0:
                self.resultado_comparacao_field.setText("0%")
                self.probabilidade_field.setText("Indefinido")
                return

            # Calcular a porcentagem da comparação corretamente
            porcentagem = (valor_comparacao * 100) // valor_mercado
            self.resultado_comparacao_field.setText(f"{porcentagem}%")

            # Definir o texto da probabilidade baseado na porcentagem
            if 120 <= porcentagem <= 200:
                self.probabilidade_field.setText("Muito improvável (de 100% à 120%)")
            if 100 <= porcentagem <= 120:
                self.probabilidade_field.setText("Improvável (de 100% à 120%)")
            elif 80 <= porcentagem < 100:
                self.probabilidade_field.setText("Pouco provável (de 80% à 10%)")
            elif 70 <= porcentagem < 80:
                self.probabilidade_field.setText("Provável (de 70% à 80%)")
            elif 60 <= porcentagem < 70:
                self.probabilidade_field.setText("Bem provável (de 60% à 70%)")
            elif 50 <= porcentagem < 60:
                self.probabilidade_field.setText("Muito provável (de 30% à 60%)")
            elif 35 <= porcentagem < 50:
                self.probabilidade_field.setText("Super provável (de 35$ à 50%)")

            elif 20 <= porcentagem < 35:
                self.probabilidade_field.setText("Praticamente vendido (de 20$ à 35%)")
            elif 0 <= porcentagem < 20:
                self.probabilidade_field.setText("Erro confira os valores (de 0% à 20%)")
            else:
                self.probabilidade_field.setText("Indefinido")

        except ValueError as e:
            print(f"Erro ao converter valores: {e}")  # Depuração de erro
            self.resultado_comparacao_field.setText("Erro")
            self.probabilidade_field.setText("Indefinido")
    def update_valor_segunda_praca(self):
        try:
            propter_rem_valor = float(self.propter_rem_total_field.text().replace('R$', '').replace('.', '').replace(',', '.'))
            valor_segunda_praca = float(self.valor_segunda_praca_bem_field.text().replace('R$', '').replace('.', '').replace(',', '.'))

            # Verifica se o campo "Valor Real da Segunda Praça" já existe
            if self.valor_real_segunda_praca_label is None and propter_rem_valor > valor_segunda_praca:
                # Cria o campo "Valor Real da Segunda Praça" se o valor do propter rem for maior
                self.valor_real_segunda_praca_label = QLabel("Valor Real da Segunda Praça (é o maior valor entre o calor da 2ª Praça, comparado com valor das dívidas Propter REM):", self)
                self.valor_real_segunda_praca_label.setStyleSheet("font-size: 16px; color: #333;")
                self.valor_real_segunda_praca_field = QLineEdit(self)
                self.valor_real_segunda_praca_field.setReadOnly(True)  # Campo somente leitura
                self.valor_real_segunda_praca_field.setText(locale.currency(propter_rem_valor, grouping=True))

                # Adiciona os novos campos ao layout
                self.main_layout.addWidget(self.valor_real_segunda_praca_label)
                self.main_layout.addWidget(self.valor_real_segunda_praca_field)
            elif self.valor_real_segunda_praca_field:
                # Atualiza o valor do campo "Valor Real da Segunda Praça"
                if propter_rem_valor > valor_segunda_praca:
                    self.valor_real_segunda_praca_field.setText(locale.currency(propter_rem_valor, grouping=True))
                else:
                    # Remove os campos se o valor do propter rem não for maior
                    self.main_layout.removeWidget(self.valor_real_segunda_praca_label)
                    self.main_layout.removeWidget(self.valor_real_segunda_praca_field)
                    self.valor_real_segunda_praca_label.deleteLater()
                    self.valor_real_segunda_praca_field.deleteLater()
                    self.valor_real_segunda_praca_label = None
                    self.valor_real_segunda_praca_field = None

        except ValueError:
            # Lidando com valores inválidos
            pass
    def verificar_pagamento_bem(self):
        if self.pagamento_bem_combobox.currentText() == "Só a vista":
                self.parcelas_label.hide()
                self.parcelas_combobox.hide()
        else:
                self.parcelas_label.show()
                self.parcelas_combobox.show()
    def validar_porcentagem(self):
        ha_incapaz = self.combo_ha_incapaz.currentText()
        porcentagem_text = self.porcentagem_segundapraca_bem_field.text()
        
        if ha_incapaz == "Sim":
            if porcentagem_text.isdigit():
                porcentagem = int(porcentagem_text)
                if 80 <= porcentagem <= 100:
                    QMessageBox.information(self, "Porcentagem válida", "Porcentagem válida")
                else:
                    self.porcentagem_segundapraca_bem_field.clear()
                    QMessageBox.warning(self, "Valor incorreto", "Valor incorreto, como há incapaz, só é possível de 80 a 100!")
            else:
                if porcentagem_text:  # se não for vazio
                    self.porcentagem_segundapraca_bem_field.clear()
                    QMessageBox.warning(self, "Valor incorreto", "Valor incorreto, como há incapaz, só é possível de 80 a 100!")
    def save_to_db_dynamic(self):
        processo_field = self.processo_field.text()  # 1
        link_processo_field = self.link_processo_field.text()  # 2
        acao_field = self.acao_field.text()  # 3
        vara_field = self.vara_field.text()  # 4
        foro_field = self.foro_field.text()  # 5
        comarca_field = self.comarca_field.text()  # 6
        email_cartorio_field = self.email_cartorio_field.text()  # 7
        nome_juiz_field = self.nome_juiz_field.text()  # 8
        oq_leiloado_combobox = self.oq_leiloado_combobox.currentText()  # 9
        ha_alienacao_combobox = self.ha_alienacao_combobox.currentText()  # 10
        combo_ha_incapaz = self.combo_ha_incapaz.currentText()  # 11
        ha_usufrutuario_combobox = self.ha_usufrutuario_combobox.currentText()  # 12
        representacao_processual_field = self.representacao_processual_field.text()  # 13
        representacao_processual_field_folhas = self.representacao_processual_field_folhas.text()  # 14
        representacao_processual_field_situacao = self.representacao_processual_field_situacao.text()  # 15
        citacoes_field = self.citacoes_field.text()  # 16
        citacoes_field_folhas = self.citacoes_field_folhas.text()  # 17
        citacoes_field_situacao = self.citacoes_field_situacao.text()  # 18
        sentenca_field = self.sentenca_field.text()  # 19
        sentenca_field_folhas = self.sentenca_field_folhas.text()  # 20
        sentenca_field_situacao = self.sentenca_field_situacao.text()  # 21
        transito_julgado_field = self.transito_julgado_field.text()  # 22
        transito_julgado_field_folhas = self.transito_julgado_field_folhas.text()  # 23
        transito_julgado_field_situacao = self.transito_julgado_field_situacao.text()  # 24
        cumprimento_sentenca_field = self.cumprimento_sentenca_field.text()  # 25
        cumprimento_sentenca_field_folhas = self.cumprimento_sentenca_field_folhas.text()  # 26
        cumprimento_sentenca_field_situacao = self.cumprimento_sentenca_field_situacao.text()  # 27
        termo_penhora_field = self.termo_penhora_field.text()  # 28
        termo_penhora_field_folhas = self.termo_penhora_field_folhas.text()  # 29
        termo_penhora_field_situacao = self.termo_penhora_field_situacao.text()  # 30
        depositario_field = self.depositario_field.text()  # 31
        depositario_field_folhas = self.depositario_field_folhas.text()  # 32
        depositario_field_situacao = self.depositario_field_situacao.text()  # 33
        intimacao_executado_field = self.intimacao_executado_field.text()  # 34
        intimacao_executado_field_folhas = self.intimacao_executado_field_folhas.text()  # 35
        intimacao_executado_field_situacao = self.intimacao_executado_field_situacao.text()  # 36
        intimacao_credor_field = self.intimacao_credor_field.text()  # 37
        intimacao_credor_field_folhas = self.intimacao_credor_field_folhas.text()  # 38
        intimacao_credor_field_situacao = self.intimacao_credor_field_situacao.text()  # 39
        dificuldade_initimar_field = self.dificuldade_initimar_field.text()  # 40
        dificuldade_initimar_field_folhas = self.dificuldade_initimar_field_folhas.text()  # 41
        dificuldade_initimar_field_situacao = self.dificuldade_initimar_field_situacao.text()  # 42
        reu_combativo_field = self.reu_combativo_field.text()  # 43
        reu_combativo_field_folhas = self.reu_combativo_field_folhas.text()  # 44
        reu_combativo_field_situacao = self.reu_combativo_field_situacao.text()  # 45
        embargos_field = self.embargos_field.text()  # 46
        embargos_field_folhas = self.embargos_field_folhas.text()  # 47
        embargos_field_situacao = self.embargos_field_situacao.text()  # 48
        despacho_nomeacao_field = self.despacho_nomeacao_field.text()  # 49
        despacho_condicoes_field = self.despacho_condicoes_field.text()  # 50
        quantas_praca_combobox = self.quantas_praca_combobox.currentText()  # 51
        inicio_ipraca_field = self.inicio_ipraca_field.text()  # 52
        fim_ipraca_field = self.fim_ipraca_field.text()  # 53
        inicio_iipraca_field = self.inicio_iipraca_field.text()  # 54
        fim_iipraca_field = self.fim_iipraca_field.text()  # 55
        inicio_iiipraca_field = self.inicio_iiipraca_field.text()  # 56
        fim_iiipraca_field = self.fim_iiipraca_field.text()  # 57
        pagamento_bem_combobox = self.pagamento_bem_combobox.currentText()  # 58
        parcelas_combobox = self.parcelas_combobox.currentText()  # 59
        publicacao_jornal_combobox = self.publicacao_jornal_combobox.currentText()  # 60
        determinacao_proposta_field = self.determinacao_proposta_field.text()  # 61
        sobre_iptu_total_combobox = self.sobre_iptu_total_combobox.currentText()  # 62
        iptu_total_field = self.iptu_total_field.text()  # 63
        sobre_condominio_total_combobox = self.sobre_condominio_total_combobox.currentText()  # 64
        condominio_total_field = self.condominio_total_field.text()  # 65
        debito_exequendo_field = self.debito_exequendo_field.text()  # 66
        data_debito_exequendo_field = self.data_debito_exequendo_field.text()  # 67
        ultimo_condominio_field = self.ultimo_condominio_field.text()  # 68
        data_ultimo_condominio_field = self.data_ultimo_condominio_field.text()  # 69
        manifestacao_propter_combobox = self.manifestacao_propter_combobox.currentText()  # 70
        manifestou_oq_field = self.manifestou_oq_field.text()  # 71
        resumo_processo_combobox = self.resumo_processo_combobox.currentText()  # 72
        resumo_processo_field = self.resumo_processo_field.text()  # 73
        onus_field = self.onus_field.text()  # 74
        descricao_bem_field = self.descricao_bem_field.text()  # 75
        cep_bem_field = self.cep_bem_field.text()  # 76
        logradouro_bem_field = self.logradouro_bem_field.text()  # 77
        num_bem_field = self.num_bem_field.text()  # 78
        complemento_bem_field = self.complemento_bem_field.text()  # 79
        bairro_bem_field = self.bairro_bem_field.text()  # 80
        combo_zona_fields = self.combo_zona_fields.currentText()  # 81
        cidade_bem_field = self.cidade_bem_field.text()  # 82
        combo_uf_fields = self.combo_uf_fields.currentText()  # 83
        matricula_bem_field = self.matricula_bem_field.text()  # 84
        inscricao_imobiliaria_bem_field = self.inscricao_imobiliaria_bem_field.text()  # 85
        cartorio_bem_field = self.cartorio_bem_field.text()  # 86
        valor_avaliacao_bem_field = self.valor_avaliacao_bem_field.text()  # 87
        valor_avaliacao_atz_data_bem_field = self.valor_avaliacao_atz_data_bem_field.text()  # 88
        area_util_bem_field = self.area_util_bem_field.text()  # 89
        area_total_bem_field = self.area_total_bem_field.text()  # 90
        porcentagem_segundapraca_bem_field = self.porcentagem_segundapraca_bem_field.text()  # 91
        propter_rem_total_field = self.propter_rem_total_field.text()  # 92
        valor_segunda_praca_bem_field = self.valor_segunda_praca_bem_field.text()  # 93
        comparacao_percentual_field = self.comparacao_percentual_field.text()  # 94
        tipo_imovel_fields = self.tipo_imovel_fields.currentText()  # 95
        vagas_fields = self.vagas_fields.currentText()  # 96
        banheiros_fields = self.banheiros_fields.currentText()  # 97
        quartos_fields = self.quartos_fields.currentText()  # 98
        suites_fields = self.suites_fields.currentText()  # 99
        ocupado_fields = self.ocupado_fields.currentText()  # 100
        combo_finalidade_fields = self.combo_finalidade_fields.currentText()  # 101
        combo_tem_condominio = self.combo_tem_condominio.currentText()  # 102
        lineedit_valor_condominio = self.lineedit_valor_condominio.text()  # 103
        link_avaliacao_i_field = self.link_avaliacao_i_field.text()  # 104
        metragem_avaliacao_i_field = self.metragem_avaliacao_i_field.text()  # 105
        valor_avaliacao_i_field = self.valor_avaliacao_i_field.text()  # 106
        link_avaliacao_ii_field = self.link_avaliacao_ii_field.text()  # 107
        metragem_avaliacao_ii_field = self.metragem_avaliacao_ii_field.text()  # 108
        valor_avaliacao_ii_field = self.valor_avaliacao_ii_field.text()  # 109
        link_avaliacao_iii_field = self.link_avaliacao_iii_field.text()  # 110
        metragem_avaliacao_iii_field = self.metragem_avaliacao_iii_field.text()  # 111
        valor_avaliacao_iii_field = self.valor_avaliacao_iii_field.text()  # 112
        valor_medio_field = self.valor_medio_field.text()  # 113
        valor_mercado_field = self.valor_mercado_field.text()  # 114
        resultado_comparacao_field = self.resultado_comparacao_field.text()  # 115
        probabilidade_field = self.probabilidade_field.text()  # 116
        checkbox_academia = self.checkbox_academia.isChecked()  # 117
        checkbox_churrasqueira = self.checkbox_churrasqueira.isChecked()  # 118
        checkbox_cinema = self.checkbox_cinema.isChecked()  # 119
        checkbox_espaco_gourmet = self.checkbox_espaco_gourmet.isChecked()  # 120
        checkbox_jardim = self.checkbox_jardim.isChecked()  # 121
        checkbox_piscina = self.checkbox_piscina.isChecked()  # 122
        checkbox_playground = self.checkbox_playground.isChecked()  # 123
        checkbox_quadra_squash = self.checkbox_quadra_squash.isChecked()  # 124
        checkbox_quadra_tenis = self.checkbox_quadra_tenis.isChecked()  # 125
        checkbox_quadra_poliesportiva = self.checkbox_quadra_poliesportiva.isChecked()  # 126
        checkbox_salao_festa = self.checkbox_salao_festa.isChecked()  # 127
        checkbox_acesso_deficiente = self.checkbox_acesso_deficiente.isChecked()  # 128
        checkbox_bicicletario = self.checkbox_bicicletario.isChecked()  # 129
        checkbox_coworking = self.checkbox_coworking.isChecked()  # 130
        checkbox_elevador = self.checkbox_elevador.isChecked()  # 131
        checkbox_lavanderia = self.checkbox_lavanderia.isChecked()  # 132
        checkbox_sauna = self.checkbox_sauna.isChecked()  # 133
        checkbox_spa = self.checkbox_spa.isChecked()  # 134
        checkbox_condominio_fechado = self.checkbox_condominio_fechado.isChecked()  # 135
        checkbox_portao_eletrico = self.checkbox_portao_eletrico.isChecked()  # 136
        checkbox_portaria = self.checkbox_portaria.isChecked()  # 137

        # Verificar se o nome já existe no banco de dados
        select_query = "SELECT processo_field FROM processos WHERE processo_field = ?"
        self.cursor.execute(select_query, (processo_field,))
        result = self.cursor.fetchone()

        if result:
#            # Se o nome já existe, atualizar o registro existente
            update_query = """
            UPDATE processos

            SET processo_field = ?, link_processo_field = ?, acao_field = ?, vara_field = ?, foro_field = ?, comarca_field = ?, email_cartorio_field = ?, nome_juiz_field = ?, oq_leiloado_combobox = ?, ha_alienacao_combobox = ?, combo_ha_incapaz = ?, ha_usufrutuario_combobox = ?, representacao_processual_field = ?, representacao_processual_field_folhas = ?, representacao_processual_field_situacao = ?, citacoes_field = ?, citacoes_field_folhas = ?, citacoes_field_situacao = ?, sentenca_field = ?, sentenca_field_folhas = ?, sentenca_field_situacao = ?, transito_julgado_field = ?, transito_julgado_field_folhas = ?, transito_julgado_field_situacao = ?, cumprimento_sentenca_field = ?, cumprimento_sentenca_field_folhas = ?, cumprimento_sentenca_field_situacao = ?, termo_penhora_field = ?, termo_penhora_field_folhas = ?, termo_penhora_field_situacao = ?, depositario_field = ?, depositario_field_folhas = ?, depositario_field_situacao = ?, intimacao_executado_field = ?, intimacao_executado_field_folhas = ?, intimacao_executado_field_situacao = ?, intimacao_credor_field = ?, intimacao_credor_field_folhas = ?, intimacao_credor_field_situacao = ?, dificuldade_initimar_field = ?, dificuldade_initimar_field_folhas = ?, dificuldade_initimar_field_situacao = ?, reu_combativo_field = ?, reu_combativo_field_folhas = ?, reu_combativo_field_situacao = ?, embargos_field = ?, embargos_field_folhas = ?, embargos_field_situacao = ?, despacho_nomeacao_field = ?, despacho_condicoes_field = ?, quantas_praca_combobox = ?, inicio_ipraca_field = ?, fim_ipraca_field = ?, inicio_iipraca_field = ?, fim_iipraca_field = ?, inicio_iiipraca_field = ?, fim_iiipraca_field = ?, pagamento_bem_combobox = ?, parcelas_combobox = ?, publicacao_jornal_combobox = ?, determinacao_proposta_field = ?, sobre_iptu_total_combobox = ?, iptu_total_field = ?, sobre_condominio_total_combobox = ?, condominio_total_field = ?, debito_exequendo_field = ?, data_debito_exequendo_field = ?, ultimo_condominio_field = ?, data_ultimo_condominio_field = ?, manifestacao_propter_combobox = ?, manifestou_oq_field = ?, resumo_processo_combobox = ?, resumo_processo_field = ?, onus_field = ?, descricao_bem_field = ?, cep_bem_field = ?, logradouro_bem_field = ?, num_bem_field = ?, complemento_bem_field = ?, bairro_bem_field = ?, combo_zona_fields = ?, cidade_bem_field = ?, combo_uf_fields = ?, matricula_bem_field = ?, inscricao_imobiliaria_bem_field = ?, cartorio_bem_field = ?, valor_avaliacao_bem_field = ?, valor_avaliacao_atz_data_bem_field = ?, area_util_bem_field = ?, area_total_bem_field = ?, porcentagem_segundapraca_bem_field = ?, propter_rem_total_field = ?, valor_segunda_praca_bem_field = ?, comparacao_percentual_field = ?, tipo_imovel_fields = ?, vagas_fields = ?, banheiros_fields = ?, quartos_fields = ?, suites_fields = ?, ocupado_fields = ?, combo_finalidade_fields = ?, combo_tem_condominio = ?, lineedit_valor_condominio = ?, link_avaliacao_i_field = ?, metragem_avaliacao_i_field = ?, valor_avaliacao_i_field = ?, link_avaliacao_ii_field = ?, metragem_avaliacao_ii_field = ?, valor_avaliacao_ii_field = ?, link_avaliacao_iii_field = ?, metragem_avaliacao_iii_field = ?, valor_avaliacao_iii_field = ?, valor_medio_field = ?, valor_mercado_field = ?, resultado_comparacao_field = ?, probabilidade_field = ?, checkbox_academia = ?, checkbox_churrasqueira = ?, checkbox_cinema = ?, checkbox_espaco_gourmet = ?, checkbox_jardim = ?, checkbox_piscina = ?, checkbox_playground = ?, checkbox_quadra_squash = ?, checkbox_quadra_tenis = ?, checkbox_quadra_poliesportiva = ?, checkbox_salao_festa = ?, checkbox_acesso_deficiente = ?, checkbox_bicicletario = ?, checkbox_coworking = ?, checkbox_elevador = ?, checkbox_lavanderia = ?, checkbox_sauna = ?, checkbox_spa = ?, checkbox_condominio_fechado = ?, checkbox_portao_eletrico = ?, checkbox_portaria = ?
            WHERE processo_field = ?
            """
            self.cursor.execute(update_query, (processo_field, link_processo_field, acao_field, vara_field, foro_field, comarca_field, email_cartorio_field, nome_juiz_field, oq_leiloado_combobox, ha_alienacao_combobox, combo_ha_incapaz, ha_usufrutuario_combobox, representacao_processual_field, representacao_processual_field_folhas, representacao_processual_field_situacao, citacoes_field, citacoes_field_folhas, citacoes_field_situacao, sentenca_field, sentenca_field_folhas, sentenca_field_situacao, transito_julgado_field, transito_julgado_field_folhas, transito_julgado_field_situacao, cumprimento_sentenca_field, cumprimento_sentenca_field_folhas, cumprimento_sentenca_field_situacao, termo_penhora_field, termo_penhora_field_folhas, termo_penhora_field_situacao, depositario_field, depositario_field_folhas, depositario_field_situacao, intimacao_executado_field, intimacao_executado_field_folhas, intimacao_executado_field_situacao, intimacao_credor_field, intimacao_credor_field_folhas, intimacao_credor_field_situacao, dificuldade_initimar_field, dificuldade_initimar_field_folhas, dificuldade_initimar_field_situacao, reu_combativo_field, reu_combativo_field_folhas, reu_combativo_field_situacao, embargos_field, embargos_field_folhas, embargos_field_situacao, despacho_nomeacao_field, despacho_condicoes_field, quantas_praca_combobox, inicio_ipraca_field, fim_ipraca_field, inicio_iipraca_field, fim_iipraca_field, inicio_iiipraca_field, fim_iiipraca_field, pagamento_bem_combobox, parcelas_combobox, publicacao_jornal_combobox, determinacao_proposta_field, sobre_iptu_total_combobox, iptu_total_field, sobre_condominio_total_combobox, condominio_total_field, debito_exequendo_field, data_debito_exequendo_field, ultimo_condominio_field, data_ultimo_condominio_field, manifestacao_propter_combobox, manifestou_oq_field, resumo_processo_combobox, resumo_processo_field, onus_field, descricao_bem_field, cep_bem_field, logradouro_bem_field, num_bem_field, complemento_bem_field, bairro_bem_field, combo_zona_fields, cidade_bem_field, combo_uf_fields, matricula_bem_field, inscricao_imobiliaria_bem_field, cartorio_bem_field, valor_avaliacao_bem_field, valor_avaliacao_atz_data_bem_field, area_util_bem_field, area_total_bem_field, porcentagem_segundapraca_bem_field, propter_rem_total_field, valor_segunda_praca_bem_field, comparacao_percentual_field, tipo_imovel_fields, vagas_fields, banheiros_fields, quartos_fields, suites_fields, ocupado_fields, combo_finalidade_fields, combo_tem_condominio, lineedit_valor_condominio, link_avaliacao_i_field, metragem_avaliacao_i_field, valor_avaliacao_i_field, link_avaliacao_ii_field, metragem_avaliacao_ii_field, valor_avaliacao_ii_field, link_avaliacao_iii_field, metragem_avaliacao_iii_field, valor_avaliacao_iii_field, valor_medio_field, valor_mercado_field, resultado_comparacao_field, probabilidade_field, checkbox_academia, checkbox_churrasqueira, checkbox_cinema, checkbox_espaco_gourmet, checkbox_jardim, checkbox_piscina, checkbox_playground, checkbox_quadra_squash, checkbox_quadra_tenis, checkbox_quadra_poliesportiva, checkbox_salao_festa, checkbox_acesso_deficiente, checkbox_bicicletario, checkbox_coworking, checkbox_elevador, checkbox_lavanderia, checkbox_sauna, checkbox_spa, checkbox_condominio_fechado, checkbox_portao_eletrico, checkbox_portaria, result[0]))
            QMessageBox.information(self, "Sucesso", f"Parte '{processo_field}' atualizada com sucesso!")


        else:
#            # Se o nome não existe, inserir um novo registro
            insert_query = """
            INSERT INTO processos (processo_field, link_processo_field, acao_field, vara_field, foro_field, comarca_field, email_cartorio_field, nome_juiz_field, oq_leiloado_combobox, ha_alienacao_combobox, combo_ha_incapaz, ha_usufrutuario_combobox, representacao_processual_field, representacao_processual_field_folhas, representacao_processual_field_situacao, citacoes_field, citacoes_field_folhas, citacoes_field_situacao, sentenca_field, sentenca_field_folhas, sentenca_field_situacao, transito_julgado_field, transito_julgado_field_folhas, transito_julgado_field_situacao, cumprimento_sentenca_field, cumprimento_sentenca_field_folhas, cumprimento_sentenca_field_situacao, termo_penhora_field, termo_penhora_field_folhas, termo_penhora_field_situacao, depositario_field, depositario_field_folhas, depositario_field_situacao, intimacao_executado_field, intimacao_executado_field_folhas, intimacao_executado_field_situacao, intimacao_credor_field, intimacao_credor_field_folhas, intimacao_credor_field_situacao, dificuldade_initimar_field, dificuldade_initimar_field_folhas, dificuldade_initimar_field_situacao, reu_combativo_field, reu_combativo_field_folhas, reu_combativo_field_situacao, embargos_field, embargos_field_folhas, embargos_field_situacao, despacho_nomeacao_field, despacho_condicoes_field, quantas_praca_combobox, inicio_ipraca_field, fim_ipraca_field, inicio_iipraca_field, fim_iipraca_field, inicio_iiipraca_field, fim_iiipraca_field, pagamento_bem_combobox, parcelas_combobox, publicacao_jornal_combobox, determinacao_proposta_field, sobre_iptu_total_combobox, iptu_total_field, sobre_condominio_total_combobox, condominio_total_field, debito_exequendo_field, data_debito_exequendo_field, ultimo_condominio_field, data_ultimo_condominio_field, manifestacao_propter_combobox, manifestou_oq_field, resumo_processo_combobox, resumo_processo_field, onus_field, descricao_bem_field, cep_bem_field, logradouro_bem_field, num_bem_field, complemento_bem_field, bairro_bem_field, combo_zona_fields, cidade_bem_field, combo_uf_fields, matricula_bem_field, inscricao_imobiliaria_bem_field, cartorio_bem_field, valor_avaliacao_bem_field, valor_avaliacao_atz_data_bem_field, area_util_bem_field, area_total_bem_field, porcentagem_segundapraca_bem_field, propter_rem_total_field, valor_segunda_praca_bem_field, comparacao_percentual_field, tipo_imovel_fields, vagas_fields, banheiros_fields, quartos_fields, suites_fields, ocupado_fields, combo_finalidade_fields, combo_tem_condominio, lineedit_valor_condominio, link_avaliacao_i_field, metragem_avaliacao_i_field, valor_avaliacao_i_field, link_avaliacao_ii_field, metragem_avaliacao_ii_field, valor_avaliacao_ii_field, link_avaliacao_iii_field, metragem_avaliacao_iii_field, valor_avaliacao_iii_field, valor_medio_field, valor_mercado_field, resultado_comparacao_field, probabilidade_field, checkbox_academia, checkbox_churrasqueira, checkbox_cinema, checkbox_espaco_gourmet, checkbox_jardim, checkbox_piscina, checkbox_playground, checkbox_quadra_squash, checkbox_quadra_tenis, checkbox_quadra_poliesportiva, checkbox_salao_festa, checkbox_acesso_deficiente, checkbox_bicicletario, checkbox_coworking, checkbox_elevador, checkbox_lavanderia, checkbox_sauna, checkbox_spa, checkbox_condominio_fechado, checkbox_portao_eletrico, checkbox_portaria)
            VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
#
            self.cursor.execute(insert_query, (processo_field, link_processo_field, acao_field, vara_field, foro_field, comarca_field, email_cartorio_field, nome_juiz_field, oq_leiloado_combobox, ha_alienacao_combobox, combo_ha_incapaz, ha_usufrutuario_combobox, representacao_processual_field, representacao_processual_field_folhas, representacao_processual_field_situacao, citacoes_field, citacoes_field_folhas, citacoes_field_situacao, sentenca_field, sentenca_field_folhas, sentenca_field_situacao, transito_julgado_field, transito_julgado_field_folhas, transito_julgado_field_situacao, cumprimento_sentenca_field, cumprimento_sentenca_field_folhas, cumprimento_sentenca_field_situacao, termo_penhora_field, termo_penhora_field_folhas, termo_penhora_field_situacao, depositario_field, depositario_field_folhas, depositario_field_situacao, intimacao_executado_field, intimacao_executado_field_folhas, intimacao_executado_field_situacao, intimacao_credor_field, intimacao_credor_field_folhas, intimacao_credor_field_situacao, dificuldade_initimar_field, dificuldade_initimar_field_folhas, dificuldade_initimar_field_situacao, reu_combativo_field, reu_combativo_field_folhas, reu_combativo_field_situacao, embargos_field, embargos_field_folhas, embargos_field_situacao, despacho_nomeacao_field, despacho_condicoes_field, quantas_praca_combobox, inicio_ipraca_field, fim_ipraca_field, inicio_iipraca_field, fim_iipraca_field, inicio_iiipraca_field, fim_iiipraca_field, pagamento_bem_combobox, parcelas_combobox, publicacao_jornal_combobox, determinacao_proposta_field, sobre_iptu_total_combobox, iptu_total_field, sobre_condominio_total_combobox, condominio_total_field, debito_exequendo_field, data_debito_exequendo_field, ultimo_condominio_field, data_ultimo_condominio_field, manifestacao_propter_combobox, manifestou_oq_field, resumo_processo_combobox, resumo_processo_field, onus_field, descricao_bem_field, cep_bem_field, logradouro_bem_field, num_bem_field, complemento_bem_field, bairro_bem_field, combo_zona_fields, cidade_bem_field, combo_uf_fields, matricula_bem_field, inscricao_imobiliaria_bem_field, cartorio_bem_field, valor_avaliacao_bem_field, valor_avaliacao_atz_data_bem_field, area_util_bem_field, area_total_bem_field, porcentagem_segundapraca_bem_field, propter_rem_total_field, valor_segunda_praca_bem_field, comparacao_percentual_field, tipo_imovel_fields, vagas_fields, banheiros_fields, quartos_fields, suites_fields, ocupado_fields, combo_finalidade_fields, combo_tem_condominio, lineedit_valor_condominio, link_avaliacao_i_field, metragem_avaliacao_i_field, valor_avaliacao_i_field, link_avaliacao_ii_field, metragem_avaliacao_ii_field, valor_avaliacao_ii_field, link_avaliacao_iii_field, metragem_avaliacao_iii_field, valor_avaliacao_iii_field, valor_medio_field, valor_mercado_field, resultado_comparacao_field, probabilidade_field, checkbox_academia, checkbox_churrasqueira, checkbox_cinema, checkbox_espaco_gourmet, checkbox_jardim, checkbox_piscina, checkbox_playground, checkbox_quadra_squash, checkbox_quadra_tenis, checkbox_quadra_poliesportiva, checkbox_salao_festa, checkbox_acesso_deficiente, checkbox_bicicletario, checkbox_coworking, checkbox_elevador, checkbox_lavanderia, checkbox_sauna, checkbox_spa, checkbox_condominio_fechado, checkbox_portao_eletrico, checkbox_portaria))
            QMessageBox.information(self, "Sucesso", f"Processo '{processo_field}' salva com sucesso!")

        self.conn.commit()
    def load_from_db_dynamic(self):
        processo = self.processo_field.text()
        select_query = """
            SELECT processo_field , link_processo_field , acao_field , vara_field , foro_field , comarca_field , email_cartorio_field , nome_juiz_field , oq_leiloado_combobox , ha_alienacao_combobox , combo_ha_incapaz , ha_usufrutuario_combobox , representacao_processual_field , representacao_processual_field_folhas , representacao_processual_field_situacao , citacoes_field , citacoes_field_folhas , citacoes_field_situacao , sentenca_field , sentenca_field_folhas , sentenca_field_situacao , transito_julgado_field , transito_julgado_field_folhas , transito_julgado_field_situacao , cumprimento_sentenca_field , cumprimento_sentenca_field_folhas , cumprimento_sentenca_field_situacao , termo_penhora_field , termo_penhora_field_folhas , termo_penhora_field_situacao , depositario_field , depositario_field_folhas , depositario_field_situacao , intimacao_executado_field , intimacao_executado_field_folhas , intimacao_executado_field_situacao , intimacao_credor_field , intimacao_credor_field_folhas , intimacao_credor_field_situacao , dificuldade_initimar_field , dificuldade_initimar_field_folhas , dificuldade_initimar_field_situacao , reu_combativo_field , reu_combativo_field_folhas , reu_combativo_field_situacao , embargos_field , embargos_field_folhas , embargos_field_situacao , despacho_nomeacao_field , despacho_condicoes_field , quantas_praca_combobox , inicio_ipraca_field , fim_ipraca_field , inicio_iipraca_field , fim_iipraca_field , inicio_iiipraca_field , fim_iiipraca_field , pagamento_bem_combobox , parcelas_combobox , publicacao_jornal_combobox , determinacao_proposta_field , sobre_iptu_total_combobox , iptu_total_field , sobre_condominio_total_combobox , condominio_total_field , debito_exequendo_field , data_debito_exequendo_field , ultimo_condominio_field , data_ultimo_condominio_field , manifestacao_propter_combobox , manifestou_oq_field , resumo_processo_combobox , resumo_processo_field , onus_field , descricao_bem_field , cep_bem_field , logradouro_bem_field , num_bem_field , complemento_bem_field , bairro_bem_field , combo_zona_fields , cidade_bem_field , combo_uf_fields , matricula_bem_field , inscricao_imobiliaria_bem_field , cartorio_bem_field , valor_avaliacao_bem_field , valor_avaliacao_atz_data_bem_field , area_util_bem_field , area_total_bem_field , porcentagem_segundapraca_bem_field , propter_rem_total_field , valor_segunda_praca_bem_field , comparacao_percentual_field , tipo_imovel_fields , vagas_fields , banheiros_fields , quartos_fields , suites_fields , ocupado_fields , combo_finalidade_fields , combo_tem_condominio , lineedit_valor_condominio , link_avaliacao_i_field , metragem_avaliacao_i_field , valor_avaliacao_i_field , link_avaliacao_ii_field , metragem_avaliacao_ii_field , valor_avaliacao_ii_field , link_avaliacao_iii_field , metragem_avaliacao_iii_field , valor_avaliacao_iii_field , valor_medio_field , valor_mercado_field , resultado_comparacao_field , probabilidade_field , checkbox_academia , checkbox_churrasqueira , checkbox_cinema , checkbox_espaco_gourmet , checkbox_jardim , checkbox_piscina , checkbox_playground , checkbox_quadra_squash , checkbox_quadra_tenis , checkbox_quadra_poliesportiva , checkbox_salao_festa , checkbox_acesso_deficiente , checkbox_bicicletario , checkbox_coworking , checkbox_elevador , checkbox_lavanderia , checkbox_sauna , checkbox_spa , checkbox_condominio_fechado , checkbox_portao_eletrico , checkbox_portaria
            FROM processos 
            WHERE processo_field = ?
        """
        self.cursor.execute(select_query, (processo,))
        processo_data = self.cursor.fetchone()
        if processo_data:
            processo_field , link_processo_field , acao_field , vara_field , foro_field , comarca_field , email_cartorio_field , nome_juiz_field , oq_leiloado_combobox , ha_alienacao_combobox , combo_ha_incapaz , ha_usufrutuario_combobox , representacao_processual_field , representacao_processual_field_folhas , representacao_processual_field_situacao , citacoes_field , citacoes_field_folhas , citacoes_field_situacao , sentenca_field , sentenca_field_folhas , sentenca_field_situacao , transito_julgado_field , transito_julgado_field_folhas , transito_julgado_field_situacao , cumprimento_sentenca_field , cumprimento_sentenca_field_folhas , cumprimento_sentenca_field_situacao , termo_penhora_field , termo_penhora_field_folhas , termo_penhora_field_situacao , depositario_field , depositario_field_folhas , depositario_field_situacao , intimacao_executado_field , intimacao_executado_field_folhas , intimacao_executado_field_situacao , intimacao_credor_field , intimacao_credor_field_folhas , intimacao_credor_field_situacao , dificuldade_initimar_field , dificuldade_initimar_field_folhas , dificuldade_initimar_field_situacao , reu_combativo_field , reu_combativo_field_folhas , reu_combativo_field_situacao , embargos_field , embargos_field_folhas , embargos_field_situacao , despacho_nomeacao_field , despacho_condicoes_field , quantas_praca_combobox , inicio_ipraca_field , fim_ipraca_field , inicio_iipraca_field , fim_iipraca_field , inicio_iiipraca_field , fim_iiipraca_field , pagamento_bem_combobox , parcelas_combobox , publicacao_jornal_combobox , determinacao_proposta_field , sobre_iptu_total_combobox , iptu_total_field , sobre_condominio_total_combobox , condominio_total_field , debito_exequendo_field , data_debito_exequendo_field , ultimo_condominio_field , data_ultimo_condominio_field , manifestacao_propter_combobox , manifestou_oq_field , resumo_processo_combobox , resumo_processo_field , onus_field , descricao_bem_field , cep_bem_field , logradouro_bem_field , num_bem_field , complemento_bem_field , bairro_bem_field , combo_zona_fields , cidade_bem_field , combo_uf_fields , matricula_bem_field , inscricao_imobiliaria_bem_field , cartorio_bem_field , valor_avaliacao_bem_field , valor_avaliacao_atz_data_bem_field , area_util_bem_field , area_total_bem_field , porcentagem_segundapraca_bem_field , propter_rem_total_field , valor_segunda_praca_bem_field , comparacao_percentual_field , tipo_imovel_fields , vagas_fields , banheiros_fields , quartos_fields , suites_fields , ocupado_fields , combo_finalidade_fields , combo_tem_condominio , lineedit_valor_condominio , link_avaliacao_i_field , metragem_avaliacao_i_field , valor_avaliacao_i_field , link_avaliacao_ii_field , metragem_avaliacao_ii_field , valor_avaliacao_ii_field , link_avaliacao_iii_field , metragem_avaliacao_iii_field , valor_avaliacao_iii_field , valor_medio_field , valor_mercado_field , resultado_comparacao_field , probabilidade_field , checkbox_academia , checkbox_churrasqueira , checkbox_cinema , checkbox_espaco_gourmet , checkbox_jardim , checkbox_piscina , checkbox_playground , checkbox_quadra_squash , checkbox_quadra_tenis , checkbox_quadra_poliesportiva , checkbox_salao_festa , checkbox_acesso_deficiente , checkbox_bicicletario , checkbox_coworking , checkbox_elevador , checkbox_lavanderia , checkbox_sauna , checkbox_spa , checkbox_condominio_fechado , checkbox_portao_eletrico , checkbox_portaria = processo_data

            self.processo_field.setText(processo_field)  # 1
            self.link_processo_field.setText(link_processo_field)  # 2
            self.acao_field.setText(acao_field)  # 3
            self.vara_field.setText(vara_field)  # 4
            self.foro_field.setText(foro_field)  # 5
            self.comarca_field.setText(comarca_field)  # 6
            self.email_cartorio_field.setText(email_cartorio_field)  # 7
            self.nome_juiz_field.setText(nome_juiz_field)  # 8
            self.oq_leiloado_combobox.setCurrentText(oq_leiloado_combobox)  # 9
            self.ha_alienacao_combobox.setCurrentText(ha_alienacao_combobox)  # 10
            self.combo_ha_incapaz.setCurrentText(combo_ha_incapaz)  # 11
            self.ha_usufrutuario_combobox.setCurrentText(ha_usufrutuario_combobox)  # 12
            self.representacao_processual_field.setText(representacao_processual_field)  # 13
            self.representacao_processual_field_folhas.setText(representacao_processual_field_folhas)  # 14
            self.representacao_processual_field_situacao.setText(representacao_processual_field_situacao)  # 15
            self.citacoes_field.setText(citacoes_field)  # 16
            self.citacoes_field_folhas.setText(citacoes_field_folhas)  # 17
            self.citacoes_field_situacao.setText(citacoes_field_situacao)  # 18
            self.sentenca_field.setText(sentenca_field)  # 19
            self.sentenca_field_folhas.setText(sentenca_field_folhas)  # 20
            self.sentenca_field_situacao.setText(sentenca_field_situacao)  # 21
            self.transito_julgado_field.setText(transito_julgado_field)  # 22
            self.transito_julgado_field_folhas.setText(transito_julgado_field_folhas)  # 23
            self.transito_julgado_field_situacao.setText(transito_julgado_field_situacao)  # 24
            self.cumprimento_sentenca_field.setText(cumprimento_sentenca_field)  # 25
            self.cumprimento_sentenca_field_folhas.setText(cumprimento_sentenca_field_folhas)  # 26
            self.cumprimento_sentenca_field_situacao.setText(cumprimento_sentenca_field_situacao)  # 27
            self.termo_penhora_field.setText(termo_penhora_field)  # 28
            self.termo_penhora_field_folhas.setText(termo_penhora_field_folhas)  # 29
            self.termo_penhora_field_situacao.setText(termo_penhora_field_situacao)  # 30
            self.depositario_field.setText(depositario_field)  # 31
            self.depositario_field_folhas.setText(depositario_field_folhas)  # 32
            self.depositario_field_situacao.setText(depositario_field_situacao)  # 33
            self.intimacao_executado_field.setText(intimacao_executado_field)  # 34
            self.intimacao_executado_field_folhas.setText(intimacao_executado_field_folhas)  # 35
            self.intimacao_executado_field_situacao.setText(intimacao_executado_field_situacao)  # 36
            self.intimacao_credor_field.setText(intimacao_credor_field)  # 37
            self.intimacao_credor_field_folhas.setText(intimacao_credor_field_folhas)  # 38
            self.intimacao_credor_field_situacao.setText(intimacao_credor_field_situacao)  # 39
            self.dificuldade_initimar_field.setText(dificuldade_initimar_field)  # 40
            self.dificuldade_initimar_field_folhas.setText(dificuldade_initimar_field_folhas)  # 41
            self.dificuldade_initimar_field_situacao.setText(dificuldade_initimar_field_situacao)  # 42
            self.reu_combativo_field.setText(reu_combativo_field)  # 43
            self.reu_combativo_field_folhas.setText(reu_combativo_field_folhas)  # 44
            self.reu_combativo_field_situacao.setText(reu_combativo_field_situacao)  # 45
            self.embargos_field.setText(embargos_field)  # 46
            self.embargos_field_folhas.setText(embargos_field_folhas)  # 47
            self.embargos_field_situacao.setText(embargos_field_situacao)  # 48
            self.despacho_nomeacao_field.setText(despacho_nomeacao_field)  # 49
            self.despacho_condicoes_field.setText(despacho_condicoes_field)  # 50
            self.quantas_praca_combobox.setCurrentText(quantas_praca_combobox)  # 51
            self.inicio_ipraca_field.setText(inicio_ipraca_field)  # 52
            self.fim_ipraca_field.setText(fim_ipraca_field)  # 53
            self.inicio_iipraca_field.setText(inicio_iipraca_field)  # 54
            self.fim_iipraca_field.setText(fim_iipraca_field)  # 55
            self.inicio_iiipraca_field.setText(inicio_iiipraca_field)  # 56
            self.fim_iiipraca_field.setText(fim_iiipraca_field)  # 57
            self.pagamento_bem_combobox.setCurrentText(pagamento_bem_combobox)  # 58
            self.parcelas_combobox.setCurrentText(parcelas_combobox)  # 59
            self.publicacao_jornal_combobox.setCurrentText(publicacao_jornal_combobox)  # 60
            self.determinacao_proposta_field.setText(determinacao_proposta_field)  # 61
            self.sobre_iptu_total_combobox.setCurrentText(sobre_iptu_total_combobox)  # 62
            self.iptu_total_field.setText(iptu_total_field)  # 63
            self.sobre_condominio_total_combobox.setCurrentText(sobre_condominio_total_combobox)  # 64
            self.condominio_total_field.setText(condominio_total_field)  # 65
            self.debito_exequendo_field.setText(debito_exequendo_field)  # 66
            self.data_debito_exequendo_field.setText(data_debito_exequendo_field)  # 67
            self.ultimo_condominio_field.setText(ultimo_condominio_field)  # 68
            self.data_ultimo_condominio_field.setText(data_ultimo_condominio_field)  # 69
            self.manifestacao_propter_combobox.setCurrentText(manifestacao_propter_combobox)  # 70
            self.manifestou_oq_field.setText(manifestou_oq_field)  # 71
            self.resumo_processo_combobox.setCurrentText(resumo_processo_combobox)  # 72
            self.resumo_processo_field.setText(resumo_processo_field)  # 73
            self.onus_field.setText(onus_field)  # 74
            self.descricao_bem_field.setText(descricao_bem_field)  # 75
            self.cep_bem_field.setText(cep_bem_field)  # 76
            self.logradouro_bem_field.setText(logradouro_bem_field)  # 77
            self.num_bem_field.setText(num_bem_field)  # 78
            self.complemento_bem_field.setText(complemento_bem_field)  # 79
            self.bairro_bem_field.setText(bairro_bem_field)  # 80
            self.combo_zona_fields.setCurrentText(combo_zona_fields)  # 81
            self.cidade_bem_field.setText(cidade_bem_field)  # 82
            self.combo_uf_fields.setCurrentText(combo_uf_fields)  # 83
            self.matricula_bem_field.setText(matricula_bem_field)  # 84
            self.inscricao_imobiliaria_bem_field.setText(inscricao_imobiliaria_bem_field)  # 85
            self.cartorio_bem_field.setText(cartorio_bem_field)  # 86
            self.valor_avaliacao_bem_field.setText(valor_avaliacao_bem_field)  # 87
            self.valor_avaliacao_atz_data_bem_field.setText(valor_avaliacao_atz_data_bem_field)  # 88
            self.area_util_bem_field.setText(area_util_bem_field)  # 89
            self.area_total_bem_field.setText(area_total_bem_field)  # 90
            self.porcentagem_segundapraca_bem_field.setText(porcentagem_segundapraca_bem_field)  # 91
            self.propter_rem_total_field.setText(propter_rem_total_field)  # 92
            self.valor_segunda_praca_bem_field.setText(valor_segunda_praca_bem_field)  # 93
            self.comparacao_percentual_field.setText(comparacao_percentual_field)  # 94
            self.tipo_imovel_fields.setCurrentText(tipo_imovel_fields)  # 95
            self.vagas_fields.setCurrentText(vagas_fields)  # 96
            self.banheiros_fields.setCurrentText(banheiros_fields)  # 97
            self.quartos_fields.setCurrentText(quartos_fields)  # 98
            self.suites_fields.setCurrentText(suites_fields)  # 99
            self.ocupado_fields.setCurrentText(ocupado_fields)  # 100
            self.combo_finalidade_fields.setCurrentText(combo_finalidade_fields)  # 101
            self.combo_tem_condominio.setCurrentText(combo_tem_condominio)  # 102
            self.lineedit_valor_condominio.setText(lineedit_valor_condominio)  # 103
            self.link_avaliacao_i_field.setText(link_avaliacao_i_field)  # 104
            self.metragem_avaliacao_i_field.setText(metragem_avaliacao_i_field)  # 105
            self.valor_avaliacao_i_field.setText(valor_avaliacao_i_field)  # 106
            self.link_avaliacao_ii_field.setText(link_avaliacao_ii_field)  # 107
            self.metragem_avaliacao_ii_field.setText(metragem_avaliacao_ii_field)  # 108
            self.valor_avaliacao_ii_field.setText(valor_avaliacao_ii_field)  # 109
            self.link_avaliacao_iii_field.setText(link_avaliacao_iii_field)  # 110
            self.metragem_avaliacao_iii_field.setText(metragem_avaliacao_iii_field)  # 111
            self.valor_avaliacao_iii_field.setText(valor_avaliacao_iii_field)  # 112
            self.valor_medio_field.setText(valor_medio_field)  # 113
            self.valor_mercado_field.setText(valor_mercado_field)  # 114
            self.resultado_comparacao_field.setText(resultado_comparacao_field)  # 115
            self.probabilidade_field.setText(probabilidade_field)  # 116
            self.checkbox_academia.setChecked(checkbox_academia)  # 117
            self.checkbox_churrasqueira.setChecked(checkbox_churrasqueira)  # 118
            self.checkbox_cinema.setChecked(checkbox_cinema)  # 119
            self.checkbox_espaco_gourmet.setChecked(checkbox_espaco_gourmet)  # 120
            self.checkbox_jardim.setChecked(checkbox_jardim)  # 121
            self.checkbox_piscina.setChecked(checkbox_piscina)  # 122
            self.checkbox_playground.setChecked(checkbox_playground)  # 123
            self.checkbox_quadra_squash.setChecked(checkbox_quadra_squash)  # 124
            self.checkbox_quadra_tenis.setChecked(checkbox_quadra_tenis)  # 125
            self.checkbox_quadra_poliesportiva.setChecked(checkbox_quadra_poliesportiva)  # 126
            self.checkbox_salao_festa.setChecked(checkbox_salao_festa)  # 127
            self.checkbox_acesso_deficiente.setChecked(checkbox_acesso_deficiente)  # 128
            self.checkbox_bicicletario.setChecked(checkbox_bicicletario)  # 129
            self.checkbox_coworking.setChecked(checkbox_coworking)  # 130
            self.checkbox_elevador.setChecked(checkbox_elevador)  # 131
            self.checkbox_lavanderia.setChecked(checkbox_lavanderia)  # 132
            self.checkbox_sauna.setChecked(checkbox_sauna)  # 133
            self.checkbox_spa.setChecked(checkbox_spa)  # 134
            self.checkbox_condominio_fechado.setChecked(checkbox_condominio_fechado)  # 135
            self.checkbox_portao_eletrico.setChecked(checkbox_portao_eletrico)  # 136
            self.checkbox_portaria.setChecked(checkbox_portaria)

            QMessageBox.information(self, 'Carregado', 'Processo carregado com sucesso !')
        else:
            # Opcional: Mostrar uma mensagem ou lidar com o caso em que o processo não é encontrado
            QMessageBox.critical(self, 'Erro ao encontrar processo', 'Verifique o número digitado')

class PartesWindow(QWidget):
    def __init__(self, processo, parent=None):
        super(PartesWindow, self).__init__(parent)
        self.processo_fields = processo
        self.setWindowTitle(f"Partes do Processo {self.processo_fields}")
        self.resize(1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #eaeaea;
            }
            QWidget {
                font-family: 'Arial';
                font-size: 17px;
                color: #333;
            }
            QLineEdit, QComboBox {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-family: 'Arial';
                font-size: 17px;
                padding: 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-size: 14px;
                color: #444;
            }
        """)

        # Criação do QScrollArea e do layout principal
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        self.main_layout = QVBoxLayout(content_widget)

        self.conn = sqlite3.connect('partes.db')
        self.cursor = self.conn.cursor()

        # Adicionar os campos iniciais
        self.setup_initial_fields()

        # Layout principal da janela, adicionando o QScrollArea
        window_layout = QVBoxLayout(self)
        window_layout.addWidget(scroll_area)

    def criar_campo_data(self, label_text, placeholder, layout):
        label = QLabel(label_text, self)
        label.setStyleSheet("font-size: 16px; color: #333;")
        field = QLineEdit(self)
        field.setPlaceholderText(placeholder)
        layout.addWidget(label)
        layout.addWidget(field)
        return label, field
    def criar_campo_combobox(self, label_text, options, layout):
        label = QLabel(label_text, self)
        label.setStyleSheet("font-size: 16px; color: #333;")
        combobox = QComboBox(self)
        combobox.setCurrentIndex(0)  # Define o índice atual para 0
        combobox.addItems(options)
        layout.addWidget(label)
        layout.addWidget(combobox)
        return label, combobox
    def criar_campo_checkbox(self, label_text, layout):
        checkbox = QCheckBox(label_text, self)
        checkbox.setStyleSheet("font-size: 16px; color: #333;")
        layout.addWidget(checkbox)
        return checkbox
    def criar_linha_separadora(self, layout):
        linha_separar = QFrame(self)
        linha_separar.setFrameShape(QFrame.HLine)
        linha_separar.setFrameShadow(QFrame.Sunken)
        layout.addWidget(linha_separar)
        return linha_separar
    def criar_campo_completo(self, label_text, layout, campo_placeholder=" ", folhas_placeholder="folhas", situacao_placeholder="situação"):
# Cria o label e o campo principal
        label = QLabel(label_text, self)
        label.setStyleSheet("font-size: 16px; color: #333;")
        campo = QLineEdit(self)
        campo.setPlaceholderText(campo_placeholder)
        layout.addWidget(label)
        layout.addWidget(campo)

# Cria o campo de folhas
        campo_folha = QLineEdit(self)
        campo_folha.setPlaceholderText(folhas_placeholder)
        layout.addWidget(campo_folha)

# Cria o campo de situação
        campo_situacao = QLineEdit(self)
        campo_situacao.setPlaceholderText(situacao_placeholder)
        layout.addWidget(campo_situacao)

# Adiciona a linha separadora
        linha_separar = QFrame(self)
        linha_separar.setFrameShape(QFrame.HLine)
        linha_separar.setFrameShadow(QFrame.Sunken)
        layout.addWidget(linha_separar)

        return label, campo, campo_folha, campo_situacao
    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Erro")
        msg.exec_()
    def show_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Validação")
        msg.exec_()
    def criar_campo_endereco(self, titulo_texto, cep_placeholder, logradouro_placeholder, numero_placeholder, complemento_placeholder, bairro_placeholder, cidade_placeholder, uf_lista, layout):
        # LABEL TITULO
        label_titulo = QLabel(titulo_texto, self)
        label_titulo.setStyleSheet("color: #333; font-size: 18px")
        layout.addWidget(label_titulo)

        # CAMPO CEP
        cep_label = QLabel("CEP", self)
        cep_label.setStyleSheet("font-size: 16px; color: #333;")
        cep_field = QLineEdit(self)
        cep_field.setPlaceholderText(cep_placeholder)
        layout.addWidget(cep_label)
        layout.addWidget(cep_field)

        # Botão para buscar endereço
        buscar_endereco_button = QPushButton("Buscar Endereço", self)
        layout.addWidget(buscar_endereco_button)

        # CAMPO Logradouro
        logradouro_label = QLabel("Logradouro", self)
        logradouro_label.setStyleSheet("font-size: 16px; color: #333;")
        logradouro_field = QLineEdit(self)
        logradouro_field.setPlaceholderText(logradouro_placeholder)
        layout.addWidget(logradouro_label)
        layout.addWidget(logradouro_field)

        # CAMPO Número
        num_label = QLabel("Número", self)
        num_label.setStyleSheet("font-size: 16px; color: #333;")
        num_field = QLineEdit(self)
        num_field.setPlaceholderText(numero_placeholder)
        layout.addWidget(num_label)
        layout.addWidget(num_field)

        # CAMPO Complemento
        complemento_label = QLabel("Complemento", self)
        complemento_label.setStyleSheet("font-size: 16px; color: #333;")
        complemento_field = QLineEdit(self)
        complemento_field.setPlaceholderText(complemento_placeholder)
        layout.addWidget(complemento_label)
        layout.addWidget(complemento_field)

        # CAMPO Bairro
        bairro_label = QLabel("Bairro", self)
        bairro_label.setStyleSheet("font-size: 16px; color: #333;")
        bairro_field = QLineEdit(self)
        bairro_field.setPlaceholderText(bairro_placeholder)
        layout.addWidget(bairro_label)
        layout.addWidget(bairro_field)

        # CAMPO Cidade
        cidade_label = QLabel("Cidade", self)
        cidade_label.setStyleSheet("font-size: 16px; color: #333;")
        cidade_field = QLineEdit(self)
        cidade_field.setPlaceholderText(cidade_placeholder)
        layout.addWidget(cidade_label)
        layout.addWidget(cidade_field)

        # COMBOBOX UF
        combo_uf_label = QLabel("UF", self)
        combo_uf_label.setStyleSheet("font-size: 16px; color: #333;")
        combo_uf_field = QComboBox(self)
        combo_uf_field.addItems(uf_lista)
        layout.addWidget(combo_uf_label)
        layout.addWidget(combo_uf_field)

        # Retorno dos campos criados
        return label_titulo, cep_label, cep_field, buscar_endereco_button, logradouro_label, logradouro_field, num_label, num_field, complemento_label, complemento_field, bairro_label, bairro_field, cidade_label, cidade_field, combo_uf_label, combo_uf_field
    def setup_initial_fields(self):
# Partes/Envolvidos
        self.titulo_partes_label = QLabel("Partes/Envolvidos", self)
        self.titulo_partes_label.setStyleSheet("font-size: 20px; color: #333;")
        self.main_layout.addWidget(self.titulo_partes_label)

# Frame 1 tipo envolvidos
        self.formulario_tipopartei_frame = QFrame(self)
        self.formulario_tipopartei_frame.setStyleSheet("""
        QFrame {
                border-radius: 5px; 
                padding: 10px;
                background-color: #f0f0f0;
        }
        """)
        self.formulario_tipopartei_layout = QHBoxLayout(self.formulario_tipopartei_frame)

# Combobox Tipo Envolvido
        self.checkbox_exequente = self.criar_campo_checkbox("Exequente", self.formulario_tipopartei_layout)
        self.checkbox_adv_exequente = self.criar_campo_checkbox("Advogado do Exequente", self.formulario_tipopartei_layout)
        self.checkbox_executado = self.criar_campo_checkbox("Executado", self.formulario_tipopartei_layout)
        self.checkbox_adv_executado = self.criar_campo_checkbox("Advogado do Executado", self.formulario_tipopartei_layout)
        self.checkbox_proprietario = self.criar_campo_checkbox("Proprietários/Coproprietarios", self.formulario_tipopartei_layout)
        self.checkbox_terceiro_interessado = self.criar_campo_checkbox("Terceiro interessado", self.formulario_tipopartei_layout)
        self.checkbox_credor_pen = self.criar_campo_checkbox("Credor de Penhora", self.formulario_tipopartei_layout)

# Adicionar o frame ao layout principal
        self.main_layout.addWidget(self.formulario_tipopartei_frame)

# Frame 2 tipo envolvidos
        self.formulario_tipoparteii_frame = QFrame(self)
        self.formulario_tipoparteii_frame.setStyleSheet("""
        QFrame {
                border-radius: 5px; 
                padding: 10px;
                background-color: #f0f0f0;
        }
        """)
        self.formulario_tipoparteii_layout = QHBoxLayout(self.formulario_tipoparteii_frame)

#  Tipo Envolvido 2
        self.checkbox_credor_hip = self.criar_campo_checkbox("Credor hipotecário", self.formulario_tipoparteii_layout)
        self.checkbox_credor_fid = self.criar_campo_checkbox("Credor Fiduciário", self.formulario_tipoparteii_layout)
        self.checkbox_proprietario_registral = self.criar_campo_checkbox("Proprietário Registral (proprietário formal)", self.formulario_tipoparteii_layout)
        self.checkbox_proiminente_comprador = self.criar_campo_checkbox("Promitente Comprador (promissário comprador)", self.formulario_tipoparteii_layout)
        self.checkbox_usufrutuario = self.criar_campo_checkbox("Usufruário", self.formulario_tipoparteii_layout)
        self.checkbox_ocupante = self.criar_campo_checkbox("Ocupante", self.formulario_tipoparteii_layout)
        self.checkbox_curador_esp = self.criar_campo_checkbox("Curador Especial", self.formulario_tipoparteii_layout)

# Adicionar o frame ao layout principal
        self.main_layout.addWidget(self.formulario_tipoparteii_frame)

# Nome completo
        self.nome_label, self.nome_field = self.criar_campo_data("Nome completo :", " ", self.main_layout)
# tipo
        self.tipo_label, self.tipo_field = self.criar_campo_data("tipo completo :", " ", self.main_layout)
        self.tipo_field.hide()
        self.tipo_label.hide()
# CPF/CNPJ
        self.cpf_cnpj_label, self.cpf_cnpj_field = self.criar_campo_data("CPF/CNPJ :", " ", self.main_layout)
        self.cpf_cnpj_field.editingFinished.connect(self.validar_cpf_cnpj_field) 
# Oab
        self.oab_label, self.oab_field = self.criar_campo_data("OAB :", " ", self.main_layout)

# Botão de salvar parte
        self.save_part_button = QPushButton("Salvar Parte", self)
        self.save_part_button.clicked.connect(self.save_part_to_db)
        self.main_layout.addWidget(self.save_part_button)

# Botão de carregar parte
        self.load_part_button = QPushButton("Carregar Parte", self)
        self.load_part_button.clicked.connect(self.load_part_from_db)
        self.main_layout.addWidget(self.load_part_button)

# Celular
        self.cel_label, self.cel_field = self.criar_campo_data("Celular", " ", self.main_layout)

# Telefone
        self.tel_label, self.tel_field = self.criar_campo_data("Telefone", " ", self.main_layout)

# Email - 1
        self.email_i_label, self.email_i_field = self.criar_campo_data("Email - 1", " ", self.main_layout)

# Email - 2
        self.email_ii_label, self.email_ii_field = self.criar_campo_data("Email - 2", " ", self.main_layout)

# Email - 2
        self.email_iii_label, self.email_iii_field = self.criar_campo_data("Email - 3", " ", self.main_layout)

#########################

# Partes/Envolvidos

# Endereço
        self.label_adiocionar_endereçoa = QLabel("Endereços", self)
        self.label_adiocionar_endereçoa.setStyleSheet("color: #333; font-size: 20px")
        self.main_layout.addWidget(self.label_adiocionar_endereçoa)

        # Frame Formulário
        self.frame_endereco = QFrame(self)
        self.frame_endereco.setStyleSheet("""
                QFrame {
                border: 2px solid #4CAF50; 
                border-radius: 5px; 
                padding: 10px;
                background-color: #f0f0f0;
                }
                QFrame > QWidget { 
                border: none;
                }
        """)
# Inicio do frame

        self.frame_enderco_layout = QVBoxLayout(self.frame_endereco)

# Enderedço 1

        self.label_titulo, self.cep_label, self.cep_field, self.buscar_endereco_button, \
        self.logradouro_label, self.logradouro_field, self.num_label, self.num_field, \
        self.complemento_label, self.complemento_field, self.bairro_label, self.bairro_field, \
        self.cidade_label, self.cidade_field, self.combo_uf_label, self.combo_uf_field = \
        self.criar_campo_endereco(
            titulo_texto="1º Endereço Completo",
            cep_placeholder="Digite o CEP",
            logradouro_placeholder="Digite o logradouro",
            numero_placeholder="Número",
            complemento_placeholder="Complemento",
            bairro_placeholder="Bairro",
            cidade_placeholder="Cidade",
            uf_lista=["SP", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SE", "TO"],
            layout=self.frame_enderco_layout
        )
        self.buscar_endereco_button.clicked.connect(self.buscar_endereco)
        self.main_layout.addWidget(self.frame_endereco)  


###################################################################
# _i
        self.label_titulo_i, self.cep_label_i, self.cep_field_i, self.buscar_endereco_button_i, \
        self.logradouro_label_i, self.logradouro_field_i, self.num_label_i, self.num_field_i, \
        self.complemento_label_i, self.complemento_field_i, self.bairro_label_i, self.bairro_field_i, \
        self.cidade_label_i, self.cidade_field_i, self.combo_uf_label_i, self.combo_uf_field_i = \
        self.criar_campo_endereco(
            titulo_texto="2º Endereço Completo",
            cep_placeholder="Digite o CEP",
            logradouro_placeholder="Digite o logradouro",
            numero_placeholder="Número",
            complemento_placeholder="Complemento",
            bairro_placeholder="Bairro",
            cidade_placeholder="Cidade",
            uf_lista=["SP", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SE", "TO"],
            layout=self.frame_enderco_layout
        )
        self.buscar_endereco_button_i.clicked.connect(self.buscar_endereco_i)
        self.buscar_endereco_button

###################################################################
# _ii
        self.label_titulo_ii, self.cep_label_ii, self.cep_field_ii, self.buscar_endereco_button_ii, \
        self.logradouro_label_ii, self.logradouro_field_ii, self.num_label_ii, self.num_field_ii, \
        self.complemento_label_ii, self.complemento_field_ii, self.bairro_label_ii, self.bairro_field_ii, \
        self.cidade_label_ii, self.cidade_field_ii, self.combo_uf_label_ii, self.combo_uf_field_ii = \
        self.criar_campo_endereco(
            titulo_texto="3º Endereço Completo",
            cep_placeholder="Digite o CEP",
            logradouro_placeholder="Digite o logradouro",
            numero_placeholder="Número",
            complemento_placeholder="Complemento",
            bairro_placeholder="Bairro",
            cidade_placeholder="Cidade",
            uf_lista=["SP", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SE", "TO"],
            layout=self.frame_enderco_layout
        )
        self.buscar_endereco_button_ii.clicked.connect(self.buscar_endereco_ii)
        self.buscar_endereco_button

###################################################################
# _iii
        self.label_titulo_iii, self.cep_label_iii, self.cep_field_iii, self.buscar_endereco_button_iii, \
        self.logradouro_label_iii, self.logradouro_field_iii, self.num_label_iii, self.num_field_iii, \
        self.complemento_label_iii, self.complemento_field_iii, self.bairro_label_iii, self.bairro_field_iii, \
        self.cidade_label_iii, self.cidade_field_iii, self.combo_uf_label_iii, self.combo_uf_field_iii = \
        self.criar_campo_endereco(
            titulo_texto="4º Endereço Completo",
            cep_placeholder="Digite o CEP",
            logradouro_placeholder="Digite o logradouro",
            numero_placeholder="Número",
            complemento_placeholder="Complemento",
            bairro_placeholder="Bairro",
            cidade_placeholder="Cidade",
            uf_lista=["SP", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SE", "TO"],
            layout=self.frame_enderco_layout
        )
        self.buscar_endereco_button_iii.clicked.connect(self.buscar_endereco_iii)
        self.buscar_endereco_button


###################################################################
# _iv
        self.label_titulo_iv, self.cep_label_iv, self.cep_field_iv, self.buscar_endereco_button_iv, \
        self.logradouro_label_iv, self.logradouro_field_iv, self.num_label_iv, self.num_field_iv, \
        self.complemento_label_iv, self.complemento_field_iv, self.bairro_label_iv, self.bairro_field_iv, \
        self.cidade_label_iv, self.cidade_field_iv, self.combo_uf_label_iv, self.combo_uf_field_iv = \
        self.criar_campo_endereco(
            titulo_texto="5º Endereço Completo",
            cep_placeholder="Digite o CEP",
            logradouro_placeholder="Digite o logradouro",
            numero_placeholder="Número",
            complemento_placeholder="Complemento",
            bairro_placeholder="Bairro",
            cidade_placeholder="Cidade",
            uf_lista=["SP", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SE", "TO"],
            layout=self.frame_enderco_layout
        )
        self.buscar_endereco_button_iv.clicked.connect(self.buscar_endereco_iv)
        self.buscar_endereco_button


    def buscar_endereco(self):
        cep = self.cep_field.text()
        if cep:
            try:
                response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
                data = response.json()

                if "erro" not in data:
                    self.logradouro_field.setText(data.get("logradouro", ""))
                    self.bairro_field.setText(data.get("bairro", ""))
                    self.cidade_field.setText(data.get("localidade", ""))
                    self.combo_uf_field.setCurrentText(data.get("uf", ""))
                else:
                    QMessageBox.warning(self, "Erro", "CEP não encontrado.")
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao buscar CEP: {str(e)}")
        else:
            QMessageBox.warning(self, "Aviso", "Por favor, insira um CEP válido.")
    def buscar_endereco_iv(self):
        cep = self.cep_field_iv.text()
        if cep:
            try:
                response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
                data = response.json()

                if "erro" not in data:
                    self.logradouro_field_iv.setText(data.get("logradouro", ""))
                    self.bairro_field_iv.setText(data.get("bairro", ""))
                    self.cidade_field_iv.setText(data.get("localidade", ""))
                    self.combo_uf_field_iv.setCurrentText(data.get("uf", ""))
                else:
                    QMessageBox.warning(self, "Erro", "CEP não encontrado.")
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao buscar CEP: {str(e)}")
        else:
            QMessageBox.warning(self, "Aviso", "Por favor, insira um CEP válido.")
    def buscar_endereco_iii(self):
        cep = self.cep_field_iii.text()
        if cep:
            try:
                response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
                data = response.json()

                if "erro" not in data:
                    self.logradouro_field_iii.setText(data.get("logradouro", ""))
                    self.bairro_field_iii.setText(data.get("bairro", ""))
                    self.cidade_field_iii.setText(data.get("localidade", ""))
                    self.combo_uf_field_iii.setCurrentText(data.get("uf", ""))
                else:
                    QMessageBox.warning(self, "Erro", "CEP não encontrado.")
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao buscar CEP: {str(e)}")
        else:
            QMessageBox.warning(self, "Aviso", "Por favor, insira um CEP válido.")
    def buscar_endereco_ii(self):
        cep = self.cep_field_ii.text()
        if cep:
            try:
                response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
                data = response.json()

                if "erro" not in data:
                    self.logradouro_field_ii.setText(data.get("logradouro", ""))
                    self.bairro_field_ii.setText(data.get("bairro", ""))
                    self.cidade_field_ii.setText(data.get("localidade", ""))
                    self.combo_uf_field_ii.setCurrentText(data.get("uf", ""))
                else:
                    QMessageBox.warning(self, "Erro", "CEP não encontrado.")
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao buscar CEP: {str(e)}")
        else:
            QMessageBox.warning(self, "Aviso", "Por favor, insira um CEP válido.")
    def buscar_endereco_i(self):
        cep = self.cep_field_i.text()
        if cep:
            try:
                response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
                data = response.json()

                if "erro" not in data:
                    self.logradouro_field_i.setText(data.get("logradouro", ""))
                    self.bairro_field_i.setText(data.get("bairro", ""))
                    self.cidade_field_i.setText(data.get("localidade", ""))
                    self.combo_uf_field_i.setCurrentText(data.get("uf", ""))
                else:
                    QMessageBox.warning(self, "Erro", "CEP não encontrado.")
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao buscar CEP: {str(e)}")
        else:
            QMessageBox.warning(self, "Aviso", "Por favor, insira um CEP válido.")
    def validar_cpf(self, cpf):
        cpf = re.sub(r'\D', '', cpf)  # Remove qualquer caractere que não seja dígito

        if len(cpf) != 11:
            return False

        # Verifica se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False

        # Cálculo do primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito1 = (soma * 10) % 11
        digito1 = digito1 if digito1 < 10 else 0

        # Cálculo do segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito2 = (soma * 10) % 11
        digito2 = digito2 if digito2 < 10 else 0

        # Verifica se os dígitos verificadores estão corretos
        return cpf[-2:] == f'{digito1}{digito2}'
    def validar_cnpj(self, cnpj):
        cnpj = re.sub(r'\D', '', cnpj)  # Remove qualquer caractere que não seja dígito

        if len(cnpj) != 14:
            return False

        # Verifica se todos os dígitos são iguais
        if cnpj == cnpj[0] * 14:
            return False

        # Cálculo do primeiro dígito verificador
        soma = sum(int(cnpj[i]) * int(w) for i, w in enumerate('543298765432'))
        digito1 = 11 - (soma % 11)
        digito1 = digito1 if digito1 < 10 else 0

        # Cálculo do segundo dígito verificador
        soma = sum(int(cnpj[i]) * int(w) for i, w in enumerate('6543298765432'))
        digito2 = 11 - (soma % 11)
        digito2 = digito2 if digito2 < 10 else 0

        # Verifica se os dígitos verificadores estão corretos
        return cnpj[-2:] == f'{digito1}{digito2}'
    def validar_cpf_cnpj_field(self):
        valor = self.cpf_cnpj_field.text()

        if len(valor) <= 11:
            valido = self.validar_cpf(valor)
            tipo_doc = "CPF"
        else:
            valido = self.validar_cnpj(valor)
            tipo_doc = "CNPJ"

        if not valido:
            QMessageBox.warning(self, "Erro", f"{tipo_doc} inválido. Por favor, insira um {tipo_doc} válido.")
            self.cpf_cnpj_field.setFocus()
            self.cpf_cnpj_field.clear()
    def save_part_to_db(self):
    # Cria uma lista com os tipos selecionados e converte para string
        selected_types = []
        if self.checkbox_exequente.isChecked():
            selected_types.append("Exequente")
        if self.checkbox_adv_exequente.isChecked():
            selected_types.append("Advogado do Exequente")
        if self.checkbox_executado.isChecked():
            selected_types.append("Executado")
        if self.checkbox_adv_executado.isChecked():
            selected_types.append("Advogado do Executado")
        if self.checkbox_proprietario.isChecked():
            selected_types.append("Proprietários/Coproprietarios")
        if self.checkbox_terceiro_interessado.isChecked():
            selected_types.append("Terceiro interessado")
        if self.checkbox_credor_pen.isChecked():
            selected_types.append("Credor de Penhora")
        if self.checkbox_credor_hip.isChecked():
            selected_types.append("Credor hipotecário")
        if self.checkbox_credor_fid.isChecked():
            selected_types.append("Credor Fiduciário")
        if self.checkbox_proprietario_registral.isChecked():
            selected_types.append("Proprietário Registral (proprietário formal)")
        if self.checkbox_proiminente_comprador.isChecked():
            selected_types.append("Promitente Comprador (promissário comprador)")
        if self.checkbox_usufrutuario.isChecked():
            selected_types.append("Usufruário")
        if self.checkbox_ocupante.isChecked():
            selected_types.append("Ocupante")
        if self.checkbox_curador_esp.isChecked():
            selected_types.append("Curador Especial")
        tipo = ', '.join(selected_types)
        nome = self.nome_field.text()
        cpf_cnpj = self.cpf_cnpj_field.text()
        logradouro = self.logradouro_field.text()
        num_bem = self.num_field.text()
        complemento = self.complemento_field.text()
        bairro = self.bairro_field.text()
        cidade = self.cidade_field.text()
        combo_uf = self.combo_uf_field.currentText()
        oab = self.oab_field.text()
        cep = self.cep_field.text()
        logradouro_i = self.logradouro_field_i.text()
        num_bem_i = self.num_field_i.text()
        complemento_i = self.complemento_field_i.text()
        bairro_i = self.bairro_field_i.text()
        cidade_i = self.cidade_field_i.text()
        combo_uf_i = self.combo_uf_field_i.currentText()
        cep_i = self.cep_field_i.text()
        logradouro_ii = self.logradouro_field_ii.text()
        num_bem_ii = self.num_field_ii.text()
        complemento_ii = self.complemento_field_ii.text()
        bairro_ii = self.bairro_field_ii.text()
        cidade_ii = self.cidade_field_ii.text()
        combo_uf_ii = self.combo_uf_field_ii.currentText()
        cep_ii = self.cep_field_ii.text()
        logradouro_iii = self.logradouro_field_iii.text()
        num_bem_iii = self.num_field_iii.text()
        complemento_iii = self.complemento_field_iii.text()
        bairro_iii = self.bairro_field_iii.text()
        cidade_iii = self.cidade_field_iii.text()
        combo_uf_iii = self.combo_uf_field_iii.currentText()
        cep_iii = self.cep_field_iii.text()
        logradouro_iv = self.logradouro_field_iv.text()
        num_bem_iv = self.num_field_iv.text()
        complemento_iv = self.complemento_field_iv.text()
        bairro_iv = self.bairro_field_iv.text()
        cidade_iv = self.cidade_field_iv.text()
        combo_uf_iv = self.combo_uf_field_iv.currentText()
        cep_iv = self.cep_field_iv.text()
        cel = self.cel_field.text()
        tel = self.tel_field.text()
        email_i = self.email_i_field.text()
        email_ii = self.email_ii_field.text()
        email_iii = self.email_iii_field.text()
        checkbox_exequente = self.checkbox_exequente.isChecked()
        checkbox_adv_exequente = self.checkbox_adv_exequente.isChecked()
        checkbox_executado = self.checkbox_executado.isChecked()
        checkbox_adv_executado = self.checkbox_adv_executado.isChecked()
        checkbox_proprietario = self.checkbox_proprietario.isChecked()
        checkbox_terceiro_interessado = self.checkbox_terceiro_interessado.isChecked()
        checkbox_credor_pen = self.checkbox_credor_pen.isChecked()
        checkbox_credor_hip = self.checkbox_credor_hip.isChecked()
        checkbox_credor_fid = self.checkbox_credor_fid.isChecked()
        checkbox_proiminente_comprador = self.checkbox_proiminente_comprador.isChecked()
        checkbox_usufrutuario = self.checkbox_usufrutuario.isChecked()
        checkbox_ocupante = self.checkbox_ocupante.isChecked()
        checkbox_curador_esp = self.checkbox_curador_esp.isChecked()

        # Verificar se o nome já existe no banco de dados
        select_query = "SELECT parte_id FROM partes WHERE nome = ?"
        self.cursor.execute(select_query, (nome,))
        result = self.cursor.fetchone()

        if result:
#            # Se o nome já existe, atualizar o registro existente
            update_query = """
            UPDATE partes
            SET tipo = ?, cpf_cnpj = ?, logradouro = ?, num_bem = ?, complemento = ?, bairro = ?, cidade = ?, combo_uf = ?, oab = ?, cep = ?, 
            logradouro_i = ?, num_bem_i = ?, complemento_i = ?, bairro_i = ?, cidade_i = ?, combo_uf_i = ?, cep_i = ?, 
            logradouro_ii = ?, num_bem_ii = ?, complemento_ii = ?, bairro_ii = ?, cidade_ii = ?, combo_uf_ii = ?, cep_ii = ?, 
            logradouro_iii = ?, num_bem_iii = ?, complemento_iii = ?, bairro_iii = ?, cidade_iii = ?, combo_uf_iii = ?, cep_iii = ?, 
            logradouro_iv = ?, num_bem_iv = ?, complemento_iv = ?, bairro_iv = ?, cidade_iv = ?, combo_uf_iv = ?, cep_iv = ?,
            cel = ?, tel = ?, email_i = ?, email_ii = ?, email_iii = ?, checkbox_exequente = ?, checkbox_adv_exequente = ?, checkbox_executado = ?, checkbox_adv_executado = ?, checkbox_proprietario = ?, checkbox_terceiro_interessado = ?, checkbox_credor_pen = ?, checkbox_credor_hip = ?, checkbox_credor_fid = ?, checkbox_proiminente_comprador = ?, checkbox_usufrutuario = ?, checkbox_ocupante = ?, checkbox_curador_esp = ?
            WHERE parte_id = ?
            """
            
            self.cursor.execute(update_query, (tipo, cpf_cnpj, logradouro, num_bem, complemento, bairro, cidade, combo_uf, oab, cep , logradouro_i, num_bem_i, complemento_i, bairro_i, cidade_i, combo_uf_i, cep_i, logradouro_ii, num_bem_ii, complemento_ii, bairro_ii, cidade_ii, combo_uf_ii, cep_ii, logradouro_iii, num_bem_iii, complemento_iii, bairro_iii, cidade_iii, combo_uf_iii, cep_iii, logradouro_iv, num_bem_iv, complemento_iv, bairro_iv, cidade_iv, combo_uf_iv, cep_iv, cel, tel, email_i, email_ii, email_iii, checkbox_exequente, checkbox_adv_exequente, checkbox_executado, checkbox_adv_executado, checkbox_proprietario, checkbox_terceiro_interessado, checkbox_credor_pen, checkbox_credor_hip, checkbox_credor_fid, checkbox_proiminente_comprador, checkbox_usufrutuario, checkbox_ocupante, checkbox_curador_esp, result[0]))
            QMessageBox.information(self, "Sucesso", f"Parte '{nome}' atualizada com sucesso!")
        else:
#            # Se o nome não existe, inserir um novo registro
            insert_query = """
            INSERT INTO partes  (processo, tipo, nome, cpf_cnpj, logradouro, num_bem, complemento, bairro, cidade, combo_uf, oab, cep, logradouro_i, num_bem_i, complemento_i, bairro_i, cidade_i, combo_uf_i, cep_i, logradouro_ii, num_bem_ii, complemento_ii, bairro_ii, cidade_ii, combo_uf_ii, cep_ii, logradouro_iii, num_bem_iii, complemento_iii, bairro_iii, cidade_iii, combo_uf_iii, cep_iii, logradouro_iv, num_bem_iv, complemento_iv, bairro_iv, cidade_iv, combo_uf_iv, cep_iv, cel, tel, email_i, email_ii, email_iii, checkbox_exequente, checkbox_adv_exequente, checkbox_executado, checkbox_adv_executado, checkbox_proprietario, checkbox_terceiro_interessado, checkbox_credor_pen, checkbox_credor_hip, checkbox_credor_fid, checkbox_proiminente_comprador, checkbox_usufrutuario, checkbox_ocupante, checkbox_curador_esp)
            VALUES (? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
#
            self.cursor.execute(insert_query, (self.processo_fields, tipo, nome, cpf_cnpj, logradouro, num_bem, complemento, bairro, cidade, combo_uf, oab, cep, logradouro_i, num_bem_i, complemento_i, bairro_i, cidade_i, combo_uf_i, cep_i, logradouro_ii, num_bem_ii, complemento_ii, bairro_ii, cidade_ii, combo_uf_ii, cep_ii, logradouro_iii, num_bem_iii, complemento_iii, bairro_iii, cidade_iii, combo_uf_iii, cep_iii, logradouro_iv, num_bem_iv, complemento_iv, bairro_iv, cidade_iv, combo_uf_iv, cep_iv, cel, tel, email_i, email_ii, email_iii, checkbox_exequente, checkbox_adv_exequente, checkbox_executado, checkbox_adv_executado, checkbox_proprietario, checkbox_terceiro_interessado, checkbox_credor_pen, checkbox_credor_hip, checkbox_credor_fid, checkbox_proiminente_comprador, checkbox_usufrutuario, checkbox_ocupante, checkbox_curador_esp))
            QMessageBox.information(self, "Sucesso", f"Parte '{nome}' salva com sucesso!")

        self.conn.commit()
    def load_part_from_db(self):
        print("Processo atual:", self.processo_fields)  # Certifique-se de que isso mostra o ID correto do processo
        select_query = "SELECT parte_id, tipo, cpf_cnpj, logradouro, num_bem, complemento, bairro, cidade, combo_uf, oab, cep , logradouro_i, num_bem_i, complemento_i, bairro_i, cidade_i, combo_uf_i, cep_i, logradouro_ii, num_bem_ii, complemento_ii, bairro_ii, cidade_ii, combo_uf_ii, cep_ii, logradouro_iii, num_bem_iii, complemento_iii, bairro_iii, cidade_iii, combo_uf_iii, cep_iii, logradouro_iv, num_bem_iv, complemento_iv, bairro_iv, cidade_iv, combo_uf_iv, cep_iv, cel, tel, email_i, email_ii, email_iii, checkbox_exequente, checkbox_adv_exequente, checkbox_executado, checkbox_adv_executado, checkbox_proprietario, checkbox_terceiro_interessado, checkbox_credor_pen, checkbox_credor_hip, checkbox_credor_fid, checkbox_proiminente_comprador, checkbox_usufrutuario, checkbox_ocupante, checkbox_curador_esp FROM partes WHERE processo = ?"
        self.cursor.execute(select_query, (self.processo_fields,))
        partes = self.cursor.fetchall()
        
        # Debug: Print fetched parts
        print("Parts fetched from DB:", partes)

        if partes:
            partes_legenda = []
            parte_map = {}

            for parte in partes:
                # Processar o campo "tipo" para definir os checkboxes
                tipo = parte[1]
                types_selected = tipo.split(', ')

                # Atualizar os checkboxes de acordo
                self.checkbox_exequente.setChecked("Exequente" in types_selected)
                self.checkbox_adv_exequente.setChecked("Advogado do Exequente" in types_selected)
                self.checkbox_executado.setChecked("Executado" in types_selected)
                self.checkbox_adv_executado.setChecked("Advogado do Executado" in types_selected)
                self.checkbox_proprietario.setChecked("Proprietários/Coproprietarios" in types_selected)
                self.checkbox_terceiro_interessado.setChecked("Terceiro interessado" in types_selected)
                self.checkbox_credor_pen.setChecked("Credor de Penhora" in types_selected)
                self.checkbox_credor_hip.setChecked("Credor hipotecário" in types_selected)
                self.checkbox_credor_fid.setChecked("Credor Fiduciário" in types_selected)
                self.checkbox_proprietario_registral.setChecked("Proprietário Registral (proprietário formal)" in types_selected)
                self.checkbox_proiminente_comprador.setChecked("Promitente Comprador (promissário comprador)" in types_selected)
                self.checkbox_usufrutuario.setChecked("Usufruário" in types_selected)
                self.checkbox_ocupante.setChecked("Ocupante" in types_selected)
                self.checkbox_curador_esp.setChecked("Curador Especial" in types_selected)

                # Criar o item de legenda para exibição
                legenda = f"{parte[0]} - {parte[2]}"
                partes_legenda.append(legenda)
                parte_map[legenda] = parte

            # Debug: Print generated legends for selection dialog
            print("Generated legends for QInputDialog:", partes_legenda)
            print("Part map:", parte_map)

            item, ok = QInputDialog.getItem(self, "Selecione uma Parte", "Partes:", partes_legenda, 0, False)
            if ok and item:
                selected_part = parte_map[item]
                # Atualizar os campos do formulário baseado no 'selected_part'
                self.nome_field.setText(selected_part[2])
                self.cpf_cnpj_field.setText(selected_part[3])
                self.logradouro_field.setText(selected_part[4])
                self.num_field.setText(selected_part[5])
                self.complemento_field.setText(selected_part[6])
                self.bairro_field.setText(selected_part[7])
                self.cidade_field.setText(selected_part[8])
                self.combo_uf_field.setCurrentText(selected_part[9])
                self.oab_field.setText(selected_part[10])
                self.cep_field.setText(selected_part[11])
                self.logradouro_field_i.setText(selected_part[12])
                self.num_field_i.setText(selected_part[13])
                self.complemento_field_i.setText(selected_part[14])
                self.bairro_field_i.setText(selected_part[15])
                self.cidade_field_i.setText(selected_part[16])
                self.combo_uf_field_i.setCurrentText(selected_part[17])
                self.cep_field_i.setText(selected_part[18])
                self.logradouro_field_ii.setText(selected_part[19])
                self.num_field_ii.setText(selected_part[20])
                self.complemento_field_ii.setText(selected_part[21])
                self.bairro_field_ii.setText(selected_part[22])
                self.cidade_field_ii.setText(selected_part[23])
                self.combo_uf_field_ii.setCurrentText(selected_part[24])
                self.cep_field_ii.setText(selected_part[25])
                self.logradouro_field_iii.setText(selected_part[26])
                self.num_field_iii.setText(selected_part[27])
                self.complemento_field_iii.setText(selected_part[28])
                self.bairro_field_iii.setText(selected_part[29])
                self.cidade_field_iii.setText(selected_part[30])
                self.combo_uf_field_iii.setCurrentText(selected_part[31])
                self.cep_field_iii.setText(selected_part[32])
                self.logradouro_field_iv.setText(selected_part[33])
                self.num_field_iv.setText(selected_part[34])
                self.complemento_field_iv.setText(selected_part[35])
                self.bairro_field_iv.setText(selected_part[36])
                self.cidade_field_iv.setText(selected_part[37])
                self.combo_uf_field_iv.setCurrentText(selected_part[38])
                self.cep_field_iv.setText(selected_part[39])
                self.cel_field.setText(selected_part[40])
                self.tel_field.setText(selected_part[41])
                self.email_i_field.setText(selected_part[42])
                self.email_ii_field.setText(selected_part[43])
                self.email_iii_field.setText(selected_part[44])
                self.nome_field.setText(selected_part[45])
                self.cpf_cnpj_field.setText(selected_part[46])
                self.logradouro_field.setText(selected_part[47])
                self.num_field.setText(selected_part[48])
                self.complemento_field.setText(selected_part[49])
                self.bairro_field.setText(selected_part[50])
                self.cidade_field.setText(selected_part[51])
                self.combo_uf_field.setCurrentText(selected_part[52])
                self.oab_field.setText(selected_part[53])
                self.cep_field.setText(selected_part[54])
                self.logradouro_field_i.setText(selected_part[55])
                self.num_field_i.setText(selected_part[56])
                self.complemento_field_i.setText(selected_part[57])
                self.bairro_field_i.setText(selected_part[58])
                self.cidade_field_i.setText(selected_part[59])
                self.combo_uf_field_i.setCurrentText(selected_part[60])
                self.cep_field_i.setText(selected_part[61])
                self.logradouro_field_ii.setText(selected_part[62])
                self.num_field_ii.setText(selected_part[63])
                self.complemento_field_ii.setText(selected_part[64])
                self.bairro_field_ii.setText(selected_part[65])
                self.cidade_field_ii.setText(selected_part[66])
                self.combo_uf_field_ii.setCurrentText(selected_part[67])
                self.cep_field_ii.setText(selected_part[68])
                self.logradouro_field_iii.setText(selected_part[69])
                self.num_field_iii.setText(selected_part[70])
                self.complemento_field_iii.setText(selected_part[71])
                self.bairro_field_iii.setText(selected_part[72])
                self.cidade_field_iii.setText(selected_part[73])
                self.combo_uf_field_iii.setCurrentText(selected_part[74])
                self.cep_field_iii.setText(selected_part[75])
                self.logradouro_field_iv.setText(selected_part[76])
                self.num_field_iv.setText(selected_part[77])
                self.complemento_field_iv.setText(selected_part[78])
                self.bairro_field_iv.setText(selected_part[79])
                self.cidade_field_iv.setText(selected_part[80])
                self.combo_uf_field_iv.setCurrentText(selected_part[81])
                self.cep_field_iv.setText(selected_part[82])
                self.cel_field.setText(selected_part[83])
                self.tel_field.setText(selected_part[84])
                self.email_i_field.setText(selected_part[85])
                self.email_ii_field.setText(selected_part[86])
                self.email_iii_field.setText(selected_part[87])
                self.checkbox_exequente.setChecked(selected_part[88])
                self.checkbox_adv_exequente.setChecked(selected_part[89])
                self.checkbox_executado.setChecked(selected_part[90])
                self.checkbox_adv_executado.setChecked(selected_part[91])
                self.checkbox_proprietario.setChecked(selected_part[92])
                self.checkbox_terceiro_interessado.setChecked(selected_part[93])
                self.checkbox_credor_pen.setChecked(selected_part[94])
                self.checkbox_credor_hip.setChecked(selected_part[95])
                self.checkbox_credor_fid.setChecked(selected_part[96])
                self.checkbox_proiminente_comprador.setChecked(selected_part[97])
                self.checkbox_usufrutuario.setChecked(selected_part[98])
                self.checkbox_ocupante.setChecked(selected_part[99])
                self.checkbox_curador_esp.setChecked(selected_part[100])


        else:
            QMessageBox.warning(self, "Aviso", "Nenhuma parte encontrada para este processo.")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())