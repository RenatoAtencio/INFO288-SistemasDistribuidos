# Antes de ejecutar, definir variables de entorno
- En la misma carpeta "Problema2" crear un .env que contenga:
    - `NAMESERVER_HOST=localhost`
    - `NAMESERVER_PORT=9090`
    - `NAMESERVER_OBJECT=logs.centralizados`
    - `MEMORIAS=memorias/memoria`
    - `LOG_HEADER=timestamp_ini,timestamp_fin,maquina,tipo_maquina,query,tiempo_ejecucion,score,rango_etario`
    - `LOG_CENTRALIZADO=../log_centralizado.log`

- Instalar las dependencias:
    - Pyro5
    - python-dotenv

# Ejecucion (ejecutar pasos en el orden que aparece)
- En una terminal inicia el Name Server con el comando `python -m Pyro5.nameserver`
- En otra terminal inicia el servidor RMI
    - `cd server`
    - `python main.py`
- En tantas terminales como esclavos existan (también se puede hacer uno por uno) ejecuta cada cliente RMI
    - `cd client`
    - `python cliente.py`