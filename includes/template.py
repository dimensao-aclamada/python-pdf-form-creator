# includes/template.py
"""
Layout (template) for PDFFormBuilder.

The function is written as a **free function** that receives the builder
instance (`self`) as its first argument.  All constants are read from the
instance (e.g. `self.MARGIN_LEFT`) – they are already attached to the
instance in PDFFormBuilder.__init__ (see the builder file).  This makes the
function completely independent and easy to unit‑test.

The function returns the same tuple that the original method returned:
    (io.BytesIO buffer, list_of_PDFFormField objects)
"""

from __future__ import annotations
import os
import io
from datetime import datetime
from dateutil.relativedelta import relativedelta
from reportlab.lib import colors
from includes.helpers import *




# ----------------------------------------------------------------------
# The actual template (formerly PDFFormBuilder.build)
# ----------------------------------------------------------------------
def build(self: "PDFFormBuilder") -> tuple[io.BytesIO, list[PDFFormField]]:
    """Desenha todo o layout e devolve (buffer, lista_de_campos)."""

    # -------------------------------------------------
    # 1️⃣  LOGOTIPOS (vários)
    # -------------------------------------------------
    logo_base_y = self.MARGIN_TOP - self.LOGO_MAX_HEIGHT
    cur_x = self.MARGIN_LEFT

    for logo_path in self.LOGO_PATHS:
        if not os.path.isfile(logo_path):
            print(f"[AVISO] Logotipo não encontrado: {logo_path}")
            continue

        self.canvas.drawImage(
            logo_path,
            cur_x,
            logo_base_y,
            width=self.LOGO_MAX_WIDTH,
            height=self.LOGO_MAX_HEIGHT,
            preserveAspectRatio=True,
            mask='auto',
        )
        cur_x += self.LOGO_MAX_WIDTH + self.LOGO_SPACING

    # posiciona o cursor logo abaixo da linha de logos
    self.y_pos = logo_base_y - 30   # 30 pts de espaçamento extra

    # -------------------------------------------------
    # 2️⃣  TÍTULO PRINCIPAL
    # -------------------------------------------------
    self.canvas.setFont("Helvetica-Bold", 16)
    self.canvas.drawString(self.MARGIN_LEFT, self.y_pos,
                           "RELATÓRIO MENSAL DAS OFICINAS")
    self.y_pos -= 20
    self.canvas.drawString(self.MARGIN_LEFT, self.y_pos, "RP CSA NASF")
    self.y_pos -= 30

    self.canvas.setFont("Helvetica", 10)
    self.canvas.drawString(self.MARGIN_LEFT, self.y_pos,
                           "Este formulário padroniza o Relatório Mensal de Serviço.")
    self.y_pos -= 15
    self.canvas.drawString(self.MARGIN_LEFT, self.y_pos,
                           "Em espírito de irmandade.")
    self.y_pos -= self.SECTION_SPACING

    # -------------------------------------------------
    # 1️⃣ IDENTIFICAÇÃO E ENCARGO
    # -------------------------------------------------
    self.add_title("IDENTIFICAÇÃO DA ESTRUTURA", 12)

    oficinas = [
        "Hospitais e Instituições (H&I)",
        "Informação ao Público (IP)",
        "Longo Alcance (LA)",
        "Eventos",
        "Arte e Grafismo (AG)",
        "Linha de Ajuda (LDA)",
        "Apoio à Informática (AI)",
    ]
    self.add_dropdown_field("oficina_servico",
                         "Oficina em Serviço",
                         oficinas,
                         required=True)

    month_year_options = generate_month_year_options(36)
    self.add_dropdown_field("periodo_referencia",
                            "Período de Referência",
                            month_year_options,
                            required=True)

    self.add_text_field("nome_responsavel",
                        "Primeiro Nome do(a) Servidor(a) Responsável",
                        required=True)

    encargos = ["Coordenador", "Vice‑Coordenador", "Secretário"]
    self.add_dropdown_field("encargo",
                            "Encargo",
                            encargos,
                            required=True)

    self.add_date_field("data_proxima_reuniao",
                        "Data da Próxima Reunião Administrativa",
                        required=True)

    # -------------------------------------------------
    # 2️⃣  ESTRUTURA EM SERVIÇO E PRESENÇA
    # -------------------------------------------------
    self.new_page()
    self.add_title("ESTRUTURA EM SERVIÇO E PRESENÇA", 12)

    self.add_dropdown_field(
        "fim_termo_coordenador",
        "Fim do Termo (Coordenador)",
        month_year_options,
        help_text="Mês/Ano previsto para a renovação do encargo.",
    )

    self.add_text_field(
        "nome_vice_coordenador",
        "Primeiro Nome do(a) Vice‑Coordenador(a)",
        help_text="Preencher 'VAGO' se aplicável.",
    )

    self.add_paragraph_field(
        "plano_eletiva_vice",
        "Plano de Eletiva (Vice), se aplicável",
        help_text="Descreva o plano (data, busca ativa, etc.) se o cargo estiver Vago.",
    )

    self.add_text_field(
        "nome_secretario",
        "Primeiro Nome do(a) Secretário(a)",
        help_text="Preencher 'VAGO' se aplicável.",
    )

    self.add_paragraph_field(
        "plano_eletiva_secretario",
        "Plano de Eletiva (Secretário), se aplicável",
        help_text="Descreva o plano (data, busca ativa, etc.) se o cargo estiver Vago.",
    )

    # -------------------------------------------------
    # 3️⃣  REUNIÕES ORDINÁRIAS (5)
    # -------------------------------------------------
    for i in range(1, 6):
        self.new_page()
        self.check_space()
        self.add_title(f"REUNIÃO ORDINÁRIA Nº {i}", 11)

        self.add_date_field(f"data_reuniao_{i}",
                            f"Data da Reunião Nº {i}")

        # Membros Presentes (texto + dropdown 0‑100)
        self.add_text_with_dropdown(
            name_text=f"membros_presentes_{i}_txt",
            name_dropdown=f"membros_presentes_{i}_opt",
            label=f"Membros Presentes (Nº {i})",
            dropdown_options=numeric_range(0, 100),
            help_text="Total de companheiros (Mesa, Servidores, Membros Interessados) presentes.",
        )

        # Estruturas/Grupos Representados (parágrafo livre)
        self.add_paragraph_field(
            f"estruturas_representadas_{i}_txt",
            f"Estruturas/Grupos Representados (Nº {i})",
            help_text="Liste os RSGs ou Servidores de outros CSAs/Oficinas que estavam presentes.",
        )

        # Quantitativos associados ao parágrafo acima
        self.add_dropdown_field(
            f"grupos_csa_{i}",
            "Grupos do CSA representados",
            numeric_range(0, 20),
            help_text="Número de grupos do CSA presentes.",
        )
        self.add_dropdown_field(
            f"representantes_mesa_{i}",
            "Representantes da Mesa do CSA",
            numeric_range(0, 10),
            help_text="Quantos representantes da Mesa do CSA estavam presentes.",
        )
        self.add_dropdown_field(
            f"outros_csas_{i}",
            "Outros CSAs representados",
            numeric_range(0, 10),
            help_text="Outros CSAs que enviaram representantes.",
        )
        self.add_dropdown_field(
            f"outras_estruturas_{i}",
            "Outras estruturas de Serviço",
            numeric_range(0, 10),
            help_text="Outras estruturas (ex.: RC, CSAP) que marcaram presença.",
        )

        # Observação da Reunião (opcional)
        self.add_paragraph_field(
            f"observacao_reuniao_{i}",
            f"Observação da Reunião (Nº {i}) (Opcional)",
            help_text="Principais temas ou decisões, se achar pertinente.",
        )

    # -------------------------------------------------
    # 4️⃣  NOSSOS PASSOS EM AÇÃO (Métricas do 5º Conceito)
    # -------------------------------------------------
    self.new_page()
    self.add_title("NOSSOS PASSOS EM AÇÃO (Métricas do 5º Conceito)", 12)

    # Alcance da Mensagem (Lista de Atividades) – substitui o campo único
    self.add_title("Alcance da Mensagem (Impacto) - Registro de Atividades (Máx. 10)", 11)

    for i in range(1, 11):  # 10 atividades
        
        if i>1:
            self.new_page()

        prefix = f"atividade_{i}"

        # 250 pts de espaço mínimo antes de cada bloco
        self.check_space(250)

        # Título da Atividade
        self.add_title(f"Atividade de Serviço Nº {i}", 10,
                       margin_top=20, margin_bottom=5)

        # 1. Descrição
        self.add_text_field(
            name=f"{prefix}_descricao",
            label="1. Nome/Descrição da Atividade",
            required=False,
            help_text="Descreva o tipo de atividade (Ex: Painel H&I, Treinamento de Protocolos, Feira IP).",
        )

        # 2. Data
        self.add_date_field(
            name_prefix=f"{prefix}_data",
            label="2. Data da Atividade",
            required=False,
        )

        # 3. Público Interno
        self.add_text_with_dropdown(
            name_text=f"{prefix}_pub_int_txt",
            name_dropdown=f"{prefix}_pub_int_opt",
            label="3. Público Interno Alcançado",
            dropdown_options=alcance_impacto_options(),
            required=False,
            help_text="Companheiros de NA (Membros da Oficina/Outras Estruturas) presentes.",
        )

        # 4. Público Externo
        self.add_text_with_dropdown(
            name_text=f"{prefix}_pub_ext_txt",
            name_dropdown=f"{prefix}_pub_ext_opt",
            label="4. Público Externo Alcançado",
            dropdown_options=alcance_impacto_options(),
            required=False,
            help_text="Residentes/Pacientes, Profissionais de Saúde/Segurança, Público em Geral.",
        )

        # 5. Nº de Servidores
        self.add_dropdown_field(
            name=f"{prefix}_servidores",
            label="5. Nº de Servidores Envolvidos",
            options=numeric_range(0, 50),
            required=False,
            width=100,
            help_text="Total de membros que trabalharam na atividade.",
        )
        # Espaço extra entre blocos
        self.y_pos -= 10

    # -------------------------------------------------
    # Campos que vêm depois de “Alcance da Mensagem”
    # -------------------------------------------------
    self.new_page()

    self.add_text_with_dropdown(
        name_text="membros_ativos_txt",
        name_dropdown="membros_ativos_opt",
        label="Membros Ativos no Serviço da Oficina",
        dropdown_options=numeric_range(0, 50),
        required=True,
        help_text="Número de membros que prestaram serviço ativamente (exceto Mesa).",
    )

    self.add_text_with_dropdown(
        name_text="documentos_criados_txt",
        name_dropdown="documentos_criados_opt",
        label="Número de Documentos Criados/Revisados",
        dropdown_options=numeric_range(0, 50),
        required=True,
        help_text="Ex: Guia de Procedimentos, Manual de Capacitação, etc.",
    )

    # -------------------------------------------------
    # 5️⃣  MOÇÕES E COMPROMISSOS
    # -------------------------------------------------
    self.new_page()
    self.add_title("MOÇÕES E COMPROMISSOS PARA APROVAÇÃO/ASSUNÇÃO", 12)

    status_mocao_options = [
        "Não Aplicável (Deixar em branco)",
        "Aprovada",
        "Reprovada",
        "Em Votação",
        "Assumido (Compromisso Interno)",
    ]

    for i in range(1, 9):
        self.check_space(150)

        self.add_text_field(
            f"mocao_item_{i}",
            f"Item para Aprovação/Assunção Nº {i}",
            help_text=f"Descreva o tema principal da Moção/Compromisso {i} (Opcional).",
        )
        self.add_dropdown_field(
            f"mocao_status_{i}",
            f"Status do Item Nº {i}",
            status_mocao_options,
        )

    # -------------------------------------------------
    # 6️⃣  COMPARTILHAMENTO DE FORÇA E DESAFIOS
    # -------------------------------------------------
    self.new_page()
    self.add_title("COMPARTILHAMENTO DE FORÇA E DESAFIOS", 12)

    self.add_paragraph_field(
        "forca_crescimento",
        "Força e Crescimento (O que deu certo)",
        required=True,
        help_text="Descreva ações de Impacto e as Parcerias de sucesso.",
    )
    self.add_paragraph_field(
        "oportunidades_resposta",
        "Oportunidades de Resposta (Onde precisamos de ajuda)",
        help_text="Problemas técnicos ou práticos que dificultaram o serviço.",
    )
    self.add_paragraph_field(
        "proximos_passos",
        "Próximos Passos em Serviço",
        required=True,
        help_text="Detalhe o Principal Objetivo de Serviço para o desenvolvimento da irmandade.",
    )

    # ---------- FINALIZA ----------
    self.canvas.save()
    self.buffer.seek(0)
    return self.buffer, self.fields
