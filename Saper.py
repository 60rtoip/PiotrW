import tkinter as tk
from tkinter import messagebox
import random
from gradient_utils import setup_macos_window, create_rounded_inner_container

class Saper(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.geometry("500x650+1220+10")  # 10px od MusicPlayer, 10px od góry
        
        # Game settings
        self.rows = 16
        self.cols = 16
        self.mines = 40
        self.cell_size = 25
        
        # Game state
        self.board = []
        self.revealed = []
        self.flagged = []
        self.game_over = False
        self.game_won = False
        self.mines_remaining = self.mines
          # Setup macOS style rounded window
        self.canvas, self.container = setup_macos_window(self, 500, 650, corner_radius=16, 
                                                        bg_color="#1C1C1E", border_color="#2C2C2E", border_width=0)

        # Draw rounded inner container with equal margins (20px from all sides)
        margin = 20
        inner_width = 500 - 2 * margin  # 460
        inner_height = 650 - 2 * margin  # 610
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
        
        # Content area for game inside the rounded container (below title bar)
        self.content_frame = tk.Frame(self.canvas, bg="#3A3A3C")
        content_margin = 15
        self.canvas.create_window(margin + content_margin, margin + 30 + 5, window=self.content_frame, anchor='nw', 
                                width=inner_width - 2 * content_margin, height=inner_height - 30 - 15)
        
        self.build_ui()
        self.new_game()

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
        # Title
        title_label = tk.Label(
            self.content_frame,
            text="Saper",
            font=("SF Pro Display", 16, "bold"),
            bg="#3A3A3C",
            fg="#FFFFFF",
            anchor="w"
        )
        title_label.pack(fill="x", pady=(5, 10))
        
        # Info panel
        self.info_frame = tk.Frame(self.content_frame, bg="#48484A", relief="flat", bd=0)
        self.info_frame.pack(fill="x", pady=(0, 10), padx=5)
        
        # Mines counter
        self.mines_label = tk.Label(
            self.info_frame,
            text=f"Miny: {self.mines_remaining}",
            font=("SF Pro Text", 12, "bold"),
            bg="#48484A",
            fg="#FFFFFF"
        )
        self.mines_label.pack(side="left", padx=10, pady=8)
        
        # New game button
        self.new_game_btn = tk.Button(
            self.info_frame,
            text="Nowa Gra",
            command=self.new_game,
            bg="#007AFF",
            fg="white",
            font=("SF Pro Text", 10, "bold"),
            bd=0,
            relief='flat',
            activebackground="#0056CC"
        )
        self.new_game_btn.pack(side="right", padx=10, pady=5)
        
        # Game status
        self.status_label = tk.Label(
            self.info_frame,
            text="Powodzenia!",
            font=("SF Pro Text", 10),
            bg="#48484A",
            fg="#FFFFFF"
        )
        self.status_label.pack(side="right", padx=10, pady=8)
        
        # Game board frame
        self.board_frame = tk.Frame(self.content_frame, bg="#3A3A3C")
        self.board_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create scrollable canvas for the board
        self.board_canvas = tk.Canvas(
            self.board_frame, 
            bg="#2C2C2E",
            highlightthickness=0,
            width=400,
            height=400
        )
        self.board_canvas.pack(fill="both", expand=True)
        
        # Scrollbars for large boards
        self.v_scrollbar = tk.Scrollbar(
            self.board_frame, 
            orient="vertical", 
            command=self.board_canvas.yview,
            bg="#5A5A5C",
            troughcolor="#3A3A3C",
            activebackground="#6A6A6C"
        )
        self.h_scrollbar = tk.Scrollbar(
            self.board_frame, 
            orient="horizontal", 
            command=self.board_canvas.xview,
            bg="#5A5A5C",
            troughcolor="#3A3A3C",
            activebackground="#6A6A6C"
        )
        
        self.board_canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # Instructions
        instructions = tk.Label(
            self.content_frame,
            text="Lewy klik - odkryj pole | Prawy klik - flaga",
            font=("SF Pro Text", 9),
            bg="#3A3A3C",
            fg="#CCCCCC"
        )
        instructions.pack(pady=(5, 0))

    def new_game(self):
        """Start a new game"""
        self.game_over = False
        self.game_won = False
        self.mines_remaining = self.mines
        
        # Clear previous board
        self.board_canvas.delete("all")
        
        # Initialize game arrays
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flagged = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Place mines
        self.place_mines()
        
        # Calculate numbers
        self.calculate_numbers()
        
        # Create visual board
        self.create_visual_board()
        
        # Update UI
        self.update_status("Powodzenia!")
        self.update_mines_count()

    def place_mines(self):
        """Randomly place mines on the board"""
        mines_placed = 0
        while mines_placed < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if self.board[row][col] != -1:  # -1 represents a mine
                self.board[row][col] = -1
                mines_placed += 1

    def calculate_numbers(self):
        """Calculate numbers for each cell based on adjacent mines"""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] != -1:  # Not a mine
                    count = 0
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = row + dr, col + dc
                            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                if self.board[nr][nc] == -1:
                                    count += 1
                    self.board[row][col] = count

    def create_visual_board(self):
        """Create the visual representation of the board"""
        board_width = self.cols * self.cell_size
        board_height = self.rows * self.cell_size
        
        # Configure scroll region
        self.board_canvas.configure(scrollregion=(0, 0, board_width, board_height))
        
        # Create cells
        self.cells = {}
        for row in range(self.rows):
            for col in range(self.cols):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Create cell rectangle
                cell_id = self.board_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="#5A5A5C",
                    outline="#3A3A3C",
                    width=1
                )
                
                self.cells[(row, col)] = cell_id
                
                # Bind events
                self.board_canvas.tag_bind(cell_id, "<Button-1>", lambda e, r=row, c=col: self.left_click(r, c))
                self.board_canvas.tag_bind(cell_id, "<Button-3>", lambda e, r=row, c=col: self.right_click(r, c))

    def left_click(self, row, col):
        """Handle left mouse click - reveal cell"""
        if self.game_over or self.game_won or self.revealed[row][col] or self.flagged[row][col]:
            return
        
        self.reveal_cell(row, col)
        
        if self.board[row][col] == -1:
            # Hit a mine
            self.game_over = True
            self.reveal_all_mines()
            self.update_status("BOOM! Przegrałeś!")
            messagebox.showinfo("Gra skończona", "Trafiłeś na minę! Spróbuj ponownie.")
        else:
            # Check for win condition
            if self.check_win():
                self.game_won = True
                self.update_status("Gratulacje! Wygrałeś!")
                messagebox.showinfo("Zwycięstwo", "Gratulacje! Oczysciłeś wszystkie pola!")

    def right_click(self, row, col):
        """Handle right mouse click - toggle flag"""
        if self.game_over or self.game_won or self.revealed[row][col]:
            return
        
        self.flagged[row][col] = not self.flagged[row][col]
        
        if self.flagged[row][col]:
            self.mines_remaining -= 1
            # Draw flag
            cell_id = self.cells[(row, col)]
            x1 = col * self.cell_size
            y1 = row * self.cell_size
            cx = x1 + self.cell_size // 2
            cy = y1 + self.cell_size // 2
            
            flag_id = self.board_canvas.create_text(
                cx, cy,
                text="🚩",
                font=("Arial", 12),
                fill="#FF3B30",
                tags=f"flag_{row}_{col}"
            )
        else:
            self.mines_remaining += 1
            # Remove flag
            self.board_canvas.delete(f"flag_{row}_{col}")
        
        self.update_mines_count()

    def reveal_cell(self, row, col):
        """Reveal a cell and potentially cascade"""
        if self.revealed[row][col] or self.flagged[row][col]:
            return
        
        self.revealed[row][col] = True
        cell_id = self.cells[(row, col)]
        
        # Change cell appearance
        self.board_canvas.itemconfig(cell_id, fill="#CCCCCC")
        
        # Draw content
        x1 = col * self.cell_size
        y1 = row * self.cell_size
        cx = x1 + self.cell_size // 2
        cy = y1 + self.cell_size // 2
        
        if self.board[row][col] == -1:
            # Mine
            self.board_canvas.create_text(
                cx, cy,
                text="💣",
                font=("Arial", 12),
                fill="#FF3B30"
            )
        elif self.board[row][col] > 0:
            # Number
            colors = ["", "#0066FF", "#00AA00", "#FF3300", "#6600CC", "#AA0000", "#00AAAA", "#000000", "#808080"]
            self.board_canvas.create_text(
                cx, cy,
                text=str(self.board[row][col]),
                font=("Arial", 10, "bold"),
                fill=colors[self.board[row][col]] if self.board[row][col] < len(colors) else "#000000"
            )
        
        # If empty cell (0), reveal adjacent cells
        if self.board[row][col] == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        self.reveal_cell(nr, nc)

    def reveal_all_mines(self):
        """Reveal all mines when game is over"""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] == -1 and not self.revealed[row][col]:
                    cell_id = self.cells[(row, col)]
                    self.board_canvas.itemconfig(cell_id, fill="#FF6B6B")
                    
                    x1 = col * self.cell_size
                    y1 = row * self.cell_size
                    cx = x1 + self.cell_size // 2
                    cy = y1 + self.cell_size // 2
                    
                    self.board_canvas.create_text(
                        cx, cy,
                        text="💣",
                        font=("Arial", 12),
                        fill="#FFFFFF"
                    )

    def check_win(self):
        """Check if the player has won"""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] != -1 and not self.revealed[row][col]:
                    return False
        return True

    def update_status(self, message):
        """Update status message"""
        self.status_label.config(text=message)

    def update_mines_count(self):
        """Update mines counter"""
        self.mines_label.config(text=f"Miny: {self.mines_remaining}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    game = Saper()
    root.mainloop()
