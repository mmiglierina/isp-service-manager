# filters.py
from datetime import datetime

def format_iso_date(date_string: str) -> str:
    """
    Transforma cadenas de fecha en formato ISO 8601 a un formato legible en español.
    Ejemplo: '2026-05-28T15:13:58.016842' -> '28/05/2026 - 15:13 hs'
    """
    if not date_string:
        return "N/A"
    try:
        # Limpieza de la cadena removiendo microsegundos y la "T" divisoria
        clean_date = date_string.split('.')[0].replace('T', ' ')
        # Parseo e instanciación de la fecha
        dt = datetime.strptime(clean_date, "%Y-%m-%d %H:%M:%S")
        # Retorno con el string formateado final
        return dt.strftime("%d/%m/%Y - %H:%M hs")
    except Exception as error:
        print(f"[LOG ERROR] Error al formatear la fecha '{date_string}': {error}")
        return date_string