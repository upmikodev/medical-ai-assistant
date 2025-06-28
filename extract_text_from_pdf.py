from pdfminer.high_level import extract_text
from strands.tools import tool
import json, os

@tool()
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Devuelve el texto (en UTF-8) extraído del PDF.
    Usa pdfminer.six internamente.
    Return:
        {"content": "<texto>"}  o  {"error": "..."}
    """
    try:
        if not os.path.exists(pdf_path):
            return json.dumps({"error": f"No existe {pdf_path}"})

        txt = extract_text(pdf_path)
        return json.dumps({"content": txt})
    except Exception as e:
        return json.dumps({"error": str(e)})
