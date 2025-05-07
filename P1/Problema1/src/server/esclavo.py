from fastapi import FastAPI, HTTPException
from uuid import uuid4
import uvicorn
import httpx
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import json
from typing import List

load_dotenv(".env")

puerto = int(os.getenv("SLAVEPORT"))
arr_databases = (os.getenv("SLAVEDB")).split(",")
API_BASE_URL = os.getenv("API_BASE_URL")

print(arr_databases)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/entry",
                params={
                    "puerto": puerto, 
                    "databases": arr_databases
                }
            )

            print("Respuesta del maestro:", response.json())
        except Exception as e:
            print("Error al conectar con el maestro:", e)

    yield  

    # Esto se ejecuta cuando se termina la ejecucion
    async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    f"{API_BASE_URL}/exit",
                    params={"puerto": puerto}
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

        for database in arr_databases:
            datos_database = recuperarDatabase(database)
            arr_coincidencias = []

            for elem in datos_database["datos"]:

                palabras_titulo = set(str(elem["titulo"]).split())
                palabras_busqueda = set(busqueda.split())

                coincidencias = palabras_titulo & palabras_busqueda
                conteo = len(coincidencias)

                if conteo > 0:

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

        for database in arr_databases:

            if database == busqueda:
                datos_database = recuperarDatabase(database)
                arr_coincidencias = []

                for elem in datos_database["datos"]:
                    palabras_titulo = set(str(elem["titulo"]).split())
                    palabras_busqueda = set(busqueda.split())

                    coincidencias = palabras_titulo & palabras_busqueda
                    conteo = len(coincidencias)

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
        return "None"

if __name__ == "__main__":
    uvicorn.run("esclavo:app", host="localhost", port=puerto, reload=True)
