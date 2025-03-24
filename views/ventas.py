import flet as ft
import config  # Para la conexión a la BD

tabla_ventas = None  # Definir la tabla como global
lbl_total = None  # Definir el total globalmente

def gestionar_ventas(page: ft.Page, set_content):
    global tabla_ventas, lbl_total  # Permitir modificaciones en la tabla y total

    page.title = "Gestión de Ventas"

    # Campo de búsqueda con autocompletado
    txt_busqueda = ft.TextField(
        label="Buscar producto",
        on_change=lambda e: buscar_producto(txt_busqueda, lista_sugerencias),
        expand=True
    )
    btn_buscar = ft.ElevatedButton("Buscar", on_click=lambda e: mostrar_modal_producto(page, txt_busqueda, lista_sugerencias))
    
    lista_sugerencias = ft.ListView(expand=True, height=200)  # Limitamos la altura
    
    # Tabla de productos agregados a la venta
    tabla_ventas = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Descripción")),
            ft.DataColumn(ft.Text("Marca")),
            ft.DataColumn(ft.Text("Cantidad")),
            ft.DataColumn(ft.Text("Costo")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[],
    )
    
    lbl_total = ft.Text("Total: 0.00")
    btn_confirmar = ft.ElevatedButton("Confirmar Venta", on_click=lambda e: confirmar_venta(page))
    
    # Organización en dos columnas para mejor distribución
    contenedor = ft.Row([
        ft.Column([
            ft.Row([txt_busqueda, btn_buscar], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            lista_sugerencias,
        ], expand=2),
        
        ft.Column([
            tabla_ventas,  # Se coloca a la derecha del buscador
            lbl_total,
            btn_confirmar
        ], expand=3)
    ])
    
    set_content(contenedor)

def buscar_producto(txt_busqueda, lista_sugerencias):
    query = txt_busqueda.value.strip()
    if not query:
        lista_sugerencias.controls.clear()
        lista_sugerencias.update()
        return
    
    conn = config.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT descripcion FROM PRODUCTO WHERE descripcion LIKE ?", (f"%{query}%",))
    resultados = cursor.fetchall()
    conn.close()
    
    lista_sugerencias.controls.clear()
    for resultado in resultados:
        sugerencia = ft.ListTile(
            title=ft.Text(resultado[0]),
            on_click=lambda e, desc=resultado[0]: seleccionar_producto(txt_busqueda, desc, lista_sugerencias)
        )
        lista_sugerencias.controls.append(sugerencia)
    
    lista_sugerencias.update()

def seleccionar_producto(txt_busqueda, descripcion, lista_sugerencias):
    txt_busqueda.value = descripcion  # Poner la descripción en la barra de búsqueda
    txt_busqueda.update()  # Actualizar el campo de texto
    lista_sugerencias.controls.clear()  # Limpiar la lista de sugerencias
    lista_sugerencias.update()  # Refrescar la interfaz


def mostrar_modal_producto(page, txt_busqueda, lista_sugerencias):
    global tabla_ventas, lbl_total  # Para modificar la tabla dentro de esta función

    descripcion = txt_busqueda.value.strip()
    if not descripcion:
        return
    
    conn = config.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT descripcion, marca, stock, pVenta, imagen FROM PRODUCTO WHERE descripcion = ?", (descripcion,))
    prod = cursor.fetchone()
    conn.close()
    
    if not prod:
        return
    
    txt_cantidad = ft.TextField(label="Cantidad", keyboard_type=ft.KeyboardType.NUMBER)
    
    def agregar_producto(e):
        global tabla_ventas, lbl_total

        cantidad = int(txt_cantidad.value)
        costo = cantidad * prod[3]
        row_index = len(tabla_ventas.rows)  # Obtener el índice de la nueva fila

        nueva_fila = ft.DataRow(cells=[
            ft.DataCell(ft.Text(prod[0])),
            ft.DataCell(ft.Text(prod[1])),
            ft.DataCell(ft.Text(str(cantidad))),
            ft.DataCell(ft.Text(f"{costo:.2f}")),
            ft.DataCell(ft.Row([
                ft.IconButton(ft.icons.EDIT, on_click=lambda e, idx=row_index: editar_producto(page, idx)),
                ft.IconButton(ft.icons.DELETE, on_click=lambda e, idx=row_index: confirmar_eliminar_producto(page, idx))
            ]))
        ])
        
        tabla_ventas.rows.append(nueva_fila) # Agregar fila
        tabla_ventas.update()  # Actualizar la tabla
        actualizar_total() # Actualizar el total
        page.close(modal) # Cerrar el modal
    
    modal = ft.AlertDialog(
        title=ft.Text("Seleccionar Producto"),
        content=ft.Column([
            ft.Text(f"Descripción: {prod[0]}"),
            ft.Text(f"Marca: {prod[1]}"),
            ft.Text(f"Stock: {prod[2]}"),
            ft.Text(f"Precio: {prod[3]:.2f}"),
            ft.Image(src=prod[4], width=100, height=100),
            txt_cantidad
        ]),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.close(modal)),
            ft.ElevatedButton("Agregar", on_click=agregar_producto)
        ]
    )
    page.open(modal)

