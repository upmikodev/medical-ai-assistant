from asyncio.log import logger
import os
import json
from strands.tools import tool

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
