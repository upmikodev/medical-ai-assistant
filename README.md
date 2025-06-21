# TFM - Asistente Virtual para Profesionales Médicos

Este repositorio contiene el código de un asistente tipo "Jarvis" pensado para apoyar tareas clínicas. Incluye módulos de clasificación y segmentación de resonancias magnéticas cerebrales, un sistema de recuperación aumentada de información (RAG) y agentes para generar y validar informes.

## Estructura del repositorio

```
.
├── backend/            # API FastAPI que actúa de intermediario
├── frontend/           # Interfaz web en React
├── execute_brain_tumor_classifier.py   # Clasificación de tumores
├── execute_brain_tumor_segmentation.py # Segmentación de tumores
├── models/             # Modelos de IA preentrenados
├── segmentations/      # Resultados de segmentación
├── pictures/           # Imágenes de ejemplo o subidas por el usuario
├── documents/          # Ejemplos de reportes clínicos
├── reportes/           # Informes generados
├── chroma_db/          # Base de datos para RAG
├── config.py           # Configuración del proyecto
├── requirements.txt    # Dependencias principales
└── README.md
```

## Instalación rápida

1. Crea y activa un entorno virtual de Python:
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # En Windows: .venv\Scripts\activate
   ```
2. Instala las dependencias principales:
   ```bash
   pip install -r requirements.txt
   ```
3. Algunos módulos (backend y frontend) tienen sus propios requisitos.

### Backend

```
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### Frontend

```
cd frontend
npm install
npm run dev
```

## Uso básico

Ejemplo de clasificación de tumor cerebral:
```bash
python execute_brain_tumor_classifier.py --input ruta/a/imagen.nii
```

Ejemplo de segmentación:
```bash
python execute_brain_tumor_segmentation.py --input ruta/a/imagen.nii
```

Los resultados y reportes se guardarán en las carpetas `segmentations/` y `reportes/` respectivamente.

## Estado del proyecto

El asistente se encuentra en desarrollo activo. Los siguientes puntos están planificados o en progreso:

- Integración completa del voicebot.
- Finalización del sistema RAG.
- Mejora de los agentes de redacción y validación de informes.
- Interfaz de usuario más completa.

## Contribuciones

Las contribuciones son bienvenidas a través de *pull requests*. Por favor, sigue las buenas prácticas de estilo y proporciona descripciones claras.

## Licencia

Este proyecto se distribuye bajo los términos de la licencia MIT.
