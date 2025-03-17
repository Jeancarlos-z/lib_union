import flet as ft
import asyncio
from views.gestion_productos import gestionar_productos
from ventas import gestionar_ventas  # Importa el módulo de ventas

def main(page: ft.Page):
    page.title = "Sistema de Librería"
    page.bgcolor = "#e0f7fa"
    page.padding = 20  # Espaciado alrededor

    def cambiar_pagina(e):
        index = e.control.selected_index
        if index == 1:
            gestionar_productos(page)
        elif index == 2:
            gestionar_ventas(page)  # Llama al módulo de ventas

    titulo = ft.Text(
        "📚 Librería de Útiles Escolares",
        size=32,
        weight="bold",
        color="#00796b"
    )

    nav_bar = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        on_change=cambiar_pagina,
        expand=True,
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

    nav_container = ft.Container(
        content=nav_bar,
        height=page.height,
    )

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
                        on_click=lambda e: gestionar_ventas(page)
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
    )

    page.add(
        ft.Row(
            [
                nav_container,
                ft.VerticalDivider(),
                ft.Container(content=content, expand=True),
            ],
            expand=True,
        )
    )

if __name__ == "__main__":
    asyncio.run(ft.app_async(target=main))
