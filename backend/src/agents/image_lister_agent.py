from strands import Agent
from strands.tools import tool
import json
import logging
from src.config.config import strands_model_4_1
from src.config.prompts import image_lister_system_prompt
from src.tools.file_system_tools import list_files_in_dir, write_file_to_local

# inicializar logger
logger = logging.getLogger(__name__)

@tool()
def image_lister_agent(patient_identifier: str) -> str:
    """
    Este agente actúa como un agente para listar las imágenes de un paciente.
    Toma un identificador de paciente y devuelve una cadena JSON con las rutas de las imágenes encontradas.
    
    Args:
        patient_identifier (str): Identificador de paciente en formato "Nombre_Apellido1_Apellido2"
    
    Tools: 
        - list_files_in_dir(path="data/pictures/"): Lista los archivos en el directorio especificado.
        - write_file_to_local(path="data/temp/lister.json", content=json_string): Escribe la cadena JSON en un archivo local.
        
    Returns:
        str: Cadena JSON que contiene el identificador de paciente y la lista de rutas de las imágenes o un error
    """
    try:
        lister_agent = Agent(
            model=strands_model_4_1,
            tools=[
                list_files_in_dir,
                write_file_to_local,
            ],
            system_prompt=image_lister_system_prompt
        )
        result = lister_agent(patient_identifier)

        # resumen humano al progreso.txt
        logger.info(f"🖼️ Resumen (ImageLister): imágenes listadas para {patient_identifier}. Resultado crudo: {result}")

        return result

    except Exception as e:
        logger.error(f"❌ Resumen (ImageLister): fallo listando imágenes para {patient_identifier} - {str(e)}")
        return json.dumps({
            "patient_identifier": patient_identifier,
            "pictures": [],
            "error": str(e)
        })
