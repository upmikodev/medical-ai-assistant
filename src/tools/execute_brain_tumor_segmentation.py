import os
import json
import logging
from PIL import Image
import cv2
import numpy as np
import nibabel as nib
import torch
import tensorflow as tf
from strands.tools import tool
from tensorflow.keras.models import load_model # <--- Esta es la clave
from sklearn.preprocessing import MinMaxScaler # Para normalizar las imágenes
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib
from skimage.transform import resize
from skimage.measure import find_contours
#import matplotlib
#matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt

# ——— Configuración básica ———
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEVICE        = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CLASS_NAMES   = ["No tumor", "Tumor"]
MODEL_PATH    = "data/models/brain_tumor_segmentation.h5"
WEIGHTS_PATH  = "data/models/model_26-0.023368.weights.h5"

IMG_SIZE = 128
VOLUME_SLICES = 100
VOLUME_START_AT = 22 # first slice of volume that we will include
SELECTED_SLICE_IDX=60
PALETTE = np.array([
    [0,   0,   0],    # fondo
    [255, 0,   0],    # clase 1 (necrosis)
    [0,   255, 0],    # clase 2 (edema)
    [0,   0,   255]   # clase 3 (realce)
], dtype=np.uint8)

SEGMENT_CLASSES = {
    0 : 'NOT tumor',
    1 : 'NECROTIC/CORE', # or NON-ENHANCING tumor CORE
    2 : 'EDEMA',
    3 : 'ENHANCING' # original 4 -> converted into 3
}

cmap = matplotlib.colors.ListedColormap(["#000000", "#1121b2", "#0c8f61", "#930000"])
norm = matplotlib.colors.BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], cmap.N)


OUT_INPUT_DIR = "data/segmentations/"
#OUT_INPUT_DIR = f"data/segmentations/" + os.path.basename(flair_path)+"/"





#--------------------------METRICAS DE EVALUACION---------------
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
def load_model(model_path: str,weights_path: str):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")
    model = tf.keras.models.load_model(model_path, custom_objects=custom_objects,compile=False)
    if not os.path.exists(weights_path):
        raise FileNotFoundError(f"Weights not found: {weights_path}")
    model.load_weights(weights_path)
    logger.info(f"Model loaded successfully from {model_path}")
    return model




def showPredicts(p,flair,flair_path, start_slice=SELECTED_SLICE_IDX):
    """Muestra 6 figuras independientes (FLAIR, GT, pred y clases) para un slice."""

    os.makedirs(OUT_INPUT_DIR, exist_ok=True)
    png_input     = os.path.join(
        OUT_INPUT_DIR+f"Imagen_Cerebral_slice_{SELECTED_SLICE_IDX}_"+ os.path.basename(flair_path).replace("_flair.nii", ".png")
    )


    png_mask = (
    OUT_INPUT_DIR+"Aleatorio_"
    + os.path.basename(flair_path).replace("_flair.nii", ".png")
    )


    png_overlay = (
    OUT_INPUT_DIR+"Resultado_segmentacion_superpuesto_"
    + os.path.basename(flair_path).replace("_flair.nii", ".png")
    )





    k = start_slice + VOLUME_START_AT                       # corte real en el volumen
    flair_2d = cv2.resize(flair[:, :, k], (IMG_SIZE, IMG_SIZE))
    #gt_2d    = cv2.resize(gt[:, :, k],    (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_NEAREST)
    core = p[:,:,:,1]
    edema= p[:,:,:,2]
    enhancing = p[:,:,:,3]


    # 1) FLAIR original
    plt.figure(figsize=(6, 6), dpi=200)
    plt.imshow(flair_2d, cmap='gray')
    plt.title('Original FLAIR')
    plt.axis('off')
    #plt.savefig(png_input, bbox_inches='tight', pad_inches=0)

    # 2) Ground-truth
    if False:
        plt.figure(figsize=(4,4))
        plt.imshow(flair_2d, cmap='gray')
        plt.imshow(gt_2d, cmap='Reds', alpha=0.3, interpolation='none')
        plt.title('Ground truth')
        plt.axis('off')

    # 3-6) Predicciones
    plt.figure(figsize=(6, 6), dpi=200)
    plt.imshow(flair_2d, cmap='gray')
    plt.imshow(p[start_slice,:,:,1:4], cmap='Reds', alpha=0.3, interpolation='none')
    plt.title('All classes predicted')
    plt.axis('off')
    plt.savefig(png_overlay, bbox_inches='tight', pad_inches=0)

    plt.figure(figsize=(4,4))
    plt.imshow(flair_2d, cmap='gray')
    plt.imshow(core[start_slice,:,:], cmap='Reds', alpha=0.3, interpolation='none')
    plt.title(f'{SEGMENT_CLASSES[1]} predicted')
    plt.axis('off')

    plt.figure(figsize=(4,4))
    plt.imshow(flair_2d, cmap='gray')
    plt.imshow(edema[start_slice,:,:], cmap='Reds', alpha=0.3, interpolation='none')
    plt.title(f'{SEGMENT_CLASSES[2]} predicted')
    plt.axis('off')
    plt.savefig(png_mask, bbox_inches='tight', pad_inches=0)

    plt.figure(figsize=(4,4))
    plt.imshow(flair_2d, cmap='gray')
    plt.imshow(enhancing[start_slice,:,:], cmap='Reds', alpha=0.3, interpolation='none')
    plt.title(f'{SEGMENT_CLASSES[3]} predicted')
    plt.axis('off')

    plt.show()



    figures = [
        ("Original FLAIR",                     flair_2d,                    None),
        ("All classes predicted",              p[start_slice, :, :, 1:4],   None),
        (f'{SEGMENT_CLASSES[1]} predicted',    core[start_slice, :, :],     None),
        (f'{SEGMENT_CLASSES[2]} predicted',    edema[start_slice, :, :],    None),
        (f'{SEGMENT_CLASSES[3]} predicted',    enhancing[start_slice, :, :],None),
    ]


    return png_input, png_mask,png_overlay










