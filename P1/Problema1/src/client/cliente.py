import httpx
import asyncio
from dotenv import load_dotenv

API_BASE_URL = "http://localhost:5000"

async def realizarBusqueda(edad: int, tipo_busqueda: int, busqueda: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE_URL}/query",
                params={
                    "edad": edad,
                    "busqueda": busqueda, 
                    "tipo_busqueda": tipo_busqueda
                }
            )
            return imprimirResultados(response.json())
        except Exception as e:
            print("Error al realizar la búsqueda:", e)


def imprimirResultados(resultados):
    for i, elem in enumerate(resultados):
        print(f"{i}) Titulo: {elem["titulo"]}, value: {elem["value"]}")


def mostrarOpciones(opciones):
    print("Ingrese su tipo de busqueda")
    for i in range(0, len(opciones)):
        print(f"{i+1}) Por {opciones[i]}")

def mostrarInputBusqueda(opcion):
    busqueda = ""

    if opcion == 1:
        busqueda = input("Ingrese su busqueda: ")
    elif opcion == 2:
        print(opcion)
        print("Ingrese sus opciones de tipo de documento, separado por una ',' o '_' si es una palabra compuesta")
        busqueda = input("> ")
    else:
        print("Opcion fuera de rango")
        exit(-1)
    
    return busqueda


if __name__ == "__main__":
    seguir = True 
    opciones = ["Titulo", "Tipo de documento"]
    
    while seguir:

        while True:
            try:
                edad = int(input("Ingrese su edad: "))
                break
            except Exception as e:
                print(f"Error: {e}")
                print("Ingrese un numero entero")

        mostrarOpciones(opciones)

        while True:
            try:
                tipoDeBusqueda = int(input("> "))
                if 1 <= tipoDeBusqueda <= len(opciones):
                    break
                else:
                    print(f"Ingrese un numero en el rango posible: [1, {len(opciones)}]")
            except Exception as e:
                print(f"Error: {e}")
                print(f"Ingrese un numero en el rango posible: [1, {len(opciones)}]")
            
        busqueda = mostrarInputBusqueda(tipoDeBusqueda)

        asyncio.run(realizarBusqueda(edad, tipoDeBusqueda, busqueda))

        opcionSeguir = input("Seguir? (s/n): ")

        if opcionSeguir.lower() != 's':
            seguir = False