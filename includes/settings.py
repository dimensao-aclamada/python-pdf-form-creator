from reportlab.lib.pagesizes import A4

PDF_FILENAME = "relatorio_mensal_oficinas_.pdf"

# -------------------------------------------------
# CONFIGURAÇÕES DE PÁGINA
# -------------------------------------------------
PAGE_WIDTH, PAGE_HEIGHT = A4

MARGIN_LEFT   = 50
MARGIN_RIGHT  = PAGE_WIDTH - 50
MARGIN_TOP    = PAGE_HEIGHT - 50
MARGIN_BOTTOM = 50
FIELD_HEIGHT  = 20
LINE_SPACING  = 25
SECTION_SPACING = 35

# -------------------------------------------------
# CONFIGURAÇÕES GLOBAIS DE ESPAÇAMENTO
# -------------------------------------------------
TITLE_MARGIN_TOP    = 12   # pts acima do título
TITLE_MARGIN_BOTTOM = 8    # pts abaixo do título

LABEL_MARGIN_TOP    = 6    # pts acima do rótulo (placeholder)
LABEL_MARGIN_BOTTOM = 4    # pts abaixo do rótulo (antes da caixa)

LABEL_SPACING      = 6    # espaço extra entre rótulo e caixa

# -------------------------------------------------
# PADES (espaço interno) PADRÃO – pode ser sobrescrito em cada chamada
# -------------------------------------------------
DEFAULT_PAD_X = 6   # pontos à esquerda e à direita
DEFAULT_PAD_Y = 4   # pontos acima e abaixo

# -------------------------------------------------
# LOGOTIPOS (vários) – ajuste o caminho/dimensões conforme necessário
# -------------------------------------------------
# Defina aqui **todos** os arquivos de logotipo que deverão aparecer
LOGO_PATHS = [
    "logos/logo-na.png",
    "logos/logo-nasf.png",
    "logos/logo-eventos.png",
    "logos/logo-longo-alcance.png",
    "logos/logo-lda.png",
    "logos/logo-ag.png",
    "logos/logo-ai.png",
]                                   # ←←← ADICIONE OU REMOVA LOGOS AQUI
LOGO_SPACING = 10                 # espaço entre um logo e outro (pts)
LOGO_MAX_HEIGHT = 40              # altura máxima de cada logo (pts)
LOGO_MAX_WIDTH  = 40             # largura máxima de cada logo (pts)
