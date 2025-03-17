import flet as ft
import asyncio
from views.gestion_productos import gestionar_productos

def main(page: ft.Page):
    page.title = "Sistema de Librería"
    page.bgcolor = "#f4f4f4"

    def abrir_gestion_productos(e):
        gestionar_productos(page)  # Llamamos a la función de la otra vista

    titulo = ft.Text("Librería de Útiles Escolares", size=30, weight="bold")

    btn_productos = ft.ElevatedButton("Gestionar Productos", on_click=abrir_gestion_productos)
    btn_ventas = ft.ElevatedButton("Registrar Venta", on_click=lambda e: print("Abrir módulo de ventas"))

    page.add(titulo, btn_productos, btn_ventas)

if __name__ == "__main__":
    asyncio.run(ft.app_async(target=main)) 

