import threading
from data_structs import Info, Support
from pygame import draw
from random import randint


# abstrakte Klasse LuckyBlock?? Wie geht sowas? Was bringt das?

class LuckyBlockFactory:    # is called to generate a random Lucky Block object
    @staticmethod       # so the method can be called without creating an object of the class
    def get_lucky_block(gc, remove_wall):  # -> "gc" is the game context
        all_blocks = [PartlyInvisible(), HigherSpeed(), LowerSpeed(), RandomTeleport(gc), RemoveWalls(gc, remove_wall), RerollPortals(gc)]
        return all_blocks[randint(0, len(all_blocks) - 1)]  # returns a random LuckyBlock object 
        # Erzeugt ein zufälliges LuckyBlock-Objekt



class LuckyBlock:       # TODO add getter and setter methods for the static attributes and make them private
                        # TODO MACHT HIER EINE ABSTRAKTE KLASSE SINN?? WAS GENAU BRINGT DAS? CHATGPT HAT DAS VORGESCHLAGEN
    _mark_speed_reset = False   # private static variables
    _visible = True

    def __init__(self):
        self.active_count = 0

    @staticmethod
    def get_visibility():
        return LuckyBlock._visible
    
    @staticmethod
    def set_visibility(status):
        LuckyBlock._visible = status

    @staticmethod  
    def get_speed_reset_status():
        return LuckyBlock._mark_speed_reset
    
    @staticmethod  
    def set_speed_reset_status(status):
        LuckyBlock._mark_speed_reset = status

    def action(self):
        raise NotImplementedError    # action method will be overwritten by the subclasses -> raises an error if the method is not overwritten



class HigherSpeed(LuckyBlock):
    def __init__(self):
        super().__init__()      # gets self.active_count from the LuckyBlock class
        self.speed = Info.moving_speed

    def action(self):
        Info.moving_speed = self.speed * 2          # THIS PART COULD LEAD TO PROBLEMS WITH SPECIFIC CELL/CELL SIZES
        timer = threading.Timer(8.0, self.reset_speed)  # timer is cancelled after n seconds when the method is called
        self.active_count += 1
        timer.start()

    def reset_speed(self):
        self.active_count -= 1
        if self.active_count == 0:
            LuckyBlock.set_speed_reset_status(True)


class LowerSpeed(LuckyBlock):
    def __init__(self):
        super().__init__()      # gets self.active_count from the LuckyBlock class
        self.speed = Info.moving_speed

    def action(self):
        Info.moving_speed = self.speed / 2
        timer = threading.Timer(8.0, self.reset_speed)  # timer is cancelled after n seconds when the method is called
        self.active_count += 1
        timer.start()

    def reset_speed(self):
        self.active_count -= 1
        if self.active_count == 0:
            LuckyBlock.set_speed_reset_status(True)



class RandomTeleport(LuckyBlock):
    def __init__(self, gc):
        self.game_context = gc

    def action(self):
        while True:
            new_x, new_y = randint(0, Info.rows - 1), randint(0, Info.cols - 1)
            if [new_x, new_y] != self.game_context.cell and [new_x, new_y] != self.game_context.end_cell and [new_x, new_y] not in self.game_context.lucky_blocks.values() and\
                all([new_x, new_y] != tp for portal in self.game_context.portals.portal_list for tp in portal[0:2]): # all() = ALL elements in the list have to be True
                        # we iterate over the portal list and check whether every portal is not equal to the new cell
                new_coords = [new_x, new_y]
                return new_coords, Support.get_pygame_coords(new_coords, "col"), Support.get_pygame_coords(new_coords, "row")  # teleport the player to a random cell 

    

class PartlyInvisible(LuckyBlock):
    def __init__(self):
        pass

    def action(self):
        # make the player blink between visible and invisible for a few seconds
        self.invisible()  

        intervals = [randint(0, 15) / 10, randint(0, 10) / 10, randint(0, 20) / 10, randint(0, 8) / 10, randint(0, 20) / 10,
                     randint(0, 10) / 10, randint(0, 12) / 10]  # add all the intervals in a list

        current_time = 0
        toggle_functions = [self.reset_visibility, self.invisible]  # toggle between visible and invisible

        for i, interval in enumerate(intervals):
            current_time += interval        # for every interval add the time to the total time and start a timer with the current time
            func = toggle_functions[i % 2]  # alternate between reset_visibility und invisible
            timer = threading.Timer(current_time, func)
            timer.start()

    def invisible(self):
        LuckyBlock.set_visibility(False)

    def reset_visibility(self):
        LuckyBlock.set_visibility(True)


class RemoveWalls(LuckyBlock):
    def __init__(self, gc, remove_wall):
        self.game_context = gc
        self.remove_wall = remove_wall

    def action(self):
         directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
         for directx, directy in directions:
            if 0 <= self.game_context.cell[0] + directx < Info.rows and 0 <= self.game_context.cell[1] + directy < Info.cols:
                self.remove_wall(self.game_context.cell[0], self.game_context.cell[1], self.game_context.cell[0] + directx, self.game_context.cell[1] + directy)


class RerollPortals(LuckyBlock):
    def __init__(self, gc):
        self.game_context = gc

    def action(self):
        for i in range(self.game_context.portals.portal_count):
            self.game_context.portals.delete_portal(i)  # delete all portals

class Invulnerable(LuckyBlock):       # later when enemies are added
    pass