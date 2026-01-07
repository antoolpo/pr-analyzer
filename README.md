# PR Analyzer 🏃‍♂️

Aplicación web para analizar récords personales de running desde archivos TCX.

## Características

- 📊 Análisis automático de récords en múltiples distancias (100m - 42km)
- 🗺️ Visualización de rutas en mapa interactivo
- 📈 Gráficas de pulsaciones y altitud
- 🎯 Predicciones de marca basadas en fórmula de Riegel
- 👤 Sistema de usuarios con autenticación
- 💾 Persistencia de datos con SQLite

## Tecnologías

- **Backend:** FastAPI + SQLModel
- **Frontend:** Bootstrap 5 + Leaflet + Chart.js
- **Base de datos:** SQLite

## Instalación Local

1. Clona el repositorio:
```bash
git clone https://github.com/antoolpo/pr-analyzer.com
cd pr-analyzer
```

2. Crea un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecuta la aplicación:
```bash
uvicorn main:app --reload
```

5. Abre tu navegador en `http://localhost:8000`

## Uso

1. Crea una cuenta o inicia sesión
2. Sube un archivo TCX desde Garmin/Strava
3. Visualiza tus récords automáticamente detectados
4. Explora las predicciones de marca para otras distancias

## Deploy

Compatible con Render, Railway, Fly.io y otros servicios de hosting gratuitos.

## Licencia

MIT