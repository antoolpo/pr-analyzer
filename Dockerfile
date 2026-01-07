# Usar Python 3.11 ligero
FROM python:3.11-slim

# Evitar archivos basura de python y ver logs inmediatamente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instalar dependencias del sistema necesarias para procesar XML (lxml)
RUN apt-get update && apt-get install -y libxml2-dev libxslt-dev gcc && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Crear directorio de datos
RUN mkdir -p data

# Exponer el puerto
EXPOSE 8000

# Comando de ejecución
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]