import flet as ft
import asyncio
from layout import crear_layout

def main(page: ft.Page):
    layout, set_content = crear_layout(page, None)  # Cargamos el layout
    page.add(layout)
    
    # Mostramos la página de inicio por defecto
    set_content("inicio")

if __name__ == "__main__":
    asyncio.run(ft.app_async(target=main))
