import threading
from data_structs import Info, Support
from pygame import draw


# abstrakte Klasse LuckyBlock?? Wie geht sowas? Was bringt das?

class LuckyBlockFactory:    # is called to generate a random Lucky Block object
    @staticmethod       # so the method can be called without creating an object of the class
    def get_lucky_block(cell):  # returns a random LuckyBlock object 
        return LowerSpeed(cell)
        # Erzeugt ein zufälliges LuckyBlock-Objekt


class LuckyBlock:
    background_color = (150, 160, 170)

    def __init__(self):
        self.cell = None
        self.max_count = 3
    
    def draw(self, win):
        draw.rect(win, self.background_color, (Support.get_pygame_coords(self.cell, "col"), Support.get_pygame_coords(self.cell, "row"), Info.cell_size, Info.cell_size))

    def check_for_collision(self, player_cell):
        self.action()
    
    def action(self):
        raise NotImplementedError    # action method will be overwritten by the subclasses -> raises an error if the method is not overwritten


class HigherSpeed(LuckyBlock):
    pass


class LowerSpeed(LuckyBlock):
    def __init__(self, cell):
        super().__init__()      # calls the __init__ method of the superclass -> otherwise self.cell and self.max_count would not be initialized
        self.timer = None
        self.speed = Info.moving_speed
        self.timer = threading.Timer(5.0, self.reset_speed)
        self.cell = cell

    def action(self):
        Info.moving_speed *= 0.5    

    def reset_speed(self):
        Info.moving_speed = self.speed
        self.timer.cancel()     # woulnd't be a problem when not cancelling the timer here, but probably better for readability
        

class RandomTeleport(LuckyBlock):
    pass


class PartlyInvisible(LuckyBlock):
    pass


class RemoveWalls(LuckyBlock):
    pass


class Invulnerable(LuckyBlock):       # later when enemies are added
    pass