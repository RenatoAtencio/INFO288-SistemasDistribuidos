Dependencias
    fastapi
    uvicorn
    httpx
    python-dotenv
    pydantic
    uuid

client/.env
    PROTOCOLO=http
    HOST=localhost
    HOSTPORT=5000

    CLIENTHOSTENDPOINT=query

server/.env
    PROTOCOLO=http
    HOST=localhost
    HOSTPORT=5000

    SLAVEPORT=8001
    SLAVEDB=autoayuda,biografia

    RELOAD=0 

    CLIENTHOSTENDPOINT=query
    HOSTSLAVEENDPOINT=query

    HOSTENTRYPOINT=entry
    HOSTEXITPOINT=exit

Como ejecutar:

En /server
    > python maestro.py -> esto levanta el maestro 
    > python esclavo.py -> esto levanta el esclavo, asegurarse de cambiar el puerto y las database que toma en el .env cada vez que se levanta un esclavo

En /client
    > python cliente.py -> esto ejecuta un programa el cual permite realizar la busqueda al maestro, se debe indicar edad, tipo de busqueda y la busqueda. Se deben seguir los pasos indicados en la consola