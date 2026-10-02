import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.font import BOLD
from PIL import Image, ImageTk
import cv2
import random
import numpy as np

# Base class for other transformation classes 
class Transformation:
    def __init__(self, description="base transform"):
       # encapsulation - the underscore marks this attribute as internal to the class
        self._description = description
 
    def apply(self, puzzle):
        #polymophic method - subclasses override this
        raise NotImplementedError("Subclasses must implement apply()")
 
    def get_description(self):
        return self._description
 
 
class SwapTransformation(Transformation): #Swaps two tiles on the board     
    def __init__(self, pos1, pos2):
        super().__init__("swap")
        self.pos1 = pos1  # (row, col)
        self.pos2 = pos2
 
    def apply(self, puzzle):
        # swap the Tile objects in the grid
        r1, c1 = self.pos1
        r2, c2 = self.pos2
        puzzle.grid[r1][c1], puzzle.grid[r2][c2] = \
            puzzle.grid[r2][c2], puzzle.grid[r1][c1]
 
 
class RotateTransformation(Transformation): # Rotates a single tile by 90 180 and 270 degrees    
    def __init__(self, pos, angle):
        super().__init__(f"rotate {angle}")
        self.pos = pos
        self.angle = angle  # 90, 180 or 270
 
    def apply(self, puzzle):
        r, c = self.pos
        tile = puzzle.grid[r][c]
        # call the tiles own rotate method
        steps = self.angle // 90
        for _ in range(steps):
            tile.rotate_clockwise() 
 
class FlipTransformation(Transformation):  # Flip a tile horizontally or vertically 
    def __init__(self, pos, direction):
        super().__init__(f"flip {direction}")
        self.pos = pos
        self.direction = direction  # "h" or "v"
 
    def apply(self, puzzle):
        r, c = self.pos
        tile = puzzle.grid[r][c]
        if self.direction == "h":
            tile.flip_horizontal()
        else:
            tile.flip_vertical() 
 
class Tile: # Provides rotational charateristics to the tiles for the shuffle puzzle section.
    def __init__(self, img_bgr, home_row, home_col):
            self._original = img_bgr.copy()
            self._home_row = home_row
            self._home_col = home_col
            self._rotation = 0
            self._mirrored = False
        
    def get_home(self):
        return self._home_row, self._home_col
 
    def get_rotation(self):
        return self._rotation       
 
    def is_mirrored(self):
        return self._mirrored      
 
    def get_current_image(self):
        img = self._original.copy() 
        if self._mirrored:
            img = cv2.flip(img, 1) 
        if self._rotation == 90:
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif self._rotation == 180:
            img = cv2.rotate(img, cv2.ROTATE_180)
        elif self._rotation == 270:
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
 
        return img
 
    def rotate_clockwise(self):
        self._rotation = (self._rotation + 90) % 360
 
    def flip_horizontal(self):
        self._rotation = (-self._rotation) % 360
        self._mirrored = not self._mirrored
 
    def flip_vertical(self):
        self._rotation = (180 - self._rotation) % 360
        self._mirrored = not self._mirrored
 
    def is_correct_orientation(self):
        return self._rotation == 0 and not self._mirrored
 
    def reset_orientation(self):
        self._rotation = 0
        self._mirrored = False

class PuzzleBoard: # Provides the grid functionality of the board
    def __init__(self, pil_image, grid_n):
        self.grid_n = grid_n
        self.grid = []
        self.hint_positions = []
        
        w, h = pil_image.size
        tile_w = w // grid_n
        tile_h = h // grid_n

        for r in range(grid_n):
            row_tiles = []
            for c in range(grid_n):
                x0 = c * tile_w
                y0 = r * tile_h
                tile_img = pil_image.crop((x0, y0, x0 + tile_w, y0 + tile_h))
                tile_bgr = cv2.cvtColor(np.array(tile_img), cv2.COLOR_RGB2BGR)
                row_tiles.append(Tile(tile_bgr, r, c))
            self.grid.append(row_tiles)

    def render_to_canvas(self, canvas):
        canvas.delete("all")
        w = int(canvas["width"])
        h = int(canvas["height"])
        tile_w = w // self.grid_n
        tile_h = h // self.grid_n

        for r in range(self.grid_n):
            for c in range(self.grid_n):
                tile = self.grid[r][c]
                img = tile.get_current_image()
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(img_rgb).resize((tile_w, tile_h))
                tk_img = ImageTk.PhotoImage(pil_img)
                tile.tk_img = tk_img

                canvas.create_image(c * tile_w, r * tile_h, anchor="nw", image=tk_img)

                if (r, c) in self.hint_positions:
                    cx = c * tile_w + tile_w // 2
                    cy = r * tile_h + tile_h // 2
                    radius = min(tile_w, tile_h) // 4
                    canvas.create_oval(
                    cx - radius,
                    cy - radius,
                    cx + radius,
                    cy + radius,
                    outline="#0F24E4",
                    width=3)
                
                home_r, home_c = tile.get_home()
                if home_r == r and home_c == c and tile.is_correct_orientation():
                    canvas.create_text(
                        c * tile_w + tile_w - 15,
                        r * tile_h + 15,
                        text="✔",
                        fill="#0FE40F",
                        font=("Arial", 18, "bold"))

