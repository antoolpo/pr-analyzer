from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from passlib.context import CryptContext

# Configuración de bcrypt para hashear contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 1. TABLA DE USUARIOS
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str  # Se guardará hasheada
    records: List["PersonalRecord"] = Relationship(back_populates="user")
    
    def set_password(self, plain_password: str):
        """Hashea y guarda la contraseña"""
        self.password = pwd_context.hash(plain_password)
    
    def verify_password(self, plain_password: str) -> bool:
        """Verifica si la contraseña coincide con el hash"""
        return pwd_context.verify(plain_password, self.password)

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