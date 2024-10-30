from pygame import image, transform, Rect, mask
from data_structs import Info, Support, Direct
from random import choice


class EnemyRegulator:
    def __init__(self, game_context, labyrinth_grid, player_offset, player_mask):
        self.game_context = game_context

        self.player_offset = player_offset
        self.enemy_count = 6
        self.enemy_list = []  # list of all enemies which are on the field at the moment
        self.ghost_size_factor = 0.92
        self.ghost_size = Info.cell_size * self.ghost_size_factor
        self.labyrinth_grid = labyrinth_grid
        self.ghost_offset = Info.cell_size * (1 - self.ghost_size_factor) / 2
        self.enemy_imgs = [image.load(f"images/ghost_color{i}.webp").convert_alpha() for i in range(1, 6)]
        self.enemy_imgs = [transform.smoothscale(ghost, (self.ghost_size, self.ghost_size)) for ghost in self.enemy_imgs]
        self.enemy_mask = mask.from_surface(self.enemy_imgs[0])
        self.player_mask = player_mask


    def create_enemy(self):
        enemy_img = choice(self.enemy_imgs)
        enemy = Enemy(self.game_context, enemy_img, self.ghost_offset, self.labyrinth_grid, self.ghost_size, self.player_offset, self.enemy_mask, self.player_mask)
        self.enemy_list.append(enemy)


    def delete_enemy(self, index):
        self.enemy_list.remove(index)

    
    def move_all_enemies(self, win):
        for enemy in self.enemy_list:
            enemy.move(win)


class Enemy:
    def __init__(self, game_context, img, ghost_offset, labyrinth_grid, ghost_size, player_offset, enemy_mask, player_mask):
        self.labyrinth_cells = labyrinth_grid
        self.game_context = game_context

        self.player_offset = player_offset
        self.cell = self.game_context.end_cell # start the enemy at the end cell
        self.x = Support.get_pygame_coords(self.cell, "col")
        self.y = Support.get_pygame_coords(self.cell, "row")
        self.ghost_offset = ghost_offset
        self.speed_ratio = 2  # "2" is half the speed of the player, "3" a third, "1" is the speed as the player
        self.ghost_moving_speed = Info.resetted_player_speed / self.speed_ratio
        self.cooldown = ((Info.cell_size + Info.wall_width) / Info.resetted_player_speed) * self.speed_ratio
        self.img = img
        self.locked_direction = None
        self.ghost_size = ghost_size
        self.hitbox = Rect(self.x + 5, self.y + 5, self.ghost_size - 8, self.ghost_size - 8)
        self.change_cell, self.direction, self.locked_direction = self.get_new_direction(self.cell[0], self.cell[1], ("right", "left", "top", "bottom"))
                # change_cell => the cell should be changed after the enemy has moved, so the collision with the player is better
        self.enemy_mask = enemy_mask
        self.player_mask = player_mask


    def move(self, win):
        self.cooldown -= 1
        if self.direction is not None:
            if self.direction == Direct.RIGHT:
                self.x += self.ghost_moving_speed
            elif self.direction == Direct.LEFT:
                self.x -= self.ghost_moving_speed
            elif self.direction == Direct.UP:
                self.y -= self.ghost_moving_speed
            elif self.direction == Direct.DOWN:
                self.y += self.ghost_moving_speed

        if self.cooldown <= 0:  # after the cooldown is reached, the enemy is on a new cell
            self.do_next_move()

        self.hitbox = Rect(self.x + 5, self.y + 5, self.ghost_size - 8, self.ghost_size - 8)
        if not self.game_context.invulnerability.active:
            self.check_for_collision()
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


    def do_next_move(self):
        if self.change_cell is not None:
            self.cell = self.change_cell 
            self.check_for_portal()

            cell_x, cell_y = self.cell
            walls = ("right" , "left", "top", "bottom")
            
            self.x = Support.get_pygame_coords(self.cell, "col")    # correct the x and y coordinates if for any speed-value would be a deviation
            self.y = Support.get_pygame_coords(self.cell, "row")

            self.change_cell, self.direction, self.locked_direction = self.get_new_direction(cell_x, cell_y, walls)  # then save the new cell as the current cell for the enemy
            self.cooldown = ((Info.cell_size + Info.wall_width) / Info.resetted_player_speed) * self.speed_ratio  # reset the cooldown


    def check_for_collision(self):  # only works if the enemy is smaller than the player -> it checks whether one of the four corner of the enemy is in the hitbox of the player
        if self.hitbox.colliderect(self.game_context.player_hitbox):    # first check the collision roughly, if the hitboxes are colliding, check if they are colliding in detail 
            offset = (self.game_context.x - self.x, self.game_context.y - self.y)   # better performance if we do a rough check first
            if self.player_mask.overlap(self.enemy_mask, offset):
                self.game_context.game_end = True


    def get_new_direction(self, cell_x, cell_y, walls):
        opposite_direction = {"right": "left", "left": "right", "top": "bottom", "bottom": "top"}

        valid_moves = [walls[i] for i in range(4) if not self.labyrinth_cells[cell_x][cell_y].walls[walls[i]]]
        if len(valid_moves) > 1 and self.locked_direction is not None:
            valid_moves.remove(self.locked_direction)  # if there is more than one valid move, the enemy should not go back where it came from
        move = choice(valid_moves)   # choose a random direction out of the valid moves

        direction_map = {       
            "right": ([cell_x, cell_y + 1], Direct.RIGHT, opposite_direction["right"]),
            "left": ([cell_x, cell_y - 1], Direct.LEFT, opposite_direction["left"]),
            "top": ([cell_x - 1, cell_y], Direct.UP, opposite_direction["top"]),
            "bottom": ([cell_x + 1, cell_y], Direct.DOWN, opposite_direction["bottom"]),
        }
        return direction_map[move]


    def draw(self, win):
        win.blit(self.img, (self.x + self.ghost_offset, self.y + self.ghost_offset))
        # draw.rect(win, (255, 0, 0), (self.hitbox[0],self.hitbox[1], self.hitbox[2], self.hitbox[3]), 1) # -> hitbox of the enemy