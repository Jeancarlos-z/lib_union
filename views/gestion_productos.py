import flet as ft

def gestionar_productos(page: ft.Page):
    page.clean()  # Limpiar pantalla

    titulo = ft.Text("Gestión de Productos", size=25, weight="bold")
    btn_volver = ft.ElevatedButton("Volver al Menú", on_click=lambda e: volver_al_menu(page))

    page.add(titulo, btn_volver)

def volver_al_menu(page: ft.Page):
    from main import main
    page.clean()
    main(page)  # Llamar directamente a la función main sin reimportar