def show_predicted_segmentations(p,slice_to_plot=SELECTED_SLICE_IDX):

    predicted_seg=p
    all = predicted_seg[slice_to_plot,:,:,1:4] # Deletion of class 0 (Keep only Core + Edema + Enhancing classes)
    zero = predicted_seg[slice_to_plot,:,:,0] # Isolation of class 0, Background (kind of useless, it is the opposite of the "all")
    core = predicted_seg[slice_to_plot,:,:,1] # Isolation of class 1, Core
    edema = predicted_seg[slice_to_plot,:,:,2] # Isolation of class 2, Edema
    enhancing = predicted_seg[slice_to_plot,:,:,3] # Isolation of class 3, Enhancing

    plt.figure(figsize=(6, 6), dpi=200)
    plt.imshow(all, cmap='gray')
    plt.title(f'Predicted Segmentation - All classes predicted')
    plt.axis('off')

    plt.figure(figsize=(4,4))
    plt.imshow(core, cmap, norm)
    plt.title(f'Predicted Segmentation - {SEGMENT_CLASSES[1]} predicted')
    plt.axis('off')

    plt.figure(figsize=(4,4))
    plt.imshow(edema, cmap, norm)
    plt.title(f'Predicted Segmentation - {SEGMENT_CLASSES[2]} predicted')
    plt.axis('off')

    plt.figure(figsize=(4,4))
    plt.imshow(enhancing, cmap='gray')
    plt.title(f'Predicted Segmentation - {SEGMENT_CLASSES[3]} predicted')
    plt.axis('off')
    plt.show()

    return None






# ——— Herramienta de Segmentacion ———
@tool(
    name="segmenter_tumor_from_image",
    description="Segmenta un tumor cerebral a partir de imágenes FLAIR y T1CE.",
)
def segmenter_tumor_from_image(flair_path: str, t1ce_path: str) -> str:
    """
    Segmenta una única imagen. NO BUSCA ficheros: espera recibir
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
        model = load_model(MODEL_PATH, WEIGHTS_PATH)
        

        X = np.empty((VOLUME_SLICES, IMG_SIZE, IMG_SIZE, 2))
        flair=nib.load(t1ce_path).get_fdata()
        t1ce=nib.load(flair_path).get_fdata()

        for j in range(VOLUME_SLICES):
            X[j,:,:,0] = cv2.resize(flair[:,:,j+VOLUME_START_AT], (IMG_SIZE,IMG_SIZE))
            X[j,:,:,1] = cv2.resize(t1ce[:,:,j+VOLUME_START_AT], (IMG_SIZE,IMG_SIZE))

        p = model.predict(X/np.max(X), verbose=1)


        png_input, png_mask,png_overlay=showPredicts(p,flair,flair_path)
        show_predicted_segmentations(p)


        return json.dumps({
            "input_slice": png_input,
            "mask_file"  : png_mask,
            "overlay_file": png_overlay
        })

    except Exception as e:
        logger.error(f"Segmentación error: {e}", exc_info=True)
        return json.dumps({"error": str(e)})



# if __name__ == "__main__":
#     import argparse, sys, json

#     flair_path="pictures/lucia_rodriguez_1_flair.nii"
#     t1ce_path="pictures/lucia_rodriguez_1_t1ce.nii"
#     result = segmenter_tumor_from_image(flair_path, t1ce_path)
#     # Pretty-print JSON result or error
#     try:
#         print(json.dumps(json.loads(result), indent=2, ensure_ascii=False))
#     except Exception:
#         print(result)