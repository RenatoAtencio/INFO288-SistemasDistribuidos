from dotenv import load_dotenv
import asyncio
import httpx
import os

load_dotenv(".env")

PROTOCOLO = os.getenv("PROTOCOLO")
HOST = os.getenv("HOST") 
HOSTPORT = int(os.getenv("HOSTPORT"))
CLIENTHOSTENDPOINT = os.getenv("CLIENTHOSTENDPOINT") 

URL = f"{PROTOCOLO}://{HOST}:{HOSTPORT}/{CLIENTHOSTENDPOINT}"

async def realizarBusqueda(edad: int, tipo_busqueda: int, busqueda: str):
    """
        Realiza la llamada a el maestro para realizar la busqueda
    """
    if tipo_busqueda == 1:
        t_bus = "titulo"
    elif tipo_busqueda == 2:
        t_bus = "tipo_doc"
    else:
        print("error en tipo de busqueda")
        exit(-1)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                URL,
                params={
                    "edad": edad,
                    "busqueda": busqueda, 
                    "tipo_busqueda": t_bus
                }
            )
            return imprimirResultados(response.json())
        except Exception as e:
            print("Error al realizar la búsqueda:", e)


def imprimirResultados(resultados):
    for i, elem in enumerate(resultados):
        print(f"{i}) Titulo: {elem["titulo"]}, Ranking: {elem["ranking"]}")


def mostrarOpciones(opciones):
    print("Ingrese su tipo de busqueda")
    for i in range(0, len(opciones)):
        print(f"{i+1}) Por {opciones[i]}")


def mostrarInputBusqueda(opcion):
    busqueda = ""

    if opcion == 1:
        busqueda = input("Ingrese su busqueda: ")
    elif opcion == 2:
        print("Ingrese sus opciones de tipo de documento, separado por una ',' o '_' si es una palabra compuesta")
        busqueda = ''.join((input("> ")).split())
    else:
        print("Opcion fuera de rango")
        exit(-1)

    
    return busqueda


if __name__ == "__main__":
    seguir = True 
    opciones = ["Titulo", "Tipo de documento"]
    
    while seguir:
        edad = -1
        while True:
            try:
                while (0 > edad):
                    edad = int(input("Ingrese su edad (mayor a 0): "))
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