def editar_producto(page, row_index):
    global tabla_ventas

    fila = tabla_ventas.rows[row_index]
    descripcion = fila.cells[0].content.value
    cantidad_actual = int(fila.cells[2].content.value)
    precio_unitario = float(fila.cells[3].content.value) / cantidad_actual  # Calcular el precio unitario

    txt_nueva_cantidad = ft.TextField(label="Nueva Cantidad", value=str(cantidad_actual), keyboard_type=ft.KeyboardType.NUMBER)

    def guardar_edicion(e):
        nueva_cantidad = int(txt_nueva_cantidad.value)
        nuevo_costo = nueva_cantidad * precio_unitario

        # Actualizar la fila
        fila.cells[2].content = ft.Text(str(nueva_cantidad))
        fila.cells[3].content = ft.Text(f"{nuevo_costo:.2f}")
        tabla_ventas.update()
        actualizar_total()
        page.close(modal)

    modal = ft.AlertDialog(
        title=ft.Text(f"Editar Producto - {descripcion}"),
        content=ft.Column([txt_nueva_cantidad]),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.close(modal)),
            ft.ElevatedButton("Guardar", on_click=guardar_edicion)
        ]
    )
    page.open(modal)

def confirmar_eliminar_producto(page, row_index):
    global tabla_ventas

    modal = ft.AlertDialog(
        title=ft.Text("Eliminar Producto"),
        content=ft.Text("¿Está seguro de que desea eliminar este producto?"),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.close(modal)),
            ft.ElevatedButton("Eliminar", on_click=lambda e: eliminar_producto(page, row_index, modal))
        ]
    )
    page.open(modal)

def eliminar_producto(page, row_index, modal):
    global tabla_ventas

    del tabla_ventas.rows[row_index]  # Eliminar la fila
    tabla_ventas.update()
    actualizar_total()
    page.close(modal)

def actualizar_total():
    global tabla_ventas, lbl_total
    
    total = sum(float(row.cells[3].content.value) for row in tabla_ventas.rows)
    lbl_total.value = f"Total: {total:.2f}"
    lbl_total.update()

def confirmar_venta(page):
    modal = ft.AlertDialog(
        title=ft.Text("Confirmar Venta"),
        content=ft.Text("¿Desea confirmar la venta?"),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.close(modal)),
            ft.ElevatedButton("Confirmar", on_click=lambda e: procesar_venta(page, modal))
        ]
    )
    page.open(modal)

def procesar_venta(page, modal):
    global tabla_ventas

    if not tabla_ventas.rows:
        return  # No hay productos en la venta, no hacer nada

    conn = config.get_connection()
    cursor = conn.cursor()

    try:
        # Insertar una nueva venta en la tabla VENTA y obtener el ID generado
        cursor.execute("INSERT INTO VENTA (fechaVenta) OUTPUT INSERTED.idVenta VALUES (GETDATE())")
        id_venta = cursor.fetchone()[0]

        # Insertar los detalles de la venta y actualizar el stock
        for row in tabla_ventas.rows:
            descripcion = row.cells[0].content.value
            cantidad = int(row.cells[2].content.value)

            # Obtener el ID del producto y sus datos
            cursor.execute("SELECT idProducto, stock, pUnidad FROM PRODUCTO WHERE descripcion = ?", (descripcion,))
            producto = cursor.fetchone()

            if not producto:
                raise Exception(f"Producto '{descripcion}' no encontrado en la base de datos.")

            id_producto, stock_actual, p_unidad = producto
            nuevo_stock = stock_actual - cantidad

            if nuevo_stock < 0:
                raise Exception(f"Stock insuficiente para '{descripcion}'. Disponible: {stock_actual}, requerido: {cantidad}")

            # Insertar en DETALLE_VENTA
            cursor.execute(
                "INSERT INTO DETALLE_VENTA (idVenta, idProducto, cantidad, pUnidad) VALUES (?, ?, ?, ?)",
                (id_venta, id_producto, cantidad, p_unidad)
            )

            # Actualizar el stock del producto
            cursor.execute("UPDATE PRODUCTO SET stock = ? WHERE idProducto = ?", (nuevo_stock, id_producto))

        # Confirmar la transacción
        conn.commit()

        # Limpiar la tabla de ventas después de registrar la venta
        tabla_ventas.rows.clear()
        actualizar_total()
        tabla_ventas.update()

        # Cerrar el modal de confirmación antes de mostrar el de éxito
        page.close(modal)

        # Crear y mostrar el modal de éxito
        modal_exito = ft.AlertDialog(
            title=ft.Text("Venta registrada"),
            content=ft.Text("La venta se ha registrado exitosamente."),
            actions=[ft.TextButton("Aceptar", on_click=lambda e: page.close(modal_exito))]
        )
        page.open(modal_exito)


    except Exception as e:
        conn.rollback()  # Revertir cambios en caso de error

        # Cerrar el modal de confirmación antes de mostrar el de error
        page.close(modal)

        modal_error = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(f"Error al procesar la venta: {str(e)}"),
            actions=[ft.TextButton("Aceptar", on_click=lambda e: page.close(modal_error))]
        )
        page.open(modal_error)

    finally:
        conn.close()