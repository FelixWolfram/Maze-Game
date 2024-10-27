import threading
from data_structs import Info, Support
from pygame import draw
from random import randint


# abstrakte Klasse LuckyBlock?? Wie geht sowas? Was bringt das?

class LuckyBlockFactory:    # is called to generate a random Lucky Block object
    @staticmethod       # so the method can be called without creating an object of the class
    def get_lucky_block(cell, remove_wall, end_cell, portals, lucky_block_cells):  # returns a random LuckyBlock object 
        all_blocks = [PartlyInvisible(), RandomTeleport(cell, end_cell, portals, lucky_block_cells), HigherSpeed(), LowerSpeed(), RemoveWalls(cell, remove_wall)]
        return all_blocks[randint(0, len(all_blocks) - 1)]
        # Erzeugt ein zufälliges LuckyBlock-Objekt



class LuckyBlock:
    background_color = (150, 160, 170)
    resetted_player_speed = Info.moving_speed
    mark_speed_reset = False
    using_speed_block = False
    visible = True

    def draw(self, win):
        draw.rect(win, self.background_color, (Support.get_pygame_coords(self.cell, "col"), Support.get_pygame_coords(self.cell, "row"), Info.cell_size, Info.cell_size))
    
    def action(self):
        raise NotImplementedError    # action method will be overwritten by the subclasses -> raises an error if the method is not overwritten



class HigherSpeed(LuckyBlock):
    def __init__(self):
        self.speed = Info.moving_speed

    def action(self):
        LuckyBlock.using_speed_block = True
        Info.moving_speed = self.speed * 2          # THIS PART COULD LEAD TO PROBLEMS WITH SPECIFIC CELL/CELL SIZES
        timer = threading.Timer(8.0, self.reset_speed)  # timer is cancelled after n seconds when the method is called
        timer.start()

    def reset_speed(self):
        LuckyBlock.mark_speed_reset = True
        LuckyBlock.using_speed_block = False



class LowerSpeed(LuckyBlock):
    def __init__(self):
        self.speed = Info.moving_speed

    def action(self):
        LuckyBlock.using_speed_block = True
        Info.moving_speed = self.speed / 2
        timer = threading.Timer(8.0, self.reset_speed)  # timer is cancelled after n seconds when the method is called
        timer.start()

    def reset_speed(self):
        LuckyBlock.mark_speed_reset = True
        LuckyBlock.using_speed_block = False
        


class RandomTeleport(LuckyBlock):
    def __init__(self, cell, end_cell, portals, lucky_block_cells):
        self.lucky_block_cells = lucky_block_cells
        self.cell = cell
        self.portals = portals
        self.end_cell = end_cell

    def action(self):
        while True:
            new_x, new_y = randint(0, Info.rows - 1), randint(0, Info.cols - 1)
            if [new_x, new_y] != self.cell and [new_x, new_y] != self.end_cell and [new_x, new_y] not in self.lucky_block_cells and\
                all([new_x, new_y] != tp for portal in self.portals for tp in portal[0:2]): # all() = ALL elements in the list have to be True
                        # we iterate over the portal list and check whether every portal is not equal to the new cell
                new_coords = [new_x, new_y]
                return new_coords, Support.get_pygame_coords(new_coords, "col"), Support.get_pygame_coords(new_coords, "row")  # teleport the player to a random cell 

    

class PartlyInvisible(LuckyBlock):
    def action(self):
        # make the player blink between visible and invisible for a few seconds
        self.invisible()  

        intervals = [randint(0, 20) / 10, randint(0, 15) / 10, randint(0, 30) / 10, randint(0, 10) / 10, randint(0, 30) / 10,
                     randint(0, 12) / 10, randint(0, 15) / 10]  # add all the intervals in a list

        current_time = 0
        toggle_functions = [self.reset_visibility, self.invisible]  # toggle between visible and invisible

        for i, interval in enumerate(intervals):
            current_time += interval        # for every interval add the time to the total time and start a timer with the current time
            func = toggle_functions[i % 2]  # alternate between reset_visibility und invisible
            timer = threading.Timer(current_time, func)
            timer.start()

    def invisible(self):
        LuckyBlock.visible = False

    def reset_visibility(self):
        LuckyBlock.visible = True



class RemoveWalls(LuckyBlock):
    def __init__(self, cell, remove_wall):
        self.cell = cell
        self.remove_wall = remove_wall

    def action(self):
         directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
         for directx, directy in directions:
            if 0 <= self.cell[0] + directx < Info.rows and 0 <= self.cell[1] + directy < Info.cols:
                self.remove_wall(self.cell[0], self.cell[1], self.cell[0] + directx, self.cell[1] + directy)


class Invulnerable(LuckyBlock):       # later when enemies are added
    pass