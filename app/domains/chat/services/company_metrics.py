from datetime import date
from typing import Optional

FITOHERB_FOUNDING_DATE = date(1997, 11, 1)


def parse_founding_date(raw_date: Optional[str]) -> date:
    """
    Faz o parse seguro de uma data ISO (YYYY-MM-DD) de fundação.
    Em caso de valor ausente ou inválido, retorna FITOHERB_FOUNDING_DATE (01/11/1997).
    """
    if not raw_date or not isinstance(raw_date, str):
        return FITOHERB_FOUNDING_DATE

    try:
        return date.fromisoformat(raw_date.strip())
    except ValueError:
        return FITOHERB_FOUNDING_DATE


def get_fitoherb_years(
    reference_date: Optional[date] = None,
    founding_date: date = FITOHERB_FOUNDING_DATE,
) -> int:
    """
    Calcula o número exato de anos completos de atuação da Fitoherb
    a partir da data de fundação (01/11/1997) até a data de referência.
    """
    ref = reference_date or date.today()
    years = ref.year - founding_date.year
    if (ref.month, ref.day) < (founding_date.month, founding_date.day):
        years -= 1
    return max(0, years)


def get_fitoherb_years_label(
    reference_date: Optional[date] = None,
    founding_date: date = FITOHERB_FOUNDING_DATE,
) -> str:
    """
    Retorna o rótulo textual atualizado dos anos de mercado da Fitoherb
    (ex.: '29 anos de mercado').
    """
    years = get_fitoherb_years(reference_date=reference_date, founding_date=founding_date)
    return f"{years} anos de mercado"
