from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from uuid import uuid4
import pandas as pd
import sys
import uvicorn

app = FastAPI(title="Nodo esclavo")

@app.get("/query")
def busqueda(type: str, busqueda: str):

    if type == "tipo_doc":
        print(f"búsqueda tipo_doc: {busqueda}")
    elif type == "titulo":
        print(f"búsqueda título: {busqueda}")
        
    return {"type": type, "busqueda": busqueda}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python nodo_esclavo.py <port> <db>")
        sys.exit(1)

    puerto = int(sys.argv[1])
    nombre_db = sys.argv[2]

    uvicorn.run("esclavo:app", host='localhost', port=puerto, reload=True)