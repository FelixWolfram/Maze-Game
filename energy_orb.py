from pygame import image, transform, Rect, mask
from data_structs import Info, Support


class MasterEnergyOrbs:
    def __init__(self, game_context, player_mask):
        self.game_context = game_context
        self.start_cell = self.game_context.cell
        self.player_mask = player_mask

        self.orb_count = Info.rows * Info.cols - 2  # -2 because the start and end cell should not have an energy orb
        self.orb_list = [[EnergyOrbs(row, col, False) if [row, col] != self.game_context.cell and [row, col] != self.game_context.end_cell else EnergyOrbs(row, col, True) for col in range(Info.cols)] for row in range(Info.rows)]


    def check_for_collision(self):
        for row in range(Info.rows):
            for col in range(Info.cols):
                if [row, col] != self.start_cell and [row, col] != self.game_context.end_cell and self.orb_list[row][col].collected == False and\
                    self.orb_list[row][col].orb_hitbox.overlap(self.player_mask, (self.game_context.x - self.orb_list[row][col].rect.x, self.game_context.y - self.orb_list[row][col].rect.y)):
                    self.orb_list[row][col].collected = True                                                  # subtract the energy orb_imgage pos (rect.x, rect.y) from the player position
                    self.game_context.points += 10


class EnergyOrbs:
    def __init__(self, row, col, collected):
        self.orb_size_factor = 0.5
        self.orb_size = Info.cell_size * self.orb_size_factor
        self.orb_img = image.load("images/energy_orb.png")
        self.orb_img = transform.smoothscale(self.orb_img, (self.orb_size, self.orb_size))
        self.target = Rect(Support.get_pygame_coords([row, col], "col"), Support.get_pygame_coords([row, col], "row"), Info.cell_size, Info.cell_size)
        self.rect = self.orb_img.get_rect()
        self.rect.center = self.target.center
        self.orb_hitbox = mask.from_surface(self.orb_img)
        self.collected = collected


    def draw(self, win):
        if not self.collected:
            win.blit(self.orb_img, self.rect)