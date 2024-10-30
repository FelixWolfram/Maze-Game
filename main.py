import sys
from labyrinth import Labyrinth
from player import Player
from portals import Portals
import pygame
from lucky_blocks import LuckyBlock
from data_structs import Direct, Info, GameContext
from enemies import EnemyRegulator
from threading import Timer
from energy_orb import MasterEnergyOrbs
from ability import Invulnerability


# TODO:
# better action if the player reaches the end
# portals could be generated right in front of the player at the moment
# enemies are slower in a 20x20 grid than a 20x30 grid -> only when the player moves they are faster
        # the reason is probably because for that grid the sleep time in the player move method is lower than the sleep time from the fps
# should the LuckyBlock class be an abstract class??? Why would that be better? -> i just saw that there are a lot of @decorators for abstract classes/methods
# TODO KANN MAN WENN MAN IN EINEM PORTAL STEHT AN EINEM GEGENER VERLIEREN? INVULNERABILITY FÜR SPIELER (LUCKY BLOCK) HINZUFÜGEN
# TODO WEITERE LUCKY-BLOCK IDEE: DER BLOCK BLINKT ROT FÜR 2 SEKUNDEN ODER SO, DANN WIRD EIN ZUFÄLLIGER GEGNER IN DEN BLOCK TELEPORTIERT
# TODO WEITERE LUCKY-BLOCK IDEE: DAS KOMPLETTES SPIELFELD WIRD SCHWARZ, BIS AUF EINEN 5x5 BEREICH UM DEN SPIELER HERUM
# TODO MANCHMAL VERWRREND, OB MAN UNSICHTBAR IST ODER TELEPORTIERT WURDE
# TODO GEGNER KÖNNTEN AUCH LUCKY BLOCKS EINSAMMELN KÖNNEN -> WENN DANN IRGENDWANN ALLE LUCKY BLOCKS WEG SIND, WERDEN EINFACH WIEDER NEUE GENERIERT
                    # DAS WÜRDE AUCH ETWAS DAS PROBLEM LÖSEN, DASS DIE GEGENER TEILWEISE NICHT GUT VOM SPAWN WEGKOMMEN -> MAN MÜSSTE VIELLECHT SCHAUEN, DASS GEGENER NICHT DIREKT IM/VORM SPIELER SPAWNEN
# TODO WENN MAN Q DRÜCKT, KANN MAN FÜR 5S ODER SO DIE GEGNER FUTTERN, DIESE RESPAWNEN DANN WIEDER (GGF. NACH 3 SEKUNDEN ODER SO) AM SPAWN
# TODO Schwierigkeitsstufen einbauen -> am Anfang 5 Gegner und mit jedem mal ins Ziel kommen werden es 2 Gegner mehr
# TODO bei zu viel Zeit mal die player.move() Methode umschreiben, dass sie überden mainloop und nicht über sleep läuft
# invulnarability funktioniertn nicht immer komplett einwandfrei -> vielleicht würde sich das auch durch das umschreiben der player.move() Methode beheben


class Game:
    def __init__(self, starting_points, highscore):
        self.game_context = GameContext()
        self.game_context.points = starting_points
        self.game_context.highscore = highscore

        self.win = pygame.display.set_mode((Info.win_width, Info.win_height))
        self.fonts = {
            "FjallaOneRegular" : pygame.font.Font("fonts/FjallaOne-Regular.ttf", 35),
            "Notable" : pygame.font.Font("fonts/Notable-Regular.ttf", 30),
            "SilkscreenRegular" : pygame.font.Font("fonts/Silkscreen-Regular.ttf", 35),
            "SilkscreenBold" : pygame.font.Font("fonts/Silkscreen-Bold.ttf", 35)
        }
        self.score_txt = self.fonts["Notable"]
        self.game_context.invulnerability = Invulnerability(self.game_context, self.score_txt)


        self.labyrinth = Labyrinth(self.game_context)
        self.game_context.portals = Portals(self.game_context)
        self.player = Player(self.game_context)

        self.game_context.add_lucky_blocks()
        self.enemies = EnemyRegulator(self.game_context, self.labyrinth.labyrinth_grid, self.player.player_offset, self.player.player_mask)
        for i in range(self.enemies.enemy_count):
            timer = Timer(i * 0.6, self.enemies.create_enemy)
            timer.start()
        
        self.score_offset = 250
        self.highscore_offset = 30
        self.cell_color = (125, 175, 100)
        self.key_press_duration = 0
        self.in_animation = False
        self.animation_type = None
        Info.moving_speed = Info.resetted_player_speed  # reset the player speed -> if it is changed and a new game starts it would be still faster/slower
        self.orbs = MasterEnergyOrbs(self.game_context, self.player.player_mask)
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
                    return None, self.game_context.highscore

            keys = pygame.key.get_pressed()
            if keys[pygame.K_q] or keys[pygame.K_SPACE]:
                self.game_context.invulnerability.activate()    # activate invulnerability -> only activates after the 30 second cooldown each time
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
                self.game_context.points += 2500
                if all(self.orbs.orb_list[i][j].collected for i in range(Info.rows) for j in range(Info.cols)):
                    self.game_context.points += 2500     # double the points if all orbs are collected
                return self.game_context.points, self.game_context.highscore    # save the points
            elif self.game_context.game_end:       # at the moment the same thing happens when you win or lose
                return 0, self.game_context.highscore        # set the points for the next round to 0

    
    def redraw_window(self):
        self.win.fill(self.cell_color)

        self.labyrinth.draw(self.win)

        for orb_row in self.orbs.orb_list:
            for orb in orb_row:
                orb.draw(self.win)

        self.labyrinth.draw_lucky_blocks(self.win)

        if LuckyBlock.get_visibility() and not self.player.player_in_portal:
            self.player.draw(self.win)
        self.game_context.portals.draw(self.win)
        self.draw_text()
        self.enemies.move_all_enemies(self.win) # move the enemies and draw them at the same time
        self.orbs.check_for_collision() # delete the orbs the player collides with
        self.game_context.invulnerability.draw_cooldown(self.win)
        pygame.display.flip()

    
    def draw_text(self):
        score = self.score_txt.render(f"Score: {self.game_context.points}", 1, (0, 0, 0))
        self.win.blit(score, (self.score_offset, Info.bar_size/2 - score.get_height()/2, score.get_width(), score.get_height()))

        self.game_context.highscore = max(self.game_context.points, self.game_context.highscore)
        highscore = self.score_txt.render(f"Highscore: {self.game_context.highscore}", 1, (0, 0, 0))
        self.win.blit(highscore, (max(Info.win_width // 2.5, score.get_width() + self.score_offset + self.highscore_offset), Info.bar_size/2 - score.get_height()/2, score.get_width(), score.get_height()))


pygame.init()
pygame.display.set_caption("Maze Game")
pygame.mouse.set_visible(False)

try:
    with open("highscore.txt", "r") as file:       # with the "with-block" the file is automatically closed after the block is executed
        highscore = int(file.read())
except FileNotFoundError:
    highscore = 0

close_game = False
set_points_for_next_round = 0
while not close_game:
    game = Game(set_points_for_next_round, highscore)
    set_points_for_next_round, highscore = game.mainloop()

with open("highscore.txt", "w") as file:
    file.write(str(highscore))
