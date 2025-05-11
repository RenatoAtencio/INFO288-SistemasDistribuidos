# 📘 Proyecto: Sistema de Búsqueda Distribuida

## 🔧 Dependencias

Asegúrate de tener instaladas las siguientes dependencias:

    fastapi
    uvicorn
    httpx
    python-dotenv
    pydantic
    uuid

---

## ⚙️ Archivos de configuración `.env`

### 📁 `client/.env`

    PROTOCOLO=http
    HOST=localhost
    HOSTPORT=5000

    CLIENTHOSTENDPOINT=query

### 📁 `server/.env`

    PROTOCOLO=http
    HOST=localhost
    HOSTPORT=5000

    SLAVEPORT=8003
    SLAVEDB=misterio,fantasia

    RELOAD=0

    CLIENTHOSTENDPOINT=query
    HOSTSLAVEENDPOINT=query

    HOSTENTRYPOINT=entry
    HOSTEXITPOINT=exit

    LOGDIRECTORY=log
    LOGCOLUMNS=operacion,estado,t_ini,t_fin,puerto_maquina,busqueda,tipo_busqueda,cant_resultados,tamano_respuesta_bytes,edad,ranking,database

    PESOTITULO=0.45
    PESOPREFERENCIAS=0.55

---

## ▶️ Cómo ejecutar el sistema

### 1. Ejecutar el servidor

Ubícate en el directorio `/server`:

    > cd server

Primero, levanta el **maestro**:

    > python maestro.py

Luego, en otra terminal, levanta uno o más **esclavos**:

    > python esclavo.py

> 🔁 **Importante:** Cada vez que levantes un esclavo, asegúrate de modificar en el archivo `.env`:
>
> * El valor de `SLAVEPORT` (puerto distinto para cada esclavo)
> * El valor de `SLAVEDB` (temáticas o bases de datos distintas, separadas por coma)

---

### 2. Ejecutar el cliente

Ubícate en el directorio `/client`:

    > cd client
    > python cliente.py

Este programa te permitirá realizar búsquedas al maestro. Deberás seguir las instrucciones que aparecen por consola e ingresar:

* Edad del usuario
* Tipo de búsqueda
* Término de búsqueda