class Ctrl_Buttons(tk.Frame): # Sets up the action buttons
    def __init__(self, master, app):
        super().__init__(master, bg="#B7E4D2")
        self.app = app
        self.create_widgets()

    def create_widgets(self):

        # Grid Select Button
        self.grid_size_var = tk.StringVar(value="3x3")
        self.grid_btn = tk.OptionMenu(
            self,
            self.grid_size_var,
            "3x3",
            "4x4",
            "5x5",)
        self.grid_btn.config(width=12, bg="#D5DDDF")
        self.grid_btn.grid(row=0, column=0, pady=5, padx=5)

        # Upload button
        self.upload_btn = tk.Button(
            self,
            text="Upload Image",
            bg="#D5DDDF",
            width=12,
            command=self.app.load_image)
        self.upload_btn.grid(row=0, column=1, pady=5, padx=5)
        
        # Shuffle button
        self.shuffle_btn = tk.Button(
            self,
            text="Shuffle",
            bg="#D5DDDF",
            width=12,
            command=self.app.shuffle_image)
        self.shuffle_btn.grid(row=0, column=2, pady=5, padx=5)
        
        # Hint Button
        self.hint_btn = tk.Button(
            self,
            text="Hint",
            bg="#D5DDDF",
            width=12,
            command=self.app.give_hint)
        self.hint_btn.grid(row=0, column=3, pady=5, padx=5, sticky='w')

        #Solve Button
        self.solve_btn = tk.Button(
            self,
            text="Solve",
            width=12,
            bg="#D5DDDF",
            command=self.app.solve_puzzle)
        self.solve_btn.grid(row= 0, column = 4, padx= 5, pady=5)

""" Sets up the zones where the images will be displayed, their headers and some manipulation,
particularly grids"""
class Image_Panels(tk.Frame): 
    def __init__(self, master, app):
        super().__init__(master, bg="#B7E4D2")
        self.app = app
        self.original_img_tk = None
        self.shuffled_img_tk = None
        self.create_widgets()

    def create_widgets(self):

        # Original Image Header
        self.original_header = tk.Label(
            self,
            text="Original Image",
            font=("Arial", 14, BOLD),
            bg="#B7E4D2")
        self.original_header.place(x=20, y=20)

        # Original Image Zone
        self.original_zone = tk.Canvas(
            self,
            bg="#edf2f7",
            width=400,
            height=300,
            bd=2,
            relief="solid",
            highlightthickness=0)
        self.original_zone.place(x=20, y=60, width=400, height=300)

        # Shuffled Image Header
        self.shuffled_header = tk.Label(
            self,
            text="Shuffled Image",
            font=("Arial", 14, BOLD),
            bg="#B7E4D2")
        self.shuffled_header.place(x=450, y=20)

        # Shuffled Image Zone
        self.shuffled_zone = tk.Canvas(
            self,
            bg="#edf2f7",
            bd=2,
            relief="solid",
            highlightthickness=0,
            width=700,
            height=500)
        self.shuffled_zone.place(x=450, y=60, width=700, height=500)

    def display_original_image(self, image):
        self.original_zone.delete("all")
        self.original_img_tk = ImageTk.PhotoImage(image)
        self.original_zone.create_image(0, 0, anchor="nw", image=self.original_img_tk)

    def display_shuffled_image(self, image):        
        self.shuffled_zone.delete("all")
        self.shuffled_img_tk = ImageTk.PhotoImage(image)
        self.shuffled_zone.create_image(0, 0, anchor="nw", image=self.shuffled_img_tk)
        self.draw_grid()

    def draw_grid(self):

        # Remove previous grid
        self.shuffled_zone.delete("grid")
        grid_size = self.app.controls.grid_size_var.get()
        rows, columns = map(int, grid_size.split("x"))

        canvas_width = 700
        canvas_height = 500

        tile_width = canvas_width / columns
        tile_height = canvas_height / rows

        for column in range(1, columns): # Vertical Lines
            x = column * tile_width
            self.shuffled_zone.create_line(x, 0, x, canvas_height,
                fill="#888888", width=1, tags="grid")

        # Horizontal lines
        for row in range(1, rows):
            y = row * tile_height
            self.shuffled_zone.create_line(0, y, canvas_width, y,
                fill="#888888", width=1, tags="grid")

