import os
import json
import logging
import re
from PIL import Image
import cv2, numpy as np
import nibabel as nib
import torch
from torchvision import models, transforms
import tensorflow as tf
from strands_tools import tool
from tensorflow.keras.models import load_model # <--- Esta es la clave
from sklearn.preprocessing import MinMaxScaler # Para normalizar las imágenes
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.pyplot as plt

# ——— Configuración básica ———
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEVICE        = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CLASS_NAMES   = ["No tumor", "Tumor"]
MODEL_PATH    = "models/brain_tumor_segmentation.h5"
IMG_SIZE = 128

#image_path='pictures\carlos_perez_paco_1_flair.nii'

def dice_coef(y_true, y_pred, smooth=100):
    y_true_f = tf.keras.backend.flatten(y_true)
    y_pred_f = tf.keras.backend.flatten(y_pred)
    intersection = tf.keras.backend.sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (tf.keras.backend.sum(y_true_f) + tf.keras.backend.sum(y_pred_f) + smooth)

def dice_coef_necrotic(y_true, y_pred, smooth=100):
    return dice_coef(y_true[:, :, :, 1], y_pred[:, :, :, 1], smooth)

def dice_coef_edema(y_true, y_pred, smooth=100):
    return dice_coef(y_true[:, :, :, 2], y_pred[:, :, :, 2], smooth)

def dice_coef_enhancing(y_true, y_pred, smooth=100):
    return dice_coef(y_true[:, :, :, 3], y_pred[:, :, :, 3], smooth)

def precision(y_true, y_pred):
    true_positives = tf.keras.backend.sum(tf.keras.backend.round(tf.keras.backend.clip(y_true * y_pred, 0, 1)))
    predicted_positives = tf.keras.backend.sum(tf.keras.backend.round(tf.keras.backend.clip(y_pred, 0, 1)))
    precision_val = true_positives / (predicted_positives + tf.keras.backend.epsilon())
    return precision_val

def sensitivity(y_true, y_pred):
    true_positives = tf.keras.backend.sum(tf.keras.backend.round(tf.keras.backend.clip(y_true * y_pred, 0, 1)))
    possible_positives = tf.keras.backend.sum(tf.keras.backend.round(tf.keras.backend.clip(y_true, 0, 1)))
    sensitivity_val = true_positives / (possible_positives + tf.keras.backend.epsilon())
    return sensitivity_val

def specificity(y_true, y_pred):
    true_negatives = tf.keras.backend.sum(tf.keras.backend.round(tf.keras.backend.clip((1-y_true) * (1-y_pred), 0, 1)))
    possible_negatives = tf.keras.backend.sum(tf.keras.backend.round(tf.keras.backend.clip(1-y_true, 0, 1)))
    specificity_val = true_negatives / (possible_negatives + tf.keras.backend.epsilon())
    return specificity_val



custom_objects = {
    'dice_coef': dice_coef,
    'dice_coef_necrotic': dice_coef_necrotic,
    'dice_coef_edema': dice_coef_edema,
    'dice_coef_enhancing': dice_coef_enhancing,
    'precision': precision,
    'sensitivity': sensitivity,
    'specificity': specificity,
    'MeanIoU': tf.keras.metrics.MeanIoU(num_classes=4) # tf.keras.metrics.MeanIoU también debe pasarse si fue personalizado
}




# ——— Función de carga del modelo ———
def load_model(model_path: str):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")
    model = tf.keras.models.load_model(model_path, custom_objects=custom_objects)
    logger.info(f"Model loaded successfully from {model_path}")
    return model



