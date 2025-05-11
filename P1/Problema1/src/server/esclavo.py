from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from datetime import datetime
import uvicorn
import os
import json
import re
import httpx
import csv
import sys
import unicodedata

load_dotenv(".env")

SLAVEPORT = int(os.getenv("SLAVEPORT"))
SLAVEDB = (os.getenv("SLAVEDB")).split(",")

HOST = os.getenv("HOST") 
PROTOCOLO = os.getenv("PROTOCOLO")
HOSTPORT = int(os.getenv("HOSTPORT"))
HOSTENTRYPOINT = os.getenv("HOSTENTRYPOINT")
HOSTEXITPOINT = os.getenv("HOSTEXITPOINT")

RELOAD=bool(int(os.getenv("RELOAD")))

LOG_DIRECTORY = os.getenv("LOGDIRECTORY")
PATH_LOG=f"../../{LOG_DIRECTORY}/esclavo_{SLAVEPORT}.log"
COLUMNAS_LOG = (os.getenv("LOGCOLUMNS")).split(",")

peso_titulo = float(os.getenv("PESOTITULO"))  
peso_preferencias = float(os.getenv("PESOPREFERENCIAS"))  

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
    ranking: int | None = None,
    database: str | None = None
    ) -> dict:
    """
        Permite crear un diccionario para agregar al log, verificando los tipos de datos.
    """

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
        "ranking": ranking,
        "database": database
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    conected = False
    async with httpx.AsyncClient() as client:
        entry_url = f"{PROTOCOLO}://{HOST}:{HOSTPORT}/{HOSTENTRYPOINT}"
        try:
            
            ini = datetime.now()
            response = await client.post(
                entry_url,
                params={
                    "puerto": SLAVEPORT, 
                    "databases": SLAVEDB
                }
            )
            fin = datetime.now()

            r = response.json()
            print("Respuesta del maestro:", r)

            if r["status"] != "success":
                raise SystemExit(f"[ERROR] {r['msg']}")  # <--- Detiene ejecucion cuando el puerto esta tomado

            conected = True
            agregar_entrada_log(
                PATH_LOG,
                crear_entrada_log(
                    operacion="conection_to_master",
                    estado="success",
                    t_ini=ini,
                    t_fin=fin,
                    puerto_maquina=SLAVEPORT
                ),
                COLUMNAS_LOG
            )

        except Exception as e:
            print("Error al conectar con el maestro:", e)
            raise SystemExit("[ERROR] No se pudo registrar con el maestro")

    yield  

    # Esto se ejecuta cuando se termina la ejecucion
    async with httpx.AsyncClient() as client:
            exit_url = f"{PROTOCOLO}://{HOST}:{HOSTPORT}/{HOSTEXITPOINT}"
            try:

                ini = datetime.now()
                response = await client.delete(
                    exit_url,
                    params={
                        "puerto": SLAVEPORT,
                        "conected": conected 
                    }
                )
                fin = datetime.now()
                print("Respuesta del maestro (exit):", response.json())

                agregar_entrada_log(
                    PATH_LOG,
                    crear_entrada_log(
                        operacion="disconect_from_master",
                        estado="success",
                        t_ini=ini,
                        t_fin=fin,
                        puerto_maquina=SLAVEPORT
                    ),
                    COLUMNAS_LOG
                )

            except Exception as e:
                print("Error al notificar cierre al maestro:", e)



app = FastAPI(title="Nodo esclavo", lifespan=lifespan)

def recuperarDatabase(nombre_db):
    ruta_db = os.path.join("..", "..", "databases", nombre_db + ".json")
    
    try:
        with open(ruta_db, "r", encoding="utf-8") as f:
            contenido = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Base de datos no encontrada")
    
    f.close()
    return contenido


