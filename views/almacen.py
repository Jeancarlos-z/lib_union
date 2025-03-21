import flet as ft
import config  # Para la conexión a la BD
import datetime

def gestionar_productos(page: ft.Page, set_content):
    page.title = "Gestión de Productos"

    # Campo de búsqueda
    txt_busqueda = ft.TextField(label="Buscar producto", on_change=lambda e: buscar_producto(txt_busqueda.value, tabla_productos))
    btn_nuevo = ft.ElevatedButton("+ Añadir Producto", on_click=lambda e: mostrar_modal_registro(page))
    
    # Tabla de productos
    tabla_productos = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Código")),
            ft.DataColumn(ft.Text("Descripción")),
            ft.DataColumn(ft.Text("Stock")),
            ft.DataColumn(ft.Text("Marca")),
            ft.DataColumn(ft.Text("Precio Venta")),
            ft.DataColumn(ft.Text("Imagen")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[],
    )
    
    # Contenedor principal
    contenedor = ft.Column([
        ft.Row([txt_busqueda, btn_nuevo], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        tabla_productos
    ])
    
    set_content(contenedor)
    buscar_producto(txt_busqueda.value, tabla_productos)

def buscar_producto(descripcion, tabla_productos):
    descripcion = descripcion.strip()
    if not descripcion:
        return  # No hacer nada si está vacío

    conn = config.get_connection()
    cursor = conn.cursor()

    query = "SELECT codBarra, descripcion, stock, marca, pVenta, imagen FROM PRODUCTO WHERE descripcion LIKE ?"
    cursor.execute(query, (f"%{descripcion}%",))
    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    # Limpiar tabla antes de agregar nuevos datos
    tabla_productos.rows.clear()

    for codBarra, desc, stock, marca, pVenta, imagen in resultados:
        tabla_productos.rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(codBarra)),
                    ft.DataCell(ft.Text(desc)),
                    ft.DataCell(ft.Text(str(stock))),
                    ft.DataCell(ft.Text(marca)),
                    ft.DataCell(ft.Text(f"S/. {pVenta}")),
                    ft.DataCell(ft.Image(src=imagen if imagen else "ruta/imagen_default.png", width=50, height=50)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.icons.EDIT, on_click=lambda e, cb=codBarra: mostrar_modal_edicion(e.page, cb)),
                        ft.IconButton(ft.icons.DELETE, on_click=lambda e, cb=codBarra: confirmar_eliminar(e.page, cb))
                    ])),
                ]
            )
        )
    
    tabla_productos.update()

def mostrar_modal_registro(page):
    txt_codBarra = ft.TextField(label="Código de Barras")
    txt_descripcion = ft.TextField(label="Descripción")
    txt_marca = ft.TextField(label="Marca")
    txt_stock = ft.TextField(label="Stock", keyboard_type=ft.KeyboardType.NUMBER)
    txt_pCaja = ft.TextField(label="Precio por Caja", keyboard_type=ft.KeyboardType.NUMBER)
    txt_pUnidad = ft.TextField(label="Precio por Unidad", keyboard_type=ft.KeyboardType.NUMBER)
    txt_pVenta = ft.TextField(label="Precio de Venta", keyboard_type=ft.KeyboardType.NUMBER)
    txt_imagen = ft.TextField(label="Imagen", disabled=True)
    
    # Botón para seleccionar imagen
    btn_seleccionar_imagen = ft.FilePicker(on_result=lambda e: seleccionar_imagen(e, txt_imagen, page))
    page.overlay.append(btn_seleccionar_imagen)
    
    btn_registrar = ft.ElevatedButton("Registrar", on_click=lambda e: registrar_producto(txt_codBarra, txt_descripcion, txt_marca, txt_stock, txt_pCaja, txt_pUnidad, txt_pVenta, txt_imagen, page))
    
    modal = ft.AlertDialog(
        title=ft.Text("Registrar Producto"),
        content=ft.Container(
            content=ft.Column([
                txt_codBarra,
                txt_descripcion,
                txt_marca,
                txt_stock,
                txt_pCaja,
                txt_pUnidad,
                txt_pVenta,
                ft.Row([
                    txt_imagen,
                    ft.IconButton(icon=ft.icons.UPLOAD_FILE, on_click=lambda _: btn_seleccionar_imagen.pick_files(allow_multiple=False))
                ]),
                btn_registrar
            ]),
            width=500  # Ajuste del ancho del modal
        ),
        actions=[ft.TextButton("Cancelar", on_click=lambda e: page.close(modal))]
    )
    page.open(modal)

