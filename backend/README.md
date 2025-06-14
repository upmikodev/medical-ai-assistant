# TFM Backend - FastAPI

Este backend actúa como intermediario entre la interfaz en React y el sistema de IA (Jarvis / Strands). Actualmente responde con una simulación, y está preparado para integrarse con el código real del orquestador.

---

## 🧩 Estructura

```
TFM_backend_def/
│
├── main.py               ← Backend FastAPI
├── requirements.txt      ← Dependencias
├── launch.bat            ← Script para Windows
├── strands_project/      ← (opcional) Carpeta con el código real de Strands
```

---

## ⚙️ Requisitos

- Python 3.11+
- Git (si usas repos remoto)
- VS Code (recomendado)

---

## 🚀 Instalación paso a paso (Terminal PowerShell)

### 1. Abrir terminal y posicionarse en el proyecto

```powershell
cd C:\Proyectos\TFM_backend_def
```

### 2. Crear entorno virtual

```powershell
python -m venv .venv
```

### 3. Activar entorno virtual

```powershell
.venv\Scripts\Activate.ps1
```

(Si da error: ejecutar antes `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)

### 4. Instalar dependencias

```powershell
pip install -r requirements.txt
```

---

## 🧪 Ejecutar servidor

```powershell
python -m uvicorn main:app --reload
```

Luego abre en el navegador:
```
http://localhost:8000/docs
```

---

## 🟡 Simulación activa

Actualmente el backend usa esta función temporal:

```python
def agent_orchestrator(query: str) -> str:
    return f"[SIMULACIÓN] Jarvis recibió la petición: '{query}'"
```

✅ Sustituir por:

```python
from strands import agent_orchestrator
```

una vez esté disponible el módulo real (`strands`).

---

## 📦 Para integrar el código real de Strands

```powershell
pip install -e ./strands_project
```

(asegúrate de que contiene `setup.py` o `pyproject.toml`)

---

## 🧷 Endpoints disponibles

- `POST /interact`: recibe texto del usuario, responde texto.
- `POST /upload-image`: recibe imagen, lanza proceso, responde texto.
