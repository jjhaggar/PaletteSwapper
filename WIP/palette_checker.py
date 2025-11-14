#!/usr/bin/env python3
import os
import json
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image

CONFIG_FILE = "palettechecker_config.txt"

# --- Configuration Functions ---

def load_config():
    """Load configuration from CONFIG_FILE if exists."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_config(config):
    """Save configuration to CONFIG_FILE."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
    except Exception as e:
        print("Error saving config:", e)

# --- Helper Functions ---

def get_image_files(directory):
    """Return a list of PNG image file paths in the given directory."""
    supported_ext = ('.png', '.PNG')
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(supported_ext)]

def confirm_overwrite(filepath):
    """Ask the user if they want to overwrite an existing file."""
    return messagebox.askyesno("Overwrite File?", f"The file\n{filepath}\nalready exists. Overwrite?")

def convert_image_to_rgb(image_path, output_dir, prefix, suffix):
    """Convert the image to RGB mode if needed and save it in the output directory."""
    try:
        img = Image.open(image_path)
    except Exception as e:
        messagebox.showerror("Error", f"Error opening image {image_path}:\n{e}")
        return

    if img.mode == "P":
        img = img.convert("RGB")
    
    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)
    output_filename = f"{prefix}{name}{suffix}{ext}"
    output_path = os.path.join(output_dir, output_filename)
    
    if os.path.exists(output_path):
        if not confirm_overwrite(output_path):
            return

    try:
        img.save(output_path)
    except Exception as e:
        messagebox.showerror("Error", f"Error saving image {output_path}:\n{e}")

def extract_colors(image_path):
    """
    Return a set of colors from the image (works for RGB or RGBA images).
    Discards any pixel that is fully transparent (alpha == 0).
    """
    try:
        img = Image.open(image_path)
    except Exception as e:
        messagebox.showerror("Error", f"Error opening image {image_path}:\n{e}")
        return set()

    if img.mode == "P":
        img = img.convert("RGBA")
    elif img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    
    raw_colors = set(img.getdata())
    # Excluir píxeles totalmente transparentes (alpha == 0)
    colors = {color for color in raw_colors if not (len(color) == 4 and color[3] == 0)}
    return colors

