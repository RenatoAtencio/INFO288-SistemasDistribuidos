from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import uvicorn
import os
import json
import re
import httpx

load_dotenv(".env")

SLAVEPORT = int(os.getenv("SLAVEPORT"))
SLAVEDB = (os.getenv("SLAVEDB")).split(",")
HOST = os.getenv("HOST") 
PROTOCOLO = os.getenv("PROTOCOLO")
HOSTPORT = int(os.getenv("HOSTPORT"))
HOSTENTRYPOINT = os.getenv("HOSTENTRYPOINT")
HOSTEXITPOINT = os.getenv("HOSTEXITPOINT")
RELOAD=bool(int(os.getenv("RELOAD")))

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient() as client:
        entry_url = f"{PROTOCOLO}://{HOST}:{HOSTPORT}/{HOSTENTRYPOINT}"
        try:
            response = await client.post(
                entry_url,
                params={
                    "puerto": SLAVEPORT, 
                    "databases": SLAVEDB
                }
            )

            r = response.json()
            print("Respuesta del maestro:", r)

            if r["status"] != "success":
                raise SystemExit(f"[ERROR] {r['msg']}")  # <--- esto detendrá todo

        except Exception as e:
            print("Error al conectar con el maestro:", e)
            raise SystemExit("[ERROR] No se pudo registrar con el maestro")

    yield  

    # Esto se ejecuta cuando se termina la ejecucion
    async with httpx.AsyncClient() as client:
            exit_url = f"{PROTOCOLO}://{HOST}:{HOSTPORT}/{HOSTEXITPOINT}"
            try:
                response = await client.delete(
                    exit_url,
                    params={"puerto": SLAVEPORT}
                )
                print("Respuesta del maestro (exit):", response.json())
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

@app.get("/query")
def busqueda(busqueda: str, tipo_busqueda: int):
    if tipo_busqueda == 1:  # Por titulo
        rsp = []
        for database in SLAVEDB:
            datos_database = recuperarDatabase(database)
            arr_coincidencias = []

            for elem in datos_database["datos"]:
                palabras_titulo = set( re.sub(r'[^A-Za-z0-9\s]+', '', str(elem["titulo"]).lower()).split() )
                palabras_busqueda = set( re.sub(r'[^A-Za-z0-9\s]+', '', busqueda.lower()).split() )

                coincidencias = palabras_titulo & palabras_busqueda
                conteo = len(coincidencias) + 1

                if conteo > 1:
                    print(f"Se encontro coincidencia para {busqueda}")
                    arr_coincidencias.append({
                        "titulo" : elem["titulo"],
                        "value": conteo
                    })

            if len(arr_coincidencias) > 0:
                rsp.append({
                    "database": database,
                    "coincidencias": arr_coincidencias 
                })
        return(rsp)
    elif tipo_busqueda == 2: # Por tipo de documento
        rsp = []
        for database in SLAVEDB:
            if database == busqueda:
                datos_database = recuperarDatabase(database)
                arr_coincidencias = []

                for elem in datos_database["datos"]:
                    palabras_titulo = set( re.sub(r'[^A-Za-z0-9\s]+', '', str(elem["titulo"]).lower()).split() )
                    palabras_busqueda = set( re.sub(r'[^A-Za-z0-9\s]+', '', busqueda.lower()).split() )
                    coincidencias = palabras_titulo & palabras_busqueda
                    conteo = len(coincidencias) + 1

                    arr_coincidencias.append({
                        "titulo" : elem["titulo"],
                        "value": conteo
                    })

                rsp.append({
                    "database": database,
                    "coincidencias": arr_coincidencias 
                })

                return(rsp)
    else:
        return {"error" : "Tipo de busqueda no definido"}

if __name__ == "__main__":
    try:
        uvicorn.run("esclavo:app", host=HOST, port=SLAVEPORT, reload=RELOAD)
    except SystemExit as e:
        print(e)