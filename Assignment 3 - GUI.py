import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.font import BOLD
from PIL import Image, ImageTk
import cv2

# Sets up the action buttons
class Ctrl_Buttons(tk.Frame):
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

        for column in range(1, columns):
            x = column * tile_width
            self.shuffled_zone.create_line(x, 0, x, canvas_height,
                fill="#888888", width=1, tags="grid")

        # Horizontal lines
        for row in range(1, rows):
            y = row * tile_height
            self.shuffled_zone.create_line(0, y, canvas_width, y,
                fill="#888888", width=1, tags="grid")

"""Conter type labels, also introduced a timer to see how fast it can be completed"""
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
 
# Basic setup for the GUI
class User_Interface(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Image Shuffle")
        self.geometry("1200x750")
        self.config(bg="#B7E4D2")

        # Game Counters
        self.timer_seconds = 0
        self.timer_running = False        
        self.moves = 0
        self.incorrect_tiles = 0
        self.original_image=None

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

    """Once the shuffle button is pressed, the original image will be displayed in the Shuffle 
    Zone. However, if no image is in the original zone, the warning message is displayed."""
    def shuffle_image(self):
        if self.original_image is None:
            messagebox.showwarning("No Image", "Please upload an image first.")
            return
        self.images.display_shuffled_image(self.original_image)

        #Timer
        self.timer_running = False
        self.timer_seconds = 0
        self.status.timer_label(text="Time: 0s")
        self.timer_running = True
        self.update_timer()

    def give_hint(self):
        messagebox.showinfo("Hint", "Hint logic goes here!")

    def solve_puzzle(self):
            messagebox.showinfo('Solve')

    def update_timer(self):
        if not self.timer_running:
            return
        self.timer_seconds += 1
        self.status.timer_label(text=f"Time: {self.timer_seconds}s")
        self.after(1000, self.update_timer)

if __name__ == "__main__":
    app = User_Interface()
    app.mainloop()
