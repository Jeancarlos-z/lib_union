import flet as ft
import config  # Para la conexión a la BD

tabla_etiquetas = None  # Variable global para la tabla

def gestionar_etiquetas(page: ft.Page, set_content):
    """Página para gestionar etiquetas de productos."""
    global tabla_etiquetas

    page.title = "Gestión de Etiquetas"
    page.bgcolor = "#121212"

    txt_busqueda = ft.TextField(
        label="Buscar producto por Código de Barras o Descripción",
        on_change=lambda e: buscar_producto(txt_busqueda, lista_sugerencias, page),
        expand=True,
        bgcolor="#1E1E1E",
        color="white",
        border_color="#D32F2F",
        border_radius=10
    )

    lista_sugerencias = ft.ListView(expand=True, height=200)

    tabla_etiquetas = ft.DataTable(
        bgcolor="#1E1E1E",
        border_radius=10,
        heading_row_color="#D32F2F",
        data_row_color={"hovered": "#333333"},
        columns=[
            ft.DataColumn(ft.Text("#", color="white")),  # Numeración
            ft.DataColumn(ft.Text("Descripción", color="white")),
            ft.DataColumn(ft.Text("Marca", color="white")),
            ft.DataColumn(ft.Text("Precio Venta", color="white")),
            ft.DataColumn(ft.Text("Acciones", color="white")),
        ],
        rows=[]
    )

    contenedor = ft.Container(
        content=ft.Column([
            txt_busqueda,
            lista_sugerencias,
            ft.Divider(color="#D32F2F"),
            tabla_etiquetas
        ]),
        expand=True,
        padding=10,
        border_radius=10,
        bgcolor="#1E1E1E",
        shadow=ft.BoxShadow(blur_radius=10, color="#D32F2F")
    )

    set_content(contenedor)

def buscar_producto(txt_busqueda, lista_sugerencias, page):
    query = txt_busqueda.value.strip()
    if not query:
        lista_sugerencias.controls.clear()
        lista_sugerencias.update()
        return

    conn = config.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT codBarra, descripcion, marca, pVenta 
        FROM PRODUCTO 
        WHERE codBarra LIKE ? OR descripcion LIKE ?
    """, (f"%{query}%", f"%{query}%"))
    resultados = cursor.fetchall()
    conn.close()

    lista_sugerencias.controls.clear()
    for resultado in resultados:
        cod_barra, descripcion, marca, p_venta = resultado
        sugerencia = ft.ListTile(
            title=ft.Text(f"{cod_barra} - {descripcion}"),
            on_click=lambda e, desc=descripcion, m=marca, p=p_venta: mostrar_modal_producto(page, txt_busqueda, desc, m, p, lista_sugerencias)
        )
        lista_sugerencias.controls.append(sugerencia)

    lista_sugerencias.update()

def mostrar_modal_producto(page, txt_busqueda, descripcion, marca, p_venta, lista_sugerencias):
    global tabla_etiquetas

    txt_descripcion = ft.TextField(label="Descripción", value=descripcion)
    txt_marca = ft.TextField(label="Marca", value=marca)
    txt_precio = ft.TextField(label="Precio Venta", value=str(p_venta))

    def agregar_producto(e):
        """Añade el producto seleccionado a la tabla de etiquetas."""
        if not txt_precio.value.replace(".", "").isdigit():
            page.snack_bar = ft.SnackBar(content=ft.Text("Ingrese un precio válido."), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        # ID único para identificar la fila
        fila_id = str(id(txt_descripcion))

        nueva_fila = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(len(tabla_etiquetas.rows) + 1))),  # Número de fila
                ft.DataCell(ft.Text(txt_descripcion.value)),
                ft.DataCell(ft.Text(txt_marca.value)),
                ft.DataCell(ft.Text(f"{float(txt_precio.value):.2f}")),
                ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, key=fila_id: eliminar_producto(key))),
                ft.DataCell(ft.Text(fila_id), visible=False)  # Campo oculto con el identificador único
            ]
        )

        tabla_etiquetas.rows.append(nueva_fila)
        tabla_etiquetas.update()
        page.close(modal)

    modal = ft.AlertDialog(
        title=ft.Text("Editar Producto"),
        content=ft.Column([txt_descripcion, txt_marca, txt_precio]),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.close(modal)),
            ft.ElevatedButton("Agregar", on_click=agregar_producto)
        ]
    )
    page.open(modal)

def eliminar_producto(fila_id):
    """Elimina un producto de la tabla sin desajustar índices."""
    global tabla_etiquetas

    # Buscar la fila a eliminar
    tabla_etiquetas.rows = [fila for fila in tabla_etiquetas.rows if fila.cells[-1].content.value != fila_id]

    # Reasignar numeración
    for i, row in enumerate(tabla_etiquetas.rows):
        row.cells[0] = ft.DataCell(ft.Text(str(i + 1)))

    tabla_etiquetas.update()
