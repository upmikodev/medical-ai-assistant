"""
report_writer_agent.py
Consolida JSON de resultados y, a continuación, genera el PDF final
dejándolo en la carpeta 'reportes/'.
"""

import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from strands.tools import tool
from reportlab.platypus import Table, TableStyle, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage

# ---------------------------------------------------------------------
# 1 · TOOL: genera el PDF a partir de temp/report.json
# ---------------------------------------------------------------------
@tool()
def generate_pdf_from_report(report_json_path: str,
                             output_folder: str = "reportes") -> str:
    """
    Genera un PDF legible a partir de un report.json y lo guarda en /reportes.
    Devuelve: {"pdf_path": "..."} o {"error": "..."}
    """
    try:
        if not os.path.exists(report_json_path):
            return json.dumps({"error": f"No existe {report_json_path}"})

        with open(report_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        os.makedirs(output_folder, exist_ok=True)
        pdf_name = f"{data.get('paciente_id','paciente')}_{data.get('fecha','')}.pdf"
        pdf_path = os.path.join(output_folder, pdf_name)

        # ---------- PDF ----------
        doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                                leftMargin=20*mm, rightMargin=20*mm,
                                topMargin=15*mm, bottomMargin=15*mm)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="Justify", alignment=TA_JUSTIFY, leading=14))


        def scaled_image(path: str, max_w_mm: float, max_h_mm: float) -> RLImage:
            """Devuelve un flowable RLImage escalado para caber en los límites dados."""
            with PILImage.open(path) as im:
                w_px, h_px = im.size
            w_pt, h_pt = w_px * 0.75, h_px * 0.75           # px → pt
            scale = min((max_w_mm*mm)/w_pt, (max_h_mm*mm)/h_pt, 1.0)
            return RLImage(path, width=w_pt*scale, height=h_pt*scale)







        E = []  # elementos

        # Título
        E.append(Paragraph("Informe Clínico Automatizado – Resonancia Craneal", styles["Title"]))
        E.append(Spacer(1, 5*mm))

        # Datos del paciente
        E.append(Paragraph("<b>Datos del paciente</b>", styles["Heading2"]))
        datos = f"""
        Nombre: {data.get('nombre','NO DISPONIBLE')}<br/>
        ID: {data.get('paciente_id','NO DISPONIBLE')}<br/>
        Fecha de la prueba: {data.get('fecha','NO DISPONIBLE')}
        """
        E.append(Paragraph(datos, styles["Normal"]))
        E.append(Spacer(1, 4*mm))

        # Motivo de la consulta
        E.append(Paragraph("<b>Motivo de la consulta</b>", styles["Heading2"]))
        E.append(Paragraph(data.get('motivo_consulta','NO DISPONIBLE'), styles["Justify"]))
        E.append(Spacer(1, 4*mm))

        # Triaje
        E.append(Paragraph("<b>Prioridad estimada (triaje automático)</b>", styles["Heading2"]))
        tri = f"""
        Riesgo: {data.get('riesgo','NO DISPONIBLE')}<br/>
        Justificación: {data.get('justificacion_triaje','NO DISPONIBLE')}
        """
        E.append(Paragraph(tri, styles["Justify"]))
        E.append(Spacer(1, 4*mm))



       # Historial clínico
        E.append(Paragraph("<b>Síntesis del historial clínico</b>", styles["Heading2"]))

        hist = data.get("resumen_historial", "NO DISPONIBLE")
        if hist != "NO DISPONIBLE":
            # convierte "- texto. - texto." en lista con viñetas
            lines = [l.strip(" -.") for l in hist.split("-") if l.strip()]
            hist_paragraph = "<br/>".join([f"{ln}" for ln in lines])
        else:
            hist_paragraph = "NO DISPONIBLE"

        E.append(Paragraph(hist_paragraph, styles["Justify"]))
        E.append(Spacer(1, 4*mm))




        # Diagnóstico preliminar
        E.append(Paragraph("<b>Diagnóstico preliminar (IA)</b>", styles["Heading2"]))
        diag = f"""
        Resultado: {data.get('tumor_resultado','NO DISPONIBLE')}<br/>
        Probabilidad: {data.get('tumor_prob','NO DISPONIBLE')}<br/>
        Observaciones: {data.get('comentarios_clasificador','NO DISPONIBLE')}
        """
        E.append(Paragraph(diag, styles["Justify"]))
        E.append(Spacer(1, 4*mm))

        # Segmentación
        E.append(Paragraph("<b>Segmentación de imagen</b>", styles["Heading2"]))
        seg = f"""
        Zona afectada: {data.get('zona_afectada','NO DISPONIBLE')}<br/>
        Volumen estimado: {data.get('volumen_cc','NO DISPONIBLE')} cc<br/>
        Imagen cerebral: {data.get('input_slice','NO DISPONIBLE')}<br/>
        Segmentacion del tumor: {data.get('mask_file','NO DISPONIBLE')}<br/>
        Máscara superpuesta: {data.get('overlay_file','NO DISPONIBLE')}
        """
        E.append(Paragraph(seg, styles["Justify"]))
        E.append(Spacer(1, 4*mm))

        input_png  = data.get("input_slice")
        mask_png   = data.get("mask_file")
        overlay_png= data.get("overlay_file")

# 3a. Mini-imágenes lado a lado (máx 70 mm × 70 mm cada una)
        mini_imgs = []
        for p in (input_png, mask_png):
            if p and os.path.exists(p):
                mini_imgs.append(scaled_image(p, 70, 70))
            else:
                mini_imgs.append(Spacer(70*mm, 70*mm))   # hueco vacío

        table = Table([mini_imgs], colWidths=[70*mm, 70*mm])
        table.setStyle(TableStyle([
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("BOX", (0,0), (-1,-1), 0.25, colors.lightgrey)
        ]))
        E.append(table)
        E.append(Spacer(1, 3*mm))

        # 3b. Overlay centrada (máx 140 mm × 90 mm)
        if overlay_png and os.path.exists(overlay_png):
            E.append(scaled_image(overlay_png, 180, 120))
            E.append(Spacer(1, 4*mm))

        E.append(Spacer(1, 4*mm))




        # Conclusión
        E.append(Paragraph("<b>Conclusión del sistema</b>", styles["Heading2"]))
        E.append(Paragraph(data.get('comentario_final_sobre_el_caso','NO DISPONIBLE'), styles["Justify"]))
        E.append(Spacer(1, 6*mm))

        # Pie
        E.append(Paragraph("<i>Informe generado automáticamente por el sistema médico asistido por IA.</i>", styles["Normal"]))

        doc.build(E)
        return json.dumps({"pdf_path": pdf_path})

    except Exception as e:
        return json.dumps({"error": str(e)})