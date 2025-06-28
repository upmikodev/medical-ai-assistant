from strands import Agent
from strands.tools import tool
import json
import os
from src.config.config import strands_model_mini
from src.config.prompts import report_system_prompt
from src.tools.strands_tools import write_file_to_local

@tool()
def report_agent(
    patient_identifier: str,
    classification: str,
    segmentation: str,
    knowledge: str,
    triage: str
) -> str:
    """
    Genera un reporte médico para un paciente en base al nombre del paciente,
    información recuperada a través de RAG de la base de conocimiento,
    la clasificación y segmentación de las imágenes MRI y el triaje automático.

    Args:
        - patient_identifier (str): El nombre del paciente en formato Nombre_Apellido1_Apellido2 o Nombre_Apellido1.
        - classification (str): Resultado de la clasificación de las imágenes MRI (JSON string).
        - segmentation (str): Resultado de la segmentación de las imágenes MRI (JSON string).
        - knowledge (str): Información recuperada a través de RAG de la base de conocimiento (JSON string).
        - triage (str): Resultado del triaje automático (JSON string).
    
    Tools:
        - write_file_to_local(path: str, content: str): Guarda el reporte en un archivo local.
    
    Returns:
        - report_path (str): Ruta del archivo final que recibirá el usuario.
    """
    try:
        # Parse JSON strings
        classification_data = json.loads(classification)
        segmentation_data = json.loads(segmentation)
        knowledge_data = json.loads(knowledge) if knowledge else {}
        triage_data = json.loads(triage) if triage else {}

        # Extract relevant data for the report
        patient_name = patient_identifier.replace("_", " ").title()
        
        # Classification data
        classification_results_str = "No disponible"
        if classification_data and classification_data.get("classifications"):
            class_info = []
            for cls in classification_data["classifications"]:
                scan_id = cls.get("scan_id", "N/A")
                result = cls.get("result", {})
                prediction = result.get("prediction", "N/A")
                probabilities = result.get("probabilities", {})
                tumor_prob = probabilities.get("Tumor", 0) * 100
                class_info.append(f"  - Scan ID: {scan_id}\n    - Predicción: {prediction}\n    - Probabilidad de Tumor: {tumor_prob:.2f}%")
            classification_results_str = "\n".join(class_info)

        # Segmentation data
        segmentation_results_str = "No disponible"
        if segmentation_data and segmentation_data.get("segmentations"):
            seg_info = []
            for seg in segmentation_data["segmentations"]:
                scan_id = seg.get("scan_id", "N/A")
                output_file = seg.get("result", {}).get("saved_mask", "N/A")
                seg_info.append(f"  - Scan ID: {scan_id}\n    - Archivo de Máscara: {output_file}")
            segmentation_results_str = "\n".join(seg_info)

        # RAG knowledge
        rag_summary = knowledge_data.get("content", "No se encontró información relevante en el historial clínico.")

        # Triage data
        triage_risk = triage_data.get("riesgo", "NO DETERMINADO")
        triage_justification = triage_data.get("justificación_triaje", "No se pudo determinar la justificación.")

        # Construct the report content
        report_content = f"""## Informe Clínico Automatizado – Resonancia Craneal

**Datos del paciente**  
- Nombre: {patient_name}  
- ID: {{NO DISPONIBLE}}  
- Fecha de la prueba: {{NO DISPONIBLE}}  

**Motivo de la consulta**  
{{NO DISPONIBLE}}

**Diagnóstico preliminar (IA)**  
{classification_results_str}  
- Fuente: `Agent::Classifier`  
- Observaciones: {{NO DISPONIBLE}}

**Segmentación de imagen**  
{segmentation_results_str}  

**Síntesis del historial clínico**  
{rag_summary}  
_(fuente: Agent::RAG)_

**Prioridad estimada (triaje automático)**  
- Riesgo: {triage_risk}  
- Justificación: {triage_justification}

**Conclusión del sistema**  
{{NO DISPONIBLE}}

---

_Informe generado automáticamente por el sistema médico asistido por IA. Validación pendiente._
"""
        # Define report file path
        report_filename = f"reporte_{patient_identifier.lower()}.md"
        report_path = os.path.join("data", "reportes", report_filename)

        # Save the report
        write_file_to_local(path=report_path, content=report_content)

        return json.dumps({"report_path": report_path})

    except Exception as e:
        return json.dumps({
            "patient_identifier": patient_identifier,
            "classification": classification,
            "segmentation": segmentation,
            "knowledge": knowledge,
            "triage": triage,
            "error": str(e)
        })