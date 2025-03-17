import flet as ft
import asyncio
from views.gestion_productos import gestionar_productos

def main(page: ft.Page):
    page.title = "Sistema de Librería"
    page.bgcolor = "#e0f7fa"
    page.padding = 20  # Espaciado alrededor

    # Función para manejar la navegación
    def cambiar_pagina(e):
        index = e.control.selected_index
        if index == 1:
            gestionar_productos(page)
        elif index == 2:
            print("Abrir módulo de ventas")

    # Título estilizado
    titulo = ft.Text(
        "📚 Librería de Útiles Escolares",
        size=32,
        weight="bold",
        color="#00796b"
    )

    # Barra de navegación con altura definida
    nav_bar = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        on_change=cambiar_pagina,
        expand=True,  # Permite que se expanda en altura
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.STORE,
                selected_icon=ft.Icons.STOREFRONT,
                label="Inicio",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.INVENTORY,
                selected_icon=ft.Icons.INVENTORY_2,
                label="Productos",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.POINT_OF_SALE,
                selected_icon=ft.Icons.ATTACH_MONEY,
                label="Ventas",
            ),
        ],
    )

    # Contenedor de la barra de navegación con altura expandida
    nav_container = ft.Container(
        content=nav_bar,
        height=page.height,  # Ajusta la altura al tamaño de la página
    )

    # Contenido principal
    content = ft.Column(
        [
            titulo,
            ft.Divider(),
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Gestionar Productos",
                        icon=ft.Icons.INVENTORY,
                        on_click=lambda e: gestionar_productos(page)
                    ),
                    ft.ElevatedButton(
                        "Registrar Venta",
                        icon=ft.Icons.POINT_OF_SALE,
                        on_click=lambda e: print("Abrir módulo de ventas")
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
    )

    # Layout de la página con altura expandida
    page.add(
        ft.Row(
            [
                nav_container,  # Contenedor con altura definida
                ft.VerticalDivider(),
                ft.Container(content=content, expand=True),  # Expande el contenido
            ],
            expand=True,  # Permite que toda la fila ocupe el espacio disponible
        )
    )

if __name__ == "__main__":
    asyncio.run(ft.app_async(target=main))
