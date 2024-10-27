from random import randint
from data_structs import Info, Support
from pygame import draw


class Portals:
    def __init__(self, end_cell):
        self.portals = []
        self.end_cell = end_cell
        self.portal_count = ((Info.rows * Info.cols) // 100) - 2  # 2 for a 20x20 maze, 4 for a 20x30 maze
        self.portals_frequency = 6   # on average n seconds a new portals will be added
        self.tp_colors = [(170, 83, 170), (64, 140, 194), (180, 120, 40), (127, 186, 132), (200, 115, 115), (163, 191, 105), (90, 90, 160)]
        self.disabled_tp_colors = []

    
    def add_portal(self, lucky_blocks_cells, cell):
        tp1 = tp2 = 0
        while tp1 == tp2 or (tp1 == self.end_cell or tp2 == self.end_cell) or tp1 == tp2 or (tp1 == cell or tp2 == cell) or\
              tp1 in lucky_blocks_cells or tp2 in lucky_blocks_cells or\
                not all([tp1, tp2] != tp for portal in self.portals for tp in portal[0:2]):   # make sure the two portals are not the same and not generating on a lucky block
            tp1 = [randint(0, Info.rows - 1), randint(0, Info.cols - 1)]
            tp2 = [randint(0, Info.rows - 1), randint(0, Info.cols - 1)]
        while True:   # get an unused color for the portal
            tp_color = self.tp_colors[randint(0, len(self.tp_colors) - 1)]
            if tp_color not in self.disabled_tp_colors:
                break
        self.disabled_tp_colors.append(tp_color)
        self.portals.append((tp1, tp2, tp_color))


    def check_for_portal(self, current_cell):
        for index, (tp1, tp2, _) in enumerate(self.portals):
            if current_cell  == tp1 or current_cell == tp2:
                teleport_destination = tp2 if current_cell == tp1 else tp1
                return index, teleport_destination, True
        return None, None, False
 

    def draw(self, win):
        for tp1, tp2, color in self.portals:
            draw.rect(win, color, (Support.get_pygame_coords(tp1, "col"), Support.get_pygame_coords(tp1, "row"), Info.cell_size, Info.cell_size))
            draw.rect(win, color, (Support.get_pygame_coords(tp2, "col"), Support.get_pygame_coords(tp2, "row"), Info.cell_size, Info.cell_size))
