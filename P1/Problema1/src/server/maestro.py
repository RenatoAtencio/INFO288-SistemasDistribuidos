from fastapi import FastAPI, HTTPException, Query
from typing import List, Annotated
from dotenv import load_dotenv
import uvicorn
import asyncio
import httpx
import os

load_dotenv(".env")
app = FastAPI(title="Nodo Maestro")
distribucion = []

PROTOCOLO = os.getenv("PROTOCOLO")
HOST = os.getenv("HOST") 
HOSTPORT = int(os.getenv("HOSTPORT"))
HOSTSLAVEENDPOINT = os.getenv("HOSTSLAVEENDPOINT") 
RELOAD=bool(int(os.getenv("RELOAD")))

@app.get("/status")
def read_root():
    """
        Permite ver si el maestro esta funcionando
    """
    return {"msg": "Nodo Maestro funcionando"}


@app.get("/conections")
def read_root():
    """
        Permite obtener la distribucion, es decir, los esclavos conectados con sus respectivos 
        puertos y las databases asociadas
    """
    return {"ditribucion" : distribucion}

async def realizarBusqueda(port: int, busqueda: str, tipo_busqueda: str, edad:int):
    """
        Realiza la llamada al esclavo
    """
    url = f"{PROTOCOLO}://{HOST}:{port}/{HOSTSLAVEENDPOINT}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                params={
                    "tipo_busqueda": tipo_busqueda,
                    "busqueda": busqueda,
                    "edad": edad
                }
            )
            print(response.json())
            return response.json()
        except Exception as e:
            return ("Error al realizar la busqueda en el esclavo:", e)


@app.get("/query")
def busqueda(edad: int, tipo_busqueda: str, busqueda: str):
    """
        Permite realizar las consultas a los esclavos

        Devuelve las respuestas ordenadas segun el ranking
    """

    respuestas = []
    if tipo_busqueda == "titulo": # Por titulo
        for nodo in distribucion:   # Broadcast
            print(f"Realizando busqueda en nodo: {nodo["puerto"]}")
            rsp = asyncio.run(realizarBusqueda(nodo["puerto"], busqueda, tipo_busqueda, edad))
            respuestas.append({
                "msg": f"respuesta del nodo {nodo["puerto"]}",
                "busqueda": busqueda,
                "respuesta" : rsp # Tiene la database, y la lista de resultados-value
            })
        
    elif tipo_busqueda == "tipo_doc": # Por tipo de documento

        arr_busqueda_por_tipo_doc = busqueda.split(',')
        for nodo in distribucion:
            for database in nodo["databases"]:
                for busqueda_tipo_doc in arr_busqueda_por_tipo_doc: # Multicast
                    
                    if busqueda_tipo_doc == database:
                        arr_busqueda_por_tipo_doc.remove(busqueda_tipo_doc)

                        print(f"Realizando busqueda en nodo: {nodo["puerto"]}")
                        rsp = asyncio.run(realizarBusqueda(nodo["puerto"], busqueda_tipo_doc, tipo_busqueda, edad))
                        
                        respuestas.append({
                            "msg": f"respuesta del nodo {nodo["puerto"]}",
                            "busqueda": busqueda,
                            "respuesta" : rsp   # Tiene la database, y la lista de resultados-value
                        })

    resultados = []
    for respu in respuestas:
        for elem in respu["respuesta"]:
            for r in elem["respuestas"]:
                resultados.append(r)

    return sorted(resultados, key=lambda x: x["ranking"], reverse=True)
    
    

@app.post("/entry")
def ingresoEsclavo(puerto: int, databases: Annotated[List[str] | None, Query()]):
    """
        Permite a un nodo ingresar a la distribucion
        
        Debe indicar su puerto(Int) y las Databases (string Arr) a las cuales que tiene acceso
    """

    for nodo in distribucion:
        if nodo["puerto"] == puerto:
            return {
                "status": "error",
                "msg": "Puerto ocupado"
            }

    distribucion.append({
        "puerto": puerto,
        "databases": databases,
    })

    return{
        "status": "success",
        "msg": "Conectado al maestro"
    }


@app.delete("/exit")
def salidaEsclavo(puerto: int, conected: bool):
    """
        Permite la salida de un esclavo de la distribucion 

        Necesita el puerto del esclavo (mismo puerto con el cual se conecto a la distribucion)
    """
    if not conected:
        return{"respuesta": "No conectado anteriormente"}
    
    for nodo in distribucion:
        if nodo["puerto"] == puerto:
            distribucion.remove(nodo)
            break

    return{"respuesta": "desconexion exitosa"}

if __name__ == "__main__":
    puerto = int(os.getenv("HOSTPORT"))
    url = os.getenv("URL")

    uvicorn.run("maestro:app", host=HOST, port=puerto, reload=RELOAD)