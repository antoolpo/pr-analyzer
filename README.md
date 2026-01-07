# 🏃‍♂️ PR Analyzer

> Análisis inteligente de récords personales de running desde archivos TCX

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descripción

PR Analyzer es una aplicación web que analiza automáticamente tus actividades de running para detectar récords personales en múltiples distancias. Sube tu archivo TCX desde Garmin, Strava o cualquier dispositivo compatible, y obtén un análisis completo de tu rendimiento.

## ✨ Características principales

### 🎯 Análisis automático de récords
- **12 distancias diferentes**: Desde 50m hasta maratón (42km)
- **Detección inteligente**: Encuentra automáticamente tu mejor tiempo en cada distancia
- **Algoritmo de ventana deslizante**: Analiza todos los segmentos posibles de tu actividad
- **Comparación con récords anteriores**: Muestra cuánto mejoraste

### 📊 Visualización de datos
- **Mapa interactivo**: Visualiza tu ruta completa con Leaflet
- **Gráficas de rendimiento**: 
  - Pulsaciones cardíacas en tiempo real
  - Perfil de altitud del recorrido
- **Estadísticas de sesión**: Tiempo total, distancia, ritmo medio y desnivel

### 🔮 Predicciones de marca
- **Fórmula de Riegel**: Predicción científica basada en tus récords actuales
- **12 distancias predichas**: Calcula tus tiempos potenciales
- **Comparación inteligente**: Compara predicciones con tus récords reales
- **Análisis de potencial**: Identifica en qué distancias puedes mejorar más

### 👤 Sistema de usuarios
- **Autenticación segura**: Contraseñas hasheadas con PBKDF2-SHA256
- **Datos privados**: Cada usuario solo ve sus propios récords
- **Persistencia**: SQLite guarda toda tu información de forma segura

## 🚀 Instalación

### Requisitos previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación local

1. **Clona el repositorio**
```bash
git clone https://github.com/antoolpo/pr-analyzer.git
cd pr-analyzer
```

2. **Crea un entorno virtual** (recomendado)
```bash
python -m venv venv

# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

3. **Instala las dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecuta la aplicación**
```bash
uvicorn main:app --reload
```

5. **Abre tu navegador**
```
http://localhost:8000
```

## 🐳 Instalación con Docker

### Opción 1: Docker Compose (recomendado)

```bash
# Construir e iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

La aplicación estará disponible en `http://localhost:8000`

### Opción 2: Docker manual

```bash
# Construir la imagen
docker build -t pr-analyzer .

# Ejecutar el contenedor
docker run -d -p 8000:8000 -v $(pwd)/data:/app/data --name pr-analyzer pr-analyzer

# Ver logs
docker logs -f pr-analyzer

# Detener
docker stop pr-analyzer
docker rm pr-analyzer
```

## 📖 Uso

### 1. Crear una cuenta
- Haz clic en "Crear una cuenta nueva"
- Elige un usuario (mínimo 3 caracteres)
- Establece una contraseña segura (6-72 caracteres)

### 2. Subir un archivo TCX
- Exporta tu actividad desde Garmin Connect, Strava, etc.
- Haz clic en "Añadir Sesión"
- Selecciona tu archivo `.tcx`
- ¡Espera unos segundos mientras se analiza!

### 3. Ver tus récords
- **Pestaña "Mis Récords"**: Todos tus récords personales actuales
- **Pestaña "Nueva Sesión"**: Análisis de la última actividad subida
- **Pestaña "Predicciones"**: Tus tiempos potenciales en otras distancias

## 🗂️ Estructura del proyecto

```
pr-analyzer/
├── main.py              # Aplicación FastAPI y endpoints
├── models.py            # Modelos de datos (SQLModel)
├── database.py          # Configuración de base de datos
├── engine.py            # Lógica de análisis de TCX
├── requirements.txt     # Dependencias
├── docker-compose.yml   # Configuración Docker
├── Dockerfile          # Imagen Docker
├── .gitignore          # Archivos ignorados por Git
├── static/             # Archivos frontend
│   ├── index.html      # Interfaz web
│   ├── script.js       # Lógica JavaScript
│   └── style.css       # Estilos
└── data/               # Base de datos (no en Git)
    └── records.db      # SQLite
```

