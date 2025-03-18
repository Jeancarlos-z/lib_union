import flet as ft
import pyodbc
from config import get_connection  # Asegúrate de tener este módulo configurado

def gestionar_ventas(page: ft.Page):
    # =============================
    # Variables Globales del Móduloo
    # =============================
    sale_items = []       # Lista de productos agregados a la venta
    total_cost = 0.0      # Costo total acumulado
    product_info = {}     # Diccionario con la información del producto seleccionado

    # =============================
    # Mensajes de Error (Cajas de mensaje)
    # =============================
    msg_buscar = ft.Text(value="", color=ft.colors.RED)
    msg_agregar = ft.Text(value="", color=ft.colors.RED)
    msg_finalizar = ft.Text(value="", color=ft.colors.RED)

    # =============================
    # Sección de Búsqueda de Producto
    # =============================
    txt_codigo = ft.TextField(label="Código", width=150)
    txt_nombre = ft.TextField(label="Nombre", width=150)
    btn_buscar = ft.ElevatedButton(text="Buscar")

    # =============================
    # Sección de Detalles del Producto
    # =============================
    txt_descripcion = ft.TextField(label="Descripción", width=300, read_only=True)
    txt_marca = ft.TextField(label="Marca", width=150, read_only=True)
    txt_costo = ft.TextField(label="Costo", width=100, read_only=True)
    txt_stock = ft.TextField(label="Stock", width=100, read_only=True)

    # =============================
    # Sección para Ingresar Cantidad y Agregar Producto
    # =============================
    txt_cantidad = ft.TextField(label="Cantidad", width=100)
    btn_agregar = ft.ElevatedButton(text="Añadir")

    # =============================
    # Tabla de Venta: Muestra productos agregados (Nombre, Cantidad, Costo Total)
    # =============================
    sale_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Cantidad")),
            ft.DataColumn(ft.Text("Costo Total")),
        ],
        rows=[],
        heading_row_color=ft.colors.BLUE_100,
    )

    # =============================
    # Sección de Totales y Finalización de Venta
    # =============================
    txt_total = ft.Text(value="Total: 0.00", size=20, weight="bold")
    btn_finalizar = ft.ElevatedButton(text="Finalizar Venta", bgcolor=ft.colors.GREEN)

    # =============================
    # Función: Buscar Producto en la BD
    # =============================
    def buscar_producto(e):
        nonlocal product_info
        msg_buscar.value = ""  # Limpiar mensaje previo
        codigo = txt_codigo.value.strip()
        nombre = txt_nombre.value.strip()
        # Verificar que se haya ingresado código o nombre
        if not codigo and not nombre:
            msg_buscar.value = "Escriba el código o el nombre del producto"
            page.update()
            return

        conn = get_connection()
        cursor = conn.cursor()
        # Buscar por código o por nombre (búsqueda parcial con LIKE)
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
            # Guardar la información del producto encontrado
            product_info = {"id": pid, "descripcion": desc, "marca": marca, "pVenta": costo, "stock": stock}
            txt_descripcion.value = desc
            txt_marca.value = marca
            txt_costo.value = f"{costo:.2f}"
            txt_stock.value = str(stock)
            msg_buscar.value = ""  # Limpiar mensaje
        else:
            msg_buscar.value = "No existe el producto"
        cursor.close()
        conn.close()
        page.update()

    btn_buscar.on_click = buscar_producto

    # =============================
    # Función: Agregar Producto a la Venta
    # =============================
    def agregar_producto(e):
        nonlocal total_cost
        msg_agregar.value = ""
        if not product_info or txt_cantidad.value.strip() == "":
            msg_agregar.value = "Complete los espacios en blanco"
            page.update()
            return
        try:
            cantidad = int(txt_cantidad.value)
        except ValueError:
            msg_agregar.value = "Ingrese una cantidad válida"
            page.update()
            return

        # Validar que la cantidad no exceda el stock disponible
        if cantidad > product_info.get("stock", 0):
            msg_agregar.value = "Cantidad supera el stock disponible"
            page.update()
            return

        costo_unit = product_info.get("pVenta", 0)
        costo_total_producto = costo_unit * cantidad

        # Agregar producto a la venta (lista y tabla)
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

        # Actualizar stock mostrado (sin modificar la BD hasta finalizar la venta)
        product_info["stock"] -= cantidad
        txt_stock.value = str(product_info["stock"])
        txt_cantidad.value = ""
        msg_agregar.value = ""
        page.update()

    btn_agregar.on_click = agregar_producto

    # =============================
    # Función: Finalizar Venta y Actualizar BD
    # =============================
    def finalizar_venta(e):
        msg_finalizar.value = ""
        if not sale_items:
            msg_finalizar.value = "Llene productos en la tabla"
            page.update()
            return

        conn = get_connection()
        cursor = conn.cursor()
        # Insertar la venta y obtener el ID generado
        cursor.execute("INSERT INTO VENTA (fechaVenta) VALUES (GETDATE()); SELECT SCOPE_IDENTITY();")
        sale_id = cursor.fetchone()[0]

        # Procesar cada producto en la venta
        for item in sale_items:
            # Actualizar stock en la tabla PRODUCTO
            cursor.execute(
                "UPDATE PRODUCTO SET stock = stock - ? WHERE idProducto = ?",
                item["cantidad"], item["id"]
            )
            # Insertar el detalle de la venta
            cursor.execute(
                "INSERT INTO DETALLE_VENTA (idVenta, idProducto, cantidad, pUnidad) VALUES (?, ?, ?, ?)",
                sale_id, item["id"], item["cantidad"], item["costo_total"] / item["cantidad"]
            )

        conn.commit()
        cursor.close()
        conn.close()

        msg_finalizar.value = "Venta finalizada y stock actualizado"
        sale_items.clear()
        sale_table.rows.clear()
        nonlocal total_cost
        total_cost = 0.0
        txt_total.value = "Total: 0.00"
        page.update()

    btn_finalizar.on_click = finalizar_venta

    # =============================
    # Función: Volver a la Ventana Principal (Importación perezosa)
    # =============================
    def volver(e):
        from main import main  # Importación dentro de la función para evitar circularidad
        page.controls.clear()  # Limpiar la página actual
        main(page)            # Mostrar la ventana principal
        page.update()
    btn_volver = ft.ElevatedButton(text="Volver", on_click=volver, bgcolor=ft.colors.AMBER)

    # =============================
    # Layout de la Interfaz
    # =============================
    # Sección Header con título y botón "Volver" en la esquina superior derecha
    header_section = ft.Row(
        [
            ft.Text("Módulo de Ventas", size=28, weight="bold", color=ft.colors.BLUE_900),
            btn_volver,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        width=800,
    )

    # Sección de Búsqueda: Agrupa el mensaje y los campos para buscar el producto
    search_section = ft.Container(
        content=ft.Column(
            [
                msg_buscar,
                ft.Row(
                    [txt_codigo, txt_nombre, btn_buscar],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10,
                )
            ],
            spacing=5
        ),
        padding=10,
        bgcolor=ft.colors.BLUE_50,
        border_radius=5,
        width=800,
    )

    # Sección de Detalles: Muestra la información del producto seleccionado
    details_section = ft.Container(
        content=ft.Row(
            [txt_descripcion, txt_marca, txt_costo, txt_stock],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        ),
        padding=10,
        bgcolor=ft.colors.BLUE_50,
        border_radius=5,
        width=800,
    )

    # Sección de Cantidad y Agregar: Mensaje y campos para ingresar la cantidad y agregar el producto
    quantity_section = ft.Container(
        content=ft.Column(
            [
                msg_agregar,
                ft.Row(
                    [txt_cantidad, btn_agregar],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10,
                )
            ],
            spacing=5
        ),
        padding=10,
        bgcolor=ft.colors.BLUE_50,
        border_radius=5,
        width=800,
    )

    # Sección de Finalización: Mensaje, total y botón para finalizar la venta
    finalize_section = ft.Container(
        content=ft.Column(
            [
                msg_finalizar,
                ft.Row(
                    [txt_total, btn_finalizar],
                    alignment=ft.MainAxisAlignment.END,
                    spacing=10,
                )
            ],
            spacing=5
        ),
        padding=10,
        bgcolor=ft.colors.GREEN_50,
        border_radius=5,
        width=800,
    )

    # Layout Principal: Agrupa todas las secciones verticalmente
    layout = ft.Column(
        [
            header_section,
            search_section,
            details_section,
            quantity_section,
            ft.Divider(),
            sale_table,
            finalize_section,
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        width=800,
    )

    # Actualizar la página
    page.controls.clear()
    page.add(layout)
    page.update()
