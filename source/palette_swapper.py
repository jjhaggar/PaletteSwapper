import os
import tkinter as tk
from tkinter import filedialog, messagebox, Label
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image

class PaletteReplacerApp:
    def __init__(self, root):
        self.root = root
        root.title('Palette Replacer')

        # GUI Setup
        tk.Label(root, text='Image Directory:').grid(row=0, column=0, sticky='w', pady=4, padx=5)
        self.images_dir_entry = tk.Entry(root, width=50)
        self.images_dir_entry.grid(row=0, column=1, sticky='we', padx=5)
        tk.Button(root, text='Browse', command=self.select_image_dir).grid(row=0, column=2, padx=5)

        tk.Label(root, text='Palette File:').grid(row=1, column=0, sticky='w', pady=4, padx=5)
        self.palette_entry = tk.Entry(root, width=50)
        self.palette_entry.grid(row=1, column=1, sticky='we', padx=5)
        tk.Button(root, text='Browse', command=self.select_palette_file).grid(row=1, column=2, padx=5)

        tk.Label(root, text='Prefix (optional):').grid(row=2, column=0, sticky='w', pady=4, padx=5)
        self.prefix_entry = tk.Entry(root, width=50)
        self.prefix_entry.grid(row=2, column=1, sticky='we', padx=5)

        tk.Label(root, text='Suffix (optional):').grid(row=3, column=0, sticky='w', pady=4, padx=5)
        self.suffix_entry = tk.Entry(root, width=50)
        self.suffix_entry.grid(row=3, column=1, sticky='we', padx=5)
        self.suffix_entry.insert(0, "_palette_swap")

        tk.Label(root, text='Output Directory (optional):').grid(row=4, column=0, sticky='w', pady=4, padx=5)
        self.output_dir_entry = tk.Entry(root, width=50)
        self.output_dir_entry.grid(row=4, column=1, sticky='we', padx=5)
        tk.Button(root, text='Browse', command=self.select_output_dir).grid(row=4, column=2, padx=5)

        self.warning_label = Label(root, text="", fg='red')
        self.warning_label.grid(row=5, column=0, columnspan=3)

        tk.Button(root, text='Apply Palette Swap', command=self.apply_palette_to_images).grid(row=6, column=0, columnspan=3, pady=10)

        # Drag & Drop Setup
        self.images_dir_entry.drop_target_register(DND_FILES)
        self.images_dir_entry.dnd_bind('<<Drop>>', self.on_drop_images)

        self.palette_entry.drop_target_register(DND_FILES)
        self.palette_entry.dnd_bind('<<Drop>>', self.on_drop_palette)

        self.output_dir_entry.drop_target_register(DND_FILES)
        self.output_dir_entry.dnd_bind('<<Drop>>', self.on_drop_output_dir)

        # Real-time warning update
        self.images_dir_entry.bind("<KeyRelease>", self.update_warning)
        self.prefix_entry.bind("<KeyRelease>", self.update_warning)
        self.suffix_entry.bind("<KeyRelease>", self.update_warning)
        self.output_dir_entry.bind("<KeyRelease>", self.update_warning)

        self.root.after(500, self.update_warning)

        # Add hints for drag & drop
        self.add_drag_drop_hints()

    def add_drag_drop_hints(self):
        tk.Label(self.root, text='(Drag & Drop supported)').grid(row=0, column=3, padx=5)
        tk.Label(self.root, text='(Drag & Drop supported)').grid(row=1, column=3, padx=5)
        tk.Label(self.root, text='(Drag & Drop supported)').grid(row=4, column=3, padx=5)

    def select_image_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.images_dir_entry.delete(0, tk.END)
            self.images_dir_entry.insert(0, directory)
        self.update_warning()

    def select_palette_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if file_path:
            self.palette_entry.delete(0, tk.END)
            self.palette_entry.insert(0, file_path)
    
    def select_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, directory)
        self.update_warning()

    def on_drop_images(self, event):
        if event.data:
            files = self.root.tk.splitlist(event.data)
            if os.path.isdir(files[0]):
                self.images_dir_entry.delete(0, tk.END)
                self.images_dir_entry.insert(0, files[0])
        self.update_warning()

    def on_drop_palette(self, event):
        if event.data:
            files = self.root.tk.splitlist(event.data)
            if os.path.isfile(files[0]) and files[0].endswith('.png'):
                self.palette_entry.delete(0, tk.END)
                self.palette_entry.insert(0, files[0])

    def on_drop_output_dir(self, event):
        if event.data:
            files = self.root.tk.splitlist(event.data)
            if os.path.isdir(files[0]):
                self.output_dir_entry.delete(0, tk.END)
                self.output_dir_entry.insert(0, files[0])
        self.update_warning()

    def update_warning(self, event=None):
        directory = self.images_dir_entry.get()
        prefix = self.prefix_entry.get()
        suffix = self.suffix_entry.get()
        output_directory = self.output_dir_entry.get() if self.output_dir_entry.get() else directory

        if not os.path.isdir(directory):
            self.warning_label.config(text="")
            return

        warning_text = ""
        for filename in os.listdir(directory):
            if filename.endswith('.png'):
                new_filename = f"{prefix}{filename.replace('.png', '')}{suffix}.png"
                output_path = os.path.join(output_directory, new_filename)
                if os.path.exists(output_path):
                    warning_text = "Warning: Some files will be overwritten."
                    break

        self.warning_label.config(text=warning_text)
        self.root.after(500, self.update_warning)  # Update warning every 500ms

    def apply_palette_to_images(self):
        directory = self.images_dir_entry.get()
        palette_path = self.palette_entry.get()
        prefix = self.prefix_entry.get()
        suffix = self.suffix_entry.get()
        output_directory = self.output_dir_entry.get() if self.output_dir_entry.get() else directory

        if not os.path.isdir(directory):
            messagebox.showerror("Error", "The specified image directory is invalid.")
            return
        
        if not os.path.isfile(palette_path):
            messagebox.showerror("Error", "The specified palette file is invalid.")
            return
        
        if self.warning_label.cget("text"):
            confirm = messagebox.askyesno("Confirmation", "Some files will be overwritten. Do you want to continue?")
            if not confirm:
                return

        try:
            new_palette_image = Image.open(palette_path)
            if new_palette_image.mode != 'P':
                messagebox.showerror("Error", "The palette image is not in indexed palette mode (P).")
                return
            new_palette = new_palette_image.getpalette()
            
            for filename in os.listdir(directory):
                if filename.endswith('.png'):
                    image_path = os.path.join(directory, filename)
                    image = Image.open(image_path)
                    if image.mode == 'P':
                        image.putpalette(new_palette)
                        new_filename = f"{prefix}{filename.replace('.png', '')}{suffix}.png"
                        output_path = os.path.join(output_directory, new_filename)
                        image.save(output_path)
            messagebox.showinfo("Success", "Palette has been successfully applied to all images.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PaletteReplacerApp(root)
    root.mainloop()