## 🔧 Tecnologías utilizadas

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)**: Framework web moderno y rápido
- **[SQLModel](https://sqlmodel.tiangolo.com/)**: ORM basado en Pydantic y SQLAlchemy
- **[SQLite](https://www.sqlite.org/)**: Base de datos ligera y eficiente
- **[lxml](https://lxml.de/)**: Parsing de archivos TCX (XML)
- **[haversine](https://pypi.org/project/haversine/)**: Cálculo de distancias geodésicas

### Frontend
- **[Bootstrap 5](https://getbootstrap.com/)**: Framework CSS moderno
- **[Leaflet](https://leafletjs.com/)**: Mapas interactivos
- **[Chart.js](https://www.chartjs.org/)**: Gráficas de rendimiento
- **Vanilla JavaScript**: Sin frameworks pesados

### Seguridad
- **PBKDF2-SHA256**: Hasheo de contraseñas (100,000 iteraciones)
- **Salt único**: Por cada contraseña guardada
- **Sin almacenamiento en texto plano**: Las contraseñas nunca se guardan sin hashear

## 📊 Distancias analizadas

| Distancia | Metros exactos | Uso común |
|-----------|---------------|-----------|
| 50m | 50 | Sprint |
| 100m | 100 | Sprint |
| 200m | 200 | Sprint |
| 400m | 400 | Sprint largo |
| 500m | 500 | Media distancia |
| 1km | 1,000 | Media distancia |
| 2km | 2,000 | Fondo corto |
| 5km | 5,000 | Fondo popular |
| 10km | 10,000 | Fondo estándar |
| 15km | 15,000 | Fondo largo |
| 21km | 21,097 | Media maratón |
| 42km | 42,195 | Maratón |

## 🧮 Algoritmo de análisis

### Ventana deslizante (Sliding Window)
El algoritmo recorre toda tu actividad buscando el segmento continuo más rápido para cada distancia:

1. **Cálculo de distancias acumuladas**: Usa fórmula de Haversine para GPS
2. **Búsqueda de mejor segmento**: Para cada distancia objetivo
3. **Optimización**: Encuentra el tramo más rápido independientemente del punto de inicio
4. **Métricas calculadas**: Tiempo, velocidad, pulsaciones, desnivel

### Predicciones (Fórmula de Riegel)
```
T2 = T1 × (D2 / D1)^1.06
```
Donde:
- T1 = Tiempo conocido en distancia D1
- T2 = Tiempo predicho en distancia D2
- 1.06 = Factor de fatiga (estándar de Riegel)

## 🚀 Deployment

### Render.com (recomendado para hobby)

1. Crea una cuenta en [Render.com](https://render.com)
2. Conecta tu repositorio de GitHub
3. Configura el servicio:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Añade variable de entorno:
   - `DATA_DIR=/tmp`

### Railway.app

1. Instala Railway CLI o usa la web
2. Conecta tu repositorio
3. Railway detecta automáticamente FastAPI
4. Configura `DATA_DIR=/tmp` en variables de entorno

### Fly.io

```bash
# Instalar flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Deploy
flyctl launch
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz un Fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 🐛 Reportar bugs

Si encuentras un bug, por favor abre un [Issue](https://github.com/antoolpo/pr-analyzer/issues) con:
- Descripción del problema
- Pasos para reproducirlo
- Comportamiento esperado vs actual
- Screenshots si es posible

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👨‍💻 Autor

**Antonio Olmedo** - [GitHub](https://github.com/antoolpo)

## 🙏 Agradecimientos

- Garmin y Strava por el formato TCX
- Comunidad de FastAPI
- Todos los runners que prueban la app

¿Preguntas? ¿Sugerencias? Abre un Issue o contáctame directamente.

---

⭐ Si te gusta el proyecto, ¡dale una estrella en GitHub!

**Happy Running! 🏃‍♂️💨**

