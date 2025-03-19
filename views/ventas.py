import flet as ft
import pyodbc
from config import get_connection  # Asegúrate de tener este módulo configurado

def gestionar_ventas(page: ft.Page, set_content):
    # Variables Globales
    sale_items = []  # Lista de productos agregados a la venta
    total_cost = 0.0  # Costo total acumulado
    product_info = {}  # Información del producto seleccionado

    # Mensajes de Error
    msg_buscar = ft.Text(value="", color=ft.colors.RED)
    msg_agregar = ft.Text(value="", color=ft.colors.RED)
    msg_finalizar = ft.Text(value="", color=ft.colors.RED)

    # Sección de Búsqueda de Producto
    txt_codigo = ft.TextField(label="Código", width=150)
    txt_nombre = ft.TextField(label="Nombre", width=150)
    btn_buscar = ft.ElevatedButton(text="Buscar")

    # Sección de Detalles del Producto
    txt_descripcion = ft.TextField(label="Descripción", width=300, read_only=True)
    txt_marca = ft.TextField(label="Marca", width=150, read_only=True)
    txt_costo = ft.TextField(label="Costo", width=100, read_only=True)
    txt_stock = ft.TextField(label="Stock", width=100, read_only=True)

    # Sección para Ingresar Cantidad y Agregar Producto
    txt_cantidad = ft.TextField(label="Cantidad", width=100)
    btn_agregar = ft.ElevatedButton(text="Añadir")

    # Tabla de Venta
    sale_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Cantidad")),
            ft.DataColumn(ft.Text("Costo Total")),
        ],
        rows=[],
        heading_row_color=ft.colors.BLUE_100,
    )

    # Sección de Totales y Finalización de Venta
    txt_total = ft.Text(value="Total: 0.00", size=20, weight="bold")
    btn_finalizar = ft.ElevatedButton(text="Finalizar Venta", bgcolor=ft.colors.GREEN)

    # Diseño de la Interfaz
    layout = ft.Column(
        [
            ft.Row([txt_codigo, txt_nombre, btn_buscar]),
            msg_buscar,
            ft.Row([txt_descripcion, txt_marca, txt_costo, txt_stock]),
            ft.Row([txt_cantidad, btn_agregar]),
            msg_agregar,
            sale_table,
            txt_total,
            ft.Row([btn_finalizar]),
            msg_finalizar,
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=10,
    )

    def buscar_producto(e):
        nonlocal product_info
        msg_buscar.value = ""  # Limpiar mensaje previo
        codigo = txt_codigo.value.strip()
        nombre = txt_nombre.value.strip()

        if not codigo and not nombre:
            msg_buscar.value = "Ingrese el código o el nombre del producto"
            page.update()
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            if codigo:
                query = "SELECT idProducto, descripcion, marca, pVenta, stock FROM PRODUCTO WHERE codBarra = ?"
                param = codigo
            else:
                query = "SELECT idProducto, descripcion, marca, pVenta, stock FROM PRODUCTO WHERE descripcion LIKE ?"
                param = f"%{nombre}%"

            cursor.execute(query, param)
            result = cursor.fetchone()
            if result:
                pid, desc, marca, costo, stock = result
                product_info = {"id": pid, "descripcion": desc, "marca": marca, "pVenta": costo, "stock": stock}
                txt_descripcion.value = desc
                txt_marca.value = marca
                txt_costo.value = f"{costo:.2f}"
                txt_stock.value = str(stock)
                msg_buscar.value = ""
            else:
                msg_buscar.value = "Producto no encontrado"
        except Exception as err:
            msg_buscar.value = f"Error: {err}"
        finally:
            cursor.close()
            conn.close()
        page.update()

    btn_buscar.on_click = buscar_producto

    def agregar_producto(e):
        nonlocal total_cost
        msg_agregar.value = ""
        if not product_info or not txt_cantidad.value.strip():
            msg_agregar.value = "Complete los espacios en blanco"
            page.update()
            return

        try:
            cantidad = int(txt_cantidad.value)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            msg_agregar.value = "Ingrese una cantidad válida"
            page.update()
            return

        if cantidad > product_info["stock"]:
            msg_agregar.value = "Cantidad supera el stock disponible"
            page.update()
            return

        costo_unit = product_info["pVenta"]
        costo_total_producto = costo_unit * cantidad

        sale_items.append({
            "id": product_info["id"],
            "nombre": product_info["descripcion"],
            "cantidad": cantidad,
            "costo_total": costo_total_producto
        })
        sale_table.rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(product_info["descripcion"])),
                    ft.DataCell(ft.Text(str(cantidad))),
                    ft.DataCell(ft.Text(f"{costo_total_producto:.2f}"))
                ]
            )
        )

        total_cost += costo_total_producto
        txt_total.value = f"Total: {total_cost:.2f}"
        product_info["stock"] -= cantidad
        txt_stock.value = str(product_info["stock"])
        txt_cantidad.value = ""
        msg_agregar.value = ""
        page.update()

    btn_agregar.on_click = agregar_producto

    set_content(layout)
