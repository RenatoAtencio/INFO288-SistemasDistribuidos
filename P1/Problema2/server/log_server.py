import Pyro5.api
import os
from dotenv import load_dotenv
load_dotenv("../.env")

HEADER = os.getenv("LOG_HEADER")
LOG_CENTRAL = os.getenv("LOG_CENTRALIZADO")


# Se declara LogServer como expuesto a llamadas remotas
@Pyro5.api.expose
class LogServer:
    def __init__(self):
        self.lineas_recibidas = 0
        self.log_file = LOG_CENTRAL
        # TODO - Cambiar el encabezado según lo que ponga el renato en los logs
        self.encabezado = HEADER

        # Crear el archivo si no existe, con encabezado
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write(self.encabezado + "\n")

    def recibir_linea_log(self, linea: str):
        if linea.strip() == self.encabezado:
            print("Encabezado del log omitido.")
            return
        
        self.lineas_recibidas += 1
        print(f"[{self.lineas_recibidas}] Línea recibida: {linea.strip()}")
        with open(self.log_file, "a") as f:
            f.write(linea.strip() + "\n")
