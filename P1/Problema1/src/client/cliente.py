import httpx
import asyncio
from dotenv import load_dotenv

API_BASE_URL = "http://localhost:5000"

async def realizarBusqueda(type: str, busqueda: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE_URL}/query",
                params={"busqueda": busqueda, "type": type}
            )
            print("Respuesta del maestro:", response.json())
        except Exception as e:
            print("Error al realizar la búsqueda:", e)

if __name__ == "__main__":
    tipo = input("Ingrese su tipo de búsqueda (Titulo o TipoDoc): ")
    busqueda = input("Ingrese su búsqueda: ")

    asyncio.run(realizarBusqueda(tipo, busqueda))