from strands import Agent
from strands.tools import tool
import json
from src.config.config import strands_model_mini
from src.config.prompts import clasificacion_system_prompt
from src.tools.execute_brain_tumor_classifier import classify_tumor_from_image
from src.tools.strands_tools import read_file_from_local, write_file_to_local

@tool()
def clasificacion_agent(patient_data: str) -> str:
    """
    El LLM recibe los datos del paciente y sus escaneos, recorre la lista `scans`
    y llama a `classify_tumor_from_image` para cada par FLAIR+T1CE.
    
    Args:
        patient_data (str): JSON string con los datos del paciente y sus escaneos (normalmente de `temp/lister.json`).

    Tools:
        - classify_tumor_from_image
        - write_file_to_local

    """
    try:
        data = json.loads(patient_data)
        patient_identifier = data.get("patient_identifier", "unknown")
        scans = data.get("scans", [])

        if not scans:
            return json.dumps({"patient_identifier": patient_identifier, "error": "No se encontraron imágenes para clasificar."})

        classifications = []
        for scan in scans:
            flair_path = scan.get("flair_path")
            t1ce_path = scan.get("t1ce_path")
            scan_id = scan.get("scan_id", "unknown_scan")

            if flair_path and t1ce_path:
                result = classify_tumor_from_image(flair_path=flair_path, t1ce_path=t1ce_path)
                classifications.append({"scan_id": scan_id, "result": json.loads(result)})
            else:
                classifications.append({"scan_id": scan_id, "result": {"error": "Rutas de imagen incompletas."}})

        final_result = {"patient_identifier": patient_identifier, "classifications": classifications}
        
        # Save results to temp/classification.json
        write_file_to_local(path="data/temp/classification.json", content=json.dumps(final_result))

        return json.dumps(final_result)
    except Exception as e:
        return json.dumps({"error": str(e)})