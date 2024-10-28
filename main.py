import sys
from labyrinth import Labyrinth
from player import Player
from portals import Portals
import pygame
from lucky_blocks import LuckyBlock
from data_structs import Direct, Info, GameContext
from enemies import EnemyRegulator
from threading import Timer


# TODO:
# better action if the player reaches the end
# Fragezeichen setzten mit Powerups: Teleport an eine zufällige Stelle, andere (zufällige Powerups), eine Wand entfernen, Fragen einbauen, Gegenerische Spieler einbauen, ggf. Leben
# portals could be generated right in front of the player
# add enemies
# are all the bugs fixed??
# generate new lucky blocks after the player has taken all of them?
# should the LuckyBlock class be an abstract class??? Why would that be better? -> i just saw that there are a lot of @decorators for abstract classes/methods
# if the player has a different speed, then the game ends and a new game starts, the player has still the same speed as before (faster/slower)
# TODO KANN MAN WENN MAN IN EINEM PORTAL STEHT AN EINEM GEGENER VERLIEREN? INVULNERABILITY FÜR SPIELER (LUCKY BLOCK) HINZUFÜGEN
# TODO WEITERE LUCKY-BLOCK IDEE: DER BLOCK BLINKT ROT FÜR 2 SEKUNDEN ODER SO, DANN WIRD EIN ZUFÄLLIGER GEGNER IN DEN BLOCK TELEPORTIERT
# TODO GEGENER JAGEN DEN SPIELER, WENN SIE LINE-OF-SIGHT HABEN
# TODO MANCHMAL VERWRREND, OB MAN UNSICHTBAR IST ODER TELEPORTIERT WURDE
# TODO BESSERES KOLLIEDIEREN MIT DEN GEGNERN -> MIT HITBOXEN UND DIESE DANN VERGLEICHEN TODO 
                    # DAFÜR HITBOXEN FÜR SPIELER UND GEGNER FESTLEGEN UND DIESE DANN VERGLEICHEN, ANSTATT DIE ZELLEN ZU VERGLEICHEN
# TODO GEGNER KÖNNTEN AUCH LUCKY BLOCKS EINSAMMELN KÖNNEN -> WENN DANN IRGENDWANN ALLE LUCKY BLOCKS WEG SIND, WERDEN EINFACH WIEDER NEUE GENERIERT
                    # DAS WÜRDE AUCH ETWAS DAS PROBLEM LÖSEN, DASS DIE GEGENER TEILWEISE NICHT GUT VOM SPAWN WEGKOMMEN -> MAN MÜSSTE VIELLECHT SCHAUEN, DASS GEGENER NICHT DIREKT IM/VORM SPIELER SPAWNEN


class Game:
    def __init__(self):
        self.game_context = GameContext()

        self.win = pygame.display.set_mode((Info.win_width, Info.win_height))

        self.labyrinth = Labyrinth(self.game_context)
        self.game_context.portals = Portals(self.game_context)

        self.player = Player(self.game_context)
        self.labyrinth.add_lucky_blocks()

        self.enemies = EnemyRegulator(self.game_context, self.labyrinth.labyrinth_grid)
        for i in range(self.enemies.enemy_count):
            timer = Timer(i * 0.6, self.enemies.create_enemy)
            timer.start()
        
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
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not self.labyrinth.labyrinth_grid[self.player.game_context.cell[0]][self.player.game_context.cell[1]].walls["left"]:
                self.player.move(Direct.LEFT, self.redraw_window, self.player.game_context.cell[0], self.player.game_context.cell[1] - 1) # last two parameters is the updated player_position
            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and not self.labyrinth.labyrinth_grid[self.player.game_context.cell[0]][self.player.game_context.cell[1]].walls["right"]:
                self.player.move(Direct.RIGHT, self.redraw_window, self.player.game_context.cell[0], self.player.game_context.cell[1] + 1)
            if (keys[pygame.K_UP] or keys[pygame.K_w]) and not self.labyrinth.labyrinth_grid[self.player.game_context.cell[0]][self.player.game_context.cell[1]].walls["top"]:
                self.player.move(Direct.UP, self.redraw_window, self.player.game_context.cell[0] - 1, self.player.game_context.cell[1])
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and not self.labyrinth.labyrinth_grid[self.player.game_context.cell[0]][self.player.game_context.cell[1]].walls["bottom"]:
                self.player.move(Direct.DOWN, self.redraw_window, self.player.game_context.cell[0] + 1, self.player.game_context.cell[1])
               
            self.redraw_window()
            
            if self.player.game_context.cell == self.game_context.end_cell:
                return
            for enemy in self.enemies.enemies:
                if enemy.cell == self.player.game_context.cell:
                    return

    
    def redraw_window(self):
        self.win.fill(self.cell_color)

        self.labyrinth.draw(self.win)
        if LuckyBlock.get_visibility() and not self.player.player_in_portal:
            self.player.draw(self.win)
        self.game_context.portals.draw(self.win)
        self.enemies.move_all_enemies(self.win) # move the enemies and draw them at the same time
        pygame.display.flip()


pygame.init()
pygame.display.set_caption("Maze Game")

close_game = False
while not close_game:
    game = Game()
    game.mainloop()
