import os
import csv
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(".env")

SLAVEPORT = int(os.getenv("SLAVEPORT"))
LOG_DIRECTORY = os.getenv("LOGDIRECTORY")
PATH_LOG=f"../../{LOG_DIRECTORY}/esclavo_{SLAVEPORT}.log"
COLUMNAS_LOG = (os.getenv("LOGCOLUMNS")).split(',')



def verificar_log(path_log, columnas):
    """
        Permite verificar o crear un .log considerando que la primera fila tenga todas las columnas definidas en el .env
    """
    if not os.path.exists(path_log):
        with open(path_log, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(columnas)
            print("log creado")
    else:
        with open(path_log, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            encabezado = next(reader, None)
            if encabezado != COLUMNAS_LOG:
                raise ValueError("El archivo existe pero no tiene el formato esperado.")
            print("log coincide con el formato")


def agregar_entrada_log(path_log, datos, columnas):
    if not isinstance(datos, dict):
        raise ValueError("Los datos deben estar en un diccionario.")
    
    # Validamos que tenga todas las columnas necesarias
    if set(datos.keys()) != set(columnas):
        raise ValueError("Los datos no tienen las columnas esperadas.")
    
    with open(path_log, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow([datos[col] for col in columnas])

def crear_entrada_log(
    operacion: str,
    estado: str,
    t_ini: datetime,
    t_fin: datetime,
    puerto_maquina: int | None = None,
    busqueda: str | None = None,
    tipo_busqueda: str | None = None,
    cant_resultados: int | None = None,
    tamano_respuesta_bytes: int | None = None,
    edad: int | None = None,
    ranking: int | None = None 
    ) -> dict:

    return {
        "operacion": operacion,
        "estado": estado,
        "t_ini": t_ini,
        "t_fin": t_fin,
        "puerto_maquina": puerto_maquina,
        "busqueda": busqueda,
        "tipo_busqueda": tipo_busqueda,
        "cant_resultados": cant_resultados,
        "tamano_respuesta_bytes": tamano_respuesta_bytes,
        "edad": edad,
        "ranking": ranking
    }


agregar_entrada_log(PATH_LOG, crear_entrada_log("test", "test", datetime.now(), datetime.now()), COLUMNAS_LOG)
