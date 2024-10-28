import sys
from labyrinth import Labyrinth
from player import Player
from portals import Portals
import pygame
from lucky_blocks import LuckyBlock
from data_structs import Direct, Info, GameContext


# TODO:
# better action if the player reaches the end
# Fragezeichen setzten mit Powerups: Teleport an eine zufällige Stelle, andere (zufällige Powerups), eine Wand entfernen, Fragen einbauen, Gegenerische Spieler einbauen, ggf. Leben
# portals could be generated right in front of the player
# add enemies
# are all the bugs fixed??
# generate new lucky blocks after the player has taken all of them?
# should the LuckyBlock class be an abstract class??? Why would that be better? -> i just saw that there are a lot of @decorators for abstract classes/methods


class Game:
    def __init__(self):
        self.game_context = GameContext()

        self.win = pygame.display.set_mode((Info.win_width, Info.win_height))

        self.labyrinth = Labyrinth(self.game_context)
        self.game_context.portals = Portals(self.game_context)

        self.player = Player(self.game_context)
        self.labyrinth.add_lucky_blocks()

        self.cell_color = (125, 175, 100)
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
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and 0 <= self.player.game_context.cell[1] - 1 <= (Info.cols - 1) and not self.labyrinth.labyrinth[self.player.game_context.cell[0]][self.player.game_context.cell[1]].walls["left"]:
                self.player.move(Direct.LEFT, self.redraw_window, self.player.game_context.cell[0], self.player.game_context.cell[1] - 1) # last two parameters is the updated player_position
            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and 0 <= self.player.game_context.cell[1] + 1 <= (Info.cols - 1) and not self.labyrinth.labyrinth[self.player.game_context.cell[0]][self.player.game_context.cell[1]].walls["right"]:
                self.player.move(Direct.RIGHT, self.redraw_window, self.player.game_context.cell[0], self.player.game_context.cell[1] + 1)
            if (keys[pygame.K_UP] or keys[pygame.K_w]) and 0 <= self.player.game_context.cell[0] - 1 <= (Info.rows - 1) and not self.labyrinth.labyrinth[self.player.game_context.cell[0]][self.player.game_context.cell[1]].walls["top"]:
                self.player.move(Direct.UP, self.redraw_window, self.player.game_context.cell[0] - 1, self.player.game_context.cell[1])
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and 0 <= self.player.game_context.cell[0] + 1 <= (Info.rows - 1) and not self.labyrinth.labyrinth[self.player.game_context.cell[0]][self.player.game_context.cell[1]].walls["bottom"]:
                self.player.move(Direct.DOWN, self.redraw_window, self.player.game_context.cell[0] + 1, self.player.game_context.cell[1])
               
            self.redraw_window()
            
            if self.player.game_context.cell == self.game_context.end_cell:
                return

    
    def redraw_window(self):
        self.win.fill(self.cell_color)

        player_visible = LuckyBlock.get_visibility()
        if player_visible:      # if the player is visible, draw teh labyrinth first
            self.labyrinth.draw(self.win)
        self.player.draw(self.win)
        self.game_context.portals.draw(self.win)
        if not player_visible:  # if the player is not visible, draw the labyrinth after the player so the player is not visble anymore
            self.labyrinth.draw(self.win)
        pygame.display.flip()


pygame.init()
pygame.display.set_caption("Maze Game")

close_game = False
while not close_game:
    game = Game()
    game.mainloop()
