

from langchain_chroma import Chroma 

from langchain_openai import OpenAIEmbeddings
import unicodedata
import json
from strands.tools import tool

@tool()
def rag_tool(paciente: str, query: str) -> str:
    """
    Realiza una búsqueda semántica en el vector store asociado al paciente
    usando embeddings. Recupera los documentos más relevantes para el contexto clínico.

    Args:
        paciente (str): Nombre del paciente, usado como nombre de la colección ChromaDB.
        query (str): Pregunta o tema sobre el que se desea recuperar contexto.

    Returns:
        str: Texto concatenado con los contenidos más relevantes encontrados o mensaje de error.
    """
    try:
        # Normalizar nombre del paciente para evitar errores con la colección
        
        print(f"Ejecutando RAG Tool para el paciente: {paciente} con query: {query}")

        collection_name = "patients"
        PERSIST_DIRECTORY = "./data/chroma_db"

        # Crear vector store apuntando a la colección del paciente
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        vector_store = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            collection_name=collection_name,
            embedding_function=embeddings
        )

        # Ejecutar búsqueda semántica
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        results = retriever.invoke(query)


        print(f"Resultados encontrados: {len(results)} documentos relevantes.")
        print(results)

        # Concatenar textos encontrados
        contenido = "\n\n".join([doc.page_content for doc in results])
        print(f"Contenido recuperado: {contenido[:500]}...")  # Mostrar solo los primeros 500 caracteres
        return contenido

    except Exception as e:
        return json.dumps({
            "error": f"Error en RAG Tool para '{paciente}': {str(e)}"
        })
