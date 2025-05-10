# ¿Que resolverá el problema 2?
En el Problema 1, cada nodo esclavo genera su propio log de eventos. En esta etapa, utilizando una arquitectura cliente-servidor basada en RMI, se centralizan todos estos logs en un único archivo .log. Este archivo consolidado servirá como base para la generación de gráficos en el Problema 3.

## Estructuración de carpetas
- Client
    - `logs/`: Carpeta que almacena todos los logs generados por los esclavos en el Problema 1.
    - `memorias/`: Carpeta que guarda el número de la última línea enviada de cada log. Esto permite retomar el envío desde ese punto en caso de fallos o si se agregan nuevas líneas al log, evitando reenviar datos duplicados.
    - `client.py:` Script del cliente RMI encargado de enviar, línea por línea, el contenido del log esclavo al servidor RMI.
- Server
    - `log_server.py`: Define la clase LogServer, un objeto remoto expuesto que recibe líneas de logs desde los clientes y las guarda en un archivo centralizado
    - `main.py`:  Inicia el servidor RMI, registra el objeto LogServer en el NameServer de Pyro5 y queda a la espera de solicitudes remotas de los clientes.

## Antes de ejecutar, definir variables de entorno
- En la misma carpeta "Problema2" crear un .env que contenga:
    - `NAMESERVER_HOST=localhost`
    - `NAMESERVER_PORT=9090`
    - `NAMESERVER_OBJECT=logs.centralizados`
    - `MEMORIAS=memorias/memoria`
    - `LOG_HEADER=operacion,estado,t_ini,t_fin,puerto_maquina,busqueda,tipo_busqueda,cant_resultados,tamano_respuesta_bytes,edad,ranking,database`
    - `LOG_CENTRALIZADO=../log_centralizado.log`

- Instalar las dependencias:
    - Pyro5
    - python-dotenv

## Ejecucion (ejecutar pasos en el orden que aparece)
- En una terminal inicia el Name Server con el comando `python -m Pyro5.nameserver`
- En otra terminal inicia el servidor RMI
    - `cd server`
    - `python main.py`
- En tantas terminales como esclavos existan (también se puede hacer uno por uno) ejecuta cada cliente RMI
    - `cd client`
    - `python client.py`