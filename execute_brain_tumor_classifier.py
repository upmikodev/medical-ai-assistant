import os
import json
import logging
import re
from PIL import Image
import cv2, numpy as np
import nibabel as nib
import torch
import torch.nn as nn
from torchvision import models, transforms

from strands_tools import tool

# ——— Configuración básica ———
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEVICE        = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CLASS_NAMES   = ["No tumor", "Tumor"]
MODEL_PATH    = "models/brain_tumor_classifier_v3.pkl"


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

def preprocess_slice(flair_slice, t1ce_slice=None):
    """
    Recibe dos arrays 2-D (192×192, 240×240, …) y devuelve
    un tensor (2,128,128) en rango 0-1 listo para el modelo.

    · Si t1ce_slice es None, duplica flair → 2 canales.
    """
    # --- resize a 128×128 ---
    flair128 = cv2.resize(flair_slice, (128, 128),
                          interpolation=cv2.INTER_LINEAR).astype(np.float32)
    flair128 /= flair128.max() if flair128.max() > 0 else 1.  # 0-1

    if t1ce_slice is None:
        t1ce128 = flair128.copy()            # duplicar canal
    else:
        t1ce128 = cv2.resize(t1ce_slice, (128, 128),
                             interpolation=cv2.INTER_LINEAR).astype(np.float32)
        t1ce128 /= t1ce128.max() if t1ce128.max() > 0 else 1.

    x = np.stack([flair128, t1ce128], axis=0)    # (2,128,128)
    return torch.from_numpy(x).float()           # tensor

# ——— Herramienta de clasificación ———
@tool
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
        flair_path = image_path
        flair_vol  = nib.load(flair_path).get_fdata()    # (H,W,S)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        k = flair_vol.shape[2] // 2          # slice central
        flair_slice = flair_vol[:, :, k]
        # Si NO tienes T1CE, pasa None → duplicaremos el canal
        x = preprocess_slice(flair_slice, t1ce_slice=None)
        # añadir dimensión batch y mover a device
        x = x.unsqueeze(0).to(device)        # (1,2,128,128)




        with torch.no_grad():
            logits = model(x)
            probs  = torch.softmax(logits, dim=1)[0].cpu().numpy()
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
