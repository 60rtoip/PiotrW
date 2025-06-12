import tkinter as tk
from tkinter import ttk

def hex_to_rgb(hex_color):
    """Konwertuje kolor hex na RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    """Konwertuje RGB na hex"""
    return '#%02x%02x%02x' % tuple(int(c) for c in rgb)

def interpolate_color(color1, color2, factor):
    """Interpoluje między dwoma kolorami RGB"""
    return tuple(c1 + (c2 - c1) * factor for c1, c2 in zip(color1, color2))

def create_gradient_border(canvas, width, height, color1="#FFB71C", color2="#FFEE00", border_width=2):
    """Tworzy gradient border od lewego dolnego rogu do prawego górnego"""
    
    # Konwertuj kolory hex na RGB
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    
    # Rysuj gradient border
    # Górna krawędź
    for i in range(width):
        factor = i / width
        color = interpolate_color(rgb1, rgb2, factor)
        hex_color = rgb_to_hex(color)
        for j in range(border_width):
            canvas.create_line(i, j, i+1, j, fill=hex_color, width=1)
    
    # Dolna krawędź
    for i in range(width):
        factor = i / width
        color = interpolate_color(rgb1, rgb2, factor)
        hex_color = rgb_to_hex(color)
        for j in range(border_width):
            canvas.create_line(i, height-j-1, i+1, height-j-1, fill=hex_color, width=1)
    
    # Prawa krawędź
    for i in range(height):
        factor = (height - i) / height
        color = interpolate_color(rgb1, rgb2, factor)
        hex_color = rgb_to_hex(color)
        for j in range(border_width):
            canvas.create_line(width-j-1, i, width-j-1, i+1, fill=hex_color, width=1)
    
    # Lewa krawędź
    for i in range(height):
        factor = (height - i) / height
        color = interpolate_color(rgb1, rgb2, factor)
        hex_color = rgb_to_hex(color)
        for j in range(border_width):
            canvas.create_line(j, i, j, i+1, fill=hex_color, width=1)

def setup_gradient_window(window, width, height, color1="#FFB71C", color2="#FFEE00", border_width=2):
    """Konfiguruje okno z gradient border"""
    # Twórz canvas dla gradientu
    canvas = tk.Canvas(window, highlightthickness=0)
    canvas.pack(fill='both', expand=True)
    
    # Rysuj gradient border
    create_gradient_border(canvas, width, height, color1, color2, border_width)
    
    # Twórz główny kontener wewnątrz
    container = tk.Frame(canvas, bg="#222222")
    canvas.create_window(border_width, border_width, window=container, anchor='nw', 
                        width=width-2*border_width, height=height-2*border_width)
    
    return canvas, container

def create_macos_rounded_window(canvas, width, height, corner_radius=12, bg_color="#2C2C2E", border_color="#3A3A3C", border_width=1):
    """Tworzy okno z zaokrąglonymi rogami w stylu macOS"""
    
    # Ustaw tło canvas na przezroczyste
    canvas.configure(bg='SystemButtonFace')
    
    # Funkcja sprawdzająca czy punkt jest w zaokrąglonym oknie
    def is_in_rounded_window(x, y):
        # Sprawdź każdy róg
        corners = [
            (corner_radius, corner_radius),  # lewy górny
            (width - corner_radius, corner_radius),  # prawy górny
            (corner_radius, height - corner_radius),  # lewy dolny
            (width - corner_radius, height - corner_radius)  # prawy dolny
        ]
        
        for corner_x, corner_y in corners:
            # Jeśli punkt jest w obszarze rogu
            if ((x < corner_radius and y < corner_radius and corner_x == corner_radius and corner_y == corner_radius) or
                (x >= width - corner_radius and y < corner_radius and corner_x == width - corner_radius and corner_y == corner_radius) or
                (x < corner_radius and y >= height - corner_radius and corner_x == corner_radius and corner_y == height - corner_radius) or
                (x >= width - corner_radius and y >= height - corner_radius and corner_x == width - corner_radius and corner_y == height - corner_radius)):
                
                # Sprawdź czy punkt jest w okręgu
                dist_sq = (x - corner_x) ** 2 + (y - corner_y) ** 2
                if dist_sq > corner_radius ** 2:
                    return False
        return True
    
    # Rysuj zaokrąglone tło
    # Główne prostokąty
    canvas.create_rectangle(corner_radius, 0, width - corner_radius, height, 
                           fill=bg_color, outline="")
    canvas.create_rectangle(0, corner_radius, width, height - corner_radius, 
                           fill=bg_color, outline="")
    
    # Zaokrąglone rogi
    for corner_x, corner_y in [(corner_radius, corner_radius), 
                               (width - corner_radius, corner_radius),
                               (corner_radius, height - corner_radius), 
                               (width - corner_radius, height - corner_radius)]:
        canvas.create_oval(corner_x - corner_radius, corner_y - corner_radius,
                          corner_x + corner_radius, corner_y + corner_radius,
                          fill=bg_color, outline="")
    
    # Rysuj subtelny border jeśli jest potrzebny
    if border_width > 0:
        # Górna i dolna krawędź
        canvas.create_rectangle(corner_radius, 0, width - corner_radius, border_width,
                               fill=border_color, outline="")
        canvas.create_rectangle(corner_radius, height - border_width, width - corner_radius, height,
                               fill=border_color, outline="")
        
        # Lewa i prawa krawędź
        canvas.create_rectangle(0, corner_radius, border_width, height - corner_radius,
                               fill=border_color, outline="")
        canvas.create_rectangle(width - border_width, corner_radius, width, height - corner_radius,
                               fill=border_color, outline="")
        
        # Zaokrąglone rogi border
        for corner_x, corner_y in [(corner_radius, corner_radius), 
                                   (width - corner_radius, corner_radius),
                                   (corner_radius, height - corner_radius), 
                                   (width - corner_radius, height - corner_radius)]:
            canvas.create_oval(corner_x - corner_radius, corner_y - corner_radius,
                              corner_x + corner_radius, corner_y + corner_radius,
                              outline=border_color, width=border_width, fill="")

def setup_macos_window(window, width, height, corner_radius=12, bg_color="#2C2C2E", border_color="#3A3A3C", border_width=1):
    """Konfiguruje okno w stylu macOS z zaokrąglonymi rogami"""
    # Ustaw przezroczystość dla rogów
    try:
        window.wm_attributes("-transparentcolor", "SystemButtonFace")
        window.configure(bg='SystemButtonFace')
    except:
        window.configure(bg='#2F2F2F')
    
    # Twórz canvas
    try:
        canvas = tk.Canvas(window, highlightthickness=0, bg='SystemButtonFace')
    except:
        canvas = tk.Canvas(window, highlightthickness=0, bg='#2F2F2F')
    canvas.pack(fill='both', expand=True)
    
    # Rysuj zaokrąglone okno
    create_macos_rounded_window(canvas, width, height, corner_radius, bg_color, border_color, border_width)
    
    # Twórz kontener wewnątrz
    container = tk.Frame(canvas, bg=bg_color)
    canvas.create_window(8, 8, window=container, anchor='nw', 
                        width=width-16, height=height-16)
    
    return canvas, container

def create_rounded_inner_container(parent_canvas, x, y, width, height, corner_radius=12, bg_color="#3A3A3C"):
    """Tworzy prawdziwie zaokrąglony kontener wewnętrzny na canvas"""
    
    # Usuń poprzednie elementy jeśli istnieją
    parent_canvas.delete("inner_container")
    
    # Rysuj główne prostokąty (środkowe części bez rogów)
    parent_canvas.create_rectangle(x + corner_radius, y, x + width - corner_radius, y + height, 
                                  fill=bg_color, outline="", tags="inner_container")
    parent_canvas.create_rectangle(x, y + corner_radius, x + width, y + height - corner_radius, 
                                  fill=bg_color, outline="", tags="inner_container")
    
    # Rysuj prawdziwie zaokrąglone rogi używając oval
    corners = [
        (x + corner_radius, y + corner_radius),  # lewy górny
        (x + width - corner_radius, y + corner_radius),  # prawy górny  
        (x + corner_radius, y + height - corner_radius),  # lewy dolny
        (x + width - corner_radius, y + height - corner_radius)  # prawy dolny
    ]
    
    for corner_x, corner_y in corners:
        parent_canvas.create_oval(corner_x - corner_radius, corner_y - corner_radius,
                                 corner_x + corner_radius, corner_y + corner_radius,
                                 fill=bg_color, outline="", tags="inner_container")

def configure_ttk_styles():
    """Konfiguruje style TTK dla lepszego wyglądu suwaków"""
    style = ttk.Style()
    
    # Skonfiguruj styl dla Scale (suwaka)
    style.configure("Gray.Horizontal.TScale", 
                   background='#5A5A5C',      # Jasno szare tło
                   troughcolor='#5A5A5C',     # Kolor ścieżki suwaka
                   lightcolor='#5A5A5C',      # Jasny kolor obramowania
                   darkcolor='#3A3A3C',       # Ciemny kolor obramowania
                   bordercolor='#5A5A5C',     # Kolor obramowania
                   focuscolor='#007AFF')      # Kolor przy focus
    
    # Mapowanie dla różnych stanów
    style.map("Gray.Horizontal.TScale",
             background=[('active', '#6A6A6C'), ('pressed', '#4A4A4C')],
             troughcolor=[('active', '#6A6A6C'), ('pressed', '#4A4A4C')])
    
    # Skonfiguruj styl dla Scrollbar (pasek przewijania)
    style.configure("Gray.Vertical.TScrollbar",
                   background='#5A5A5C',      # Jasno szare tło
                   troughcolor='#3A3A3C',     # Ciemniejsze tło ścieżki
                   bordercolor='#5A5A5C',     # Kolor obramowania
                   arrowcolor='#FFFFFF',      # Kolor strzałek
                   lightcolor='#6A6A6C',      # Jasny kolor 3D
                   darkcolor='#3A3A3C')       # Ciemny kolor 3D
    
    # Mapowanie dla różnych stanów scrollbara
    style.map("Gray.Vertical.TScrollbar",
             background=[('active', '#6A6A6C'), ('pressed', '#4A4A4C')],
             arrowcolor=[('active', '#FFFFFF'), ('pressed', '#CCCCCC')])
    
    return style
