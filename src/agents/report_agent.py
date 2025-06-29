from strands import Agent
from strands.tools import tool
import json
import os
from src.config.config import strands_model_mini
from src.config.prompts import report_system_prompt
from src.tools.file_system_tools import write_file_to_local

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

        # Construct the report content as a dictionary
        report_data = {
            "paciente_id": patient_identifier,
            "nombre": patient_name,
            "fecha": "NO DISPONIBLE",
            "edad": "NO DISPONIBLE",
            "motivo_consulta": "NO DISPONIBLE",
            "tumor_prob": None,  # Will be filled if classification data is available
            "tumor_resultado": "NO DISPONIBLE",
            "comentarios_clasificador": "NO DISPONIBLE",
            "zona_afectada": "NO DISPONIBLE",
            "volumen_cc": None,
            "input_slice": "NO DISPONIBLE",
            "mask_file": "NO DISPONIBLE",
            "overlay_file": "NO DISPONIBLE",
            "resumen_historial": rag_summary,
            "riesgo": triage_risk,
            "justificacion_triaje": triage_justification,
            "comentario_final_sobre_el_caso": "NO DISPONIBLE",
            "scans": []
        }

        if classification_data and classification_data.get("classifications"):
            for cls in classification_data["classifications"]:
                scan_id = cls.get("scan_id", "N/A")
                result = cls.get("result", {})
                prediction = result.get("prediction", "N/A")
                probabilities = result.get("probabilities", {})
                tumor_prob = probabilities.get("Tumor", 0)
                
                report_data["tumor_resultado"] = prediction
                report_data["tumor_prob"] = tumor_prob
                report_data["comentarios_clasificador"] = f"Predicción: {prediction}, Probabilidad de Tumor: {tumor_prob:.2f}%"
                
                report_data["scans"].append({
                    "scan_id": scan_id,
                    "flair_path": "NO DISPONIBLE", # This info is not directly in classification_data
                    "t1ce_path": "NO DISPONIBLE", # This info is not directly in classification_data
                    "p_tumor": tumor_prob,
                    "mask_file": "NO DISPONIBLE"
                })

        if segmentation_data and segmentation_data.get("segmentations"):
            for seg in segmentation_data["segmentations"]:
                scan_id = seg.get("scan_id", "N/A")
                result = seg.get("result", {})
                input_slice = result.get("input_slice", "N/A")
                mask_file = result.get("mask_file", "N/A")
                overlay_file = result.get("overlay_file", "N/A")

                report_data["input_slice"] = input_slice
                report_data["mask_file"] = mask_file
                report_data["overlay_file"] = overlay_file
                report_data["zona_afectada"] = "NO DISPONIBLE" # This info is not directly in segmentation_data
                report_data["volumen_cc"] = None # This info is not directly in segmentation_data

                # Update existing scan or add new one
                found = False
                for scan in report_data["scans"]:
                    if scan["scan_id"] == scan_id:
                        scan["mask_file"] = mask_file
                        found = True
                        break
                if not found:
                    report_data["scans"].append({
                        "scan_id": scan_id,
                        "flair_path": "NO DISPONIBLE",
                        "t1ce_path": "NO DISPONIBLE",
                        "p_tumor": None,
                        "mask_file": mask_file
                    })

        # Define report JSON file path
        report_json_filename = f"reporte_{patient_identifier.lower()}.json"
        report_json_path = os.path.join("data", "temp", report_json_filename)

        # Save the report content to a JSON file
        write_file_to_local(path=report_json_path, content=json.dumps(report_data, indent=2))

        # Generate PDF from the JSON report
        from src.tools.report_pdf_agent import generate_pdf_from_report
        pdf_response = generate_pdf_from_report(report_json_path)
        
        # Check for errors during PDF generation
        pdf_data = json.loads(pdf_response)
        if "error" in pdf_data:
            return json.dumps({"error": f"PDF generation failed: {pdf_data['error']}"})

        return json.dumps({"report_path": pdf_data["pdf_path"]})

    except Exception as e:
        return json.dumps({
            "patient_identifier": patient_identifier,
            "classification": classification,
            "segmentation": segmentation,
            "knowledge": knowledge,
            "triage": triage,
            "error": str(e)
        })