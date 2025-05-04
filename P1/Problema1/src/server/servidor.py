from maestro import ServicioChat
import Pyro5.api

def main():
    daemon = Pyro5.api.Daemon(host="127.0.0.1", port=0)  # puerto dinámico
    chat_service = ServicioChat()  # Crear una instancia única de ServicioChat para evitar generar una instacia por conexion
    uri = daemon.register(chat_service)  # Registrar la instancia, no la clase

    ns = Pyro5.api.locate_ns(host="127.0.0.1", port=4002)  # igual que RMI
    ns.register("Chat", uri)

    print("Servidor escuchando... URI:", uri)
    daemon.requestLoop()

if __name__ == "__main__":
    main()