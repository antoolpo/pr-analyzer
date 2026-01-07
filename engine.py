import lxml.etree as ET
from datetime import datetime
from haversine import haversine
from typing import List, Optional
import math

# Las distancias que queremos analizar
OBJETIVOS = {
    "100m": 100,
    "200m": 200,
    "500m": 500,
    "1km": 1000,
    "2km": 2000,
    "5km": 5000,
    "10km": 10000,
    "15km": 15000,
    "21km": 21097,
    "42km": 42195
}

class TrackPoint:
    def __init__(self, lat, lon, ele, time, hr):
        self.lat = lat
        self.lon = lon
        self.ele = ele
        self.time = time
        self.hr = hr
        self.dist_acumulada = 0.0

def parse_tcx(file_content: bytes) -> List[TrackPoint]:
    """Lee el XML del TCX y extrae puntos útiles."""
    try:
        tree = ET.fromstring(file_content)
    except ET.XMLSyntaxError:
        return []
        
    # Los archivos TCX de Garmin/Strava usan este namespace
    ns = {'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
    
    points = []
    
    # Buscar todos los Trackpoints
    for trackpoint in tree.findall('.//ns:Trackpoint', ns):
        # Tiempo es obligatorio
        time_node = trackpoint.find('ns:Time', ns)
        if time_node is None: continue
        time_str = time_node.text
        # Manejo básico de fecha ISO
        time_obj = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        
        # Posición es obligatoria para calcular distancia
        position = trackpoint.find('ns:Position', ns)
        if position is None: continue
            
        lat = float(position.find('ns:LatitudeDegrees', ns).text)
        lon = float(position.find('ns:LongitudeDegrees', ns).text)
        
        # Elevación
        ele_node = trackpoint.find('ns:AltitudeMeters', ns)
        ele = float(ele_node.text) if ele_node is not None else 0.0
        
        # Frecuencia Cardíaca (Opcional)
        hr = None
        hr_node = trackpoint.find('.//ns:HeartRateBpm/ns:Value', ns)
        if hr_node is not None:
            hr = int(hr_node.text)
            
        points.append(TrackPoint(lat, lon, ele, time_obj, hr))
        
    return points

def calcular_distancias_acumuladas(points: List[TrackPoint]):
    """Recorre los puntos y calcula la distancia total acumulada metro a metro."""
    if not points: return
    
    total_dist = 0.0
    points[0].dist_acumulada = 0.0
    
    for i in range(1, len(points)):
        prev = points[i-1]
        curr = points[i]
        # Distancia geodésica entre dos coordenadas
        dist = haversine((prev.lat, prev.lon), (curr.lat, curr.lon), unit='m')
        total_dist += dist
        curr.dist_acumulada = total_dist

def analizar_mejor_segmento(points: List[TrackPoint], distancia_objetivo_metros: int):
    """
    Algoritmo Sliding Window.
    Busca el tramo continuo de X metros que se hizo en el menor tiempo.
    """
    if not points or points[-1].dist_acumulada < distancia_objetivo_metros:
        return None

    mejor_tiempo = float('inf')
    mejor_data = None
    
    start_idx = 0
    
    # end_idx avanza hacia el final
    for end_idx in range(1, len(points)):
        distancia_actual = points[end_idx].dist_acumulada - points[start_idx].dist_acumulada
        
        # Cuando la ventana cubre la distancia requerida...
        while distancia_actual >= distancia_objetivo_metros:
            
            # Calculamos tiempo
            tiempo_segmento = (points[end_idx].time - points[start_idx].time).total_seconds()
            
            # Evitar tiempos de 0 o negativos por errores de GPS
            if tiempo_segmento > 0:
                if tiempo_segmento < mejor_tiempo:
                    mejor_tiempo = tiempo_segmento
                    
                    # --- Calcular métricas de ESTE segmento específico ---
                    segment_points = points[start_idx : end_idx+1]
                    
                    # 1. Desnivel Positivo Acumulado en el segmento
                    elev_gain = 0
                    for k in range(1, len(segment_points)):
                        diff = segment_points[k].ele - segment_points[k-1].ele
                        if diff > 0:
                            elev_gain += diff
                    
                    # 2. Pulsaciones Medias
                    hrs = [p.hr for p in segment_points if p.hr is not None]
                    avg_hr = int(sum(hrs)/len(hrs)) if hrs else 0
                    
                    # 3. Velocidad Media (km/h)
                    # Usamos la distancia real del segmento (puede ser 1005m para pedir 1km)
                    dist_exacta_segmento = points[end_idx].dist_acumulada - points[start_idx].dist_acumulada
                    velocidad_media = (dist_exacta_segmento / tiempo_segmento) * 3.6
                    
                    mejor_data = {
                        "tiempo": mejor_tiempo,
                        "hr": avg_hr,
                        "ele": elev_gain,
                        "speed": velocidad_media
                    }

            # Intentamos cerrar la ventana desde el inicio (start_idx) para ver si encontramos
            # un tramo más corto en distancia pero que cumpla el objetivo >= metros
            start_idx += 1
            if start_idx >= len(points): break
            distancia_actual = points[end_idx].dist_acumulada - points[start_idx].dist_acumulada

    return mejor_data

def calcular_velocidad_laps(points):
    laps = []
    ultimo_km = 0
    for p in points:
        km_actual = int(p.dist_acumulada // 1000)
        if km_actual > ultimo_km:
            laps.append(km_actual)
            ultimo_km = km_actual
    return laps

def obtener_resumen_completo(points, resultados_segmentos):
    """
    Combina los puntos del mapa, los datos de las gráficas y 
    los récords detectados en esta sesión específica.
    """
    total_seg = (points[-1].time - points[0].time).total_seconds()
    distancia_total = points[-1].dist_acumulada / 1000.0
    
    # Cálculo de desnivel positivo acumulado
    desnivel_total = 0
    for i in range(1, len(points)):
        diff = points[i].ele - points[i-1].ele
        if diff > 0: desnivel_total += diff

    # Formatear tiempo (HH:MM:SS o MM:SS)
    m, s = divmod(int(total_seg), 60)
    h, m = divmod(m, 60)
    tiempo_str = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"

    return {
        "stats_globales": {
            "tiempo": tiempo_str,
            "distancia": f"{distancia_total:.2f} km",
            "velocidad": f"{(distancia_total / (total_seg/3600)):.1f} km/h" if total_seg > 0 else "0.0 km/h",
            "desnivel": f"{int(desnivel_total)} m"
        },
        "records_sesion": resultados_segmentos, # Aquí van los récords de esta subida
        "path": [[p.lat, p.lon] for p in points],
        "hrs": [p.hr for p in points if p.hr is not None],
        "altitudes": [round(p.ele, 1) for p in points]
    }