from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

# 1. TABLA DE USUARIOS
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str 
    records: List["PersonalRecord"] = Relationship(back_populates="user")

# 2. TABLA DE RÉCORDS (Base de datos)
class PersonalRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id") 
    
    distancia_nombre: str = Field(index=True)
    distancia_metros: int
    tiempo_segundos: float
    velocidad_media_kmh: float
    pulsaciones_medias: Optional[int] = None
    desnivel_positivo: float
    fecha_actividad: datetime
    nombre_archivo: str
    
    user: Optional[User] = Relationship(back_populates="records")

# 3. MODELOS DE APOYO (No crean tablas, solo validan datos)
class UserAuth(SQLModel):
    """Para el Login y Registro"""
    username: str
    password: str

class SegmentResult(SQLModel):
    """Para la respuesta JSON tras analizar un archivo"""
    distancia_nombre: str
    tiempo_segundos: float
    velocidad_media_kmh: float
    pulsaciones_medias: Optional[int]
    desnivel_positivo: float
    es_nuevo_record: bool
    diferencia_con_anterior: Optional[float] = None