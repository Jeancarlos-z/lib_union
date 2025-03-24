import flet as ft
import win32com.client as win32
import pythoncom

def modify_shapes_in_group(group):
    """ Función recursiva para modificar texto dentro de formas agrupadas """
    for shape in group.GroupItems:
        try:
            if shape.TextFrame.HasText:
                text = shape.TextFrame.TextRange.Text
                if "descripcion" in text:
                    shape.TextFrame.TextRange.Text = text.replace("descripcion", "LAPICERO")
                elif "precio" in text:
                    shape.TextFrame.TextRange.Text = text.replace("precio", "2.3")
                elif "marca" in text:
                    shape.TextFrame.TextRange.Text = text.replace("marca", "OVE")
            if shape.Type == 6:  # 6 = Forma agrupada
                modify_shapes_in_group(shape)
        except Exception as e:
            print(f"Error modificando forma en grupo: {e}")

def create_word_file():
    pythoncom.CoInitialize()  # Inicializa COM correctamente
    word = win32.Dispatch("Word.Application")
    word.Visible = False  # No mostrar la ventana de Word
    
    file_path = r"C:\Users\Kitsu\Documents\GitHub-Proyectos\lib_union\Precios-P.docx"  # Ruta completa
    save_path = r"C:\Users\Kitsu\Documents\GitHub-Proyectos\lib_union\Precios-Generado.docx"
    
    doc = word.Documents.Open(file_path)
    
    # Iterar sobre todas las formas en el documento
    for shape in doc.Shapes:
        try:
            if shape.Type == 6:  # 6 = Forma agrupada
                modify_shapes_in_group(shape)
            elif shape.TextFrame.HasText:
                text = shape.TextFrame.TextRange.Text
                if "descripcion" in text:
                    shape.TextFrame.TextRange.Text = text.replace("descripcion", "LAPICERO")
                elif "precio" in text:
                    shape.TextFrame.TextRange.Text = text.replace("precio", "2.3")
                elif "marca" in text:
                    shape.TextFrame.TextRange.Text = text.replace("marca", "OVE")
        except Exception as e:
            print(f"Error modificando forma: {e}")
    
    # Guardar y cerrar
    doc.SaveAs(save_path)
    doc.Close()
    word.Quit()
    print("Documento generado correctamente.")

def main(page: ft.Page):
    def on_click(e):
        create_word_file()
        page.add(ft.Text("Archivo Word generado con éxito."))
    
    button = ft.ElevatedButton("Generar Word", on_click=on_click)
    page.add(button)

ft.app(target=main)
