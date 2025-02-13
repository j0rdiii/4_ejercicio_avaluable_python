from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from fastapi.openapi.utils import get_openapi

app = FastAPI()

class Producto(BaseModel):
    id: int = Field(..., gt=0, description="Identificador único del producto")
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del producto")
    precio: float = Field(..., gt=0, description="Precio del producto")
    categoria: str = Field(..., min_length=1, max_length=50, description="Categoria del producto")

productos: List[Producto] = []
ventas_totales: float = 0.0

@app.post("/productos", response_model=dict)
def agregar_producto(producto: Producto):
    if any(p.id == producto.id for p in productos):
        raise HTTPException(status_code=400, detail="Producto existente")
    productos.append(producto)
    return {"mensaje": "Producto agregado correctamente"}

@app.get("/productos", response_model=List[Producto])
def obtener_productos():
    return productos

@app.get("/productos/{id}", response_model=Producto)
def obtener_producto(id: int):
    for producto in productos:
        if producto.id == id:
            return producto
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@app.put("/productos/{id}", response_model=dict)
def modificar_producto(id: int, datos: Producto):
    for i, producto in enumerate(productos):
        if producto.id == id:
            productos[i] = datos
            return {"mensaje": "Producto modificado correctamente"}
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@app.delete("/productos/{id}", response_model=dict)
def eliminar_producto(id: int):
    global productos
    for producto in productos:
        if producto.id == id:
            productos.remove(producto)
            return {"mensaje": "Producto eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@app.delete("/productos/vender/{id}", response_model=dict)
def vender_producto(id: int):
    global ventas_totales
    for producto in productos:
        if producto.id == id:
            ventas_totales += producto.precio
            productos.remove(producto)
            return {"mensaje": "Producto vendido", "ventas_totales": ventas_totales}
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@app.get("/ventas", response_model=dict)
def consultar_beneficios():
    return {"beneficios_totales": ventas_totales}

@app.get("/openapi.json")
def get_open_api_endpoint():
    return get_openapi(title="API de Gestión de Productos", version="1.0", description= "API para gestionar un catálogo de productos", routes=app.routes)