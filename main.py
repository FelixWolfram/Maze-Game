import sys
from labyrinth import Labyrinth
from player import Player
from portals import Portals
import pygame
from lucky_blocks import LuckyBlock, PartlyInvisible, HigherSpeed, LowerSpeed
from data_structs import Direct, Info, GameContext, Support
from enemies import EnemyRegulator
from threading import Timer
from energy_orb import MasterEnergyOrbs
from ability import Invulnerability


# TODO:
# portals could be generated right in front of the player at the moment
# you could get teleported into an emeny

class Game:
    def __init__(self, starting_points, highscore, win_streak, inv_progress):
        self.game_context = GameContext()
        self.game_context.points = starting_points
        self.game_context.highscore = highscore
        self.win_streak = win_streak

        self.win = pygame.display.set_mode((Info.win_width, Info.win_height))
        self.fonts = {
            "FjallaOneRegular" : pygame.font.Font("fonts/FjallaOne-Regular.ttf", 35),
            "Notable" : pygame.font.Font("fonts/Notable-Regular.ttf", 30),
            "SilkscreenRegular" : pygame.font.Font("fonts/Silkscreen-Regular.ttf", 35),
            "SilkscreenBold" : pygame.font.Font("fonts/Silkscreen-Bold.ttf", 35)
        }
        self.score_txt = self.fonts["Notable"]
        self.game_context.invulnerability = Invulnerability(self.game_context, self.score_txt, inv_progress)

        self.labyrinth = Labyrinth(self.game_context)
        self.game_context.portals = Portals(self.game_context)
        self.player = Player(self.game_context)

        self.game_context.add_lucky_blocks()
        self.enemies = EnemyRegulator(self.game_context, self.labyrinth.labyrinth_grid, self.player.player_offset, self.player.player_mask)
        for i in range(self.enemies.enemy_start_count + self.win_streak * 2):
            timer = Timer(i * 0.6, self.enemies.create_enemy)
            timer.start()
        self.enemies.move_all_enemies() # move the enemies and draw them at the same time
        
        self.score_offset = 250
        self.highscore_offset = 30
        self.win_streak_offset = 30
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
                    self.clear_all_timers()
                    return None, self.game_context.highscore, 0, 0

            if not self.player.in_movement:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_q] or keys[pygame.K_SPACE]:
                    self.game_context.invulnerability.activate()    # activate invulnerability -> only activates after the 30 second cooldown each time
                if (keys[pygame.K_UP] or keys[pygame.K_w]) and not self.labyrinth.labyrinth_grid[self.player.game_context.cell[0]][self.player.game_context.cell[1]].walls["top"]:
                    self.player.move(Direct.UP, self.player.game_context.cell[0] - 1, self.player.game_context.cell[1])
                elif (keys[pygame.K_DOWN] or keys[pygame.K_s]) and not self.labyrinth.labyrinth_grid[self.player.game_context.cell[0]][self.player.game_context.cell[1]].walls["bottom"]:
                    self.player.move(Direct.DOWN, self.player.game_context.cell[0] + 1, self.player.game_context.cell[1])
                elif (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not self.labyrinth.labyrinth_grid[self.player.game_context.cell[0]][self.player.game_context.cell[1]].walls["left"]:
                    self.player.move(Direct.LEFT, self.player.game_context.cell[0], self.player.game_context.cell[1] - 1) # last two parameters is the updated player_position
                elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and not self.labyrinth.labyrinth_grid[self.player.game_context.cell[0]][self.player.game_context.cell[1]].walls["right"]:
                    self.player.move(Direct.RIGHT, self.player.game_context.cell[0], self.player.game_context.cell[1] + 1)

            if self.player.in_movement:
                if not self.player.animate_move():  # return false, if the player has reached the destination cell
                    self.player.move_counter = 0
                    self.player.in_movement = False
                    self.player.after_move()    # correct the offset of the player and the hitbox, check for portals/lucky blocks, ...
            pygame.event.clear()    # clear the event queue to avoid multiple key presses

            if self.player.game_context.cell == self.game_context.end_cell:
                self.game_context.points += 2500
                if all(self.orbs.orb_list[i][j].collected for i in range(Info.rows) for j in range(Info.cols)):
                    self.game_context.points += 5000     # double the points if all orbs are collected
                self.clear_all_timers()
                return self.game_context.points, self.game_context.highscore, self.win_streak + 1, self.game_context.invulnerability.percentage    # save the points
            elif self.game_context.game_end:       # at the moment the same thing happens when you win or lose
                self.clear_all_timers()
                return 0, self.game_context.highscore, 0, start_inv_progress        # set the points for the next round to 0
            
            self.redraw_window()

    
    def redraw_window(self):
        self.win.fill(self.cell_color)
        self.labyrinth.draw(self.win)

        for orb_row in self.orbs.orb_list:
            for orb in orb_row:
                orb.draw(self.win)
        self.labyrinth.draw_lucky_blocks(self.win)

        for i in range(len(self.game_context.tp_red)):
            pygame.draw.rect(self.win, (255, 30, 30), (Support.get_pygame_coords(self.game_context.tp_red[i][0], "col"), Support.get_pygame_coords(self.game_context.tp_red[i][0], "row"), Info.cell_size, Info.cell_size))
            pygame.draw.rect(self.win, (255, 30, 30), (Support.get_pygame_coords(self.game_context.tp_red[i][1], "col"), Support.get_pygame_coords(self.game_context.tp_red[i][1], "row"), Info.cell_size, Info.cell_size))
        if LuckyBlock.get_visibility() and not self.player.player_in_portal:
            self.player.draw(self.win)
        
        self.game_context.portals.draw(self.win)
        self.draw_text()

        for enemy in self.enemies.enemy_list:
            enemy.draw(self.win)
        self.orbs.check_for_collision() # delete the orbs the player collides with
        self.game_context.invulnerability.draw_cooldown(self.win)
        pygame.display.flip()

    
    def draw_text(self):
        score = self.score_txt.render(f"Score: {self.game_context.points}", 1, (0, 0, 0))
        self.win.blit(score, (self.score_offset, Info.bar_size/2 - score.get_height()/2, score.get_width(), score.get_height()))

        self.game_context.highscore = max(self.game_context.points, self.game_context.highscore)
        highscore = self.score_txt.render(f"Highscore: {self.game_context.highscore}", 1, (0, 0, 0))
        self.win.blit(highscore, (max(Info.win_width // 2.48, score.get_width() + self.score_offset + self.highscore_offset), Info.bar_size/2 - score.get_height()/2, score.get_width(), score.get_height()))

        win_streak_text = self.score_txt.render(f"Win streak: {self.win_streak}", 1, (0, 0, 0))
        self.win.blit(win_streak_text, (max(Info.win_width // 1.37, score.get_width()+ highscore.get_width() + self.score_offset + self.highscore_offset + self.win_streak_offset), Info.bar_size/2 - score.get_height()/2, score.get_width(), score.get_height()))


    def clear_all_timers(self):
        self.enemies.timer.cancel()
        while self.game_context.tp_red:
            self.player.clear_tp_red()
        for self.player.tp_timer in self.player.tp_timer:
            self.player.tp_timer.cancel()
        for luckyblock in self.game_context.lucky_blocks.keys():
            if type(luckyblock) == PartlyInvisible or type(luckyblock) == HigherSpeed or type(luckyblock) == LowerSpeed:
                luckyblock.reset_all_timers()
                luckyblock.reset_visibility() if type(luckyblock) == PartlyInvisible else luckyblock.reset_speed()


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
win_streak = 0
start_inv_progress = 1
inv_progress = start_inv_progress    # progress of the invulnerability ability should be saved to continue the progress in the next round
while not close_game:
    game = Game(set_points_for_next_round, highscore, win_streak, inv_progress)
    set_points_for_next_round, highscore, win_streak, inv_progress = game.mainloop()

with open("highscore.txt", "w") as file:
    file.write(str(highscore))