from enum import Enum


class Direct(Enum):
    UP = 0
    DOWN = 1 
    LEFT = 2 
    RIGHT = 3


class GameContext:
    def __init__(self):
        self.cell = None
        self.end_cell = None
        self.lucky_blocks = {}
        self.portals = None


class Info:
    rows = 20
    cols = 30
    cell_size = int(800 / rows)
    if (cell_size) % 2 != 0:
        cell_size -= 1      # cell size should be an even number to avoid problems with the animation of the player when moving -> easier to change the moving speed
    wall_width = cell_size // 10
    moving_speed = ((cell_size + wall_width) / 11) if (cols > (rows * 1.1)) else 1
    resetted_player_speed = moving_speed    # because the speed of the player is changed with this variable we can reset it
    win_width = cols * cell_size + (wall_width * (cols + 1))
    win_height = rows * cell_size + (wall_width * (rows + 1))
    fps = 120



class Cell:
    def __init__(self, i, j):
        self.walls = {
            "top": True,
            "right": True,
            "bottom": True,
            "left": True
        }
        self.visited = False
        self.i = i
        self.j = j
        # maybe add the questoin cell here


class Support:
    @staticmethod
    def get_pygame_coords(cell, r_or_c):
        coordinate = (cell[1] if r_or_c == "col" else cell[0])
        return (coordinate * Info.cell_size + (coordinate + 1) * Info.wall_width)