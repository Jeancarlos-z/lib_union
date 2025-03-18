import flet as ft
from views.almacen import gestionar_productos

def crear_layout(page: ft.Page, buscador_inicial):
    """Función que crea la barra de navegación y gestiona las vistas."""
    page.title = "Sistema de Librería"
    page.bgcolor = "#121212"
    page.padding = 20

    # Función para cambiar la vista según la opción seleccionada
    def cambiar_pagina(e):
        index = e.control.selected_index
        if index == 0:
            set_content(buscador_inicial)  # ✅ Restaurar el buscador
        elif index == 1:
            gestionar_productos(page, set_content)  # ✅ Mantener la gestión de productos
        elif index == 2:
            set_content("ventas")

    # Barra de navegación
    nav_bar = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        on_change=cambiar_pagina,
        expand=True,
        bgcolor="#1E1E1E",
        indicator_color="#D32F2F",
        selected_label_text_style=ft.TextStyle(color="#D32F2F", weight="bold"),
        unselected_label_text_style=ft.TextStyle(color="#AAAAAA"),
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.STORE,
                selected_icon=ft.Icons.STOREFRONT,
                label="Inicio",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.INVENTORY,
                selected_icon=ft.Icons.INVENTORY_2,
                label="Almacén",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.POINT_OF_SALE,
                selected_icon=ft.Icons.ATTACH_MONEY,
                label="Ventas",
            ),
        ],
    )

    # Contenedor de navegación
    nav_container = ft.Container(
        content=nav_bar,
        height=page.height,
        border=ft.border.all(2, "#D32F2F"),
        padding=10,
    )

    # Área de contenido dinámico
    contenido_container = ft.Container(expand=True)

    # Función para actualizar el contenido dinámico
    def set_content(vista):
        if isinstance(vista, ft.Control):
            contenido_container.content = vista  # ✅ Carga contenido dinámico directamente
        elif vista == "ventas":
            contenido_container.content = ft.Text("💰 Módulo de Ventas en construcción...", size=24, color="white")

        page.update()

    # Layout principal con la barra de navegación y el contenido
    layout = ft.Row(
        [
            nav_container,
            ft.VerticalDivider(color="#D32F2F", thickness=2),
            contenido_container,  # ✅ Aquí se actualizará el contenido
        ],
        expand=True,
    )

    return layout, set_content