def registrar_producto(txt_codBarra, txt_descripcion, txt_marca, txt_stock, txt_pCaja, txt_pUnidad, txt_pVenta, txt_imagen, page):
    """Registra un nuevo producto en la base de datos."""
    codBarra = txt_codBarra.value.strip()
    descripcion = txt_descripcion.value.strip()
    marca = txt_marca.value.strip()
    stock = txt_stock.value.strip()
    pCaja = txt_pCaja.value.strip()
    pUnidad = txt_pUnidad.value.strip()
    pVenta = txt_pVenta.value.strip()
    imagen = txt_imagen.value.strip()
    fechaRegistro = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Validar campos obligatorios
    if not codBarra or not descripcion or not marca or not stock or not pCaja or not pUnidad or not pVenta or not imagen:
        dialogo_error = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚠️ Error"),
            content=ft.Text("Todos los campos son obligatorios."),
            actions=[ft.TextButton("Aceptar", on_click=lambda e: page.close(dialogo_error))],
        )
        page.open(dialogo_error)
        return

    # Validar que los valores numéricos sean correctos
    try:
        stock = int(stock)
        pCaja = float(pCaja)
        pUnidad = float(pUnidad)
        pVenta = float(pVenta)

        if stock < 0 or pCaja < 0 or pUnidad < 0 or pVenta < 0:
            raise ValueError
    except ValueError:
        dialogo_error = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚠️ Error"),
            content=ft.Text("Stock y precios deben ser valores positivos."),
            actions=[ft.TextButton("Aceptar", on_click=lambda e: page.close(dialogo_error))],
        )
        page.open(dialogo_error)
        return

    # Insertar en la base de datos
    conn = config.get_connection()
    cursor = conn.cursor()

    query = """INSERT INTO PRODUCTO (codBarra, descripcion, imagen, marca, stock, pCaja, pUnidad, pVenta, fechaRegistro)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    cursor.execute(query, (codBarra, descripcion, imagen, marca, stock, pCaja, pUnidad, pVenta, fechaRegistro))
    conn.commit()

    cursor.close()
    conn.close()

    # Mostrar mensaje de éxito
    dialogo_exito = ft.AlertDialog(
        modal=True,
        title=ft.Text("✅ Éxito"),
        content=ft.Text("Producto registrado con éxito."),
        actions=[ft.TextButton("Aceptar", on_click=lambda e: page.close(dialogo_exito))],
    )
    page.open(dialogo_exito)

    # Limpiar los campos después del registro
    txt_codBarra.value = ""
    txt_descripcion.value = ""
    txt_marca.value = ""
    txt_stock.value = ""
    txt_pCaja.value = ""
    txt_pUnidad.value = ""
    txt_pVenta.value = ""
    txt_imagen.value = ""
    page.update()

def seleccionar_imagen(e, txt_imagen, page):
    if e.files:
        txt_imagen.value = e.files[0].path
        txt_imagen.update()

def mostrar_modal_edicion(page, codBarra):
    conn = config.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PRODUCTO WHERE codBarra = ?", (codBarra,))
    prod = cursor.fetchone()
    conn.close()
    
    if not prod:
        return
    
    txt_codBarra = ft.TextField(label="Código de Barras", value=prod[1], disabled=True)
    txt_descripcion = ft.TextField(label="Descripción", value=prod[2])
    txt_marca = ft.TextField(label="Marca", value=prod[4])
    txt_stock = ft.TextField(label="Stock", value=str(prod[5]), keyboard_type=ft.KeyboardType.NUMBER)
    txt_pCaja = ft.TextField(label="Precio por Caja", value=str(prod[6]), keyboard_type=ft.KeyboardType.NUMBER)
    txt_pUnidad = ft.TextField(label="Precio por Unidad", value=str(prod[7]), keyboard_type=ft.KeyboardType.NUMBER)
    txt_pVenta = ft.TextField(label="Precio de Venta", value=str(prod[8]), keyboard_type=ft.KeyboardType.NUMBER)
    txt_imagen = ft.TextField(label="Imagen", value=prod[3])
    
    btn_seleccionar_imagen = ft.FilePicker(on_result=lambda e: seleccionar_imagen(e, txt_imagen, page))
    page.overlay.append(btn_seleccionar_imagen)

    btn_guardar = ft.ElevatedButton("Actualizar", on_click=lambda e: actualizar_producto(codBarra, txt_descripcion, txt_marca, txt_stock, txt_pCaja, txt_pUnidad, txt_pVenta, txt_imagen, page))
    
    modal = ft.AlertDialog(
        title=ft.Text("Editar Producto"),
        content=ft.Container(
            content=ft.Column([
                txt_codBarra, 
                txt_descripcion, 
                txt_marca, 
                txt_stock, 
                txt_pCaja, 
                txt_pUnidad, 
                txt_pVenta, 
                ft.Row([
                    txt_imagen,
                    ft.IconButton(icon=ft.icons.UPLOAD_FILE, on_click=lambda _: btn_seleccionar_imagen.pick_files(allow_multiple=False))
                ]),
            ]),
            width=500 
        ),
        actions=[btn_guardar, ft.TextButton("Cancelar", on_click=lambda e: page.close(modal))]
    )
    page.open(modal)

def actualizar_producto(codBarra, txt_descripcion, txt_marca, txt_stock, txt_pCaja, txt_pUnidad, txt_pVenta, txt_imagen, page):
    """Actualiza un producto en la base de datos."""
    descripcion = txt_descripcion.value.strip()
    marca = txt_marca.value.strip()
    stock = txt_stock.value.strip()
    pCaja = txt_pCaja.value.strip()
    pUnidad = txt_pUnidad.value.strip()
    pVenta = txt_pVenta.value.strip()
    imagen = txt_imagen.value.strip()
    fechaRegistro = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not descripcion or not marca or not stock or not pCaja or not pUnidad or not pVenta or not imagen:
        dialogo_error = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚠️ Error"),
            content=ft.Text("Todos los campos son obligatorios."),
            actions=[ft.TextButton("Aceptar", on_click=lambda e: page.close(dialogo_error))],
        )
        page.open(dialogo_error)
        return

    try:
        stock = int(stock)
        pCaja = float(pCaja)
        pUnidad = float(pUnidad)
        pVenta = float(pVenta)

        if stock < 0 or pCaja < 0 or pUnidad < 0 or pVenta < 0:
            raise ValueError
    except ValueError:
        dialogo_error = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚠️ Error"),
            content=ft.Text("Stock y precios deben ser valores positivos."),
            actions=[ft.TextButton("Aceptar", on_click=lambda e: page.close(dialogo_error))],
        )
        page.open(dialogo_error)
        return

    conn = config.get_connection()
    cursor = conn.cursor()

    query = """UPDATE PRODUCTO SET descripcion = ?, marca = ?, stock = ?, pCaja = ?, pUnidad = ?, pVenta = ?, imagen = ?, fechaRegistro = ? WHERE codBarra = ?"""
    cursor.execute(query, (descripcion, marca, stock, pCaja, pUnidad, pVenta, imagen, fechaRegistro, codBarra))
    conn.commit()

    cursor.close()
    conn.close()

    dialogo_exito = ft.AlertDialog(
        modal=True,
        title=ft.Text("✅ Éxito"),
        content=ft.Text("Producto actualizado con éxito."),
        actions=[ft.TextButton("Aceptar", on_click=lambda e: page.close(dialogo_exito))],
    )
    page.open(dialogo_exito)

def confirmar_eliminar(page, codBarra):
    conn = config.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT descripcion, marca FROM PRODUCTO WHERE codBarra = ?", (codBarra,))
    prod = cursor.fetchone()
    conn.close()
    
    if not prod:
        return
    
    descripcion, marca = prod
    
    def eliminar_producto(e):
        conn = config.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM PRODUCTO WHERE codBarra = ?", (codBarra,))
        conn.commit()
        cursor.close()
        conn.close()
        page.close(modal)
        buscar_producto("", page.controls[1])
    
    modal = ft.AlertDialog(
        title=ft.Text("Confirmar Eliminación"),
        content=ft.Text(f"¿Está seguro que desea eliminar el producto: '{descripcion}' '{marca}'?"),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.close(modal)),
            ft.TextButton("Eliminar", on_click=eliminar_producto, style=ft.ButtonStyle(color=ft.colors.RED)),
        ],
    )
    page.open(modal)

