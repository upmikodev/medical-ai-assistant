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
        Máscara: {data.get('nombre_archivo_segmentado','NO DISPONIBLE')}
        """
        E.append(Paragraph(seg, styles["Justify"]))
        E.append(Spacer(1, 4*mm))

        # Historial clínico
        E.append(Paragraph("<b>Síntesis del historial clínico</b>", styles["Heading2"]))
        E.append(Paragraph(data.get('resumen_historial','NO DISPONIBLE'), styles["Justify"]))
        E.append(Spacer(1, 4*mm))

        # Triaje
        E.append(Paragraph("<b>Prioridad estimada (triaje automático)</b>", styles["Heading2"]))
        tri = f"""
        Riesgo: {data.get('riesgo','NO DISPONIBLE')}<br/>
        Justificación: {data.get('justificacion_triaje','NO DISPONIBLE')}
        """
        E.append(Paragraph(tri, styles["Justify"]))
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