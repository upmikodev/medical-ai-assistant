from asyncio.log import logger
import os
import json
from strands.tools import tool

from src.config.config import strands_model_nano 
from src.tools.execute_brain_tumor_classifier import classify_tumor_from_image

@tool
def find_patient_images_tool(patient_identifier: str, image_directory: str = "pictures") -> str:
    """Finds image files for a given patient identifier in a specified directory.
    Uses an LLM to intelligently match filenames against the patient identifier.
    Args:
        patient_identifier (str): The identifier of the patient (e.g., nombre_apellido1_apellido2).
        image_directory (str): The directory to search for images (defaults to 'pictures').
    Returns:
        str: A JSON string representing a list of full image paths, or an error message.
    """
    logger.info(f"Tool: Finding images for patient '{patient_identifier}' in '{image_directory}'")
    if not strands_model_nano:
        logger.error("Tool: find_patient_images_tool - strands_model_nano is not initialized.")
        return json.dumps({"error": "LLM for image finding not available."})

    try:
        if not os.path.exists(image_directory) or not os.path.isdir(image_directory):
            logger.warning(f"Tool: Image directory '{image_directory}' not found or is not a directory.")
            return json.dumps({"error": f"Image directory '{image_directory}' not found."})

        files_in_dir = [
            f for f in os.listdir(image_directory)
            if os.path.isfile(os.path.join(image_directory, f))
        ]

        if not files_in_dir:
            logger.info(f"Tool: No files found in directory '{image_directory}'.")
            return json.dumps([]) # Return empty list if no files

        # Prompt for the LLM to select relevant files
        # Note: This prompt might need refinement for optimal performance.
        prompt = (
            f"Given the patient identifier '{patient_identifier}' and the following list of filenames: "
            f"{json.dumps(files_in_dir)}. "
            f"Please identify which of these filenames are medical images belonging to this specific patient. "
            f"Typically, filenames follow a pattern like '{patient_identifier}_NUMBER.extension' (e.g., {patient_identifier}_1.png, {patient_identifier}_2.jpg) or exactly '{patient_identifier}.extension'. "
            f"Prioritize images with lower numbers if multiple numbered images exist (e.g., prefer '_1' over '_2'). "
            f"Return your answer as a JSON formatted list of strings, where each string is only the filename. For example: [\"image1.png\", \"image2.jpg\"]. "
            f"If no files match, return an empty JSON list []."
        )

        logger.info(f"Tool: Sending prompt to LLM for image selection (first 100 chars): {prompt[:100]}...")
        llm_response_str = strands_model_nano.invoke(prompt)
        
        logger.info(f"Tool: LLM response for image selection: {llm_response_str}")

        try:
            selected_filenames = json.loads(llm_response_str)
            if not isinstance(selected_filenames, list):
                logger.warning(f"Tool: LLM did not return a valid list for image selection. Response: {llm_response_str}")
                return json.dumps({"error": "LLM did not return a valid list for image selection.", "details": llm_response_str})
        except json.JSONDecodeError:
            logger.warning(f"Tool: LLM response was not valid JSON for image selection. Response: {llm_response_str}")
            # Try to extract filenames if LLM failed to produce perfect JSON but listed them (simple extraction)
            # This is a fallback and might not be robust.
            extracted_by_fallback = [fn for fn in files_in_dir if fn in llm_response_str and patient_identifier in fn]
            if extracted_by_fallback:
                logger.info(f"Tool: Fallback extraction found: {extracted_by_fallback}")
                selected_filenames = extracted_by_fallback
            else:
                return json.dumps({"error": "LLM response was not valid JSON and fallback failed.", "details": llm_response_str})

        # Construct full paths for selected files
        image_paths = [os.path.join(image_directory, fn) for fn in selected_filenames if isinstance(fn, str) and os.path.exists(os.path.join(image_directory, fn))]
        
        logger.info(f"Tool: Found {len(image_paths)} image(s) for patient '{patient_identifier}': {image_paths}")
        return json.dumps(image_paths)

    except Exception as e:
        logger.error(f"Tool: Error in find_patient_images_tool for '{patient_identifier}': {e}", exc_info=True)
        return json.dumps({"error": f"Error finding images for '{patient_identifier}': {str(e)}"})


    except Exception as e:
        logger.error(f"Tool: Error in find_patient_images_tool for '{patient_identifier}': {e}", exc_info=True)
        return json.dumps({"error": f"Error finding images for '{patient_identifier}': {str(e)}"})

@tool(
    name="classify_single_image_tool",
    description="Classifies a single image file for brain tumor detection using the classifier model."
)
def classify_single_image_tool(image_path: str) -> str:
    """Invokes the brain tumor classification logic for a single image file.
    Args:
        image_path (str): The full path to the image file.
    Returns:
        str: A JSON string with the classification result (which might include 'prediction' and 'probabilities') or an error.
    """
    logger.info(f"Tool: Classifying single image at: {image_path}")
    try:
        # classify_tumor_from_image_or_patient_id can handle direct image paths
        result = classify_tumor_from_image(image_path)
        logger.info(f"Tool: Classification result for '{image_path}': {result}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Tool: Error during classification for '{image_path}': {e}", exc_info=True)
        return json.dumps({"error": f"Classification error for '{image_path}': {str(e)}"})