import tkinter as tk
from tkinter import messagebox

def mostrar_mensaje():
    messagebox.showinfo("¡BiIIIIIIIIIIIIInvenido!", "Gracias por utilizar nuestro sistema")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Bienvenido")
ventana.geometry("400x300")
ventana.configure(bg="#87CEEB")  # Color de fondo celeste

# Etiqueta de bienvenida
etiqueta = tk.Label(ventana, text="¡Bienvenido!", font=("Arial", 24, "bold"), bg="#87CEEB", fg="#FFFFFF")
etiqueta.pack(pady=50)

# Botón para mostrar el mensaje
boton = tk.Button(ventana, text="Entrar", font=("Arial", 14), command=mostrar_mensaje, bg="#4682B4", fg="white", padx=10, pady=5)
boton.pack(pady=20)

# Ejecutar la aplicación
ventana.mainloop() 
