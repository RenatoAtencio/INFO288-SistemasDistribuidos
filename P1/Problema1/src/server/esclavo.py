from fastapi import FastAPI, HTTPException
from uuid import uuid4
import uvicorn
import httpx
from contextlib import asynccontextmanager

API_BASE_URL = "http://localhost:5000"  

puerto = 8000
nombre_db = "test"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código a ejecutar al inicio
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/entry",
                params={"puerto": puerto, "db": nombre_db}
            )
            print("Respuesta del maestro:", response.json())
        except Exception as e:
            print("Error al conectar con el maestro:", e)

    yield  # Aquí se ejecuta la aplicación

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

@app.get("/query")
def busqueda(type: str, busqueda: str):
    if type == "tipo_doc":
        print(f"búsqueda tipo_doc: {busqueda}")
    elif type == "titulo":
        print(f"búsqueda título: {busqueda}")
        
    return {"type": type, "busqueda": busqueda}

if __name__ == "__main__":

    uvicorn.run("esclavo:app", host="localhost", port=puerto, reload=True)
