from math import floor
from pygame import image, transform, Rect, mask, key, K_q, K_SPACE
from data_structs import Direct, Info, Support
from lucky_blocks import LuckyBlock, RandomTeleport
from threading import Timer


class Player:
    def __init__(self, game_context):
        self.game_context = game_context

        self.player_scale = 0.95 
        self.player_imgs = [image.load(f"images/Pacman{i}.png").convert_alpha() for i in range(1, 5)]
        self.player_imgs = [transform.smoothscale(player_img, (Info.cell_size * self.player_scale, Info.cell_size * self.player_scale)) for player_img in self.player_imgs]
        self.player_mask = mask.from_surface(self.player_imgs[0])   # get the mask for the first image at first
        self.player_in_portal = False
        self.image_duration = 0.4  # image changes every n/2 seconds -> one cicle takes n seconds
        self.draw_counter = 0
        self.delete_portal_on_next_move = False  # saves the index of the portal which should be deleted once the player moves -> happens after the teleportation of the player

        self.player_is_horizontal = True
        self.last_horizontal = Direct.RIGHT
        self.last_vertical = Direct.DOWN
        self.in_movement = False
        self.move_counter = 0
        self.max_move_counter = floor((Info.cell_size + Info.wall_width) / Info.moving_speed)      # DER TEIL GEHT NOCH BESSER / KÜRZER

        self.save_move = None
        self.tp_timer = []

        self.player_color = (80, 68, 220)
        self.sleep_time = round(0.103 / (Info.cell_size + Info.wall_width), 3)
        
        self.valid_moves = ("w", "a", "s", "d")
        self.player_offset = Info.cell_size * (1 - self.player_scale) / 2

        self.game_context.x = Support.get_pygame_coords(self.game_context.cell, "col") + self.player_offset 
        self.game_context.y = Support.get_pygame_coords(self.game_context.cell, "row") + self.player_offset
        self.game_context.player_hitbox = Rect(self.game_context.x + 2 + self.player_offset, self.game_context.y + self.player_offset + 2,
                                           Info.cell_size - 2 * self.player_offset - 4, Info.cell_size - 2 * self.player_offset - 4)


    def move(self, move, new_x, new_y):
        self.in_movement = True
        self.save_move = move
        self.game_context.cell = [new_x, new_y]

        self.modify_player_img(move)

        if self.delete_portal_on_next_move:
            self.game_context.portals.delete_portal(0)  # delete the portal at index 0 -> we put the portal at index 0 as we marked it, that it should be deleted
            self.game_context.portals.add_portal()  # add a new portal on the new cell
            self.delete_portal_on_next_move = False

        if self.player_in_portal:   # player wants to move out of the portal, so the player should be normal size again
            self.player_in_portal = False


    def animate_move(self):
        self.end_move = {   # all the conditions for the player for the different directions to stop moving
            Direct.LEFT : self.game_context.x - Info.moving_speed <= Support.get_pygame_coords(self.game_context.cell, "col"),
            Direct.RIGHT : self.game_context.x + Info.moving_speed >= Support.get_pygame_coords(self.game_context.cell, "col"),
            Direct.UP : self.game_context.y - Info.moving_speed <= Support.get_pygame_coords(self.game_context.cell, "row"),
            Direct.DOWN : self.game_context.y + Info.moving_speed >= Support.get_pygame_coords(self.game_context.cell, "row")
        }
        if self.end_move[self.save_move]:  # if the player has reached the cell, stop the movement
            return False
        
        keys = key.get_pressed()
        if keys[K_q] or keys[K_SPACE]:
            self.game_context.invulnerability.activate()    # activate invulnerability -> only activates after the 30 second cooldown each time

        if self.game_context.game_end:
            return

        direction_vectors = {
            Direct.LEFT: (-Info.moving_speed, 0),
            Direct.RIGHT: (Info.moving_speed, 0), 
            Direct.UP: (0, -Info.moving_speed),
            Direct.DOWN: (0, Info.moving_speed)
        }
        directx, directy = direction_vectors[self.save_move]

        self.game_context.x += directx  # move the player and the hitbox
        self.game_context.y += directy
        self.game_context.player_hitbox[0] += directx
        self.game_context.player_hitbox[1] += directy
        return True   # return true, if the player has not reached the destination cell yet


    def correct_player_position(self):
        self.game_context.x = Support.get_pygame_coords(self.game_context.cell, "col") + self.player_offset    # correct the player position to the cell position if there is a deviation
        self.game_context.y = Support.get_pygame_coords(self.game_context.cell, "row") + self.player_offset    # deviation can be caused by the moving speed and the cell size
        self.game_context.player_hitbox = Rect(self.game_context.x + 2 + self.player_offset, self.game_context.y + self.player_offset + 2,
                                               Info.cell_size - 2 * self.player_offset - 4, Info.cell_size - 2 * self.player_offset - 4)


    def after_move(self):
        self.correct_player_position()
        if LuckyBlock.get_speed_reset_status():     # reset speed if the duration of the speed change is over
            Info.moving_speed = Info.resetted_player_speed
            LuckyBlock.set_speed_reset_status(False)
        self.check_for_portal()
        self.check_for_lucky_block()


    def check_for_portal(self):
        index, teleport_destination, teleported = self.game_context.portals.check_for_portal(self.game_context.cell)
        if teleported:  # if the player is moving into a teleport-cell -> teleport the player to the destination
            self.game_context.cell = teleport_destination
            self.game_context.x = Support.get_pygame_coords(self.game_context.cell, "col")
            self.game_context.y = Support.get_pygame_coords(self.game_context.cell, "row")
            save_portal = self.game_context.portals.portal_list[index]
            self.game_context.portals.delete_portal(index, True)
            self.game_context.portals.portal_list.insert(0, save_portal)  # put the portal at the beginning of the list, so it gets deleted on the next move
            self.delete_portal_on_next_move = True
            self.player_in_portal = True    # if we are standing in a portal, shrink the player a bit, so you don't see the player under the portal
            self.correct_player_position()  # especially important to change the hitbox here so ghost hits are detected


    def check_for_lucky_block(self):
        if self.game_context.lucky_blocks:
            if self.game_context.cell in self.game_context.lucky_blocks.values():
                self.game_context.points += 200
                lucky_block_on_player = list(self.game_context.lucky_blocks.keys())[list(self.game_context.lucky_blocks.values()).index(self.game_context.cell)] # get the lucky block which is on the player cell
                if type(lucky_block_on_player) == RandomTeleport:
                    new_cell, self.game_context.x, self.game_context.y = lucky_block_on_player.action()
                    self.game_context.tp_red.append([self.game_context.cell, new_cell])  # save the cells to mark the tp cells red for a short time
                    self.game_context.cell = new_cell
                    timer = Timer(1, self.clear_tp_red)        # delete the saved cells
                    timer.start()
                    self.tp_timer.append(timer)
                    self.game_context.invulnerability.activate_after_tp()
                else:
                    lucky_block_on_player.action()
                del self.game_context.lucky_blocks[lucky_block_on_player]
        else:   # if there are no lucky blocks left, generate new ones
            self.game_context.add_lucky_blocks()

    
    def clear_tp_red(self):
        self.game_context.tp_red.pop(0)
        self.tp_timer.pop(0).cancel()

    
    def clear_timers(self):
        for timer in self.tp_timer:
            timer.cancel()
        self.tp_timer.clear()


    def modify_player_img(self, move):
        if (move == Direct.LEFT or move == Direct.RIGHT):
            if self.last_horizontal != move:  # image needs to flipped in that case
                self.player_imgs[0] = transform.flip(self.player_imgs[0], True, False) # flip the image horizontally
                self.player_imgs[1] = transform.flip(self.player_imgs[1], True, False)
            self.player_is_horizontal = True
            self.last_horizontal = move
        elif (move == Direct.UP or move == Direct.DOWN) :
            if move != self.last_vertical:
                self.player_imgs[2] = transform.flip(self.player_imgs[2], False, True) # flip the image vertically
                self.player_imgs[3] = transform.flip(self.player_imgs[3], False, True)
            self.player_is_horizontal = False
            self.last_vertical = move


    def draw(self, win):
        if LuckyBlock.get_visibility():
            if self.player_is_horizontal:
                win.blit(self.player_imgs[0] if self.draw_counter < ((Info.fps * self.image_duration) / 2) else self.player_imgs[1], (self.game_context.x, self.game_context.y))
            else:   
                win.blit(self.player_imgs[2] if self.draw_counter < ((Info.fps * self.image_duration) / 2) else self.player_imgs[3], (self.game_context.x, self.game_context.y))
        self.draw_counter = (self.draw_counter + 1) if self.draw_counter < (Info.fps * self.image_duration - 1) else 0
        # draw.rect(win, (255, 0, 0), (self.game_context.player_hitbox), 2) # -> hitbox of the player