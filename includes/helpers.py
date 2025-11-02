import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta

# ----------------------------------------------------------------------
# custom helper functions
# ----------------------------------------------------------------------

def alcance_impacto_options():
    base = numeric_range(0, 100)
    base.extend(["1000", "10000"])
    return base


# -------------------------------------------------
# generic helper functions
# -------------------------------------------------
def generate_day_options():
    return [str(i) for i in range(1, 32)]

def generate_year_options(num_years=3):
    today = datetime.now()
    return [str(today.year + i) for i in range(num_years)]

def generate_month_options():
    return [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
    ]

def generate_month_year_options(num_months=36):
    months_pt = generate_month_options()
    today = datetime.now()
    options = []
    for i in range(num_months):
        date = today + relativedelta(months=i)
        month = months_pt[date.month - 1]
        year = date.year
        options.append(f"{month}/{year}")
    return options

def numeric_range(start: int, stop: int, step: int = 1):
    """Retorna lista de strings numéricas de start a stop (inclusive)."""
    return [str(v) for v in range(start, stop + 1, step)]

