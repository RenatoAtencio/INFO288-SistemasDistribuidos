from fastapi import FastAPI, HTTPException, Query
import os
import uvicorn
from dotenv import load_dotenv
import httpx
import asyncio
from typing import List, Annotated

app = FastAPI(title="Nodo Maestro")
distribucion = []

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

async def realizarBusqueda(port: int, busqueda: str, tipo_busqueda: int):
    """
        Realiza la llamada al esclavo
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"http://localhost:{port}/query",
                params={
                    "tipo_busqueda": tipo_busqueda,
                    "busqueda": busqueda
                }
            )
            return response.json()
        except Exception as e:
            return ("Error al realizar la busqueda en el esclavo:", e)


@app.get("/query")
def busqueda(edad: int, tipo_busqueda: int, busqueda: str):
    """
        Permite realizar las consultas a los esclavos

        Devuelve las respuestas ordenadas segun el ranking
    """


    if tipo_busqueda == 1: # Por titulo
        
        for nodo in distribucion:   # Broadcast
            print(f"Realizando busqueda en nodo: {nodo["puerto"]}")
            respuesta = asyncio.run(realizarBusqueda(nodo["puerto"], busqueda, tipo_busqueda))
            rsp = {
                "msg": f"respuesta del nodo {nodo["puerto"]}",
                "busqueda": busqueda,
                "respuesta" : respuesta # Tiene la database, y la lista de resultados-value
            }
        
        print(rsp)
            
    elif tipo_busqueda == 2: # Por tipo de documento
        respuestas = []
        arr_busqueda_por_tipo_doc = busqueda.split(',')

        for nodo in distribucion:
            for database in nodo["databases"]:
                for busqueda_tipo_doc in arr_busqueda_por_tipo_doc: # Multicast
                    
                    if busqueda_tipo_doc == database:
                        arr_busqueda_por_tipo_doc.remove(busqueda_tipo_doc)

                        print(f"Realizando busqueda en nodo: {nodo["puerto"]}")
                        rsp = asyncio.run(realizarBusqueda(nodo["puerto"], busqueda_tipo_doc, tipo_busqueda))
                        
                        respuestas.append({
                            "msg": f"respuesta del nodo {nodo["puerto"]}",
                            "busqueda": busqueda,
                            "respuesta" : rsp   # Tiene la database, y la lista de resultados-value
                        })

        
        print(respuestas)

    # Parcear las respuestas segun el ranking

    
    

@app.post("/entry")
def ingresoEsclavo(puerto: int, databases: Annotated[List[str] | None, Query()]):
    """
        Permite a un nodo ingresar a la distribucion
        
        Debe indicar su puerto(Int) y las Databases (string Arr) a las cuales que tiene acceso
    """

    for nodo in distribucion:
        if nodo["puerto"] == puerto:
            return {"response": "puerto tomado"}

    print(databases)

    distribucion.append({
        "puerto": puerto,
        "databases": databases,
    })

    return{"Respuesta": "conexion exitosa"}


@app.delete("/exit")
def salidaEsclavo(puerto: int):
    """
        Permite la salida de un esclavo de la distribucion 

        Necesita el puerto del esclavo (mismo puerto con el cual se conecto a la distribucion)
    """
    for nodo in distribucion:
        if nodo["puerto"] == puerto:
            distribucion.remove(nodo)
            break

    return{"respuesta": "desconexion exitosa"}

if __name__ == "__main__":

    load_dotenv(".env")
    puerto = int(os.getenv("HOSTPORT"))
    url = os.getenv("URL")

    uvicorn.run("maestro:app", host='localhost', port=puerto, reload=True)