"""Counter type labels, also introduced a timer to see how fast it can be completed"""
class Status_Bar(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg="#B7E4D2")
        self.app = app
        self.create_widgets()

    def create_widgets(self):

        # Timer Label
        self.timer_label = tk.Label(
            self,
            text="Time: 0s",
            font=("Arial", 14, BOLD),
            bg="#B7E4D2")
        self.timer_label.grid(row=0, column=0, padx=15)

        # Moves Counter
        self.moves_label = tk.Label(
            self,
            text="Moves: 0",
            font=("Arial", 14, BOLD),
            bg="#B7E4D2")
        self.moves_label.grid(row=0, column=1, padx=15)

        # Incorrect tiles remaining
        self.incorrect_label = tk.Label(
            self,
            text="Incorrect: 0",
            font=("Arial", 14, BOLD),
            bg="#B7E4D2")        
        self.incorrect_label.grid(row=0, column=2, padx=15)

class GameLogic:
    def __init__(self):
        self.moves = 0
        self.selected_tile = None

    def select_tile(self, tile_pos):
        if self.selected_tile is None:
            self.selected_tile = tile_pos
            return False
        elif self.selected_tile == tile_pos:
            self.selected_tile = None
            return False
        else:
            first = self.selected_tile
            self.selected_tile = None
            return (first, tile_pos)

    def swap_tiles(self, puzzle, pos1, pos2):
        SwapTransformation(pos1, pos2).apply(puzzle)
        self.moves += 1

    def rotate_tile(self, puzzle, pos, angle):
        RotateTransformation(pos, angle).apply(puzzle)
        self.moves += 1

    def flip_tile(self, puzzle, pos, direction):
        FlipTransformation(pos, direction).apply(puzzle)
        self.moves += 1

    def check_win(self, puzzle):
        for r in range(puzzle.grid_n):
            for c in range(puzzle.grid_n):
                tile = puzzle.grid[r][c]
                home_r, home_c = tile.get_home()
                if home_r != r or home_c != c:
                    return False
                if not tile.is_correct_orientation():
                    return False
        return True
 
