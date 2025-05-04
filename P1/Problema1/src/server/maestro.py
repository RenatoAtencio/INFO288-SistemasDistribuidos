import Pyro5.api

@Pyro5.api.expose
class ServicioChat:
    def __init__(self):
        self.clientes = []

    def alta(self, cliente_uri, apodo):
        print("Cliente conectado:", cliente_uri)
        cliente_proxy = Pyro5.api.Proxy(cliente_uri)  # Crear un proxy para el cliente
        self.clientes.append(cliente_proxy)
        print(f"CLIENTES: {len(self.clientes)} conectados")
        
    def baja(self, cliente_uri, apodo):
        self.clientes = [c for c in self.clientes if c._pyroUri != cliente_uri]
        print(f"Cliente desconectado: {apodo} | {len(self.clientes)} clientes restantes")

    def envio(self, esc_uri, apodo, mensaje):
        try:
            print(f"Procesando búsqueda de {apodo}: {mensaje}")
            with Pyro5.api.Proxy(esc_uri) as cliente_proxy:
                cliente_proxy._pyroTimeout = 8

                respuesta = "resultados"  # Aquí podrías integrar una búsqueda real

                cliente_proxy.notificacion("Servidor",f"Resultado para '{mensaje}': {respuesta}")
        except Pyro5.errors.TimeoutError:
            print(f"Tiempo de espera agotado para {esc_uri}")
        except Exception as e:
            print(f"Error respondiendo a {esc_uri}: {e}")