def quitar_tildes(texto: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def obtenerSet(sentencia: str):
    stopwords = {
        'el', 'la', 'los', 'las', 'un', 'una', 
        'y', 'o', 'de', 'que', 'en', 'a', 'por', 
        'con', 'para', 'es', 'al', 'del'}
    
    sentencia = quitar_tildes(sentencia.lower())
    palabras = re.sub(r'[^A-Za-z0-9\s]+', '', sentencia.lower()).split()
    sentenciaSet = set(palabra for palabra in palabras if palabra not in stopwords)
    return sentenciaSet

def compararABusqueda(busqueda, titulo):
    set1 = obtenerSet(busqueda)
    set2 = obtenerSet(titulo)

    interseccion = set1 & set2
    coincidencias = len(interseccion)
    coincidencias_norm = coincidencias/len(set2)
    return [coincidencias, coincidencias_norm]

@app.get("/query")
def busqueda(busqueda: str, tipo_busqueda: str, edad: int):
    preferencias = {
        # col =            0-14, 15-29, 30-54, >55
        "ciencia_ficcion":  [8.5, 9.0, 7.5, 3.0],
        "aventura":         [9.0, 8.5, 6.7, 5.0],
        "romance":          [6.0, 8.5, 7.5, 5.5],
        "historia":         [3.0, 4.5, 6.7, 9.0],
        "biografia":        [2.0, 3.3, 6.5, 9.5],
        "misterio":         [6.5, 9.5, 8.0, 6.0],
        "fantasia":         [9.5, 9.8, 6.5, 4.0],
        "autoayuda":        [1.4, 6.9, 8.5, 5.3],
        "poesia":           [3.5, 5.0, 6.0, 7.5],
        "tecnologia":       [6.3, 9.5, 8.0, 5.0],
    }   
    rsp = []

    if 0 <= edad <= 14:
        index = 0
    elif 15 <= edad <= 29:
        index = 1
    elif 30 <= edad <= 54:
        index = 2
    else:
        index = 3

    ini1 = datetime.now()

    if tipo_busqueda == "titulo":      # Busqueda por titulo (Implica buscar en todas las databases)
        for database in SLAVEDB:
            datos_database = recuperarDatabase(database)
            arr_coincidencias = []

            for elem in datos_database["datos"]:    # Recorre los elementos de la db
                ini = datetime.now()
                coincidencias, coincidencias_norm = compararABusqueda(busqueda, str(elem["titulo"]))   
                ranking = round(peso_titulo * coincidencias_norm + peso_preferencias * preferencias[database][index], 3)

                if coincidencias >= 1:
                    arr_coincidencias.append({
                        "titulo" : elem["titulo"],
                        "ranking": ranking,
                    })

                    fin = datetime.now()

                    agregar_entrada_log(
                        PATH_LOG,
                        crear_entrada_log(
                            operacion="busqueda en db",
                            estado="success",
                            t_ini=ini,
                            t_fin=fin,
                            puerto_maquina=SLAVEPORT,
                            busqueda=busqueda,
                            tipo_busqueda=tipo_busqueda,
                            edad=edad,
                            ranking=ranking,
                            database=database
                        ),
                        COLUMNAS_LOG
                    )

            if len(arr_coincidencias) > 0:          # Evitar agregar un [] si no se encontro ningun titulo similar en la db
                rsp.append({
                    "database": database,
                    "respuestas": arr_coincidencias 
                })

    elif tipo_busqueda == "tipo_doc":    # Por tipo de documento (Implica devolver todos los elem de la db especifica)
        for database in SLAVEDB:
            
            if database == busqueda:
                datos_database = recuperarDatabase(database)
                arr_coincidencias = []

                for elem in datos_database["datos"]:
                    ini = datetime.now()
                    coincidencias, coincidencias_norm = compararABusqueda(busqueda, str(elem["titulo"]))
                    ranking = round((peso_titulo * coincidencias_norm) + (peso_preferencias * preferencias[database][index]) * float(elem["popularidad"]),3)

                    arr_coincidencias.append({
                        "titulo" : elem["titulo"],
                        "ranking": ranking,
                    })

                    fin = datetime.now()

                    agregar_entrada_log(
                        PATH_LOG,
                        crear_entrada_log(
                            operacion="busqueda en db",
                            estado="success",
                            t_ini=ini,
                            t_fin=fin,
                            puerto_maquina=SLAVEPORT,
                            busqueda=busqueda,
                            tipo_busqueda=tipo_busqueda,
                            edad=edad,
                            ranking=ranking,
                            database=database
                        ),
                        COLUMNAS_LOG
                    )

                rsp.append({
                    "database": database,
                    "respuestas": arr_coincidencias 
                })

                break
    else:
        return {"error" : "Tipo de busqueda no definido"}

    cant = 0
    for e in rsp:
        cant += len(e["respuestas"])

    fin1 = datetime.now()
    agregar_entrada_log(
        PATH_LOG,
        crear_entrada_log(
            operacion="mandar_resultados_a_master",
            estado="success",
            t_ini=ini1,
            t_fin=fin1,
            puerto_maquina=SLAVEPORT,
            busqueda=busqueda,
            tipo_busqueda=tipo_busqueda,
            cant_resultados=cant,
            tamano_respuesta_bytes=sys.getsizeof(rsp),
            edad=edad
        ),
        COLUMNAS_LOG
    )
    
    return rsp
    
if __name__ == "__main__":
    try:
        verificar_log(PATH_LOG, COLUMNAS_LOG)
        uvicorn.run("esclavo:app", host=HOST, port=SLAVEPORT, reload=RELOAD)
    except SystemExit as e:
        print(e)    