from strands import Agent
from strands.tools import tool
import uuid
import json
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
from src.tools.strands_tools import read_file_from_local

@tool()
def orchestrator_agent(query: str) -> str:
    """
    Orchestrates the execution of various agents based on the user's query.
    """
    try:
        # Step 1: Plan the execution
        print("Tool #1: planner_agent")
        plan_response = planner_agent(query)
        print(str(plan_response))

        # Assuming the plan_response contains the patient identifier
        # This part needs to be more robust if planner_agent output format changes
        patient_identifier_match = None
        if "Carlos Pérez Paco" in plan_response:
            patient_identifier_match = "Carlos_Perez_Paco"
        
        if not patient_identifier_match:
            return json.dumps({"error": "Could not extract patient identifier from planner response."})

        # Step 2: Image Listing
        print("Tool #2: image_lister_agent")
        image_lister_response = image_lister_agent(patient_identifier_match)
        print(image_lister_response)

        # Read the output of image_lister_agent from temp/lister.json
        print("Reading temp/lister.json...")
        lister_output_json = read_file_from_local(path="temp/lister.json")
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

        # Step 5: Report Generation
        print("Tool #5: report_agent")
        # For now, pass relevant data directly. This might need to be refined based on report_agent's needs.
        report_response = report_agent(
            patient_identifier=patient_identifier_match,
            classification=json.dumps(classification_data),
            segmentation=json.dumps(segmentation_results),
            knowledge="", # RAG agent not implemented yet
            triage="" # Triage agent not implemented yet
        )
        print(report_response)

        # Step 6: Report Validation
        print("Tool #6: report_validator_agent")
        # Assuming report_agent returns the path to the generated report
        report_path = json.loads(report_response).get("report_path")
        if report_path:
            validation_response = report_validator_agent(report_path=report_path, classification_data=json.dumps(classification_data), segmentation_results=json.dumps(segmentation_results))
            print(validation_response)
            return validation_response
        else:
            return json.dumps({"error": "Report path not returned by report_agent."})

    except Exception as e:
        return json.dumps({"error": str(e)})