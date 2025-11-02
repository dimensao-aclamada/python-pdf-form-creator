
"""
EDITABLE PDF BUILDER
Form Generator using PyPDF2 + ReportLab
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    DictionaryObject,
    ArrayObject,
    NameObject,
    NumberObject,
    create_string_object,
)
import io
import os

# Configurações e helpers do seu projeto:
from includes.settings import *
from includes.helpers import *
from includes.settings import (PDF_FILENAME)
# -------------------------------------------------
# CLASSE AUXILIAR PARA GUARDAR INFORMAÇÕES DE CAMPO
# -------------------------------------------------
class PDFFormField:
    """Representa um widget que será inserido no PDF final."""
    def __init__(self, name, field_type, x, y, width, height,
                 options=None, required=False):
        self.name = name
        self.field_type = field_type       # 'text', 'dropdown', 'radio'
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.options = options or []
        self.required = required
        self.page_num = 0                  # será preenchido ao ser adicionado


# -------------------------------------------------
# BUILDER – CRIA O PDF ESTÁTICO COM REPORTLAB
# -------------------------------------------------
class PDFFormBuilder:
    """Desenha o layout (ReportLab) e registra todos os widgets."""
    def __init__(self):
        # -------------------------------------------------
        # 1️⃣  Copia as constantes globais para a instância
        # -------------------------------------------------
        # margens / espaçamentos
        self.MARGIN_LEFT = MARGIN_LEFT
        self.MARGIN_RIGHT = MARGIN_RIGHT
        self.MARGIN_TOP = MARGIN_TOP
        self.MARGIN_BOTTOM = MARGIN_BOTTOM
        self.TITLE_MARGIN_TOP = TITLE_MARGIN_TOP
        self.TITLE_MARGIN_BOTTOM = TITLE_MARGIN_BOTTOM
        self.SECTION_SPACING = SECTION_SPACING
        self.LABEL_MARGIN_TOP = LABEL_MARGIN_TOP
        self.LABEL_MARGIN_BOTTOM = LABEL_MARGIN_BOTTOM
        self.LABEL_SPACING = LABEL_SPACING
        self.FIELD_HEIGHT = FIELD_HEIGHT
        self.LINE_SPACING = LINE_SPACING
        self.DEFAULT_PAD_X = DEFAULT_PAD_X
        self.DEFAULT_PAD_Y = DEFAULT_PAD_Y

        # logos
        self.LOGO_PATHS = LOGO_PATHS
        self.LOGO_MAX_WIDTH = LOGO_MAX_WIDTH
        self.LOGO_MAX_HEIGHT = LOGO_MAX_HEIGHT
        self.LOGO_SPACING = LOGO_SPACING

        # -------------------------------------------------
        # 2️⃣  Cria o canvas e inicializa a lista de campos
        # -------------------------------------------------
        self.fields = []
        self.buffer = io.BytesIO()
        self.canvas = canvas.Canvas(self.buffer, pagesize=A4)
        self.y_pos = self.MARGIN_TOP
        self.current_page = 0

    # -----------------------------------------------------------------
    # HELPERS DE TEXTO
    # -----------------------------------------------------------------
    def add_title(self, text, font_size=14,
                  margin_top=TITLE_MARGIN_TOP,
                  margin_bottom=TITLE_MARGIN_BOTTOM):
        """Desenha um título com margens configuráveis."""
        self.y_pos -= margin_top
        self.canvas.setFont("Helvetica-Bold", font_size)
        self.canvas.drawString(self.MARGIN_LEFT, self.y_pos, text)
        self.y_pos -= (margin_bottom + self.SECTION_SPACING - margin_top)

    def add_help_text(self, text):
        self.canvas.setFont("Helvetica-Oblique", 8)
        self.canvas.setFillColor(colors.grey)
        self.canvas.drawString(self.MARGIN_LEFT + 5, self.y_pos, text)
        self.canvas.setFillColor(colors.black)
        self.y_pos -= 15

    # -----------------------------------------------------------------
    # CAMPOS BÁSICOS (texto, parágrafo, dropdown, rádio, data)
    # -----------------------------------------------------------------
    def add_text_field(self, name, label, required=False,
                       help_text="", pad_x=DEFAULT_PAD_X,
                       pad_y=DEFAULT_PAD_Y,
                       margin_top=LABEL_MARGIN_TOP,
                       margin_bottom=LABEL_MARGIN_BOTTOM,
                       label_spacing=LABEL_SPACING):
        """Campo de texto simples (1 linha) com padding e espaçamento."""
        self.y_pos -= margin_top
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(self.MARGIN_LEFT, self.y_pos,
                               f"{label}{' *' if required else ''}")
        self.y_pos -= 20                     # linha do label

        if help_text:
            self.add_help_text(help_text)

        self.y_pos -= label_spacing          # espaço extra entre label e caixa
        self.y_pos -= margin_bottom          # margem inferior antes da caixa

        total_width = self.MARGIN_RIGHT - self.MARGIN_LEFT
        self.canvas.setStrokeColor(colors.black)
        self.canvas.rect(self.MARGIN_LEFT, self.y_pos,
                         total_width, self.FIELD_HEIGHT)

        widget_x = self.MARGIN_LEFT + pad_x
        widget_y = self.y_pos + pad_y
        widget_w = total_width - 2 * pad_x
        widget_h = self.FIELD_HEIGHT - 2 * pad_y

        field = PDFFormField(name, 'text',
                             widget_x, widget_y,
                             widget_w, widget_h,
                             required=required)
        field.page_num = self.current_page
        self.fields.append(field)

        self.y_pos -= self.LINE_SPACING

    def add_paragraph_field(self, name, label, required=False,
                            help_text="", pad_x=DEFAULT_PAD_X,
                            pad_y=DEFAULT_PAD_Y,
                            margin_top=LABEL_MARGIN_TOP,
                            margin_bottom=LABEL_MARGIN_BOTTOM,
                            label_spacing=LABEL_SPACING):
        """Campo de texto multilinha (área) com padding e espaçamento."""
        self.y_pos -= margin_top
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(self.MARGIN_LEFT, self.y_pos,
                               f"{label}{' *' if required else ''}")
        self.y_pos -= 20

        if help_text:
            self.add_help_text(help_text)

        self.y_pos -= label_spacing
        self.y_pos -= margin_bottom

        total_width = self.MARGIN_RIGHT - self.MARGIN_LEFT
        self.canvas.setStrokeColor(colors.black)
        self.canvas.rect(self.MARGIN_LEFT, self.y_pos - 40,
                         total_width, 60)

        widget_x = self.MARGIN_LEFT + pad_x
        widget_y = self.y_pos - 40 + pad_y
        widget_w = total_width - 2 * pad_x
        widget_h = 60 - 2 * pad_y

        field = PDFFormField(name, 'text',
                             widget_x, widget_y,
                             widget_w, widget_h,
                             required=required)
        field.page_num = self.current_page
        self.fields.append(field)

        self.y_pos -= 85

    def add_dropdown_field(self, name, label, options,
                           required=False, help_text="",
                           width=None, pad_x=DEFAULT_PAD_X,
                           pad_y=DEFAULT_PAD_Y,
                           margin_top=LABEL_MARGIN_TOP,
                           margin_bottom=LABEL_MARGIN_BOTTOM,
                           label_spacing=LABEL_SPACING):
        """Dropdown (combo) com padding e espaçamento."""
        self.y_pos -= margin_top
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(self.MARGIN_LEFT, self.y_pos,
                               f"{label}{' *' if required else ''}")
        self.y_pos -= 20

        if help_text:
            self.add_help_text(help_text)

        self.y_pos -= label_spacing
        self.y_pos -= margin_bottom

        field_width = width or (self.MARGIN_RIGHT - self.MARGIN_LEFT)

        self.canvas.setStrokeColor(colors.black)
        self.canvas.rect(self.MARGIN_LEFT, self.y_pos,
                         field_width, self.FIELD_HEIGHT)

        self.canvas.setFillColor(colors.grey)
        self.canvas.drawString(self.MARGIN_LEFT + field_width - 15,
                               self.y_pos + 5, "▼")
        self.canvas.setFillColor(colors.black)

        widget_x = self.MARGIN_LEFT + pad_x
        widget_y = self.y_pos + pad_y
        widget_w = field_width - 2 * pad_x
        widget_h = self.FIELD_HEIGHT - 2 * pad_y

        field = PDFFormField(name, 'dropdown',
                             widget_x, widget_y,
                             widget_w, widget_h,
                             options=options,
                             required=required)
        field.page_num = self.current_page
        self.fields.append(field)

        self.y_pos -= self.LINE_SPACING

    def add_radio_group(self, name, label, options,
                        required=False, help_text=""):
        """Grupo de botões de rádio (não utiliza padding próprio)."""
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(self.MARGIN_LEFT, self.y_pos,
                               f"{label}{' *' if required else ''}")
        self.y_pos -= 20

        if help_text:
            self.add_help_text(help_text)

        radio_size = 12
        offset = 20

        for opt in options:
            self.canvas.setStrokeColor(colors.black)
            self.canvas.circle(self.MARGIN_LEFT + 6,
                               self.y_pos + 4,
                               radio_size / 2,
                               stroke=1, fill=0)

            self.canvas.setFont("Helvetica", 9)
            self.canvas.drawString(self.MARGIN_LEFT + offset, self.y_pos, opt)

            field = PDFFormField(name, 'radio',
                                 self.MARGIN_LEFT, self.y_pos - 2,
                                 radio_size, radio_size,
                                 options=[opt],
                                 required=required)
            field.radio_value = opt
            field.page_num = self.current_page
            self.fields.append(field)

            self.y_pos -= 18

        self.y_pos -= 10

    def add_date_field(self, name_prefix, label, required=False,
                       help_text="",
                       margin_top=LABEL_MARGIN_TOP,
                       margin_bottom=LABEL_MARGIN_BOTTOM,
                       label_spacing=LABEL_SPACING):
        """Três dropdowns (dia/mês/ano) com padding + espaçamento."""
        self.y_pos -= margin_top
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(self.MARGIN_LEFT, self.y_pos,
                               f"{label}{' *' if required else ''}")
        self.y_pos -= 20

        if help_text:
            self.add_help_text(help_text)

        self.y_pos -= label_spacing
        self.y_pos -= margin_bottom

        day_width   = 60  
        month_width = 80  # Simplificado e reduzido
        year_width  = 70  
        spacing = 15      # Espaçamento entre os campos
        cur_x = MARGIN_LEFT

        # --------- DIA ----------
        self.canvas.setFont("Helvetica", 9)
        self.canvas.drawString(cur_x, self.y_pos + 5, "Dia:")

        self.canvas.setStrokeColor(colors.black)
        self.canvas.rect(cur_x + 25, self.y_pos, day_width, self.FIELD_HEIGHT)
        self.canvas.setFillColor(colors.grey)
        self.canvas.drawString(cur_x + day_width + 15,
                               self.y_pos + 5, "▼")
        self.canvas.setFillColor(colors.black)

        field = PDFFormField(f"{name_prefix}_dia", 'dropdown',
                             cur_x + 25 + self.DEFAULT_PAD_X,
                             self.y_pos + self.DEFAULT_PAD_Y,
                             day_width - 2 * self.DEFAULT_PAD_X,
                             self.FIELD_HEIGHT - 2 * self.DEFAULT_PAD_Y,
                             options=generate_day_options(),
                             required=required)
        field.page_num = self.current_page
        self.fields.append(field)

        cur_x += day_width + 25 + spacing

        # --------- MÊS ----------
        self.canvas.drawString(cur_x, self.y_pos + 5, "Mês:")

        self.canvas.rect(cur_x + 30, self.y_pos, month_width, self.FIELD_HEIGHT)
        self.canvas.setFillColor(colors.grey)
        self.canvas.drawString(cur_x + month_width + 20,
                               self.y_pos + 5, "▼")
        self.canvas.setFillColor(colors.black)

        field = PDFFormField(f"{name_prefix}_mes", 'dropdown',
                             cur_x + 30 + self.DEFAULT_PAD_X,
                             self.y_pos + self.DEFAULT_PAD_Y,
                             month_width - 2 * self.DEFAULT_PAD_X,
                             self.FIELD_HEIGHT - 2 * self.DEFAULT_PAD_Y,
                             options=generate_month_options(),
                             required=required)
        field.page_num = self.current_page
        self.fields.append(field)

        cur_x += month_width + 30 + spacing

        # --------- ANO ----------
        self.canvas.drawString(cur_x, self.y_pos + 5, "Ano:")

        self.canvas.rect(cur_x + 30, self.y_pos, year_width, self.FIELD_HEIGHT)
        self.canvas.setFillColor(colors.grey)
        self.canvas.drawString(cur_x + year_width + 20,
                               self.y_pos + 5, "▼")
        self.canvas.setFillColor(colors.black)

        field = PDFFormField(f"{name_prefix}_ano", 'dropdown',
                             cur_x + 30 + self.DEFAULT_PAD_X,
                             self.y_pos + self.DEFAULT_PAD_Y,
                             year_width - 2 * self.DEFAULT_PAD_X,
                             self.FIELD_HEIGHT - 2 * self.DEFAULT_PAD_Y,
                             options=generate_year_options(5),
                             required=required)
        field.page_num = self.current_page
        self.fields.append(field)

        self.y_pos -= self.LINE_SPACING

    # -----------------------------------------------------------------
    # TEXT + DROPDOWN (campo quantitativo)
    # -----------------------------------------------------------------
    def add_text_with_dropdown(self,
                               name_text: str,
                               name_dropdown: str,
                               label: str,
                               dropdown_options,
                               required=False,
                               help_text="",
                               width_text=None,
                               width_dropdown=80,
                               pad_x_text=DEFAULT_PAD_X,
                               pad_y_text=DEFAULT_PAD_Y,
                               pad_x_dd=DEFAULT_PAD_X,
                               pad_y_dd=DEFAULT_PAD_Y,
                               margin_top=LABEL_MARGIN_TOP,
                               margin_bottom=LABEL_MARGIN_BOTTOM,
                               label_spacing=LABEL_SPACING):
        """Campo texto + dropdown com padding e espaçamento."""
        self.y_pos -= margin_top
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(self.MARGIN_LEFT, self.y_pos,
                               f"{label}{' *' if required else ''}")
        self.y_pos -= 20

        if help_text:
            self.add_help_text(help_text)

        self.y_pos -= label_spacing
        self.y_pos -= margin_bottom

        total_width = self.MARGIN_RIGHT - self.MARGIN_LEFT
        if width_text is None:
            width_text = total_width - width_dropdown - 10   # 10 pts entre os widgets

        # Borda que envolve ambos os widgets
        self.canvas.setStrokeColor(colors.black)
        self.canvas.rect(self.MARGIN_LEFT, self.y_pos,
                         total_width, self.FIELD_HEIGHT)

        # ---------- Texto ----------
        txt_x = self.MARGIN_LEFT + pad_x_text
        txt_y = self.y_pos + pad_y_text
        txt_w = width_text - 2 * pad_x_text
        txt_h = self.FIELD_HEIGHT - 2 * pad_y_text

        txt_field = PDFFormField(name_text, 'text',
                                 txt_x, txt_y, txt_w, txt_h,
                                 required=required)
        txt_field.page_num = self.current_page
        self.fields.append(txt_field)

        # ---------- Dropdown ----------
        ddl_x = self.MARGIN_LEFT + width_text + 10 + pad_x_dd
        ddl_y = self.y_pos + pad_y_dd
        ddl_w = width_dropdown - 2 * pad_x_dd
        ddl_h = self.FIELD_HEIGHT - 2 * pad_y_dd

        self.canvas.setFillColor(colors.grey)
        self.canvas.drawString(ddl_x + ddl_w - 15,
                               ddl_y + 5, "▼")
        self.canvas.setFillColor(colors.black)

        ddl_field = PDFFormField(name_dropdown, 'dropdown',
                                 ddl_x, ddl_y, ddl_w, ddl_h,
                                 options=dropdown_options,
                                 required=required)
        ddl_field.page_num = self.current_page
        self.fields.append(ddl_field)

        self.y_pos -= self.LINE_SPACING

    # -----------------------------------------------------------------
    # CONTROLE DE PÁGINAS
    # -----------------------------------------------------------------
    def new_page(self):
        self.canvas.showPage()
        self.current_page += 1
        self.y_pos = self.MARGIN_TOP

    def check_space(self, needed_space=200):
        if self.y_pos < needed_space:
            self.new_page()

# -------------------------------------------------
#  PATCH TEMPLATE (build) ONTO PDFFormBuilder
# -------------------------------------------------
# **Importante:** o patch vem *depois* da definição da classe.
from includes.template import build as _build_template
PDFFormBuilder.build = _build_template
# -------------------------------------------------
# ADIÇÃO DE ANOTAÇÕES (PyPDF2)
# -------------------------------------------------
def add_form_fields_to_pdf(pdf_buffer, fields, output_filename):
    """Incorpora as anotações interativas ao PDF já desenhado."""
    reader = PdfReader(pdf_buffer)
    writer = PdfWriter()

    # copia páginas
    for page in reader.pages:
        writer.add_page(page)

    # agrupa campos por página
    fields_by_page = {}
    for f in fields:
        fields_by_page.setdefault(f.page_num, []).append(f)

    # cria anotações
    for page_num, page_fields in fields_by_page.items():
        page = writer.pages[page_num]

        if "/Annots" not in page:
            page[NameObject("/Annots")] = ArrayObject()

        for f in page_fields:
            if f.field_type == "text":
                annot = create_text_field(f, page)
            elif f.field_type == "dropdown":
                annot = create_dropdown_field(f, page)
            elif f.field_type == "radio":
                annot = create_radio_field(f, page)
            else:
                continue
            page["/Annots"].append(writer._add_object(annot))

    with open(output_filename, "wb") as out_f:
        writer.write(out_f)

    print(f"PDF gerado com sucesso → {output_filename}")


def create_text_field(field, page):
    annot = DictionaryObject()
    annot.update(
        {
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject("/Widget"),
            NameObject("/FT"): NameObject("/Tx"),
            NameObject("/T"): create_string_object(field.name),
            NameObject("/Rect"): ArrayObject(
                [
                    NumberObject(field.x),
                    NumberObject(field.y),
                    NumberObject(field.x + field.width),
                    NumberObject(field.y + field.height),
                ]
            ),
            NameObject("/P"): page,
            NameObject("/F"): NumberObject(4),          # imprimir
        }
    )
    if field.height > 30:  # multiline
        annot[NameObject("/Ff")] = NumberObject(4096)
    return annot


def create_dropdown_field(field, page):
    opts = ArrayObject()
    for o in field.options:
        opts.append(create_string_object(o))

    annot = DictionaryObject()
    annot.update(
        {
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject("/Widget"),
            NameObject("/FT"): NameObject("/Ch"),
            NameObject("/T"): create_string_object(field.name),
            NameObject("/Rect"): ArrayObject(
                [
                    NumberObject(field.x),
                    NumberObject(field.y),
                    NumberObject(field.x + field.width),
                    NumberObject(field.y + field.height),
                ]
            ),
            NameObject("/Opt"): opts,
            NameObject("/P"): page,
            NameObject("/F"): NumberObject(4),
            NameObject("/Ff"): NumberObject(131072),   # combo‑box
        }
    )
    return annot


def create_radio_field(field, page):
    annot = DictionaryObject()
    annot.update(
        {
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject("/Widget"),
            NameObject("/FT"): NameObject("/Btn"),
            NameObject("/T"): create_string_object(field.name),
            NameObject("/Rect"): ArrayObject(
                [
                    NumberObject(field.x),
                    NumberObject(field.y),
                    NumberObject(field.x + field.width),
                    NumberObject(field.y + field.height),
                ]
            ),
            NameObject("/P"): page,
            NameObject("/F"): NumberObject(4),
            NameObject("/Ff"): NumberObject(49152),    # radio
            NameObject("/AS"): NameObject("/Off"),
            NameObject("/V"): NameObject("/Off"),
        }
    )
    if hasattr(field, "radio_value"):
        annot[NameObject("/TU")] = create_string_object(field.radio_value)
    return annot


# -------------------------------------------------
# FUNÇÃO PRINCIPAL – GERA O PDF FINAL
# -------------------------------------------------
def create_pdf_form(filename=PDF_FILENAME):
    print("Construindo layout do PDF…")
    builder = PDFFormBuilder()
    pdf_buf, fields = builder.build()          # ← agora funciona

    print(f"Adicionando {len(fields)} widgets ao PDF…")
    add_form_fields_to_pdf(pdf_buf, fields, filename)


# -------------------------------------------------
# EXECUÇÃO
# -------------------------------------------------
if __name__ == "__main__":
    try:
        create_pdf_form()
    except ImportError as exc:
        print("Pacotes ausentes. Instale com:")
        print("    pip install reportlab pypdf python-dateutil")
        print(f"Detalhes: {exc}")
    except Exception as exc:
        print(f"Erro ao gerar o PDF: {exc}")
        import traceback
        traceback.print_exc()
