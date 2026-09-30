"""
This file handles  transformations and tiles:
base classes, Tile class, Transformation
hierarchy (inheritance + polymorphism).

"""
 

import cv2

  
class Transformation:
    """
    The base class for tile transformations
    shows inheritance and polymorphism. Every subclass
    implements the apply() method.
    """
 
    def __init__(self, description="base transform"):
       # encapsulation - the underscore marks this attribute as internal to the class
        self._description = description
 
    def apply(self, puzzle):
        #polymophic method - subclasses override this
        raise NotImplementedError("Subclasses must implement apply()")
 
    def get_description(self):
        return self._description
 
 
class SwapTransformation(Transformation):
    #Swaps two tiles on the board
 
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
 
 
class RotateTransformation(Transformation):
    # Rotates a single tile by 90 180 and 270 degrees
 
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
 
 
class FlipTransformation(Transformation):
    # Flip a tile horizontally or vertically
 
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
 
 
class Tile:
    # Represents one puzzle piece and its current orientation.
 
    def __init__(self, img_bgr, home_row, home_col):
        self._original = img_bgr.copy()
        self._home_row = home_row
        self._home_col = home_col
        
       
        self._rotation = 0        # clockwise rotation: 0, 90, 180 or 270
        self._mirrored = False    # True after an odd number of flips
 
    #  getters (encapsulation)
    def get_home(self):
        return self._home_row, self._home_col
 
    def get_rotation(self):
        # Returns the current clockwise rotation in degrees.
        return self._rotation
    
       
 
    def is_mirrored(self):
        # Return True if the tile is curently mirrored
        return self._mirrored
       
 
    def get_current_image(self):
        # Redraw the tile from scratch using its current rotation/mirror state.
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
                # negate the rotation and toggle the mirrored flag because a fliping
        # reverses the direction of any rotation already applied
        self._rotation = (-self._rotation) % 360
        self._mirrored = not self._mirrored
 
    def flip_vertical(self):
        # Same thing as flip_horizontal just mirrored around the
        # other axis which flips the sign the other way 
        self._rotation = (180 - self._rotation) % 360
        self._mirrored = not self._mirrored
 
    def is_correct_orientation(self):
        # A tile can be spun back to normal ( rotated 90 four
        # times) or flipped back to normal (flipped twice). it should
        # count as correct in that case whether just when it has never
        # been touched.
        return self._rotation == 0 and not self._mirrored
 
    def reset_orientation(self):
        self._rotation = 0
        self._mirrored = False
