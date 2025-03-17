import flet as ft
import config  # Importamos la conexión desde config.py

def gestionar_productos(page: ft.Page):
    page.title = "Gestión de Productos"

    # Campos de búsqueda y resultados
    txt_busqueda = ft.TextField(label="Buscar producto", on_change=lambda e: buscar_producto(e, txt_busqueda, txt_stock, txt_marca, txt_pVenta))
    txt_stock = ft.TextField(label="Stock", disabled=True)
    txt_marca = ft.TextField(label="Marca", disabled=True)
    txt_pVenta = ft.TextField(label="Precio de Venta", disabled=True)

    # Botón para volver al menú
    btn_volver = ft.ElevatedButton("Volver al Menú", on_click=lambda e: page.go("/"))

    # Contenedor principal
    page.add(
        ft.Column([
            txt_busqueda,
            txt_stock,
            txt_marca,
            txt_pVenta,
            btn_volver
        ])
    )

def buscar_producto(evento, txt_busqueda, txt_stock, txt_marca, txt_pVenta):
    descripcion = txt_busqueda.value.strip()
    if not descripcion:
        return  # Si no hay búsqueda, no hacer nada

    conn = config.get_connection()  # Usamos la conexión desde config.py
    cursor = conn.cursor()

    query = "SELECT stock, marca, pVenta FROM PRODUCTO WHERE descripcion LIKE ?"
    cursor.execute(query, f"%{descripcion}%")
    resultado = cursor.fetchone()

    if resultado:
        stock, marca, pVenta = resultado
        txt_stock.value = str(stock)
        txt_marca.value = marca
        txt_pVenta.value = f"S/. {pVenta}"

        evento.page.update()  # Refrescar la página para mostrar los cambios

    cursor.close()
    conn.close()
