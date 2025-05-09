import Pyro5.api
from log_server import LogServer

def main():
    # Proceso que escucha las solicitudes RMI en este nodo Servidor
    daemon = Pyro5.api.Daemon() 

    # Se registra LogServer como objeto remoto, para que pueda ser accedida desde otros programas.
    # La uri es la dirección única que permite localizar este objeto
    uri = daemon.register(LogServer)
    print(f"URI del objeto: {uri}")

    # Se conecta al nameserver (es como un DNS)
    ns = Pyro5.api.locate_ns(host = "localhost", port = 9090)
    # Se registra el objeto remoto como "logs.centralizados"
    ns.register("logs.centralizados", uri)

    print("Servidor de Logs RMI corriendo...")
    daemon.requestLoop()

if __name__ == "__main__":
    main()