#!/usr/bin/env python3
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image
from datetime import datetime

class ConvertToIndexApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Convertir Imágenes a Modo Indexado")
        self.geometry("600x650")
        
        # Variables de configuración
        self.folder_path = tk.StringVar()
        self.palette_path = tk.StringVar()
        self.prefix = tk.StringVar()
        self.suffix = tk.StringVar()
        
        # Opciones de log
        self.save_log_var = tk.BooleanVar(value=True)
        self.log_path_mode = tk.StringVar(value="relative")  # "relative" o "absolute"
        self.color_format_var = tk.StringVar(value="tuple")  # "tuple" o "hex"
        # El nombre del archivo log se generará al iniciar la conversión
        
        self.create_widgets()
    
    def create_widgets(self):
        # Carpeta de imágenes
        folder_frame = ttk.LabelFrame(self, text="Carpeta de Imágenes (Arrastrar y soltar)")
        folder_frame.pack(fill="x", padx=10, pady=5)
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=80)
        self.folder_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.folder_entry.drop_target_register(DND_FILES)
        self.folder_entry.dnd_bind('<<Drop>>', self.drop_folder)
        browse_folder_btn = ttk.Button(folder_frame, text="Seleccionar...", command=self.browse_folder)
        browse_folder_btn.pack(side="left", padx=5, pady=5)
        
        # Paleta a usar
        palette_frame = ttk.LabelFrame(self, text="Paleta a Usar (Arrastrar y soltar)")
        palette_frame.pack(fill="x", padx=10, pady=5)
        self.palette_entry = ttk.Entry(palette_frame, textvariable=self.palette_path, width=80)
        self.palette_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.palette_entry.drop_target_register(DND_FILES)
        self.palette_entry.dnd_bind('<<Drop>>', self.drop_palette)
        browse_palette_btn = ttk.Button(palette_frame, text="Seleccionar...", command=self.browse_palette)
        browse_palette_btn.pack(side="left", padx=5, pady=5)
        
        # Opciones de nombres para archivos de salida
        options_frame = ttk.LabelFrame(self, text="Opciones de Nombres")
        options_frame.pack(fill="x", padx=10, pady=5)
        prefix_label = ttk.Label(options_frame, text="Prefijo:")
        prefix_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        prefix_entry = ttk.Entry(options_frame, textvariable=self.prefix, width=20)
        prefix_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        suffix_label = ttk.Label(options_frame, text="Sufijo:")
        suffix_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        suffix_entry = ttk.Entry(options_frame, textvariable=self.suffix, width=20)
        suffix_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # Opciones para el manejo del log
        log_frame = ttk.LabelFrame(self, text="Opciones de Log")
        log_frame.pack(fill="x", padx=10, pady=5)
        save_log_chk = ttk.Checkbutton(log_frame, text="Guardar log", variable=self.save_log_var)
        save_log_chk.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        rb_label = ttk.Label(log_frame, text="Formato de rutas en el log:")
        rb_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        relative_rb = ttk.Radiobutton(log_frame, text="Rutas relativas", variable=self.log_path_mode, value="relative")
        relative_rb.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        absolute_rb = ttk.Radiobutton(log_frame, text="Rutas absolutas", variable=self.log_path_mode, value="absolute")
        absolute_rb.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        color_format_label = ttk.Label(log_frame, text="Formato de colores en log:")
        color_format_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        tuple_rb = ttk.Radiobutton(log_frame, text="Formato actual", variable=self.color_format_var, value="tuple")
        tuple_rb.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        hex_rb = ttk.Radiobutton(log_frame, text="Código hexadecimal", variable=self.color_format_var, value="hex")
        hex_rb.grid(row=2, column=2, padx=5, pady=5, sticky="w")
        
        # Botón para iniciar la conversión
        convert_btn = ttk.Button(self, text="Convertir Imágenes", command=self.start_conversion)
        convert_btn.pack(pady=10)
        
        # Área de texto para mostrar el estado y log en la UI
        self.status_text = tk.Text(self, height=12)
        self.status_text.pack(fill="both", padx=10, pady=10, expand=True)
    
    def drop_folder(self, event):
        files = self.tk.splitlist(event.data)
        if files:
            folder = files[0]
            if os.path.isdir(folder):
                self.folder_path.set(folder)
            else:
                messagebox.showerror("Error", "Por favor, suelta una carpeta.")
    
    def drop_palette(self, event):
        files = self.tk.splitlist(event.data)
        if files:
            file = files[0]
            if os.path.isfile(file):
                self.palette_path.set(file)
            else:
                messagebox.showerror("Error", "Por favor, suelta un archivo de paleta.")
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
    
    def browse_palette(self):
        file = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if file:
            self.palette_path.set(file)
    
    def log(self, message):
        self.status_text.insert("end", message + "\n")
        self.status_text.see("end")
        self.update()
    
    def write_error_log(self, message):
        if not self.save_log_var.get():
            return
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.error_log_filename, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def write_aggregated_log(self, message):
        if not self.save_log_var.get():
            return
        with open(self.error_log_filename, "a", encoding="utf-8") as f:
            f.write(message + "\n")
    
    def format_log_path(self, path):
        try:
            folder = self.folder_path.get()
            if self.log_path_mode.get() == "relative":
                return os.path.relpath(path, folder)
            else:
                return os.path.abspath(path)
        except Exception:
            return path
    
    def start_conversion(self):
        folder = self.folder_path.get()
        palette_file = self.palette_path.get()
        prefix = self.prefix.get()
        suffix = self.suffix.get()
        
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Error", "Selecciona una carpeta válida de imágenes.")
            return
        if not palette_file or not os.path.isfile(palette_file):
            messagebox.showerror("Error", "Selecciona un archivo de paleta válido.")
            return
        
        # Crear un nuevo archivo de log con fecha y hora actual
        self.error_log_filename = f"conversion_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            palette_img = Image.open(palette_file).convert("P")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la paleta: {e}")
            return
        
        # Obtener el índice de transparencia de la paleta (si lo tiene)
        trans_idx = palette_img.info.get('transparency')
        if trans_idx is None:
            self.log("Advertencia: La paleta no tiene índice de transparencia. La transparencia no se conservará.")
        
        # Preparar el conjunto de colores permitidos a partir de la paleta
        palette_list = palette_img.getpalette()
        allowed_colors = set()
        for i in range(0, len(palette_list), 3):
            allowed_colors.add((palette_list[i], palette_list[i+1], palette_list[i+2]))
        
        allowed_ext = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
        
        # Variables para agrupar información
        total_files = 0
        converted_files = 0
        already_indexed = []
        semitransparent_files = []
        unknown_colors_details = []   # Lista de tuplas: (ruta_formateada, [lista de colores])
        unknown_colors_aggregated = {}  # Dict: color -> cantidad de imágenes en las que aparece
        conversion_errors = []
        
        # Recorrer de forma recursiva la carpeta
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(allowed_ext):
                    total_files += 1
                    file_path = os.path.join(root, file)
                    formatted_path = self.format_log_path(file_path)
                    
                    try:
                        with Image.open(file_path) as img:
                            # Si la imagen ya está en modo indexado, agrupar y omitir conversión
                            if img.mode == "P":
                                already_indexed.append(formatted_path)
                                continue
                            
                            # Convertir a RGBA para analizar transparencia y colores
                            rgba_img = img.convert("RGBA")
                            data = list(rgba_img.getdata())
                            
                            semitransparent_flag = False
                            unknown_colors = set()
                            
                            for pixel in data:
                                r, g, b, a = pixel
                                if a not in (0, 255):
                                    semitransparent_flag = True
                                if a == 255 and (r, g, b) not in allowed_colors:
                                    unknown_colors.add((r, g, b))
                            
                            if semitransparent_flag:
                                semitransparent_files.append(formatted_path)
                            
                            if unknown_colors:
                                unknown_colors_sorted = sorted(unknown_colors)
                                unknown_colors_details.append((formatted_path, unknown_colors_sorted))
                                for color in unknown_colors_sorted:
                                    unknown_colors_aggregated[color] = unknown_colors_aggregated.get(color, 0) + 1
                            
                            # Proceder a la conversión
                            rgb_img = rgba_img.convert("RGB")
                            quant_img = rgb_img.quantize(palette=palette_img, dither=Image.FLOYDSTEINBERG)
                            
                            if trans_idx is not None:
                                quant_data = list(quant_img.getdata())
                                new_data = [trans_idx if data[i][3] == 0 else quant_data[i] for i in range(len(data))]
                                quant_img.putdata(new_data)
                                quant_img.info["transparency"] = trans_idx
                            
                            name, _ = os.path.splitext(file)
                            new_name = f"{prefix}{name}{suffix}.png"
                            new_path = os.path.join(root, new_name)
                            quant_img.save(new_path)
                            self.log(f"Convertido: {self.format_log_path(new_path)}")
                            converted_files += 1
                    except Exception as e:
                        err_msg = f"Error al convertir {formatted_path}: {e}"
                        conversion_errors.append(err_msg)
                        self.log(err_msg)
                        if self.save_log_var.get():
                            self.write_error_log(err_msg)
        
        # Construir el bloque agrupado para el log
        aggregated_msg = ""
        if already_indexed:
            aggregated_msg += "Imágenes ya en modo indexado:\n" + "\n".join(already_indexed) + "\n\n"
        if semitransparent_files:
            aggregated_msg += "Imágenes con píxeles semitransparentes:\n" + "\n".join(semitransparent_files) + "\n\n"
        if unknown_colors_details:
            aggregated_msg += "Imágenes con colores no presentes en la paleta:\n"
            for path, colors in unknown_colors_details:
                if self.color_format_var.get() == "hex":
                    colors_formatted = [f"{r:02X}{g:02X}{b:02X}" for (r, g, b) in colors]
                else:
                    colors_formatted = colors
                aggregated_msg += f"{path} | {len(colors)} colores | {colors_formatted}\n"
            aggregated_msg += "\n"
        if unknown_colors_aggregated:
            aggregated_msg += "Lista agregada de colores desconocidos (cantidad de imágenes en las que aparecieron):\n"
            for color, count in sorted(unknown_colors_aggregated.items()):
                if self.color_format_var.get() == "hex":
                    color_str = f"{color[0]:02X}{color[1]:02X}{color[2]:02X}"
                else:
                    color_str = str(color)
                aggregated_msg += f"{color_str}: {count}\n"
            aggregated_msg += "\n"
        
        # En el resumen, "Total de colores desconocidos encontrados" es el número de colores únicos
        summary_msg = (
            f"Resumen final:\n"
            f"Total de archivos procesados: {total_files}\n"
            f"Imágenes ya en modo indexado: {len(already_indexed)}\n"
            f"Imágenes con píxeles semitransparentes: {len(semitransparent_files)}\n"
            f"Imágenes con colores no presentes en la paleta: {len(unknown_colors_details)}\n"
            f"Total de colores desconocidos encontrados: {len(unknown_colors_aggregated)}\n"
            f"Archivos convertidos: {converted_files}\n"
        )
        aggregated_msg += summary_msg
        
        if self.save_log_var.get():
            self.write_aggregated_log(aggregated_msg)
        
        final_msg = summary_msg
        if conversion_errors:
            final_msg += "\nSe produjeron errores en algunos archivos. Revisa el log para más detalles."
        self.log(final_msg)
        final_msg += f"\n\nLog de errores: {self.error_log_filename}" if self.save_log_var.get() else ""
        messagebox.showinfo("Conversión Completa", final_msg)

if __name__ == "__main__":
    app = ConvertToIndexApp()
    app.mainloop()
