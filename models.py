from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
import hashlib
import secrets

# Alternativa sin bcrypt - usando hashlib (incluido en Python)
class PasswordHasher:
    @staticmethod
    def hash(password: str) -> str:
        """Hashea una contraseña usando PBKDF2-SHA256"""
        salt = secrets.token_hex(32)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}${pwd_hash.hex()}"
    
    @staticmethod
    def verify(password: str, hashed: str) -> bool:
        """Verifica una contraseña contra su hash"""
        try:
            salt, pwd_hash = hashed.split('$')
            new_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return pwd_hash == new_hash.hex()
        except:
            return False

pwd_context = PasswordHasher()

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
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)

class SegmentResult(SQLModel):
    """Para la respuesta JSON tras analizar un archivo"""
    distancia_nombre: str
    tiempo_segundos: float
    velocidad_media_kmh: float
    pulsaciones_medias: Optional[int]
    desnivel_positivo: float
    es_nuevo_record: bool
    diferencia_con_anterior: Optional[float] = None