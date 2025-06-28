from asyncio.log import logger
import os
import json
from strands.tools import tool

from src.config.config import strands_model_nano 
from src.tools.execute_brain_tumor_classifier import classify_tumor_from_image


@tool
def find_patient_images_tool(patient_identifier: str, image_directory: str = "data/pictures") -> str:
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

@tool(
    name="list_files_in_dir",
    description="Lists files in a local directory"
)
def list_files_in_dir(directory: str) -> str:
    """
    Lists files in a local directory, optionally filtering by prefix.
    Args:
        directory (str): The directory to list files from.
    Returns:
        str: A JSON string representing a list of file names or an error message.
    """
    logger.info(f"Tool: Listing files in '{directory}'")
    try:
        all_files = [
            f.lower() for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]
        logger.info(f"Tool: Found {len(all_files)} file(s) in '{directory}'")
        return json.dumps(all_files)
    except FileNotFoundError:
        logger.warning(f"Tool: Directory '{directory}' not found")
        return json.dumps({"error": f"Directory '{directory}' not found"})
    except Exception as e:
        logger.error(f"Tool: Error listing files in '{directory}': {e}")
        return json.dumps({"error": f"Error listing files in '{directory}': {str(e)}"})

@tool(
    name="read_file_from_local",
    description="Reads the content of a local text file"
)
def read_file_from_local(path: str, encoding: str = 'utf-8') -> str:
    """
    Reads the content of a local text file.
    Args:
        path (str): The path to the file to read.
        encoding (str): The encoding of the file (defaults to 'utf-8').
    Returns:
        str: A JSON string with the file content or an error message.
    """
    logger.info(f"Tool: Reading local file '{path}'")
    try:
        with open(path, 'r', encoding=encoding) as f:
            content = f.read()
        return json.dumps({"content": content})
    except Exception as e:
        logger.error(f"Tool: Error reading file '{path}': {e}")
        return json.dumps({"error": f"Error reading file '{path}': {str(e)}"})

@tool(
    name="write_file_to_local",
    description="Writes text content to a local file"
)
def write_file_to_local(path: str, content: str) -> str:
    """
    Writes text content to a local file.
    Creates the directory path if it doesn't exist.
    Returns a JSON string indicating success or an error message.
    """
    logger.info(f"Tool: Writing local file '{path}'")
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Tool: Successfully wrote to '{path}'")
        return json.dumps({"success": f"Successfully wrote to '{path}'"})
    except Exception as e:
        logger.error(f"Tool: Error writing file '{path}': {e}")
        return json.dumps({"error": f"Error writing file '{path}': {str(e)}"})

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
        result = classify_tumor_from_image_or_patient_id(image_path)
        logger.info(f"Tool: Classification result for '{image_path}': {result}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Tool: Error during classification for '{image_path}': {e}", exc_info=True)
        return json.dumps({"error": f"Classification error for '{image_path}': {str(e)}"})

if __name__ == '__main__':
    # Example usage of tools
    # Create dummy files/dirs for testing
    if not os.path.exists("./test_dir"):
        os.makedirs("./test_dir")
    with open("./test_dir/sample.txt", "w") as f:
        f.write("Hello Strands!")
    with open("./test_dir/another_sample.txt", "w") as f:
        f.write("Another one!")
    
    print("Testing list_files_in_dir...")
    files_json = list_files_in_dir("./test_dir", prefix="sample")
    print(json.loads(files_json))

    print("\nTesting read_file_from_local...")
    content_json = read_file_from_local("./test_dir/sample.txt")
    print(json.loads(content_json))

    print("\nTesting write_file_to_local...")
    write_status_json = write_file_to_local("./test_dir/output.txt", "This is output.")
    print(json.loads(write_status_json))
    if os.path.exists("./test_dir/output.txt"):
        with open("./test_dir/output.txt", "r") as f:
            print(f"Content of output.txt: {f.read()}")
    
    print("\nTesting find_patient_images_tool...")
    # Ensure strands_model_nano is usable for this test, might need to init config here if run standalone
    if strands_model_nano:
        # Create dummy patient images for testing
        if not os.path.exists("pictures"):
            os.makedirs("pictures")
        dummy_patient_id = "test_patient_alpha"
        with open(f"pictures/{dummy_patient_id}_1.png", "w") as f: f.write("dummy_png_content_1")
        with open(f"pictures/{dummy_patient_id}_2.jpg", "w") as f: f.write("dummy_jpg_content_2")
        with open(f"pictures/other_file.txt", "w") as f: f.write("not_an_image")
        with open(f"pictures/{dummy_patient_id}_config.json", "w") as f: f.write("{}")

        found_images_json = find_patient_images_tool(patient_identifier=dummy_patient_id)
        print(f"Found images for '{dummy_patient_id}': {json.loads(found_images_json)}")
    else:
        print("Skipping find_patient_images_tool test as strands_model_nano is not available.")

    # Test classify_single_image_tool (this will likely use dummy/error if model/image not fully set up)
    print("\nTesting classify_single_image_tool...")
    # Assume a dummy image path for testing if the above didn't create it
    dummy_image_for_classification = f"pictures/{dummy_patient_id}_1.png"
    if not os.path.exists(dummy_image_for_classification) and strands_model_nano: # only create if prev test ran
         with open(dummy_image_for_classification, "w") as f: f.write("dummy_png_content_for_classify_tool")
    
    if os.path.exists(dummy_image_for_classification):
        classification_result_json = classify_single_image_tool(dummy_image_for_classification)
        print(f"Classification for '{dummy_image_for_classification}': {json.loads(classification_result_json)}")
    else:
        print(f"Skipping classify_single_image_tool test, dummy image '{dummy_image_for_classification}' not found.")