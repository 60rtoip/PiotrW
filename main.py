import tkinter as tk
from ctypes import windll, Structure, c_long, byref
from VolumeMixer import VolumeMixer
from AppLauncher import AppLauncher
from MusicPlayer import MusicPlayer
from Saper import Saper

# Pomocnicza struktura RECT z Windows API
class RECT(Structure):
    _fields_ = [("left", c_long),
                ("top", c_long),
                ("right", c_long),
                ("bottom", c_long)]

def get_taskbar_height():
    rect = RECT()
    hwnd = windll.user32.FindWindowW("Shell_TrayWnd", None)
    if hwnd:
        windll.user32.GetWindowRect(hwnd, byref(rect))
        screen_height = windll.user32.GetSystemMetrics(1)
        return screen_height - rect.top
    return 40  # domyślnie, jeśli coś pójdzie nie tak

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.is_collapsed = False

        # Singleton pattern - track open windows
        self.open_windows = {
            'mixer': None,
            'launcher': None,
            'music': None,
            'saper': None
        }

        # Konfiguracja szerokości
        self.panel_width = 380
        self.toggle_area_width = 10
        self.full_width = self.panel_width + self.toggle_area_width
        self.collapsed_width = self.toggle_area_width

        screen_height = self.winfo_screenheight()
        taskbar_height = get_taskbar_height()
        self.usable_height = screen_height - taskbar_height

        self.geometry(f"{self.full_width}x{self.usable_height}+0+0")

        # Canvas
        self.canvas = tk.Canvas(self, bg='yellow', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        # Główna ramka z zawartością
        self.container = tk.Frame(self.canvas, bg="#222222")
        self.canvas.create_rectangle(0, 0, self.panel_width, self.usable_height, fill="#222222", outline="")
        self.canvas_container = self.canvas.create_window(0, 0, window=self.container, anchor='nw',
                                                          width=self.panel_width, height=self.usable_height)

        # Panel boczny na przycisk
        self.toggle_area = tk.Frame(self, bg="#111")
        self.toggle_area.place(x=self.panel_width, y=0, width=self.toggle_area_width, height=self.usable_height)

        # Przycisk zwijania
        self.toggle_btn = tk.Button(self.toggle_area, text="⇤", command=self.toggle_panel,
                                    bg="#444", fg="white", font=("Arial", 10), bd=0)
        self.toggle_btn.place(x=0, y=self.usable_height // 2 - 25, width=10, height=50)

        # Przycisk zamknięcia
        close_btn = tk.Button(self.container, text="X", command=self.quit,
                              bg="red", fg="white", font=("Arial", 10), bd=0)
        close_btn.place(x=self.panel_width - 30, y=10, width=20, height=20)        # # Dragowanie
        # self.bind("<Button-1>", self.start_move)
        # self.bind("<B1-Motion>", self.do_move)

        self.build_ui()

    # def start_move(self, event): # Dragowanie
    #     self.x = event.x
    #     self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def build_ui(self):
        # Szerokość przycisków w znakach (nie pikselach!)
        button_width = 20  # 20 znaków szerokości
        button_height = 1  # Niższa wysokość w jednostkach tekstu
        button_spacing = 20  # 20px odstępu między przyciskami
        
        self.mixer_button = tk.Button(
            self.container, text="Mikser Głośności", command=self.open_mixer,
            bg="green", fg="white", font=("Arial", 16),
            width=button_width, height=button_height
        )
        self.mixer_button.pack(pady=(150, button_spacing//2))

        self.app_launcher_button = tk.Button(
            self.container, text="Aplikacje", command=self.open_app_launcher,
            bg="blue", fg="white", font=("Arial", 16),
            width=button_width, height=button_height
        )
        self.app_launcher_button.pack(pady=button_spacing//2)

        self.music_player_button = tk.Button(
            self.container, text="Odtwarzacz Muzyki", command=self.open_music_player,
            bg="purple", fg="white", font=("Arial", 16),
            width=button_width, height=button_height
        )
        self.music_player_button.pack(pady=button_spacing//2)

        self.saper_button = tk.Button(
            self.container, text="Saper", command=self.open_saper,
            bg="orange", fg="white", font=("Arial", 16),
            width=button_width, height=button_height
        )
        self.saper_button.pack(pady=button_spacing//2)

    def toggle_panel(self):
        if self.is_collapsed:
            # Rozwiń
            self.geometry(f"{self.full_width}x{self.usable_height}+0+0")
            self.canvas.itemconfigure(self.canvas_container, state='normal')
            self.canvas.itemconfigure(self.canvas_container, width=self.panel_width)
            self.toggle_area.place(x=self.panel_width, y=0, width=self.toggle_area_width, height=self.usable_height)
            self.toggle_btn.config(text="⇤")
        else:
            # Zwiń
            self.geometry(f"{self.collapsed_width}x{self.usable_height}+0+0")
            self.canvas.itemconfigure(self.canvas_container, state='hidden')
            self.toggle_area.place(x=0, y=0, width=self.toggle_area_width, height=self.usable_height)
            self.toggle_btn.config(text="⇥")
        self.is_collapsed = not self.is_collapsed

    def open_mixer(self):
        # Check if window already exists and is still valid
        try:
            if self.open_windows['mixer'] and self.open_windows['mixer'].winfo_exists():
                # Bring existing window to front
                self.open_windows['mixer'].lift()
                self.open_windows['mixer'].focus_force()
                return
        except tk.TclError:
            # Window was destroyed, clear reference
            self.open_windows['mixer'] = None
        
        # Create new window and store reference
        self.open_windows['mixer'] = VolumeMixer(self)

    def open_app_launcher(self):
        # Check if window already exists and is still valid
        try:
            if self.open_windows['launcher'] and self.open_windows['launcher'].winfo_exists():
                # Bring existing window to front
                self.open_windows['launcher'].lift()
                self.open_windows['launcher'].focus_force()
                return
        except tk.TclError:
            # Window was destroyed, clear reference
            self.open_windows['launcher'] = None
        
        # Create new window and store reference
        self.open_windows['launcher'] = AppLauncher(self)

    def open_music_player(self):
        # Check if window already exists and is still valid
        try:
            if self.open_windows['music'] and self.open_windows['music'].winfo_exists():
                # Bring existing window to front
                self.open_windows['music'].lift()
                self.open_windows['music'].focus_force()
                return
        except tk.TclError:
            # Window was destroyed, clear reference
            self.open_windows['music'] = None
        
        # Create new window and store reference
        self.open_windows['music'] = MusicPlayer(self)

    def open_saper(self):
        # Check if window already exists and is still valid
        try:
            if self.open_windows['saper'] and self.open_windows['saper'].winfo_exists():
                # Bring existing window to front
                self.open_windows['saper'].lift()
                self.open_windows['saper'].focus_force()
                return
        except tk.TclError:
            # Window was destroyed, clear reference
            self.open_windows['saper'] = None
        
        # Create new window and store reference
        self.open_windows['saper'] = Saper(self)

if __name__ == "__main__":
    app = App()
    app.mainloop()