def preprocess_nifti_for_prediction(image_path_t1ce,image_path_flair, seg_path=None, target_size=(128, 128)):
    """
    Carga y preprocesa un par de imágenes NIfTI (T1CE y FLAIR) para la predicción.
    Opcionalmente, carga la máscara de segmentación si está disponible para comparación.

    Args:
        image_path_t1ce (str): Ruta al archivo .nii de la imagen T1CE.
        image_path_flair (str): Ruta al archivo .nii de la imagen FLAIR.
        seg_path (str, optional): Ruta al archivo .nii de la máscara de segmentación (verdad fundamental).
                                  Necesario si quieres visualizar la verdad fundamental.
        target_size (tuple): Tamaño (alto, ancho) al que se redimensionarán las rebanadas.

    Returns:
        tuple: (processed_volume_3d, seg_volume_3d_categorical)
               - processed_volume_3d: Volumen 3D preprocesado (alto, ancho, profundidad, canales).
                                       Listo para extraer rebanadas.
               - seg_volume_3d_categorical: Máscara 3D categórica (alto, ancho, profundidad).
                                            None si seg_path no se proporciona.
    """
    # Cargar imágenes
    img_t1ce = nib.load(image_path_t1ce).get_fdata()
    img_flair = nib.load(image_path_flair).get_fdata()

    # Normalizar imágenes
    scaler = MinMaxScaler()
    img_t1ce = scaler.fit_transform(img_t1ce.reshape(-1, img_t1ce.shape[-1])).reshape(img_t1ce.shape)
    img_flair = scaler.fit_transform(img_flair.reshape(-1, img_flair.shape[-1])).reshape(img_flair.shape)

    processed_volume = np.stack([img_t1ce, img_flair], axis=-1) # (depth, height, width, channels)

    num_slices = processed_volume.shape[2]
    resized_volume = np.zeros((target_size[0], target_size[1], num_slices, processed_volume.shape[3]), dtype=np.float32)

    for i in range(num_slices):
        slice_t1ce = tf.image.resize(processed_volume[:, :, i, 0][..., tf.newaxis], target_size)
        slice_flair = tf.image.resize(processed_volume[:, :, i, 1][..., tf.newaxis], target_size)
        resized_volume[:, :, i, 0] = slice_t1ce[:, :, 0]
        resized_volume[:, :, i, 1] = slice_flair[:, :, 0]

    seg_volume_categorical = None
    if seg_path:
        seg = nib.load(seg_path).get_fdata()
        seg = seg.astype(np.uint8)

        # Reasignar la clase 4 a 3 (crucial)
        seg[seg==4] = 3

        resized_seg = np.zeros(target_size + (num_slices,), dtype=np.uint8)
        for i in range(num_slices):
            resized_seg[:, :, i] = tf.image.resize(seg[:, :, i][..., tf.newaxis], target_size, method='nearest')[:, :, 0]
        seg_volume_categorical = resized_seg

    return resized_volume, seg_volume_categorical         # tensor

# ——— Herramienta de clasificación ———
@tool(
    name="segmenter_tumor_from_image",
    description="Segmenta un tumor cerebral a partir de imágenes FLAIR y T1CE.",
)
def segmenter_tumor_from_image(flair_path: str, t1ce_path: str) -> str:
    """
    Clasifica una única imagen. NO BUSCA ficheros: espera recibir
    la ruta exacta al archivo de imagen.

    Args:
        flair_path (str): Ruta al archivo .nii de la imagen FLAIR.
        t1ce_path (str): Ruta al archivo .nii de la imagen T1CE.

    Returns:
        str: Resultado de la segmentación en formato JSON.
    """
    for p in (flair_path, t1ce_path):
        if not os.path.isfile(p):
            err = f"Image file not found: {p}"
            logger.error(err)
            return json.dumps({"error": err})
    try:
        model = load_model(MODEL_PATH)
        
        processed_volume, seg_truth_volume_categorical = preprocess_nifti_for_prediction(
            #image_t1ce_path,
            image_path_t1ce=t1ce_path,
            image_path_flair=flair_path,
            #seg_path=segmentation_truth_path,
            target_size=(IMG_SIZE, IMG_SIZE)
        )
        selected_slice_idx = 95
        input_slice = processed_volume[:, :, selected_slice_idx, :][np.newaxis, ...]
        print(f"Realizando predicción para la rebanada {selected_slice_idx}...")
        predicted_output = model.predict(input_slice)
        predicted_mask_categorical = np.argmax(predicted_output, axis=-1)[0]

        cmap = ListedColormap(['black', 'red', 'green', 'blue']) # 0: Fondo, 1: Necrótico, 2: Edema, 3: Realzante
        norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], cmap.N) # Límite para 4 clases

        legend_elements = [
            Patch(facecolor='black', edgecolor='black', label='Background'),
            Patch(facecolor='red', edgecolor='red', label='Necrotic (Class 1)'),
            Patch(facecolor='green', edgecolor='green', label='Edema (Class 2)'),
            Patch(facecolor='blue', edgecolor='blue', label='Enhancing (Class 3)')
        ]

        plt.imshow(predicted_mask_categorical, cmap=cmap, norm=norm)
        plt.title(f'Predicted Mask - Slice {selected_slice_idx}')
        plt.legend(handles=legend_elements, loc='lower left', bbox_to_anchor=(0.0, -0.3))
        plt.axis('off')

        rgba = plt.cm.get_cmap("jet")(predicted_mask_categorical / 3.0)

        # 2. Conviértelo a RGB uint8 (descarta alfa)
        rgb  = (rgba[...,:3] * 255).astype(np.uint8)        # (H,W,3) uint8

        # 3. Asegura carpeta y guarda con Pillow
        os.makedirs("segmentations", exist_ok=True)
        png_name = (
            "segmentations/Resultado_segmentacion_"
            + os.path.basename(flair_path).replace("_flair.nii", ".png")
        )
        Image.fromarray(rgb).save(png_name, format="PNG")
        logger.info(f"Segmentación guardada como: {png_name}")
        return json.dumps({"saved_mask": png_name})

    except Exception as e:
        logger.error(f"Segmentación error: {e}", exc_info=True)
        return json.dumps({"error": str(e)})
