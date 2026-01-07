from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from database import create_db_and_tables, get_session
from models import PersonalRecord, User, UserAuth
from pydantic import ValidationError
import engine
import os

app = FastAPI(title="pr_analyzer")

# Crear tablas al iniciar
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

# --- RUTAS DE AUTENTICACIÓN ---

@app.post("/register")
async def register(request: Request, session: Session = Depends(get_session)):
    try:
        # Leer y parsear el body
        body = await request.json()
        print(f"\n📦 Datos recibidos:")
        print(f"   Username: '{body.get('username')}' (len={len(body.get('username', ''))})")
        print(f"   Password length: {len(body.get('password', ''))}")
        
        # Validar con Pydantic
        auth = UserAuth(**body)
        
    except ValidationError as e:
        print(f"❌ Error de validación: {e}")
        # Extraer el mensaje de error más legible
        errors = e.errors()
        if errors:
            first_error = errors[0]
            field = first_error.get('loc', [''])[0]
            msg = first_error.get('msg', 'Error de validación')
            
            if 'password' in str(field).lower() and 'longer' in msg.lower():
                raise HTTPException(
                    status_code=400,
                    detail="La contraseña no puede tener más de 72 caracteres"
                )
            elif 'password' in str(field).lower() and 'shorter' in msg.lower():
                raise HTTPException(
                    status_code=400,
                    detail="La contraseña debe tener al menos 6 caracteres"
                )
            else:
                raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=400, detail="Error de validación")
    except Exception as e:
        print(f"❌ Error general: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    print(f"📝 Intento de registro - Usuario: {auth.username}")
    
    # Verificar si el usuario ya existe
    statement = select(User).where(User.username == auth.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        print(f"❌ Usuario '{auth.username}' ya existe")
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
    
    try:
        # Crear usuario con contraseña hasheada
        new_user = User(username=auth.username)
        new_user.set_password(auth.password)  # Hashea automáticamente
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        print(f"✅ Usuario '{auth.username}' creado con ID: {new_user.id}")
        return {"id": new_user.id, "username": new_user.username}
        
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")

@app.post("/login")
def login(auth: UserAuth, session: Session = Depends(get_session)):
    print(f"🔐 Intento de login - Usuario: {auth.username}")
    
    # Buscar usuario por nombre
    user = session.exec(select(User).where(User.username == auth.username)).first()
    
    if not user:
        print(f"❌ Usuario '{auth.username}' no encontrado")
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    
    # Verificar contraseña hasheada
    if not user.verify_password(auth.password):
        print(f"❌ Contraseña incorrecta para usuario '{auth.username}'")
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    
    print(f"✅ Login exitoso - Usuario: {auth.username} (ID: {user.id})")
    return {"id": user.id, "username": user.username}

# --- RUTAS DE DATOS (MODIFICADAS CON USER_ID) ---

@app.get("/records/{user_id}")
def get_all_records(user_id: int, session: Session = Depends(get_session)):
    # Solo devolvemos los récords que pertenecen a este usuario específico
    return session.exec(
        select(PersonalRecord).where(PersonalRecord.user_id == user_id)
    ).all()

@app.post("/upload/{user_id}")
async def upload_tcx(user_id: int, file: UploadFile = File(...), session: Session = Depends(get_session)):
    if not file.filename.lower().endswith('.tcx'):
        raise HTTPException(status_code=400, detail="Formato no válido")
    
    content = await file.read()
    points = engine.parse_tcx(content)
    if not points:
        raise HTTPException(status_code=400, detail="Archivo vacío o corrupto")
    
    engine.calcular_distancias_acumuladas(points)
    records_sesion = []
    
    for nombre, metros in engine.OBJETIVOS.items():
        dato = engine.analizar_mejor_segmento(points, metros)
        if dato:
            # Filtramos por el usuario actual
            st = select(PersonalRecord).where(
                PersonalRecord.distancia_nombre == nombre,
                PersonalRecord.user_id == user_id
            )
            record_actual = session.exec(st).first()
            
            es_nuevo = False
            diferencia = None
            
            if not record_actual:
                es_nuevo = True
                record_actual = PersonalRecord(
                    user_id=user_id,
                    distancia_nombre=nombre, 
                    distancia_metros=metros, 
                    tiempo_segundos=dato["tiempo"], 
                    velocidad_media_kmh=dato["speed"], 
                    pulsaciones_medias=dato["hr"], 
                    desnivel_positivo=dato["ele"], 
                    fecha_actividad=points[0].time, 
                    nombre_archivo=file.filename
                )
                session.add(record_actual)
            elif dato["tiempo"] < record_actual.tiempo_segundos:
                es_nuevo = True
                diferencia = record_actual.tiempo_segundos - dato["tiempo"]
                
                record_actual.tiempo_segundos = dato["tiempo"]
                record_actual.velocidad_media_kmh = dato["speed"]
                record_actual.pulsaciones_medias = dato["hr"]
                record_actual.desnivel_positivo = dato["ele"]
                record_actual.fecha_actividad = points[0].time
                record_actual.nombre_archivo = file.filename
                session.add(record_actual)
            
            records_sesion.append({
                "distancia_nombre": nombre,
                "tiempo_segundos": dato["tiempo"],
                "velocidad_media_kmh": dato["speed"],
                "pulsaciones_medias": dato["hr"],
                "desnivel_positivo": dato["ele"],
                "es_nuevo_record": es_nuevo,
                "diferencia_con_anterior": diferencia
            })
    
    session.commit()

    # Calcular estadísticas globales
    total_seg = (points[-1].time - points[0].time).total_seconds()
    distancia_total = points[-1].dist_acumulada / 1000.0
    
    # Calcular desnivel positivo total
    desnivel_total = 0
    for i in range(1, len(points)):
        diff = points[i].ele - points[i-1].ele
        if diff > 0:
            desnivel_total += diff
    
    # Formatear tiempo (HH:MM:SS o MM:SS)
    m, s = divmod(int(total_seg), 60)
    h, m = divmod(m, 60)
    tiempo_str = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
    
    # Calcular ritmo medio (min/km)
    ritmo_medio_decimal = (total_seg / 60) / distancia_total if distancia_total > 0 else 0
    ritmo_min = int(ritmo_medio_decimal)
    ritmo_seg = int((ritmo_medio_decimal - ritmo_min) * 60)

    resumen = {
        "stats_globales": {
            "tiempo": tiempo_str,
            "distancia_total": f"{distancia_total:.2f} km",
            "ritmo_medio": f"{ritmo_min}:{ritmo_seg:02d} min/km",
            "desnivel": f"{int(desnivel_total)} m"
        },
        "records": records_sesion,
        "path": [[p.lat, p.lon] for p in points],
        "hrs": [p.hr for p in points if p.hr is not None],
        "altitudes": [round(p.ele, 1) for p in points]
    }
    
    return resumen