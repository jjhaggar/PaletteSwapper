import os
from tkinter import filedialog, messagebox
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageOps

def invertir_imagen(ruta):
    """
    Abre la imagen en 'ruta', la convierte si es necesario y 
    devuelve True si se invirtió correctamente.
    """
    try:
        img = Image.open(ruta)
        # Convertir a RGB si es indexada
        if img.mode == 'P':
            img = img.convert("RGB")
        # Si tiene canal alfa, separamos alfa y trabajamos sobre RGB
        if img.mode == 'RGBA':
            r, g, b, a = img.split()
            rgb_img = Image.merge("RGB", (r, g, b))
            inverted = ImageOps.invert(rgb_img)
            r2, g2, b2 = inverted.split()
            img_invertida = Image.merge("RGBA", (r2, g2, b2, a))
        elif img.mode in ['RGB', 'L']:
            img_invertida = ImageOps.invert(img)
        else:
            # Convertir otros modos a RGB
            img_invertida = ImageOps.invert(img.convert("RGB"))
        img_invertida.save(ruta)
        return True
    except Exception as e:
        print(f"Error procesando {ruta}: {e}")
        return False

def procesar_carpeta(carpeta):
    total = 0
    procesadas = 0
    errores = 0
    for root_dir, _, files in os.walk(carpeta):
        for file in files:
            ruta = os.path.join(root_dir, file)
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                total += 1
                if invertir_imagen(ruta):
                    procesadas += 1
                else:
                    errores += 1
    return total, procesadas, errores

def procesar_archivo_o_carpeta(ruta):
    if os.path.isdir(ruta):
        return procesar_carpeta(ruta)
    else:
        if ruta.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            total = 1
            procesadas = 1 if invertir_imagen(ruta) else 0
            errores = 0 if procesadas == 1 else 1
            return total, procesadas, errores
    return 0, 0, 0

def drop(event):
    files = root.tk.splitlist(event.data)
    total_global = 0
    procesadas_global = 0
    errores_global = 0
    for f in files:
        ruta = f.strip()
        if os.path.exists(ruta):
            total, procesadas, errores = procesar_archivo_o_carpeta(ruta)
            total_global += total
            procesadas_global += procesadas
            errores_global += errores
        else:
            print(f"La ruta no existe: {ruta}")
    if total_global == 0:
        messagebox.showinfo("Proceso completado", "No se encontraron imágenes para procesar.")
    else:
        mensaje = f"Se procesaron {procesadas_global} de {total_global} imágenes."
        if errores_global:
            mensaje += f"\nHubo {errores_global} errores (revisa la consola para más detalles)."
        messagebox.showinfo("Proceso completado", mensaje)

def seleccionar_carpeta():
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta con imágenes")
    if carpeta:
        total, procesadas, errores = procesar_carpeta(carpeta)
        if total == 0:
            messagebox.showinfo("Proceso completado", "No se encontraron imágenes para procesar.")
        else:
            mensaje = f"Se procesaron {procesadas} de {total} imágenes."
            if errores:
                mensaje += f"\nHubo {errores} errores (revisa la consola para más detalles)."
            messagebox.showinfo("Proceso completado", mensaje)

# Configuración de la ventana principal usando TkinterDnD para drag and drop
root = TkinterDnD.Tk()
root.title("Inversor de Colores - Drag and Drop")
root.geometry("500x300")

# Etiqueta con instrucciones y fondo destacado
instrucciones = (
    "Arrastra y suelta aquí archivos o carpetas con imágenes\n"
    "para invertir sus colores.\n\n"
    "O haz clic en 'Seleccionar carpeta' para elegir manualmente."
)
label = tk.Label(root, text=instrucciones, wraplength=480, justify="center", bg="lightgreen", relief="raised", bd=2)
label.pack(pady=20, padx=20, fill="both", expand=True)

# Registrar la etiqueta como destino de drop
label.drop_target_register(DND_FILES)
label.dnd_bind('<<Drop>>', drop)

# Botón para seleccionar carpeta manualmente
boton = tk.Button(root, text="Seleccionar carpeta", command=seleccionar_carpeta)
boton.pack(pady=10)

root.mainloop()
