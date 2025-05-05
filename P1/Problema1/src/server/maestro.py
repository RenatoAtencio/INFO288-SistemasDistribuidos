from fastapi import FastAPI, HTTPException
import os
import uvicorn
from dotenv import load_dotenv

app = FastAPI(title="Nodo Maestro")
distribucion = []

@app.get("/status")
def read_root():
    return {"message": "Nodo Maestro funcionando"}


@app.get("/conections")
def read_root():
    return distribucion


@app.get("/query")
def busqueda(type: str, busqueda: str):

    if type == "tipo_doc":
        for nodo in distribucion:
            if nodo["db_tipo_doc"] == type:
                # Buscar en el nodo especifico
                return {"response": "búsqueda por tipo_doc"}

    elif type == "titulo":
        for nodo in distribucion:
            # Duscar en todos los nodos
            print(f"búsqueda título: {busqueda}")

    return {"type": type, "busqueda": busqueda}


@app.post("/entry")
def ingresoEsclavo(puerto: int, db: str):

    for nodo in distribucion:
        if nodo["puerto"] == puerto:
            return {"response": "puerto tomado"}

    distribucion.append({
        "puerto": puerto,
        "db_tipo_doc": db,
    })

    return{
        "response": "conexion exitosa"
    }


@app.delete("/exit")
def salidaEsclavo(puerto: int):
    
    for nodo in distribucion:
        if nodo["puerto"] == puerto:
            distribucion.remove(nodo)
            break

    return{
        "response": "desconexion exitosa"
    }

if __name__ == "__main__":

    load_dotenv(".env")

    puerto = int(os.getenv("HOSTPORT"))
    url = os.getenv("URL")

    uvicorn.run("maestro:app", host='localhost', port=puerto, reload=True)