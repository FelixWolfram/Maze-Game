from pygame import image, transform
from data_structs import Info, Support, Direct
from random import randint, choice


class EnemyRegulator:
    def __init__(self, game_context, labyrinth_grid):
        self.game_context = game_context

        self.enemy_count = 15
        self.enemies = []  # list of all enemies which are on the field at the moment
        self.ghost_size = 0.92
        self.labyrinth_grid = labyrinth_grid
        self.ghost_offset = Info.cell_size * (1 - self.ghost_size) / 2
        self.enemy_imgs = [image.load(f"images/ghost_color{i}.webp") for i in range(1, 6)]
        self.enemy_imgs = [transform.smoothscale(ghost, (Info.cell_size * self.ghost_size, Info.cell_size * self.ghost_size)) for ghost in self.enemy_imgs]


    def create_enemy(self):
        enemy_img = choice(self.enemy_imgs)
        self.enemies.append(Enemy(self.game_context, enemy_img, self.ghost_offset, self.labyrinth_grid))

    
    def delete_enemy(self, index):
        self.enemies.remove(index)

    
    def move_all_enemies(self, win):
        for enemy in self.enemies:
            enemy.move(win)


class Enemy:
    def __init__(self, game_context, img, ghost_offset, labyrinth_grid):
        self.labyrinth_cells = labyrinth_grid
        self.game_context = game_context
        self.cell = self.game_context.end_cell # start the enemy at the end cell
        self.x = Support.get_pygame_coords(self.cell, "col")
        self.y = Support.get_pygame_coords(self.cell, "row")
        self.ghost_offset = ghost_offset
        self.speed_ratio = 2  # "2" is half the speed of the player, "3" a third, "1" is the speed as the player
        self.ghost_moving_speed = Info.resetted_player_speed / self.speed_ratio
        self.cooldown = 0
        self.img = img
        self.change_cell = None # the cell should be changed after the enemy has moved, so the collision with the player is better
        self.direction = None
        self.locked_direction = None


    def move(self, win):
        self.cooldown += 1
        if self.direction is not None:
            if self.direction == Direct.RIGHT:
                self.x += self.ghost_moving_speed
            elif self.direction == Direct.LEFT:
                self.x -= self.ghost_moving_speed
            elif self.direction == Direct.UP:
                self.y -= self.ghost_moving_speed
            elif self.direction == Direct.DOWN:
                self.y += self.ghost_moving_speed

        if self.cooldown >= ((Info.cell_size + Info.wall_width) / Info.resetted_player_speed) * self.speed_ratio:  # after the cooldown is reached, the enemy is on a new cell
            if self.change_cell is not None:
                self.cell = self.change_cell 
            
            self.check_for_portal()

            x, y = self.cell
            walls = ("right" , "left", "top", "bottom")
            opposite_direction = {"right": "left", "left": "right", "top": "bottom", "bottom": "top"}

            valid_moves = [walls[i] for i in range(4) if not self.labyrinth_cells[x][y].walls[walls[i]]]
            if len(valid_moves) > 1 and self.locked_direction is not None:
                valid_moves.remove(self.locked_direction)  # if there is more than one valid move, the enemy should not go back where it came from
            move = choice(valid_moves)   # choose a random direction out of the valid moves

            direction_map = {       
                "right": ([x, y + 1], Direct.RIGHT, opposite_direction["right"]),
                "left": ([x, y - 1], Direct.LEFT, opposite_direction["left"]),
                "top": ([x - 1, y], Direct.UP, opposite_direction["top"]),
                "bottom": ([x + 1, y], Direct.DOWN, opposite_direction["bottom"]),
            }
            self.x = Support.get_pygame_coords(self.cell, "col")    # correct the x and y coordinates if for any speed-value would be a deviation
            self.y = Support.get_pygame_coords(self.cell, "row")
            self.change_cell, self.direction, self.locked_direction = direction_map[move]  # then save the new cell as the current cell for the enemy
            self.cooldown = 0
        self.draw(win)


    def check_for_portal(self):
        index, teleport_destination, teleported = self.game_context.portals.check_for_portal(self.cell)
        if teleported:  # if the player is moving into a teleport-cell -> teleport the player to the destination
            self.cell = teleport_destination
            self.x = Support.get_pygame_coords(self.cell, "col")
            self.y = Support.get_pygame_coords(self.cell, "row")
            self.game_context.portals.delete_portal(index)
            self.game_context.portals.add_portal()
            self.locked_direction = None
            self.direction = None


    def draw(self, win):
        win.blit(self.img, (self.x + self.ghost_offset, self.y + self.ghost_offset))