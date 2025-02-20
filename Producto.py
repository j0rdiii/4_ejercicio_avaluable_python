from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from fastapi.openapi.utils import get_openapi

# Inicializo la aplicación FastAPI
app = FastAPI()

# Defino el modelo de datos para un producto
class Producto(BaseModel):
    id: int = Field(..., gt=0, description="Identificador único del producto")
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del producto")
    precio: float = Field(..., gt=0, description="Precio del producto")
    categoria: str = Field(..., min_length=1, max_length=50, description="Categoria del producto")

# Lista para almacenar productos y variable para ventas totales
productos: List[Producto] = []
ventas_totales: float = 0.0

# Endpoint para agregar un nuevo producto
@app.post("/productos", response_model=dict)
def agregar_producto(producto: Producto):
    # Verifica si el producto ya existe
    if any(p.id == producto.id for p in productos):
        raise HTTPException(status_code=400, detail="Producto existente")
    productos.append(producto)
    return {"mensaje": "Producto agregado correctamente"}

# Endpoint para obtener la lista de productos
@app.get("/productos", response_model=List[Producto])
def obtener_productos():
    return productos

# Endpoint para obtener un producto por su ID
@app.get("/productos/{id}", response_model=Producto)
def obtener_producto(id: int):
    for producto in productos:
        if producto.id == id:
            return producto
    raise HTTPException(status_code=404, detail="Producto no encontrado")

# Endpoint para modificar un producto existente
@app.put("/productos/{id}", response_model=dict)
def modificar_producto(id: int, datos: Producto):
    for i, producto in enumerate(productos):
        if producto.id == id:
            productos[i] = datos # Reemplaza el producto con los nuevos datos
            return {"mensaje": "Producto modificado correctamente"}
    raise HTTPException(status_code=404, detail="Producto no encontrado")

# Endpoint para eliminar un producto por su ID
@app.delete("/productos/{id}", response_model=dict)
def eliminar_producto(id: int):
    global productos    # Indica que una variable dentro de una función se refiere a una variable que está fuera de la función en lugar de crear una nueva variable local.
    for producto in productos:
        if producto.id == id:
            productos.remove(producto)
            return {"mensaje": "Producto eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Producto no encontrado")

# Endpoint para vender un producto, eliminándolo del inventario y sumando al total de ventas
@app.delete("/productos/vender/{id}", response_model=dict)
def vender_producto(id: int):
    global ventas_totales
    for producto in productos:
        if producto.id == id:
            ventas_totales += producto.precio # Agrega el precio del producto a las ventas totales
            productos.remove(producto)
            return {"mensaje": "Producto vendido", "ventas_totales": ventas_totales}
    raise HTTPException(status_code=404, detail="Producto no encontrado")

# Endpoint para consultar los beneficios totales de las ventas
@app.get("/ventas", response_model=dict)
def consultar_beneficios():
    return {"beneficios_totales": ventas_totales}

# Endpoint para obtener la documentación OpenAPI en formato JSON
@app.get("/openapi.json")
def get_open_api_endpoint():
    return get_openapi(title="API de Gestión de Productos", version="1.0", description= "API para gestionar un catálogo de productos", routes=app.routes)