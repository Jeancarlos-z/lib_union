import flet as ft
import config  # Importamos la conexión desde config.py
import datetime

def gestionar_productos(page: ft.Page, set_content):
    page.title = "Registro de Productos"

    # Campos de entrada para registrar productos
    txt_codBarra = ft.TextField(label="Código de Barras")
    txt_descripcion = ft.TextField(label="Descripción del Producto")
    txt_marca = ft.TextField(label="Marca")
    txt_stock = ft.TextField(label="Stock", keyboard_type=ft.KeyboardType.NUMBER)
    txt_pCaja = ft.TextField(label="Precio por Caja", keyboard_type=ft.KeyboardType.NUMBER)
    txt_pUnidad = ft.TextField(label="Precio por Unidad", keyboard_type=ft.KeyboardType.NUMBER)
    txt_pVenta = ft.TextField(label="Precio de Venta", keyboard_type=ft.KeyboardType.NUMBER)
    txt_imagen = ft.TextField(label="URL de la Imagen", disabled=True)  # Se llenará automáticamente al subir la imagen

    # Botón para seleccionar imagen
    btn_seleccionar_imagen = ft.FilePicker(on_result=lambda e: seleccionar_imagen(e, txt_imagen, page))
    page.overlay.append(btn_seleccionar_imagen)

    # Botón para registrar un producto
    btn_registrar = ft.ElevatedButton("Registrar Producto", on_click=lambda e: registrar_producto(
        txt_codBarra, txt_descripcion, txt_marca, txt_stock, txt_pCaja, txt_pUnidad, txt_pVenta, txt_imagen, page
    ))

    # Contenedor con los campos de entrada
    contenedor_productos = ft.Column([
        ft.Text("🛒 Registro de Productos", size=20, weight="bold"),
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
    ])

    # ACTUALIZA SOLO EL CONTENIDO DINÁMICO DEL LAYOUT
    set_content(contenedor_productos)

def seleccionar_imagen(evento, txt_imagen, page):
    """Permite seleccionar una imagen y guarda la URL."""
    if evento.files:
        imagen_url = evento.files[0].path  # Se guarda la URL local de la imagen
        txt_imagen.value = imagen_url
        page.update()

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
