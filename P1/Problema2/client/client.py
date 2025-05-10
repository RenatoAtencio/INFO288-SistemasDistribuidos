import Pyro5.api
import os
from dotenv import load_dotenv
load_dotenv("../.env")


HOST = os.getenv("NAMESERVER_HOST")
PORT = int(os.getenv("NAMESERVER_PORT"))
OBJ = os.getenv("NAMESERVER_OBJECT")
MEMORIA = os.getenv("MEMORIAS")

def enviar_logs(ruta_log):
    try:
        ns = Pyro5.api.locate_ns(host = HOST, port = PORT)
        uri = ns.lookup(OBJ)
        servidor = Pyro5.api.Proxy(uri)

        # Crear archivo de memoria para este log
        memoria_path = f"{MEMORIA}_{os.path.basename(ruta_log)}.txt"
        ultima_linea_enviada = 0

        if os.path.exists(memoria_path):
            with open(memoria_path, "r") as f:
                ultima_linea_enviada = int(f.read().strip() or 0)

        with open(ruta_log, "r") as archivo:
            lineas = archivo.readlines()
        
        # Cortar ejecución si el log ya fue enviado
        total_lineas = len(lineas)
        if ultima_linea_enviada >= total_lineas:
            print("Este log ya ha sido enviado completamente.")
            return
                
        # Enviar líneas restantes
        for i in range (ultima_linea_enviada, total_lineas):
            servidor.recibir_linea_log(lineas[i])
            # Actualizar memoria
            with open(memoria_path, "w") as f:
                f.write(str(i+1))
        
        print("Log enviado correctamente hasta el final")
    
    except Exception as e:
        print(f"Error al enviar logs: {e}")

if __name__ == "__main__":
    while True:
        ruta = input("\nIngrese la ruta del log que desea enviar al servidor: ")
        if os.path.isfile(ruta):
            break
        else:
            print("La ruta ingresada no existe. Intente nuevamente")
    
    while True:
        enviar_logs(ruta)
        continuar = input("\n¿Desea volver a enviar el log? (s/n): ").strip().lower()
        if continuar != "s":
            print("Cerrando cliente ...\n")
            break