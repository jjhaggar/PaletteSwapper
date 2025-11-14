import os
import datetime
from tkinter import filedialog, messagebox, BooleanVar, Checkbutton
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image

def tiene_semitransparencia(ruta):
    """
    Abre la imagen en 'ruta', la convierte a RGBA y revisa
    si el canal alfa contiene algún valor distinto de 0 y 255.
    Retorna True si se encuentra semitransparencia, False en caso contrario.
    """
    try:
        img = Image.open(ruta).convert("RGBA")
        alpha = img.split()[-1]  # Obtiene el canal alfa
        # Itera por cada valor alfa; si alguno no es 0 ni 255, hay semitransparencia
        for a in alpha.getdata():
            if a not in (0, 255):
                return True
        return False
    except Exception as e:
        print(f"Error comprobando {ruta}: {e}")
        return False

def procesar_archivo(ruta):
    """
    Procesa un único archivo de imagen.
    Retorna una tupla: (total_imagenes, con_semitransparencia, sin_semitransparencia, errores)
    """
    if not ruta.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        return 0, 0, 0, 0
    try:
        total = 1
        if tiene_semitransparencia(ruta):
            return total, 1, 0, 0
        else:
            return total, 0, 1, 0
    except Exception as e:
        print(f"Error procesando {ruta}: {e}")
        return 1, 0, 0, 1

def procesar_carpeta(carpeta, recursive=True):
    """
    Recorre la carpeta (y opcionalmente sus subdirectorios) y procesa
    cada imagen encontrada. Retorna:
    (total_imagenes, con_semitransparencia, sin_semitransparencia, errores, lista_de_rutas_con_semitransparencia)
    """
    total = 0
    semitransparent = 0
    non_semitransparent = 0
    errores = 0
    semitransparent_files = []
    if recursive:
        for root_dir, _, files in os.walk(carpeta):
            for file in files:
                ruta = os.path.join(root_dir, file)
                if ruta.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    t, s, ns, err = procesar_archivo(ruta)
                    total += t
                    semitransparent += s
                    non_semitransparent += ns
                    errores += err
                    if s == 1:
                        semitransparent_files.append(os.path.abspath(ruta))
    else:
        for file in os.listdir(carpeta):
            ruta = os.path.join(carpeta, file)
            if os.path.isfile(ruta) and ruta.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                t, s, ns, err = procesar_archivo(ruta)
                total += t
                semitransparent += s
                non_semitransparent += ns
                errores += err
                if s == 1:
                    semitransparent_files.append(os.path.abspath(ruta))
    return total, semitransparent, non_semitransparent, errores, semitransparent_files

def procesar_archivo_o_carpeta(ruta, recursive=True):
    """
    Determina si 'ruta' es un archivo o una carpeta y la procesa
    en consecuencia.
    """
    if os.path.isdir(ruta):
        return procesar_carpeta(ruta, recursive)
    else:
        if ruta.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            t, s, ns, err = procesar_archivo(ruta)
            st_files = [os.path.abspath(ruta)] if s == 1 else []
            return t, s, ns, err, st_files
    return 0, 0, 0, 0, []

def generar_log(semitransparent_files):
    """
    Genera un archivo de log con la lista de archivos que tienen semitransparencia.
    El nombre del archivo incluye fecha y hora para evitar sobrescribir.
    """
    if semitransparent_files:
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"semitransparency_log_{now}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Log de imágenes con semitransparencia generado el {now}\n")
            for path in semitransparent_files:
                f.write(path + "\n")
        return filename
    return None

def drop(event):
    """
    Función invocada al arrastrar y soltar archivos o carpetas.
    Procesa cada uno según la opción de recursividad seleccionada.
    """
    files = root.tk.splitlist(event.data)
    total_global = 0
    semitransparent_global = 0
    non_semitransparent_global = 0
    errors_global = 0
    global semitransparent_files_global
    semitransparent_files_global = []
    for f in files:
        ruta = f.strip()
        if os.path.exists(ruta):
            t, s, ns, err, st_files = procesar_archivo_o_carpeta(ruta, recursive=recursive_var.get())
            total_global += t
            semitransparent_global += s
            non_semitransparent_global += ns
            errors_global += err
            semitransparent_files_global.extend(st_files)
        else:
            print(f"La ruta no existe: {ruta}")
    mensaje = f"Total imágenes procesadas: {total_global}\n"
    mensaje += f"Imágenes con semitransparencia: {semitransparent_global}\n"
    mensaje += f"Imágenes sin semitransparencia: {non_semitransparent_global}\n"
    if errors_global:
        mensaje += f"Errores: {errors_global}\n"
    if semitransparent_global > 0:
        log_filename = generar_log(semitransparent_files_global)
        mensaje += f"\nSe ha generado un log: {log_filename}"
    messagebox.showinfo("Resultado", mensaje)

def seleccionar_carpeta():
    """
    Abre un diálogo para seleccionar una carpeta y procesa las imágenes en ella.
    """
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta con imágenes")
    if carpeta:
        t, s, ns, err, st_files = procesar_carpeta(carpeta, recursive=recursive_var.get())
        global semitransparent_files_global
        semitransparent_files_global = st_files
        mensaje = f"Total imágenes procesadas: {t}\n"
        mensaje += f"Imágenes con semitransparencia: {s}\n"
        mensaje += f"Imágenes sin semitransparencia: {ns}\n"
        if err:
            mensaje += f"Errores: {err}\n"
        if s > 0:
            log_filename = generar_log(semitransparent_files_global)
            mensaje += f"\nSe ha generado un log: {log_filename}"
        messagebox.showinfo("Resultado", mensaje)

# Configuración de la ventana principal con TkinterDnD2
root = TkinterDnD.Tk()
root.title("Chequeador de Semitransparencia")
root.geometry("500x350")

# Variable para la opción recursiva (marcada por defecto)
recursive_var = BooleanVar(value=True)

# Etiqueta con instrucciones y fondo destacado (color verde claro)
instrucciones = (
    "Arrastra y suelta aquí archivos o carpetas con imágenes\n"
    "para comprobar si tienen semitransparencia (canal alfa con valores distintos de 0 y 255).\n\n"
    "O haz clic en 'Seleccionar carpeta' para elegir manualmente.\n\n"
    "La opción 'Procesar recursivamente subdirectorios' está marcada por defecto."
)
label = tk.Label(root, text=instrucciones, wraplength=480, justify="center", 
                 bg="lightgreen", relief="raised", bd=2)
label.pack(pady=10, padx=10, fill="both", expand=True)

# Registrar la etiqueta como destino de drop
label.drop_target_register(DND_FILES)
label.dnd_bind('<<Drop>>', drop)

# Checkbutton para activar o desactivar la búsqueda recursiva
chk_recursive = Checkbutton(root, text="Procesar recursivamente subdirectorios", variable=recursive_var)
chk_recursive.pack(pady=5)

# Botón para seleccionar carpeta manualmente
boton = tk.Button(root, text="Seleccionar carpeta", command=seleccionar_carpeta)
boton.pack(pady=10)

root.mainloop()
