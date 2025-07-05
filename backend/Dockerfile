# Imagen base ligera
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Copiamos dependencias
COPY requirements.txt .

# Instalamos dependencias del sistema + python
RUN apt-get update && apt-get install -y \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

# Copiamos el código completo del backend
COPY . .

# Puerto de exposición
EXPOSE 8000

# Arranca FastAPI con uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
