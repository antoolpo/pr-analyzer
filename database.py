import os
from sqlmodel import SQLModel, create_engine, Session

# Permitir configurar la carpeta de datos mediante variable de entorno
# Esto es útil para servicios como Render que usan /tmp
data_dir = os.getenv("DATA_DIR", "data")
os.makedirs(data_dir, exist_ok=True)

sqlite_file_name = f"{data_dir}/records.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session