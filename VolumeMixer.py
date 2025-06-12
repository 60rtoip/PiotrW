import tkinter as tk
from tkinter import ttk
from ctypes import windll
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from gradient_utils import setup_macos_window, configure_ttk_styles, create_rounded_inner_container

class VolumeMixer(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes('-topmost', True)  # Zawsze na wierzchu
        self.geometry("400x300+400+10")  # Top position with margin 10px  # Mniejsza wysokość, 10px od góry
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
        self.close_btn.pack(side='right', padx=10, pady=5)        # Content area for volume controls inside the rounded container (below title bar)
        self.content_frame = tk.Frame(self.canvas, bg="#3A3A3C")
        content_margin = 15
        self.canvas.create_window(margin + content_margin, margin + 30 + 5, window=self.content_frame, anchor='nw', 
                                width=inner_width - 2 * content_margin, height=inner_height - 30 - 15)

        # Create scrollable frame for volume controls
        self.scroll_canvas = tk.Canvas(self.content_frame, bg="#3A3A3C", highlightthickness=0)
        self.scroll_canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollable frame that will contain all volume controls
        self.scrollable_frame = tk.Frame(self.scroll_canvas, bg="#3A3A3C")
        self.scroll_canvas_window = self.scroll_canvas.create_window(0, 0, window=self.scrollable_frame, anchor="nw")
        
        # Bind mouse wheel scrolling
        self.scroll_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
          # Bind canvas resize to update scroll region
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.scroll_canvas.bind("<Configure>", self._on_canvas_configure)

        self.volume_controls = []
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
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session._ctl.QueryInterface(ISimpleAudioVolume):
                app_name = session.Process.name()
                volume_interface = session._ctl.QueryInterface(ISimpleAudioVolume)                # Kontener dla każdej aplikacji z zaokrąglonym tłem
                app_frame = tk.Frame(self.scrollable_frame, bg="#2C2C2E", relief="flat", bd=0)
                app_frame.pack(fill="x", pady=3, padx=5)
                
                # Wewnętrzny frame z paddingiem
                inner_frame = tk.Frame(app_frame, bg="#2C2C2E")
                inner_frame.pack(fill="x", padx=8, pady=6)

                # App name label
                label = tk.Label(
                    inner_frame,
                    text=app_name.replace('.exe', ''),
                    font=("SF Pro Text", 12),
                    bg='#2C2C2E',
                    fg='#FFFFFF',
                    anchor='w'
                )
                label.pack(side="left")

                # Container dla kontrolek po prawej
                controls_frame = tk.Frame(inner_frame, bg="#2C2C2E")
                controls_frame.pack(side="right", fill="x", expand=True, padx=(10, 0))                # Volume slider (macOS style)
                slider_frame = tk.Frame(controls_frame, bg="#2C2C2E")
                slider_frame.pack(side="right", fill="x", expand=True)
                
                scale = ttk.Scale(
                    slider_frame,
                    from_=0,
                    to=100,
                    orient="horizontal",
                    style="Gray.Horizontal.TScale",
                    command=lambda val, v=volume_interface: self.set_volume(v, val)
                )
                scale.set(volume_interface.GetMasterVolume() * 100)
                scale.pack(side="right", fill="x", expand=True, padx=(0, 8))

                # Mute button (macOS style)
                current_volume = volume_interface.GetMasterVolume()
                is_muted = volume_interface.GetMute()
                mute_text = "🔇" if is_muted or current_volume == 0 else "🔊"
                
                mute_btn = tk.Button(
                    controls_frame,
                    text=mute_text,
                    command=lambda v=volume_interface, b=None: self.toggle_mute(v),
                    bg="#3A3A3C",
                    fg="white",
                    font=("Arial", 10),
                    bd=0,
                    relief='flat',
                    activebackground="#48484A",
                    width=3,
                    height=1
                )
                mute_btn.pack(side="right", padx=(0, 5))

                self.volume_controls.append((label, scale, volume_interface, mute_btn))

    def set_volume(self, volume_interface, value):
        volume = float(value) / 100.0
        volume_interface.SetMasterVolume(volume, None)

    def toggle_mute(self, volume_interface):
        is_muted = volume_interface.GetMute()
        volume_interface.SetMute(not is_muted, None)