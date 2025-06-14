import os
import json
import logging
import re
from PIL import Image

import torch
import torch.nn as nn
from torchvision import models, transforms

from strands_tools import tool

# ——— Configuración básica ———
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEVICE        = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CLASS_NAMES   = ["No tumor", "Tumor"]
MODEL_PATH    = "models/brain_tumor_classifier.pkl"
TRANSFORM_PREDICT = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5]),
])

# ——— Función de carga del modelo ———
def load_model(model_path: str):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")

    # Para evitar el error "weights only load failed":
    checkpoint = torch.load(
        model_path,
        map_location=DEVICE,
        weights_only=False  # Asegúrate de que esto sea False si guardaste el modelo completo
    )

    # Si el checkpoint es el modelo completo, devuélvelo directamente
    if not isinstance(checkpoint, dict):
        model = checkpoint
        model.to(DEVICE)
        model.eval()
        logger.info(f"Model loaded successfully (as full model object) from {model_path}")
        return model

    # Si es un diccionario, intenta cargar el state_dict
    # Creamos la arquitectura base primero
    model = models.densenet121(weights=None) # O la arquitectura que corresponda
    model.classifier = nn.Linear(model.classifier.in_features, len(CLASS_NAMES))


    if "model_state" in checkpoint:
        model.load_state_dict(checkpoint["model_state"])
    elif "state_dict" in checkpoint:
        model.load_state_dict(checkpoint["state_dict"])
    else:
        # Si es un diccionario pero no tiene las claves esperadas, puede ser un state_dict directamente
        try:
            model.load_state_dict(checkpoint)
        except RuntimeError as e:
            logger.error(f"Failed to load state_dict directly from checkpoint dictionary: {e}")
            raise ValueError(f"Checkpoint dictionary at {model_path} does not contain expected keys ('model_state' or 'state_dict') and is not a direct state_dict.")

    model.to(DEVICE)
    model.eval()
    logger.info(f"Model state_dict loaded successfully from {model_path}")
    return model

# ——— Herramienta de clasificación ———
@tool(
    name="classify_tumor_from_image",
    description="Clasifica una imagen de un cerebro como 'Tumor' o 'No tumor'.",
)
def classify_tumor_from_image(image_path: str) -> str:
    """
    Clasifica una única imagen. NO BUSCA ficheros: espera recibir
    la ruta exacta al archivo de imagen.
    """
    logger.info(f"Request to classify: {image_path}")
    if not os.path.isfile(image_path):
        err = f"Image file not found: {image_path}"
        logger.error(err)
        return json.dumps({"error": err})

    try:
        model = load_model(MODEL_PATH)
        img = Image.open(image_path).convert("RGB")
        tensor = TRANSFORM_PREDICT(img).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            logits = model(tensor)
            probs  = torch.softmax(logits, dim=1)[0]
            idx    = probs.argmax().item()

        result = {
            "prediction": CLASS_NAMES[idx],
            "probabilities": {
                CLASS_NAMES[i]: probs[i].item()
                for i in range(len(CLASS_NAMES))
            }
        }
        logger.info(f"Result for {image_path}: {result}")
        return json.dumps(result)

    except Exception as e:
        logger.error(f"Classification error: {e}", exc_info=True)
        return json.dumps({"error": str(e)})
