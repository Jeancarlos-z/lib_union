import flet as ft
import win32com.client as win32
import pythoncom
import os
import config  # Para la conexión a la BD

tabla_etiquetas = None  # Variable global para la tabla
ruta_plantilla = r"C:\Users\Kitsu\Documents\GitHub-Proyectos\lib_union\Precios-P.docx"

def gestionar_etiquetas(page: ft.Page, set_content):
    """Página para gestionar etiquetas de productos."""
    global tabla_etiquetas

    page.title = "Gestión de Etiquetas"
    page.bgcolor = "#121212"

    txt_busqueda = ft.TextField(
        label="Buscar producto",
        on_change=lambda e: buscar_producto(txt_busqueda, lista_sugerencias, page),
        expand=True,
        bgcolor="#1E1E1E",
        color="white",
        border_color="#D32F2F",
        border_radius=10
    )

    lista_sugerencias = ft.ListView(expand=True, height=200)

    btn_generar_word = ft.ElevatedButton(
        "Generar Word",
        on_click=lambda e: seleccionar_carpeta_guardado(page),
        bgcolor="#D32F2F",
        color="white"
    )

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

    # Contenedor para organizar el layout con el buscador a la izquierda y la tabla a la derecha
    contenedor = ft.Row([
        ft.Container(
            content=ft.Column([
                ft.Row([txt_busqueda], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                lista_sugerencias,
            ]),
            expand=2,
            padding=10,
            border_radius=10,
            bgcolor="#1E1E1E",
            shadow=ft.BoxShadow(blur_radius=10, color="#D32F2F")
        ),
        ft.Container(
            content=ft.Column([tabla_etiquetas, btn_generar_word]),
            expand=3,
            padding=10,
            border_radius=10,
            bgcolor="#1E1E1E",
            shadow=ft.BoxShadow(blur_radius=10, color="#D32F2F")
        )
    ])

    set_content(contenedor)

def seleccionar_carpeta_guardado(page):
    file_picker = ft.FilePicker(on_result=lambda e: generar_documento_word(e, page))
    page.overlay.append(file_picker)
    page.update()
    file_picker.get_directory_path()

def generar_documento_word(e, page):
    if not e.path:
        return

    if not tabla_etiquetas.rows:
        page.snack_bar = ft.SnackBar(content=ft.Text("No hay productos en la tabla."), bgcolor="red")
        page.snack_bar.open = True
        page.update()
        return

    ruta_guardado = f"{e.path}\\Precios-Generado.docx"

    pythoncom.CoInitialize()
    word = win32.Dispatch("Word.Application")
    word.Visible = False  

    try:
        doc = word.Documents.Open(ruta_plantilla)

        total_etiquetas = len(tabla_etiquetas.rows)

        # Reemplazar textos de las etiquetas existentes
        for i in range(total_etiquetas):
            descripcion = tabla_etiquetas.rows[i].cells[1].content.value
            marca = tabla_etiquetas.rows[i].cells[2].content.value
            precio = "S/ " + tabla_etiquetas.rows[i].cells[3].content.value

            reemplazar_texto_en_formas(doc, f"d{i+1}", descripcion)
            reemplazar_texto_en_formas(doc, f"m{i+1}", marca)
            reemplazar_texto_en_formas(doc, f"p{i+1}", precio)

        # Eliminar los grupos sobrantes
        for i in range(total_etiquetas + 1, 13):  # De la siguiente etiqueta hasta la 12
            eliminar_grupo_por_marcadores(doc, [f"d{i}", f"p{i}", f"m{i}"])

        doc.SaveAs(ruta_guardado)
        doc.Close()
        word.Quit()

        dialogo_exito = ft.AlertDialog(
            title=ft.Text("✅ Éxito"),
            content=ft.Text(f"El archivo se guardó en:\n{ruta_guardado}"),
            actions=[
                ft.TextButton("Abrir carpeta", on_click=lambda e: abrir_carpeta(ruta_guardado)),
                ft.TextButton("Cerrar", on_click=lambda e: page.close(dialogo_exito))
            ],
            open=True
        )
        page.dialog = dialogo_exito
        page.open(dialogo_exito)

    except Exception as ex:
        word.Quit()
        dialogo_error = ft.AlertDialog(
            title=ft.Text("❌ Error"),
            content=ft.Text(f"Ocurrió un error: {str(ex)}"),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: page.close(dialogo_error))],
            open=True
        )
        page.dialog = dialogo_error
        page.open(dialogo_error)

    page.update()

def reemplazar_texto_en_formas(doc, marcador, nuevo_texto):
    for shape in doc.Shapes:
        try:
            if shape.Type == 6:
                modificar_formas_en_grupo(shape, marcador, nuevo_texto)
            elif shape.TextFrame.HasText:
                texto_actual = shape.TextFrame.TextRange.Text.strip()
                if texto_actual == marcador:
                    shape.TextFrame.TextRange.Text = nuevo_texto
        except Exception:
            pass

def modificar_formas_en_grupo(group, marcador, nuevo_texto):
    for shape in group.GroupItems:
        try:
            if shape.Type == 6:
                modificar_formas_en_grupo(shape, marcador, nuevo_texto)
            elif shape.TextFrame.HasText:
                texto_actual = shape.TextFrame.TextRange.Text.strip()
                if texto_actual == marcador:
                    shape.TextFrame.TextRange.Text = nuevo_texto
        except Exception:
            pass


def eliminar_grupo_por_marcadores(doc, marcadores):
    for shape in list(doc.Shapes):  # Crear copia para evitar problemas al eliminar
        try:
            if shape.Type == 6:  # Grupo
                if contiene_marcador_en_grupo(shape, marcadores):
                    shape.Delete()
        except Exception as e:
            print(f"Error eliminando grupo: {e}")

def contiene_marcador_en_grupo(group, marcadores):
    """Evalúa si algún marcador está dentro de un grupo"""
    for shape in group.GroupItems:
        try:
            if shape.Type == 6:
                if contiene_marcador_en_grupo(shape, marcadores):
                    return True
            elif shape.TextFrame.HasText:
                texto = shape.TextFrame.TextRange.Text
                if any(marcador in texto for marcador in marcadores):
                    return True
        except:
            continue
    return False

def abrir_carpeta(ruta_archivo):
    os.startfile(os.path.dirname(ruta_archivo))
    
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
        content=ft.Column([txt_descripcion, txt_marca, txt_precio], tight=True),  # 📏 Ajusta el tamaño automático
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
