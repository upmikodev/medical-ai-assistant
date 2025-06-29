import re
from strands import Agent
from strands.tools import tool
import uuid
import json
import re
from src.config.config import strands_model_mini
from src.config.prompts import orchestrator_system_prompt
from src.agents.planner_agent import planner_agent
from src.agents.image_lister_agent import image_lister_agent
from src.agents.classification_agent import clasificacion_agent
from src.agents.segmentator_agent import segmentator_agent
from src.agents.rag_agent import rag_agent
from src.agents.triage_agent import triage_agent
from src.agents.report_agent import report_agent
from src.agents.report_validator_agent import report_validator_agent
from src.tools.file_system_tools import read_file_from_local

@tool()
def orchestrator_agent(query: str) -> str:
    """
    Orchestrates the execution of various agents based on the user's query.
    """
    try:
        # Step 1: Plan the execution
        print("Tool #1: planner_agent")
        plan_response = planner_agent(query)
        # New regex to specifically target 'patient_name: "..."'
        match = re.search(r'(?:patient_name|paciente)[\s:=]*"([^"]+)"', plan_response)
        if match:
            patient_name = match.group(1).strip()
            patient_identifier_match = patient_name.replace(" ", "_")
        else:
            return json.dumps({"error": "Could not extract patient identifier from planner response."})

        # Step 2: Image Listing
        print("Tool #2: image_lister_agent")
        image_lister_response = image_lister_agent(patient_identifier_match)
        print(image_lister_response)

        # Read the output of image_lister_agent from temp/lister.json
        print("Reading temp/lister.json...")
        lister_output_json = read_file_from_local(path="data/temp/lister.json")
        lister_data = json.loads(json.loads(lister_output_json)["content"])
        print(f"Lister data: {lister_data}")
        
        if "error" in lister_data:
            return json.dumps({"error": f"Image lister failed: {lister_data['error']}"})

        patient_data_for_classification = json.dumps(lister_data)

        # Step 3: Classification
        print("Tool #3: clasificacion_agent")
        classification_response = clasificacion_agent(patient_data_for_classification)
        print(classification_response)

        classification_data = json.loads(classification_response)
        if "error" in classification_data:
            return json.dumps({"error": f"Classification failed: {classification_data['error']}"})

        # Step 4: Segmentation (conditional)
        segmentation_results = []
        should_segment = False
        for classification in classification_data.get("classifications", []):
            if classification.get("result", {}).get("prediction") == "Tumor" and \
               classification.get("result", {}).get("probabilities", {}).get("Tumor", 0) > 0.6:
                should_segment = True
                break
        
        if should_segment:
            print("Tool #4: segmentator_agent")
            segmentation_response = segmentator_agent(patient_data_for_classification)
            print(segmentation_response)
            segmentation_results = json.loads(segmentation_response)
            if "error" in segmentation_results:
                return json.dumps({"error": f"Segmentation failed: {segmentation_results['error']}"})

        # Step 5: RAG (Retrieve clinical history)
        print("Tool #5: rag_agent")
        rag_response = rag_agent(json.dumps({"patient_identifier": patient_identifier_match, "query": "historial clínico del paciente"}))
        print(rag_response)
        rag_data = json.loads(rag_response)
        if "error" in rag_data:
            return json.dumps({"error": f"RAG failed: {rag_data['error']}"})
        
        # Step 6: Triage (Evaluate urgency)
        print("Tool #6: triage_agent")
        triage_input_data = {}
        if classification_data and classification_data.get("classifications"):
            for cls in classification_data["classifications"]:
                prediction = cls.get("result", {}).get("prediction")
                if prediction:
                    triage_input_data["diagnostico_preliminar"] = prediction
                    break
        
        if segmentation_results and segmentation_results.get("segmentations"):
            for seg in segmentation_results["segmentations"]:
                mask_file = seg.get("result", {}).get("mask_file")
                if mask_file:
                    triage_input_data["zona_afectada"] = "cerebro" # Placeholder, as specific zone is not extracted
                    triage_input_data["volumen_lesion"] = "NO DETERMINADO" # Placeholder, as volume is not extracted
                    break

        if rag_data and rag_data.get("context"):
            triage_input_data["historial_clinico"] = rag_data["context"]

        triage_response = triage_agent(json.dumps(triage_input_data))
        print(triage_response)
        triage_data = json.loads(triage_response)
        if "error" in triage_data:
            return json.dumps({"error": f"Triage failed: {triage_data['error']}"})

        # Step 7: Report Generation
        print("Tool #7: report_agent")
        report_response = report_agent(
            patient_identifier=patient_identifier_match,
            classification=json.dumps(classification_data),
            segmentation=json.dumps(segmentation_results),
            knowledge=json.dumps(rag_data),
            triage=json.dumps(triage_data)
        )
        print(report_response)

        # Step 8: Report Validation
        print("Tool #8: report_validator_agent")
        report_path = json.loads(report_response).get("report_path")
        if report_path:
            validation_response = report_validator_agent(report_path=report_path, classification_data=json.dumps(classification_data), segmentation_results=json.dumps(segmentation_results))
            print(validation_response)
            return validation_response
        else:
            return json.dumps({"error": "Report path not returned by report_agent."})

    except Exception as e:
        return json.dumps({"error": str(e)})