# Brings all the previous classes together plus mouse / keystroke inputs.
class User_Interface(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Image Shuffle")
        self.geometry("1200x750")
        self.config(bg="#B7E4D2")

        # Game Counters
        self.timer_seconds = 0
        self.timer_running = False        
        self.original_image = None
        self.logic = GameLogic()
        self.puzzle = None
        
        self.create_widgets()

    def create_widgets(self):

        self.label1 = tk.Label(
            self,
            text="Image Shuffler",
            font=("Arial", 22, BOLD),
            bg="#B7E4D2")
        self.label1.pack(pady=10)

        self.instruction_label = tk.Label(
            self,
            text="Select Grid Size → Upload an Image → Hit Shuffle",
            font=("Arial", 13),
            bg="#B7E4D2")
        self.instruction_label.pack(pady= 5)

        # Control panel (buttons)
        self.controls = Ctrl_Buttons(self, self)
        self.controls.pack(anchor="w")

        # Image Panels
        self.images = Image_Panels(self, self)
        self.images.place(x=10, y=130, width=1160, height=580)

        # Counters
        self.status = Status_Bar(self, self)
        self.status.place(x=650, y=710)

    """Loads an image from a desired location then resizes the image for the specified areas"""
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])

        if not file_path:
            return

        img_cv = cv2.imread(file_path)
        if img_cv is None:
            messagebox.showerror("Error", "Could not load image.")
            return

        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(img_cv)

        # Resizes the images for both Original Image zone and Shuffle Image Zone
        self.original_image = image.resize((700, 500))
        original_display = image.resize((400, 300))
        self.images.display_original_image(original_display)       

    def pad_image_to_grid(self, image, grid_n):
        w, h = image.size
        tile_w = w // grid_n
        tile_h = h // grid_n
        new_w = tile_w * grid_n
        new_h = tile_h * grid_n
        padded = Image.new("RGB", (new_w, new_h), (255, 255, 255))
        padded.paste(image.resize((new_w, new_h)), (0, 0))
        return padded
    
    """Once the shuffle button is pressed, the original image will be displayed in the Shuffle 
    Zone. However, if no image is in the original zone, the warning message is displayed."""
    def shuffle_image(self):
        if self.original_image is None:
            messagebox.showwarning("No Image", "Please upload an image first.")
            return

        grid_n = int(self.controls.grid_size_var.get()[0])
        padded = self.pad_image_to_grid(self.original_image, grid_n)

        self.puzzle = PuzzleBoard(padded, grid_n)
        self.apply_random_transformations()

        self.puzzle.render_to_canvas(self.images.shuffled_zone)
        self.images.draw_grid()

        self.bind_tile_events()

        # Reset timer
        self.timer_seconds = 0
        self.timer_running = True
        self.status.timer_label.config(text=f"Time: {self.timer_seconds}s")
        self.update_timer()

        self.logic.moves = 0
        self.status.moves_label.config(text="Moves: 0")

    def bind_tile_events(self):
        canvas = self.images.shuffled_zone
        canvas.bind("<Button-1>", self.on_left_click)
        canvas.bind("<Button-3>", self.on_right_click)
        canvas.bind("<Shift-Button-1>", self.on_shift_left_click)

    def apply_random_transformations(self):
        grid_n = self.puzzle.grid_n
        transform_count = {3: 6, 4: 12, 5: 20}[grid_n]

        for _ in range(transform_count):
            r = random.randint(0, grid_n - 1)
            c = random.randint(0, grid_n - 1)
            pos = (r, c)
            action = random.choice(["swap", "rotate", "flip"])

            if action == "swap":
                r2 = random.randint(0, grid_n - 1)
                c2 = random.randint(0, grid_n - 1)
                SwapTransformation(pos, (r2, c2)).apply(self.puzzle)

            elif action == "rotate":
                angle = random.choice([90, 180, 270])
                RotateTransformation(pos, angle).apply(self.puzzle)

            elif action == "flip":
                direction = random.choice(["h", "v"])
                FlipTransformation(pos, direction).apply(self.puzzle)
                
    # Hint Function
    def give_hint(self):
        if self.puzzle is None:
            return
    
        incorrect_positions = []
        for r in range(self.puzzle.grid_n):
            for c in range(self.puzzle.grid_n):
                tile = self.puzzle.grid[r][c]
                home_r, home_c = tile.get_home()
                if home_r != r or home_c != c or not tile.is_correct_orientation():
                    incorrect_positions.append((r, c))
    
        if len(incorrect_positions) < 2:
            return        
        pos1, pos2 = random.sample(incorrect_positions, 2)

        self.puzzle.hint_positions = [pos1, pos2]
        self.puzzle.render_to_canvas(self.images.shuffled_zone)
        self.images.draw_grid()
        self.status.incorrect_label.config(text=f"Incorrect: {self.count_incorrect_tiles()}")

    def get_tile_pos(self, event):
        grid_n = self.puzzle.grid_n
        w = int(self.images.shuffled_zone["width"])
        h = int(self.images.shuffled_zone["height"])
        tile_w = w // grid_n
        tile_h = h // grid_n
        return (event.y // tile_h, event.x // tile_w)

    def redraw_puzzle(self):
        self.puzzle.render_to_canvas(self.images.shuffled_zone)
        self.images.draw_grid()
        self.puzzle.hint_positions = []
        self.status.moves_label.config(text=f"Moves: {self.logic.moves}")

    # Mouse Clicks
    def on_left_click(self, event):
        pos = self.get_tile_pos(event)
        selection = self.logic.select_tile(pos)
        if selection is False:
            return
        pos1, pos2 = selection
        self.logic.swap_tiles(self.puzzle, pos1, pos2)
        self.redraw_puzzle()
        self.status.incorrect_label.config(text=f"Incorrect: {self.count_incorrect_tiles()}")

    def on_right_click(self, event):
        pos = self.get_tile_pos(event)
        self.logic.rotate_tile(self.puzzle, pos, 90)
        self.redraw_puzzle()
        self.status.incorrect_label.config(text=f"Incorrect: {self.count_incorrect_tiles()}")

    def on_shift_left_click(self, event):
        pos = self.get_tile_pos(event)
        self.logic.flip_tile(self.puzzle, pos, "h")
        self.redraw_puzzle()
        self.status.incorrect_label.config(text=f"Incorrect: {self.count_incorrect_tiles()}")

    def solve_puzzle(self):
        if self.puzzle is None:
            return
        for row in self.puzzle.grid:
            for tile in row:
                tile.reset_orientation()
        self.logic.moves = 0
        self.redraw_puzzle()
        self.status.incorrect_label.config(text=f"Incorrect: {self.count_incorrect_tiles()}")

    def count_incorrect_tiles(self):
        incorrect = 0
        for r in range(self.puzzle.grid_n):
            for c in range(self.puzzle.grid_n):
                tile = self.puzzle.grid[r][c]
                home_r, home_c = tile.get_home()
                if home_r != r or home_c != c or not tile.is_correct_orientation():
                    incorrect += 1
        return incorrect

    def update_timer(self):
        if not self.timer_running:
            return
        self.timer_seconds += 1
        self.status.timer_label.config(text=f"Time: {self.timer_seconds}s")
        self.after(1000, self.update_timer)
        if self.puzzle is not None and self.logic.check_win(self.puzzle):
            self.timer_running = False
            messagebox.showinfo("Solved!", "You solved the puzzle!")
        return

if __name__ == "__main__":
    app = User_Interface()
    app.mainloop()
