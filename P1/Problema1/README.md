Como ejecutar:

En /server
    > python maestro.py -> esto levanta el maestro 
    > python esclavo.py -> esto levanta el esclavo, asegurarse de cambiar el puerto y las database que toma en el .env cada vez que se levanta un esclavo

En /client
    > python cliente.py -> esto ejecuta un programa el cual permite realizar la busqueda al maestro, se debe indicar edad, tipo de busqueda y la busqueda. Se deben seguir los pasos indicados en la consola

Dependencias
    fastapi
    uvicorn
    httpx
    python-dotenv
    pydantic
    uuid
