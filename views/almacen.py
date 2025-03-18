import flet as ft
import config  # Importamos la conexión desde config.py

def gestionar_productos(page: ft.Page, set_content):
    page.title = "Gestión de Productos"

    # Campos de búsqueda y resultados
    txt_busqueda = ft.TextField(label="Buscar producto", on_change=lambda e: buscar_producto(e, txt_busqueda, txt_stock, txt_marca, txt_pVenta, img_producto))
    txt_stock = ft.TextField(label="Stock", disabled=True)
    txt_marca = ft.TextField(label="Marca", disabled=True)
    txt_pVenta = ft.TextField(label="Precio de Venta", disabled=True)
    img_producto = ft.Image(width=150, height=150)  # Imagen del producto

    # Botón para volver
    btn_volver = ft.ElevatedButton("Volver al Menú", on_click=lambda e: set_content("inicio"))

    # Contenedor con los campos de búsqueda
    contenedor_productos = ft.Column([
        txt_busqueda,
        txt_stock,
        txt_marca,
        txt_pVenta,
        img_producto, 
        btn_volver
    ])

    # ACTUALIZA SOLO EL CONTENIDO DINÁMICO DEL LAYOUT
    set_content(contenedor_productos)  

def buscar_producto(evento, txt_busqueda, txt_stock, txt_marca, txt_pVenta, img_producto):
    descripcion = txt_busqueda.value.strip()
    if not descripcion:
        return  # Si no hay búsqueda, no hacer nada

    conn = config.get_connection()  
    cursor = conn.cursor()

    query = "SELECT stock, marca, pVenta, imagen FROM PRODUCTO WHERE descripcion LIKE ?"
    cursor.execute(query, (f"%{descripcion}%",))
    resultado = cursor.fetchone()

    if resultado:
        stock, marca, pVenta, imagen = resultado
        txt_stock.value = str(stock)
        txt_marca.value = marca
        txt_pVenta.value = f"S/. {pVenta}"
        
        # Cargar imagen si existe
        img_producto.src = imagen if imagen else "ruta/imagen_default.png"

    cursor.close()
    conn.close()
    
    evento.page.update()  # Refrescar UI con los nuevos datos
