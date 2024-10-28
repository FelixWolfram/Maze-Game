from math import floor
from pygame import image, transform
from data_structs import Direct, Info, Support
from lucky_blocks import LuckyBlock, RandomTeleport
from time import sleep


class Player:
    def __init__(self, game_context):
        self.game_context = game_context

        self.player_scale = 0.95 
        self.player_imgs = [image.load(f"images/Pacman{i}.png") for i in range(1, 5)]
        self.player_imgs = [transform.smoothscale(player_img, (Info.cell_size * self.player_scale, Info.cell_size * self.player_scale)) for player_img in self.player_imgs]
        self.shrinked_player_imgs = [transform.smoothscale(player_img, (Info.cell_size * (self.player_scale * 0.5), Info.cell_size * (self.player_scale * 0.5))) for player_img in self.player_imgs]
        self.shrinked_player = False
        self.image_duration = 0.4  # image changes every n/2 seconds -> one cicle takes n seconds
        self.draw_counter = 0
        
        self.player_is_horizontal = True
        self.last_horizontal = Direct.RIGHT
        self.last_vertical = Direct.DOWN

        self.player_color = (80, 68, 220)
        self.sleep_time = round(0.103 / (Info.cell_size + Info.wall_width), 3)
        
        self.valid_moves = ("w", "a", "s", "d")
        self.player_offset = Info.cell_size * (1 - self.player_scale) / 2
        self.shrinked_player_offset = Info.cell_size * (1 - self.player_scale * 0.5) / 2
        self.x = Support.get_pygame_coords(self.game_context.cell, "col") + self.player_offset 
        self.y = Support.get_pygame_coords(self.game_context.cell, "row") + self.player_offset
        self.portals_for_delete_index = []     # when the player teleported to a new cell, the portal on the old cell should be deleted


    def move(self, move, redraw_window, new_x, new_y):
        self.game_context.cell = [new_x, new_y]
        self.modify_player_img(move)

        if self.shrinked_player:   # player wants to move out of the portal, so the player should be normal size again
            self.shrinked_player = False

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

        self.x = Support.get_pygame_coords(self.game_context.cell, "col") + self.player_offset    # correct the player position to the cell position if there is a deviation
        self.y = Support.get_pygame_coords(self.game_context.cell, "row") + self.player_offset    # deviation can be caused by the moving speed and the cell size
    
        if LuckyBlock.get_speed_reset_status():
            Info.moving_speed = Info.resetted_player_speed
            LuckyBlock.set_speed_reset_status(False)
        if self.portals_for_delete_index:    # if the player teleported to a new cell and now left the cell again
            self.game_context.portals.delete_portal(self.portals_for_delete_index.pop())
        
        self.check_for_portal()
        self.check_for_lucky_block()

        if self.portals_for_delete_index:   # if we are standing in a portal, shrink the player a bit, so you don't see the player under the portal
            self.shrinked_player = True
        

    def check_for_portal(self):
        if self.game_context.portals.portal_list:
            index, teleport_destination, teleported = self.game_context.portals.check_for_portal()
            if teleported:  # if the player is moving into a teleport-cell -> teleport the player to the destination
                self.game_context.cell = teleport_destination
                self.x = Support.get_pygame_coords(self.game_context.cell, "col")
                self.y = Support.get_pygame_coords(self.game_context.cell, "row")
                self.portals_for_delete_index.append(index)


    def check_for_lucky_block(self):
        if self.game_context.lucky_blocks:
            if self.game_context.cell in self.game_context.lucky_blocks.values():
                lucky_block_on_player = list(self.game_context.lucky_blocks.keys())[list(self.game_context.lucky_blocks.values()).index(self.game_context.cell)] # get the lucky block which is on the player cell
                if type(lucky_block_on_player) == RandomTeleport:
                    self.game_context.cell, self.x, self.y = lucky_block_on_player.action()
                else:
                    lucky_block_on_player.action()
                del self.game_context.lucky_blocks[lucky_block_on_player]

    
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
            img = self.player_imgs if not self.shrinked_player else self.shrinked_player_imgs
            extra_offset = self.shrinked_player_offset if self.shrinked_player else 0
            if self.player_is_horizontal:
                win.blit(img[0] if self.draw_counter < ((Info.fps * self.image_duration) / 2) else img[1], (self.x + extra_offset, self.y + extra_offset))
            else:   
                win.blit(img[2] if self.draw_counter < ((Info.fps * self.image_duration) / 2) else img[3], (self.x + extra_offset, self.y + extra_offset))
        self.draw_counter = (self.draw_counter + 1) if self.draw_counter < (Info.fps * self.image_duration - 1) else 0