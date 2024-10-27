from os import system
import sys
from labyrinth import Labyrinth
from player import Player
from portals import Portals
import pygame
from lucky_blocks import LuckyBlock
from data_structs import Direct, Info
from math import sqrt

# TODO:
# better action if the player reaches the end
# Fragezeichen setzten mit Powerups: Teleport an eine zufällige Stelle, andere (zufällige Powerups), eine Wand entfernen, Fragen einbauen, Gegenerische Spieler einbauen, ggf. Leben
# portals could be generated right in front of the player
# add that if you have a speed lucky block, you will get other lucky blocks instead of just going over it -> WOULD BE NICE
# add enemies
# better colors/GUI -> confusing sometimes
# are all the bugs fixed??

class Game:
    def __init__(self):
        self.cell_color = (125, 175, 100)


        self.win = pygame.display.set_mode((Info.win_width, Info.win_height))
        self.lucky_blocks = {}

        self.labyrinth = Labyrinth(self.lucky_blocks)
        self.portals = Portals(self.labyrinth.end_cell)
        self.labyrinth.add_portals(self.portals.add_portal, self.portals.portal_count)

        self.player = Player(self.labyrinth.start_cell, self.portals, self.lucky_blocks, self.cell_color)
        self.labyrinth.add_lucky_blocks(self.portals.portals)


        self.key_press_duration = 0
        self.in_animation = False
        self.animation_type = None

        sys.setrecursionlimit(Info.rows * Info.cols)    # change the recursion limit to the number of cells in the labyrinth to avoid RecursionError


    def mainloop(self):
        global close_game
        run = True
        while run:
            pygame.time.Clock().tick(Info.fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    close_game = True
                    run = False
                    return

            keys = pygame.key.get_pressed()
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and 0 <= self.player.cell[1] - 1 <= (Info.cols - 1) and not self.labyrinth.labyrinth[self.player.cell[0]][self.player.cell[1]].walls["left"]:
                self.player.move(Direct.LEFT, self.redraw_window, self.player.cell[0], self.player.cell[1] - 1) # last two parameters is the updated player_position
            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and 0 <= self.player.cell[1] + 1 <= (Info.cols - 1) and not self.labyrinth.labyrinth[self.player.cell[0]][self.player.cell[1]].walls["right"]:
                self.player.move(Direct.RIGHT, self.redraw_window, self.player.cell[0], self.player.cell[1] + 1)
            if (keys[pygame.K_UP] or keys[pygame.K_w]) and 0 <= self.player.cell[0] - 1 <= (Info.rows - 1) and not self.labyrinth.labyrinth[self.player.cell[0]][self.player.cell[1]].walls["top"]:
                self.player.move(Direct.UP, self.redraw_window, self.player.cell[0] - 1, self.player.cell[1])
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and 0 <= self.player.cell[0] + 1 <= (Info.rows - 1) and not self.labyrinth.labyrinth[self.player.cell[0]][self.player.cell[1]].walls["bottom"]:
                self.player.move(Direct.DOWN, self.redraw_window, self.player.cell[0] + 1, self.player.cell[1])
               
            self.redraw_window()
            
            if self.player.cell == self.labyrinth.end_cell:
                return

    
    def redraw_window(self):
        self.win.fill(self.cell_color)

        if LuckyBlock.visible:
            self.labyrinth.draw(self.win)
        self.player.draw(self.win)
        self.portals.draw(self.win)
        if not LuckyBlock.visible:
            self.labyrinth.draw(self.win)
        pygame.display.flip()


pygame.init()
pygame.display.set_caption("Maze Game")

close_game = False
while not close_game:
    game = Game()
    game.mainloop()
