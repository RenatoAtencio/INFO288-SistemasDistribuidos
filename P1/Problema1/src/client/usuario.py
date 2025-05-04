import Pyro5.api

@Pyro5.api.expose
class Usuario:
    def __init__(self):
        self.apodo = ""  # Inicializarlo vacío, lo asignarás luego

    def notificacion(self, emisor, mensaje):
        print(f"\n[{emisor}] {mensaje}")
        print(f"{self.apodo}", end="", flush=True)