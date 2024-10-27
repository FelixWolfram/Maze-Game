from math import floor
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT
from pygame import draw
from data_structs import Direct, Info, Support
from lucky_blocks import LuckyBlock, RandomTeleport, HigherSpeed, LowerSpeed
from time import sleep
from random import randint


class Player:
    def __init__(self, start_cell, portals, lucky_blocks, cell_color):
        self.cell = start_cell
        self.cell_color = cell_color
        self.portals = portals
        self.player_color = (80, 68, 220)
        self.sleep_time = round(0.103 / (Info.cell_size + Info.wall_width), 3)
        self.lucky_blocks = lucky_blocks

        self.valid_moves = ("w", "a", "s", "d")
        self.x = self.cell[1] * Info.cell_size + Info.wall_width * (self.cell[1] + 1)
        self.y = self.cell[0] * Info.cell_size + Info.wall_width * (self.cell[0] + 1)
        self.portals_for_delete_index = []     # when the player teleported to a new cell, the portal on the old cell should be deleted


    def move(self, move, redraw_window, new_x, new_y):
        self.cell = [new_x, new_y]

        for _ in range(floor((Info.cell_size + Info.wall_width) / Info.moving_speed)):

            if move == Direct.LEFT:
                self.x -= Info.moving_speed
            elif move == Direct.RIGHT:
                self.x += Info.moving_speed
            elif move == Direct.UP:
                self.y -= Info.moving_speed
            elif move == Direct.DOWN:
                self.y += Info.moving_speed

            sleep(self.sleep_time)
            redraw_window()

        self.x = Support.get_pygame_coords(self.cell, "col")    # correct the player position to the cell position if there is a deviation
        self.y = Support.get_pygame_coords(self.cell, "row")    # deviation can be caused by the moving speed and the cell size
    
        if LuckyBlock.mark_speed_reset:
            Info.moving_speed = LuckyBlock.resetted_player_speed
            LuckyBlock.mark_speed_reset = False
        if self.portals_for_delete_index:    # if the player teleported to a new cell and now left the cell again
            color_to_delete = self.portals.portals[self.portals_for_delete_index[0]][2]
            self.portals.disabled_tp_colors.remove(color_to_delete)  # remove the color of the disabled portal out of the used colors list
            
            del self.portals.portals[self.portals_for_delete_index.pop()]  # delete the portal on the old cell
            self.portals.add_portal(self.lucky_blocks.values(), self.cell)  # add a new portal on the new cell
        
        self.check_for_portal()
        self.check_for_lucky_block()
        

    def check_for_portal(self):
        if self.portals.portals:
            index, teleport_destination, teleported = self.portals.check_for_portal(self.cell)
            if teleported:  # if the player is moving into a teleport-cell -> teleport the player to the destination
                self.cell = teleport_destination
                self.x = Support.get_pygame_coords(self.cell, "col")
                self.y = Support.get_pygame_coords(self.cell, "row")
                self.portals_for_delete_index.append(index)


    def check_for_lucky_block(self):
        if self.lucky_blocks:
            if self.cell in self.lucky_blocks.values():
                lucky_block_on_player = list(self.lucky_blocks.keys())[list(self.lucky_blocks.values()).index(self.cell)] # get the lucky block which is on the player cell
                
                if not ((type(lucky_block_on_player) == HigherSpeed or type(lucky_block_on_player) == LowerSpeed) and\
                         LuckyBlock.using_speed_block): # if you already have another speed, do not change the speed
                    if type(lucky_block_on_player) == RandomTeleport:
                        self.cell, self.x, self.y = lucky_block_on_player.action()
                    else:
                        lucky_block_on_player.action()
                    del self.lucky_blocks[lucky_block_on_player]


    def draw(self, win):
        player_color = self.player_color if LuckyBlock.visible else self.cell_color
        draw.rect(win, player_color, (self.x, self.y, Info.cell_size, Info.cell_size))