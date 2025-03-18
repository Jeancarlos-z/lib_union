import flet as ft
import asyncio
from layout import crear_layout
import config  # Para la conexión a la BD

def main(page: ft.Page):
    # 📌 Función para la búsqueda de productos
    def buscar_producto(evento):
        descripcion = txt_busqueda.value.strip()
        if not descripcion:
            return  # No hacer nada si está vacío

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
            img_producto.src = imagen if imagen else "ruta/imagen_default.png"

        cursor.close()
        conn.close()
        
        page.update()  # Refrescar la UI

    # 📌 Buscador de productos en la vista de inicio
    txt_busqueda = ft.TextField(label="Buscar producto", on_change=buscar_producto)
    txt_stock = ft.TextField(label="Stock", disabled=True)
    txt_marca = ft.TextField(label="Marca", disabled=True)
    txt_pVenta = ft.TextField(label="Precio de Venta", disabled=True)
    img_producto = ft.Image(width=150, height=150)

    buscador = ft.Column([
        ft.Text("🏠 Bienvenido a la Librería", size=24, color="white"),
        txt_busqueda,
        txt_stock,
        txt_marca,
        txt_pVenta,
        img_producto
    ])

    # 📌 Pasamos el buscador a `crear_layout`
    layout, set_content = crear_layout(page, buscador)  
    page.add(layout)

    # 🔹 Mostrar el buscador en la vista de inicio
    set_content(buscador)

if __name__ == "__main__":
    asyncio.run(ft.app_async(target=main))
