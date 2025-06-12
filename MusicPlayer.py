import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import os
import random
import threading
import time
from gradient_utils import setup_macos_window, create_rounded_inner_container, configure_ttk_styles

class MusicPlayer(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.geometry("400x400+400+630")  # Reduced height by 50px (taskbar height + 10px margin)
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Music player state
        self.current_song = None
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.shuffle_mode = False
        self.playlist = []
        self.music_folder = "Music"
        self.is_closing = False  # Flag to prevent operations during closing
        
        # Ensure music folder exists
        if not os.path.exists(self.music_folder):
            os.makedirs(self.music_folder)
        
        # Setup macOS style rounded window - updated height to 400
        self.canvas, self.container = setup_macos_window(self, 400, 400, corner_radius=16, 
                                                        bg_color="#1C1C1E", border_color="#2C2C2E", border_width=0)
        
        # Configure TTK styles for sliders
        configure_ttk_styles()

        # Draw rounded inner container with equal margins (20px from all sides)
        margin = 20
        inner_width = 400 - 2 * margin  # 360
        inner_height = 400 - 2 * margin  # 360 (reduced from 410)
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
        self.close_btn.pack(side='right', padx=10, pady=5)
        
        # Content area for music player controls inside the rounded container (below title bar)
        self.content_frame = tk.Frame(self.canvas, bg="#3A3A3C")
        content_margin = 15
        self.canvas.create_window(margin + content_margin, margin + 30 + 5, window=self.content_frame, anchor='nw', 
                                width=inner_width - 2 * content_margin, height=inner_height - 30 - 15)
        
        self.build_ui()
        self.load_playlist()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def build_ui(self):
        # Current song display (bez tytułu "Music Player")
        self.current_song_frame = tk.Frame(self.content_frame, bg="#48484A", relief="flat", bd=0)
        self.current_song_frame.pack(fill="x", pady=(5, 10), padx=5)
        
        self.current_song_label = tk.Label(
            self.current_song_frame,
            text="No song selected",
            font=("SF Pro Text", 12, "bold"),
            bg="#48484A",
            fg="#FFFFFF",
            anchor="center"
        )
        self.current_song_label.pack(pady=10)
        
        # Control buttons frame
        self.controls_frame = tk.Frame(self.content_frame, bg="#3A3A3C")
        self.controls_frame.pack(fill="x", pady=(0, 10))
        
        # Previous button
        self.prev_btn = tk.Button(
            self.controls_frame,
            text="⏮",
            command=self.previous_song,
            bg="#5A5A5C",
            fg="white",
            font=("Arial", 12),
            bd=0,
            relief='flat',
            activebackground="#6A6A6C",
            width=4,
            height=1
        )
        self.prev_btn.pack(side="left", padx=5)
        
        # Play/Pause button
        self.play_btn = tk.Button(
            self.controls_frame,
            text="▶",
            command=self.toggle_play_pause,
            bg="#007AFF",
            fg="white",
            font=("Arial", 12),
            bd=0,
            relief='flat',
            activebackground="#0056CC",
            width=4,
            height=1
        )
        self.play_btn.pack(side="left", padx=5)
        
        # Next button
        self.next_btn = tk.Button(
            self.controls_frame,
            text="⏭",
            command=self.next_song,
            bg="#5A5A5C",
            fg="white",
            font=("Arial", 12),
            bd=0,
            relief='flat',
            activebackground="#6A6A6C",
            width=4,
            height=1
        )
        self.next_btn.pack(side="left", padx=5)
        
        # Shuffle button
        self.shuffle_btn = tk.Button(
            self.controls_frame,
            text="🔀",
            command=self.toggle_shuffle,
            bg="#5A5A5C",
            fg="white",
            font=("Arial", 10),
            bd=0,
            relief='flat',
            activebackground="#6A6A6C",
            width=4,
            height=1
        )
        self.shuffle_btn.pack(side="right", padx=5)
        
        # Add music button
        self.add_btn = tk.Button(
            self.controls_frame,
            text="➕",
            command=self.add_music,
            bg="#34C759",
            fg="white",
            font=("Arial", 12),
            bd=0,
            relief='flat',
            activebackground="#248A3D",
            width=4,
            height=1
        )
        self.add_btn.pack(side="right", padx=5)
        
        # Volume control
        self.volume_frame = tk.Frame(self.content_frame, bg="#3A3A3C")
        self.volume_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            self.volume_frame,
            text="Volume:",
            font=("SF Pro Text", 10),
            bg="#3A3A3C",
            fg="#FFFFFF"
        ).pack(side="left")
        
        self.volume_scale = ttk.Scale(
            self.volume_frame,
            from_=0,
            to=100,
            orient="horizontal",
            style="Gray.Horizontal.TScale",
            command=self.set_volume
        )
        self.volume_scale.set(70)
        self.volume_scale.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Playlist frame
        tk.Label(
            self.content_frame,
            text="Playlist:",
            font=("SF Pro Text", 12, "bold"),
            bg="#3A3A3C",
            fg="#FFFFFF",
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        # Playlist listbox without scrollbar - removed scroll functionality
        self.playlist_frame = tk.Frame(self.content_frame, bg="#3A3A3C")
        self.playlist_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.playlist_listbox = tk.Listbox(
            self.playlist_frame,
            bg="#48484A",
            fg="white",
            selectbackground="#007AFF",
            selectforeground="white",
            bd=0,
            highlightthickness=0,
            font=("SF Pro Text", 10)
        )
        self.playlist_listbox.pack(fill="both", expand=True)
        
        # Bind double-click to play song
        self.playlist_listbox.bind("<Double-Button-1>", self.on_song_select)

    def load_playlist(self):
        """Load all supported audio files from Music folder"""
        self.playlist = []
        supported_formats = ('.mp3', '.wav', '.ogg', '.m4a')
        
        if os.path.exists(self.music_folder):
            for file in os.listdir(self.music_folder):
                if file.lower().endswith(supported_formats):
                    self.playlist.append(file)
        
        self.update_playlist_display()

    def update_playlist_display(self):
        """Update the playlist display in the listbox"""
        self.playlist_listbox.delete(0, tk.END)
        for song in self.playlist:
            self.playlist_listbox.insert(tk.END, os.path.splitext(song)[0])

    def add_music(self):
        """Add music files to the playlist"""
        file_types = [
            ("Audio files", "*.mp3 *.wav *.ogg *.m4a"),
            ("MP3 files", "*.mp3"),
            ("WAV files", "*.wav"),
            ("OGG files", "*.ogg"),
            ("M4A files", "*.m4a"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select music files",
            filetypes=file_types
        )
        
        if files:
            for file_path in files:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(self.music_folder, filename)
                
                try:
                    # Copy file to Music folder
                    import shutil
                    shutil.copy2(file_path, dest_path)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not copy {filename}: {str(e)}")
            
            # Reload playlist
            self.load_playlist()

    def on_song_select(self, event):
        """Handle song selection from listbox"""
        selection = self.playlist_listbox.curselection()
        if selection:
            self.current_index = selection[0]
            self.play_current_song()

    def play_current_song(self):
        """Play the currently selected song"""
        if self.is_closing:
            return
            
        if not self.playlist:
            return
        
        if 0 <= self.current_index < len(self.playlist):
            song_file = self.playlist[self.current_index]
            song_path = os.path.join(self.music_folder, song_file)
            
            try:
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                self.is_playing = True
                self.is_paused = False
                self.current_song = song_file
                
                # Update display
                song_name = os.path.splitext(song_file)[0]
                self.current_song_label.config(text=song_name)
                self.play_btn.config(text="⏸")
                
                # Update listbox selection
                self.playlist_listbox.selection_clear(0, tk.END)
                self.playlist_listbox.selection_set(self.current_index)
                
                # Start monitoring thread
                threading.Thread(target=self.monitor_song, daemon=True).start()
                
            except pygame.error as e:
                messagebox.showerror("Error", f"Could not play {song_file}: {str(e)}")

    def toggle_play_pause(self):
        """Toggle between play and pause"""
        if self.is_closing:
            return
            
        if self.is_playing:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
                self.play_btn.config(text="⏸")
            else:
                pygame.mixer.music.pause()
                self.is_paused = True
                self.play_btn.config(text="▶")
        else:
            if self.current_song:
                pygame.mixer.music.unpause()
                self.is_playing = True
                self.is_paused = False
                self.play_btn.config(text="⏸")
            else:
                # Start playing first song if available
                if self.playlist:
                    self.current_index = 0
                    self.play_current_song()

    def next_song(self):
        """Play next song in playlist"""
        if not self.playlist:
            return
        
        if self.shuffle_mode:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)
        
        self.play_current_song()

    def previous_song(self):
        """Play previous song in playlist"""
        if not self.playlist:
            return
        
        if self.shuffle_mode:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index - 1) % len(self.playlist)
        
        self.play_current_song()

    def toggle_shuffle(self):
        """Toggle shuffle mode"""
        self.shuffle_mode = not self.shuffle_mode
        if self.shuffle_mode:
            self.shuffle_btn.config(bg="#007AFF", activebackground="#0056CC")
        else:
            self.shuffle_btn.config(bg="#5A5A5C", activebackground="#6A6A6C")

    def set_volume(self, value):
        """Set the volume of the music player"""
        volume = float(value) / 100
        pygame.mixer.music.set_volume(volume)

    def monitor_song(self):
        """Monitor if the current song has finished playing"""
        while self.is_playing and not self.is_closing:
            if not pygame.mixer.music.get_busy() and not self.is_paused:
                # Song finished, play next song
                self.after(100, self.next_song)
                break
            time.sleep(0.5)

    def destroy(self):
        """Override destroy to properly cleanup"""
        self.is_closing = True
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except:
            pass
        super().destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide root window
    app = MusicPlayer(root)
    app.mainloop()
