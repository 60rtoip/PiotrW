import tkinter as tk
from tkinter import ttk, filedialog, colorchooser
from PIL import Image, ImageTk
import os
import json
import subprocess
from gradient_utils import setup_macos_window, create_rounded_inner_container, configure_ttk_styles

class AppLauncher(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.geometry("400x300+400+320")  # Below VolumeMixer (10+300+10=320)
        
        # Setup macOS style rounded window
        self.canvas, self.container = setup_macos_window(self, 400, 300, corner_radius=16, 
                                                        bg_color="#1C1C1E", border_color="#2C2C2E", border_width=0)

        # Configure TTK styles for sliders
        configure_ttk_styles()

        # Draw rounded inner container with equal margins (20px from all sides)
        margin = 20
        inner_width = 400 - 2 * margin  # 360
        inner_height = 300 - 2 * margin  # 260
        create_rounded_inner_container(self.canvas, margin, margin, inner_width, inner_height, corner_radius=12, bg_color="#3A3A3C")
        
        # Title bar positioned over the gray container - slightly lighter than outer part
        self.title_bar = tk.Frame(self.canvas, bg="#2A2A2C", height=30)
        self.canvas.create_window(margin, margin, window=self.title_bar, anchor='nw', width=inner_width, height=30)
        
        # Bind drag events to title bar only
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        
        # Menu or custom button on the left side of the title bar
        self.menu_btn = tk.Button(
            self.title_bar,
            text="+",  # lub "+" jeśli ma to być np. dodawanie aplikacji
            bg="#5A5A5C",
            command=self.open_add_dialog,
            fg="white",
            font=("Arial", 10, "bold"),
            bd=0,
            relief='flat',
            activebackground="#6A6A6C"
        )
        self.menu_btn.pack(side='left', padx=10, pady=5)

        # Close button in the title bar (right side)
        self.close_btn = tk.Button(
            self.title_bar,
            text="✕",
            command=self.destroy,
            bg="#FF5F57",
            fg="white",
            font=("Arial", 8, "bold"),
            bd=0,
            relief='flat',
            activebackground="#FF3B30"
        )
        self.close_btn.pack(side='right', padx=10, pady=5)
        
        # Content area for app launcher inside the rounded container (below title bar)
        self.content_frame = tk.Frame(self.canvas, bg="#3A3A3C")
        content_margin = 15
        self.canvas.create_window(margin + content_margin, margin + 30 + 5, window=self.content_frame, anchor='nw', 
                                width=inner_width - 2 * content_margin, height=inner_height - 30 - 15)
        
        # Create scrollable frame for app list
        self.scroll_canvas = tk.Canvas(self.content_frame, bg="#3A3A3C", highlightthickness=0)
        self.scroll_canvas.pack(fill="both", expand=True, padx=5, pady=(5, 5))  # More space for enhanced "Add app" button
        
        # Scrollable frame that will contain all app items
        self.scrollable_frame = tk.Frame(self.scroll_canvas, bg="#3A3A3C")
        self.scroll_canvas_window = self.scroll_canvas.create_window(0, 0, window=self.scrollable_frame, anchor="nw")
        
        # Bind mouse wheel scrolling
        self.scroll_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        
        # Bind canvas resize to update scroll region
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.scroll_canvas.bind("<Configure>", self._on_canvas_configure)
        
        self.app_file = "apps.json"
        self.apps = self.load_apps()
        self.build_ui()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _on_frame_configure(self, event):
        """Update scroll region when frame size changes"""
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Update scrollable frame width when canvas size changes"""
        canvas_width = event.width
        self.scroll_canvas.itemconfig(self.scroll_canvas_window, width=canvas_width)

    def build_ui(self):

        # App list frame inside scrollable frame
        self.app_frame = self.scrollable_frame

        self.refresh_app_list()

        # Add app button at the top (outside scrollable area) - enhanced for better visibility
        add_btn = tk.Button(
            self.content_frame,
            text="+",
            command=self.open_add_dialog,
            bg="#007AFF",
            fg="white",
            font=("Arial", 11, "bold"),
            bd=0,
            relief='flat',
            activebackground="#0056CC",
            cursor="hand2",
            height=2
        )
        add_btn.pack(pady=(8, 0), padx=8, fill="x", side="bottom")

    def refresh_app_list(self):
        for widget in self.app_frame.winfo_children():
            widget.destroy()

        for idx, app in enumerate(self.apps):
            row = tk.Frame(self.app_frame, bg=app.get("color", "#48484A"))
            row.pack(fill="x", pady=3, padx=5)

            if app.get("icon"):
                try:
                    img = Image.open(app["icon"])
                    img = img.resize((20, 20), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    icon_label = tk.Label(row, image=photo, bg=app.get("color", "#48484A"))
                    icon_label.image = photo
                    icon_label.pack(side="left", padx=5)
                except:
                    pass

            label = tk.Label(row, text=app.get("name", os.path.basename(app["path"])), 
                           anchor="w", bg=app.get("color", "#48484A"), fg="white",
                           font=("Arial", 10))
            label.pack(side="left", padx=5, expand=True)

            run_btn = tk.Button(row, text="▶", command=lambda p=app["path"]: self.run_app(p),
                              bg="#5A5A5C", fg="white", font=("Arial", 8), bd=0, 
                              relief='flat', activebackground="#6A6A6C")
            run_btn.pack(side="right", padx=3)

            edit_btn = tk.Button(row, text="✎", command=lambda i=idx: self.edit_app(i),
                               bg="#5A5A5C", fg="white", font=("Arial", 8), bd=0,
                               relief='flat', activebackground="#6A6A6C")
            edit_btn.pack(side="right", padx=3)

            del_btn = tk.Button(row, text="✕", command=lambda i=idx: self.delete_app(i),
                              bg="#FF5F57", fg="white", font=("Arial", 8), bd=0,
                              relief='flat', activebackground="#FF3B30")
            del_btn.pack(side="right", padx=3)

    def load_apps(self):
        if os.path.exists(self.app_file):
            try:
                with open(self.app_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_apps(self):
        try:
            with open(self.app_file, 'w', encoding='utf-8') as f:
                json.dump(self.apps, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving apps: {e}")

    def run_app(self, path):
        try:
            subprocess.Popen(path, shell=True)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Could not run application: {str(e)}")

    def delete_app(self, index):
        if 0 <= index < len(self.apps):
            self.apps.pop(index)
            self.save_apps()
            self.refresh_app_list()

    def edit_app(self, index):
        if 0 <= index < len(self.apps):
            self.open_edit_dialog(index)

    def open_add_dialog(self):
        self.open_edit_dialog()

    def open_edit_dialog(self, edit_index=None):
        dialog = AppEditDialog(self, self.apps[edit_index] if edit_index is not None else None)
        self.wait_window(dialog)
        
        if dialog.result:
            if edit_index is not None:
                self.apps[edit_index] = dialog.result
            else:
                self.apps.append(dialog.result)
            self.save_apps()
            self.refresh_app_list()

class AppEditDialog(tk.Toplevel):
    def __init__(self, parent, app_data=None):
        super().__init__(parent)
        self.result = None
        self.app_data = app_data or {}
        
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.geometry("400x350+810+10")  # Obok AppLauncher, 10px od góry

        # Setup macOS style rounded window
        self.canvas, self.container = setup_macos_window(self, 400, 350, corner_radius=16, 
                                                    bg_color="#1C1C1E", border_color="#2C2C2E", border_width=0)

        # Draw rounded inner container with equal margins
        margin = 20
        inner_width = 400 - 2 * margin  # 360
        inner_height = 350 - 2 * margin  # 310
        create_rounded_inner_container(self.canvas, margin, margin, inner_width, inner_height, corner_radius=12, bg_color="#3A3A3C")
        
        # Title bar positioned over the gray container
        self.title_bar = tk.Frame(self.canvas, bg="#2A2A2C", height=30)
        self.canvas.create_window(margin, margin, window=self.title_bar, anchor='nw', width=inner_width, height=30)
        
        # Bind drag events to title bar
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        
        title_label = tk.Label(self.title_bar, text="Dodaj/Edytuj aplikację", 
                              bg="#2A2A2C", fg="white", font=("Arial", 12, "bold"))
        title_label.pack(side="left", padx=10, pady=5)

        close_btn = tk.Button(
            self.title_bar,
            text="✕",
            command=self.destroy,
            bg="#FF5F57",
            fg="white",
            font=("Arial", 8, "bold"),
            bd=0,
            relief='flat',
            activebackground="#FF3B30"
        )
        close_btn.pack(side="right", padx=10, pady=5)

        # Content frame inside the rounded container
        self.content_frame = tk.Frame(self.canvas, bg="#3A3A3C")
        content_margin = 15
        self.canvas.create_window(margin + content_margin, margin + 30 + 5, 
                                window=self.content_frame, anchor='nw',
                                width=inner_width - 2 * content_margin,                                height=inner_height - 30 - 15)
        self.build_content()
        
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
        
    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")
    
    def build_content(self):
        # Name
        tk.Label(self.content_frame, text="Nazwa:", bg="#3A3A3C", fg="white", 
                font=("Arial", 10)).pack(anchor="w", pady=(5, 2))
        self.name_entry = tk.Entry(self.content_frame, bg="#48484A", fg="white", 
                                  font=("Arial", 10), bd=0, relief='flat')
        self.name_entry.pack(fill="x", pady=(0, 5))
        self.name_entry.insert(0, self.app_data.get("name", ""))

        # Path
        tk.Label(self.content_frame, text="Ścieżka:", bg="#3A3A3C", fg="white", 
                font=("Arial", 10)).pack(anchor="w", pady=(0, 2))
        
        path_frame = tk.Frame(self.content_frame, bg="#3A3A3C")
        path_frame.pack(fill="x", pady=(0, 5))
        
        self.path_entry = tk.Entry(path_frame, bg="#48484A", fg="white", 
                                  font=("Arial", 10), bd=0, relief='flat')
        self.path_entry.pack(side="left", fill="x", expand=True)
        self.path_entry.insert(0, self.app_data.get("path", ""))
        
        browse_btn = tk.Button(path_frame, text="...", command=self.browse_file,
                              bg="#5A5A5C", fg="white", font=("Arial", 8), bd=0,
                              relief='flat', activebackground="#6A6A6C")
        browse_btn.pack(side="right", padx=(5, 0))

        # Icon
        tk.Label(self.content_frame, text="Ikona:", bg="#3A3A3C", fg="white", 
                font=("Arial", 10)).pack(anchor="w", pady=(0, 2))
        
        icon_frame = tk.Frame(self.content_frame, bg="#3A3A3C")
        icon_frame.pack(fill="x", pady=(0, 5))
        
        self.icon_entry = tk.Entry(icon_frame, bg="#48484A", fg="white", 
                                  font=("Arial", 10), bd=0, relief='flat')
        self.icon_entry.pack(side="left", fill="x", expand=True)
        self.icon_entry.insert(0, self.app_data.get("icon", ""))
        
        icon_browse_btn = tk.Button(icon_frame, text="...", command=self.browse_icon,
                                   bg="#5A5A5C", fg="white", font=("Arial", 8), bd=0,
                                   relief='flat', activebackground="#6A6A6C")
        icon_browse_btn.pack(side="right", padx=(5, 0))

        # Color
        tk.Label(self.content_frame, text="Kolor:", bg="#3A3A3C", fg="white", 
                font=("Arial", 10)).pack(anchor="w", pady=(0, 2))
        
        color_frame = tk.Frame(self.content_frame, bg="#3A3A3C")
        color_frame.pack(fill="x", pady=(0, 10))
        
        self.color_entry = tk.Entry(color_frame, bg="#48484A", fg="white", 
                                   font=("Arial", 10), bd=0, relief='flat')
        self.color_entry.pack(side="left", fill="x", expand=True)
        self.color_entry.insert(0, self.app_data.get("color", "#48484A"))
        
        color_btn = tk.Button(color_frame, text="🎨", command=self.choose_color,
                             bg="#5A5A5C", fg="white", font=("Arial", 10), bd=0,
                             relief='flat', activebackground="#6A6A6C")
        color_btn.pack(side="right", padx=(5, 0))

        # Buttons
        btn_frame = tk.Frame(self.content_frame, bg="#3A3A3C")
        btn_frame.pack(fill="x", pady=(5, 0))
        
        cancel_btn = tk.Button(btn_frame, text="Anuluj", command=self.destroy,
                              bg="#5A5A5C", fg="white", font=("Arial", 10), bd=0,
                              relief='flat', activebackground="#6A6A6C")
        cancel_btn.pack(side="right", padx=(5, 0))
        
        save_btn = tk.Button(btn_frame, text="Zapisz", command=self.save_app,
                            bg="#34C759", fg="white", font=("Arial", 10), bd=0,
                            relief='flat', activebackground="#2FB850")
        save_btn.pack(side="right")

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Wybierz aplikację",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, filename)
            if not self.name_entry.get():
                name = os.path.splitext(os.path.basename(filename))[0]
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, name)

    def browse_icon(self):
        filename = filedialog.askopenfilename(
            title="Wybierz ikonę",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.ico"), ("All files", "*.*")]
        )
        if filename:
            self.icon_entry.delete(0, tk.END)
            self.icon_entry.insert(0, filename)

    def choose_color(self):
        color = colorchooser.askcolor(title="Wybierz kolor")
        if color[1]:
            self.color_entry.delete(0, tk.END)
            self.color_entry.insert(0, color[1])

    def save_app(self):
        name = self.name_entry.get().strip()
        path = self.path_entry.get().strip()
        
        if not name or not path:
            tk.messagebox.showerror("Error", "Nazwa i ścieżka są wymagane!")
            return
        
        self.result = {
            "name": name,
            "path": path,
            "icon": self.icon_entry.get().strip(),
            "color": self.color_entry.get().strip() or "#48484A"
        }
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = AppLauncher(root)
    app.mainloop()