def generate_palette_image(palette_rows, output_dir, add_datetime_suffix, save_png=True):
    """
    Generate a palette image composed of one row per group.
    Each row contains the colors of that group. If a row has fewer pixels
    than the maximum width, the remaining pixels are filled with transparent pixels.
    The image is created in mode "RGBA" (transparent background).

    Si save_png es True se guarda el PNG; en caso contrario solo se devuelve el objeto Image.
    """
    if not palette_rows:
        messagebox.showwarning("Warning", "No colors selected to generate palette image.")
        return None

    max_width = max(len(row) for row in palette_rows)
    num_rows = len(palette_rows)
    
    palette_img = Image.new("RGBA", (max_width, num_rows), (0, 0, 0, 0))
    
    for row_index, row in enumerate(palette_rows):
        for col_index, color in enumerate(row):
            palette_img.putpixel((col_index, row_index), color)
    
    base_filename = "palette"
    if add_datetime_suffix:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename += f"_{timestamp}"
    png_output_path = os.path.join(output_dir, base_filename + ".png")
    
    if save_png:
        if os.path.exists(png_output_path):
            if not confirm_overwrite(png_output_path):
                return palette_img
        try:
            palette_img.save(png_output_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving palette image:\n{e}")
    
    return palette_img

def export_palette_gif(palette_img, output_dir, add_datetime_suffix):
    """
    Export the given palette image in GIF format.
    A pixel is considered semitransparent if its alpha is > 0 and < 255.
    """
    semitransparent_found = False
    for pixel in palette_img.getdata():
        if len(pixel) == 4 and 0 < pixel[3] < 255:
            semitransparent_found = True
            break

    if semitransparent_found:
        cont = messagebox.askyesno("Transparency Warning",
                                     "The palette contains semitransparent colors.\n"
                                     "When exporting to GIF these will be lost.\n"
                                     "Do you want to continue exporting to GIF?")
        if not cont:
            return

    gif_img = palette_img.convert("P", palette=Image.ADAPTIVE)
    base_filename = "palette"
    if add_datetime_suffix:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename += f"_{timestamp}"
    gif_output_path = os.path.join(output_dir, base_filename + ".gif")
    
    if os.path.exists(gif_output_path):
        if not confirm_overwrite(gif_output_path):
            return
    try:
        gif_img.save(gif_output_path, save_all=True)
    except Exception as e:
        messagebox.showerror("Error", f"Error saving palette GIF:\n{e}")

def generate_log(common_colors, image_colors, output_dir):
    """
    Generate a log file with:
      - Common Colors (present in all images)
      - Unique Colors by Image (colors appearing only in one image)
      - Almost Common Colors (colors that appear in more than one image, with count and listing of images)
    """
    color_frequency = {}
    color_images = {}
    for image_name, colors in image_colors.items():
        for color in colors:
            color_frequency[color] = color_frequency.get(color, 0) + 1
            color_images.setdefault(color, []).append(image_name)
    
    num_images = len(image_colors)
    unique_colors_by_image = {
        image: {color for color in colors if color_frequency[color] == 1}
        for image, colors in image_colors.items()
    }
    almost_common = {
        color: (color_frequency[color], color_images[color])
        for color in color_frequency
        if color_frequency[color] > 1 and color_frequency[color] < num_images
    }
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"palette_log_{timestamp}.txt"
    log_path = os.path.join(output_dir, log_filename)
    
    try:
        with open(log_path, "w") as log_file:
            log_file.write("Common Colors:\n")
            for color in sorted(common_colors):
                log_file.write(f"{color}\n")
            
            log_file.write("\nUnique Colors by Image:\n")
            for image_name, unique_colors in unique_colors_by_image.items():
                if unique_colors:
                    log_file.write(f"\nImage: {image_name}\n")
                    for color in sorted(unique_colors):
                        log_file.write(f"{color}\n")
            
            log_file.write("\nAlmost Common Colors:\n")
            for color, (freq, _) in almost_common.items():
                log_file.write(f"{color}: appears in {freq} images\n")
            
            log_file.write("\nAlmost Common Colors Summary:\n")
            for color, (freq, images) in almost_common.items():
                log_file.write(f"{color}: appears in {freq} images ({', '.join(images)})\n")
    except Exception as e:
        messagebox.showerror("Error", f"Error writing log file:\n{e}")

# --- Main Application Class ---

class PaletteCheckerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.config_data = load_config()
        default_geometry = "800x600"
        self.geometry(self.config_data.get("window_geometry", default_geometry))
        self.title("Palette Checker")
        self.create_widgets()
        self.load_previous_config()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_widgets(self):
        # Row 0: Input Directory
        self.input_dir_label = ttk.Label(self, text="Input Directory:")
        self.input_dir_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.input_dir_entry = ttk.Entry(self, width=80)
        self.input_dir_entry.grid(row=0, column=1, padx=5, pady=5)
        self.input_dir_button = ttk.Button(self, text="Browse...", command=self.select_input_directory)
        self.input_dir_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Row 1: Output Directory
        self.output_dir_label = ttk.Label(self, text="Output Directory:")
        self.output_dir_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.output_dir_entry = ttk.Entry(self, width=80)
        self.output_dir_entry.grid(row=1, column=1, padx=5, pady=5)
        self.output_dir_button = ttk.Button(self, text="Browse...", command=self.select_output_directory)
        self.output_dir_button.grid(row=1, column=2, padx=5, pady=5)
        
        # Row 2: Prefix and Suffix
        self.prefix_label = ttk.Label(self, text="Prefix:")
        self.prefix_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.prefix_entry = ttk.Entry(self, width=20)
        self.prefix_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.suffix_label = ttk.Label(self, text="Suffix:")
        self.suffix_label.grid(row=2, column=2, padx=5, pady=5, sticky="e")
        self.suffix_entry = ttk.Entry(self, width=20)
        self.suffix_entry.grid(row=2, column=3, padx=5, pady=5, sticky="w")
        
        # Row 3: Separator
        sep1 = ttk.Separator(self, orient="horizontal")
        sep1.grid(row=3, column=0, columnspan=4, sticky="ew", pady=5)
        
        # Row 4: Group Label for Colors
        group_label1 = ttk.Label(self, text="Colors to add to palette", font=("TkDefaultFont", 10, "bold"))
        group_label1.grid(row=4, column=0, columnspan=4, sticky="w", padx=5, pady=2)
        
        # Row 5: Checkbuttons for color groups
        self.include_common_var = tk.BooleanVar(value=self.config_data.get("include_common", True))
        self.common_check = ttk.Checkbutton(self, text="Common", variable=self.include_common_var)
        self.common_check.grid(row=5, column=0, padx=5, pady=5)
        
        self.include_almost_var = tk.BooleanVar(value=self.config_data.get("include_almost", True))
        self.almost_check = ttk.Checkbutton(self, text="Almost", variable=self.include_almost_var)
        self.almost_check.grid(row=5, column=1, padx=5, pady=5)
        
        self.include_unique_var = tk.BooleanVar(value=self.config_data.get("include_unique", True))
        self.unique_check = ttk.Checkbutton(self, text="Unique", variable=self.include_unique_var)
        self.unique_check.grid(row=5, column=2, padx=5, pady=5)
        
        # Row 6: Separator
        sep2 = ttk.Separator(self, orient="horizontal")
        sep2.grid(row=6, column=0, columnspan=4, sticky="ew", pady=5)
        
        # Row 7: Group Label for Save Options
        group_label2 = ttk.Label(self, text="Save palette", font=("TkDefaultFont", 10, "bold"))
        group_label2.grid(row=7, column=0, columnspan=4, sticky="w", padx=5, pady=2)
        
        # Row 8: Checkbuttons for save options
        self.export_png_var = tk.BooleanVar(value=self.config_data.get("export_png", True))
        self.png_check = ttk.Checkbutton(self, text="as PNG", variable=self.export_png_var)
        self.png_check.grid(row=8, column=0, padx=5, pady=5)
        
        self.export_gif_var = tk.BooleanVar(value=self.config_data.get("export_gif", True))
        self.gif_check = ttk.Checkbutton(self, text="as GIF", variable=self.export_gif_var)
        self.gif_check.grid(row=8, column=1, padx=5, pady=5)
        
        self.datetime_suffix_var = tk.BooleanVar(value=self.config_data.get("datetime_suffix", True))
        self.suffix_check = ttk.Checkbutton(self, text="with Date", variable=self.datetime_suffix_var)
        self.suffix_check.grid(row=8, column=2, padx=5, pady=5)
        
        # Row 9: Separator
        sep3 = ttk.Separator(self, orient="horizontal")
        sep3.grid(row=9, column=0, columnspan=4, sticky="ew", pady=5)
        
        # Row 10: Action Buttons and Show Log Check
        self.convert_button = ttk.Button(self, text="Convert Color Mode", command=self.handle_convert_color_mode)
        self.convert_button.grid(row=10, column=0, padx=5, pady=15)
        self.check_button = ttk.Button(self, text="Check Colors", command=self.handle_check_colors)
        self.check_button.grid(row=10, column=1, padx=5, pady=15)
        self.display_log_var = tk.BooleanVar(value=self.config_data.get("display_log", True))
        self.log_check = ttk.Checkbutton(self, text="Show Log", variable=self.display_log_var)
        self.log_check.grid(row=10, column=2, padx=5, pady=15)
    
    def load_previous_config(self):
        """Pre-populate fields from configuration."""
        if "input_dir" in self.config_data:
            self.input_dir_entry.insert(0, self.config_data["input_dir"])
        if "output_dir" in self.config_data:
            self.output_dir_entry.insert(0, self.config_data["output_dir"])
        if "prefix" in self.config_data:
            self.prefix_entry.insert(0, self.config_data["prefix"])
        if "suffix" in self.config_data:
            self.suffix_entry.insert(0, self.config_data["suffix"])
    
    def select_input_directory(self):
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            self.input_dir_entry.delete(0, tk.END)
            self.input_dir_entry.insert(0, directory)
    
    def select_output_directory(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, directory)
    
    def ask_output_directory(self, current_input):
        response = messagebox.askyesno("Output Directory Not Specified",
                                       "No output directory specified.\nDo you want to use the input directory as output?")
        if response:
            return current_input
        else:
            return None

    def handle_convert_color_mode(self):
        input_dir = self.input_dir_entry.get().strip()
        output_dir = self.output_dir_entry.get().strip()
        prefix = self.prefix_entry.get()
        suffix = self.suffix_entry.get()
        
        if not os.path.isdir(input_dir):
            messagebox.showerror("Error", "Invalid input directory.")
            return
        if output_dir == "":
            result = self.ask_output_directory(input_dir)
            if result is None:
                return
            output_dir = result
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, output_dir)
        elif not os.path.isdir(output_dir):
            messagebox.showerror("Error", "Invalid output directory.")
            return
        
        image_files = get_image_files(input_dir)
        if not image_files:
            messagebox.showinfo("Info", "No PNG images found in the input directory.")
            return
        
        for image_path in image_files:
            convert_image_to_rgb(image_path, output_dir, prefix, suffix)
        messagebox.showinfo("Success", "Conversion complete.")
    
    def handle_check_colors(self):
        input_dir = self.input_dir_entry.get().strip()
        output_dir = self.output_dir_entry.get().strip()
        
        if not os.path.isdir(input_dir):
            messagebox.showerror("Error", "Invalid input directory.")
            return
        if output_dir == "":
            result = self.ask_output_directory(input_dir)
            if result is None:
                return
            output_dir = result
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, output_dir)
        elif not os.path.isdir(output_dir):
            messagebox.showerror("Error", "Invalid output directory.")
            return
        
        image_files = get_image_files(input_dir)
        if not image_files:
            messagebox.showinfo("Info", "No PNG images found in the input directory.")
            return
        
        image_colors = {}
        for image_path in image_files:
            colors = extract_colors(image_path)
            image_name = os.path.basename(image_path)
            image_colors[image_name] = colors
        
        common_colors = set.intersection(*image_colors.values()) if image_colors else set()
        
        color_frequency = {}
        for colors in image_colors.values():
            for color in colors:
                color_frequency[color] = color_frequency.get(color, 0) + 1
        num_images = len(image_colors)
        almost_common_set = {color for color, count in color_frequency.items() if count > 1 and count < num_images}
        unique_set = {color for color, count in color_frequency.items() if count == 1}
        
        palette_rows = []
        if self.include_common_var.get():
            palette_rows.append(sorted(common_colors))
        if self.include_almost_var.get():
            palette_rows.append(sorted(almost_common_set))
        if self.include_unique_var.get():
            palette_rows.append(sorted(unique_set))
        
        generate_log(common_colors, image_colors, output_dir)
        
        palette_img = None
        if self.export_png_var.get() or self.export_gif_var.get():
            palette_img = generate_palette_image(palette_rows, output_dir, self.datetime_suffix_var.get(), save_png=self.export_png_var.get())
        
        if palette_img and self.export_gif_var.get():
            export_palette_gif(palette_img, output_dir, self.datetime_suffix_var.get())
        
        log_files = sorted([f for f in os.listdir(output_dir) if f.startswith("palette_log_") and f.endswith(".txt")])
        if log_files and self.display_log_var.get():
            latest_log = os.path.join(output_dir, log_files[-1])
            try:
                with open(latest_log, "r") as log_file:
                    log_content = log_file.read()
                self.show_log_window(log_content)
            except Exception as e:
                messagebox.showerror("Error", f"Error reading log file:\n{e}")
        
        messagebox.showinfo("Success", "Color check complete.")
    
    def show_log_window(self, log_content):
        """Open a separate window to display the log."""
        log_window = tk.Toplevel(self)
        log_window.title("Log")
        text_widget = tk.Text(log_window, wrap="none", width=80, height=25)
        text_widget.insert(tk.END, log_content)
        text_widget.configure(state="disabled")
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(log_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
    
    def on_close(self):
        config = {
            "input_dir": self.input_dir_entry.get().strip(),
            "output_dir": self.output_dir_entry.get().strip(),
            "window_geometry": self.geometry(),
            "display_log": self.display_log_var.get(),
            "include_common": self.include_common_var.get(),
            "include_almost": self.include_almost_var.get(),
            "include_unique": self.include_unique_var.get(),
            "export_png": self.export_png_var.get(),
            "export_gif": self.export_gif_var.get(),
            "datetime_suffix": self.datetime_suffix_var.get(),
            "prefix": self.prefix_entry.get(),
            "suffix": self.suffix_entry.get()
        }
        save_config(config)
        self.destroy()

# --- Main Execution ---

if __name__ == "__main__":
    app = PaletteCheckerApp()
    app.mainloop()
