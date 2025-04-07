import flet as ft
import win32com.client as win32
import pythoncom

def group_contains_keywords(group, keywords):
    """ Verifica si alguna forma dentro del grupo contiene los textos clave """
    for shape in group.GroupItems:
        try:
            if shape.Type == 6:  # Grupo dentro de grupo
                if group_contains_keywords(shape, keywords):
                    return True
            elif shape.TextFrame.HasText:
                text = shape.TextFrame.TextRange.Text
                if any(keyword in text for keyword in keywords):
                    return True
        except Exception as e:
            print(f"Error revisando forma en grupo: {e}")
    return False

def create_word_file():
    pythoncom.CoInitialize()
    word = win32.Dispatch("Word.Application")
    word.Visible = False

    file_path = r"C:\Users\Kitsu\Documents\GitHub-Proyectos\lib_union\Precios-P.docx"
    save_path = r"C:\Users\Kitsu\Documents\GitHub-Proyectos\lib_union\Precios-Eliminado.docx"
    
    doc = word.Documents.Open(file_path)

    keywords = ["m2"]
    shapes_to_delete = []

    for shape in doc.Shapes:
        try:
            if shape.Type == 6:  # Forma agrupada
                if group_contains_keywords(shape, keywords):
                    shapes_to_delete.append(shape)
        except Exception as e:
            print(f"Error evaluando grupo: {e}")
    
    for shape in shapes_to_delete:
        shape.Delete()

    doc.SaveAs(save_path)
    doc.Close()
    word.Quit()
    print("Documento generado y grupo eliminado correctamente.")

def main(page: ft.Page):
    def on_click(e):
        create_word_file()
        page.add(ft.Text("Archivo Word con grupo eliminado generado con éxito."))
    
    button = ft.ElevatedButton("Eliminar grupo del Word", on_click=on_click)
    page.add(button)

ft.app(target=main)
