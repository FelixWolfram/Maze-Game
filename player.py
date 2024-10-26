from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT
from pygame import draw
from data_structs import Direct, Info, Support
from time import sleep
from random import randint


class Player:
    def __init__(self, start_cell, power_ups):
        self.cell = start_cell
        self.power_ups = power_ups
        self.player_color = (80, 68, 220)
        self.sleep_time = round(0.103 / (Info.cell_size + Info.wall_width), 3)

        self.valid_moves = ("w", "a", "s", "d")
        self.x = self.cell[1] * Info.cell_size + Info.wall_width * (self.cell[1] + 1)
        self.y = self.cell[0] * Info.cell_size + Info.wall_width * (self.cell[0] + 1)  


    def move(self, move, redraw_window, new_x, new_y):
        self.cell = [new_x, new_y]

        for _ in range(round((Info.cell_size + Info.wall_width) / Info.moving_speed)):
            if len(self.power_ups.portals) < self.power_ups.max_portals and randint(0, round(1 / self.sleep_time) * self.power_ups.portals_frequency) == 0:
                self.power_ups.add_portal()   # also check for adding a new portals during the move animation

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

        if self.power_ups.portals:
            teleport_destination, teleported = self.power_ups.check_for_portal(self.cell)
            if teleported:  # if the player is moving into a teleport-cell
                self.cell = teleport_destination
                self.x = Support.get_pygame_coords(self.cell, "col")
                self.y = Support.get_pygame_coords(self.cell, "row")


    def draw(self, win):
        draw.rect(win, self.player_color, (self.x, self.y, Info.cell_size, Info.cell_size))