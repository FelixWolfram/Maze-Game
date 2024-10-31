from threading import Timer
from pygame import draw, image, Rect, transform
from data_structs import Info


class Invulnerability:
    def __init__(self, game_context, key_text, inv_progress):
        self.game_context = game_context

        self.cooldown = 30
        self.percentage = inv_progress
        self.active = False
        self.in_cooldown = False if self.percentage >= 1 else True
        self.key_text = key_text
        self.invulnerability_duration = 3.0
        self.inv_duration_after_tp = 1.2
        self.active_count = 0
        self.text = key_text.render("Q", 1, (0, 0, 0))
        self.circle_offset = 80
        self.circle_pos = (Info.win_width * 0.04 + self.circle_offset, Info.bar_size // 1.75)
        self.circle_rad = Info.bar_size // 2.7
        self.inv_img = image.load("images/shield.png").convert_alpha()
        self.img_scale = 1.3
        self.inv_img = transform.smoothscale(self.inv_img, (self.circle_rad * self.img_scale, self.circle_rad * self.img_scale))
        self.img_rect = self.inv_img.get_rect()
        self.loading_bar_width = Info.win_width * 0.06 + 6
        self.loading_bar_red = self.loading_bar_orange = self.loading_bar_green = Rect(0, 0, self.loading_bar_width, Info.bar_size // 2.2)
        self.loading_bar_red.center = (self.circle_pos[0] - self.loading_bar_width + 8, self.circle_pos[1])
        self.loading_bar_orange.center = (self.circle_pos[0] - self.loading_bar_width + 8, self.circle_pos[1])
        self.loading_bar_green.center = (self.circle_pos[0] - self.loading_bar_width + 8, self.circle_pos[1])
        
        self.points_for_inv = 3000
        self.start_points = self.game_context.points - self.points_for_inv * self.percentage


    def activate(self):
        if not self.in_cooldown and not self.active:
            timer = Timer(self.invulnerability_duration, self.deactivate)
            timer.start()
            self.active = True
            self.active_count += 1

    
    def activate_after_tp(self):
        timer = Timer(self.inv_duration_after_tp, self.deactivate_after_tp)
        timer.start()
        self.active = True
        self.active_count += 1

    
    def deactivate_after_tp(self):
        self.active_count -= 1
        if self.active_count == 0:
            self.active = False
       

    def deactivate(self):
        self.active_count -= 1
        if self.active_count == 0:
            self.active = False
            self.in_cooldown = True
            self.percentage = 0
            self.start_points = self.game_context.points


    def draw_cooldown(self, win):
        circle_color = (255, 0, 0) if self.in_cooldown else (255, 165, 0) if self.active else (0, 255, 0)
        img_target = Rect(self.circle_pos[0] - self.circle_rad, self.circle_pos[1] - self.circle_rad, self.circle_rad * 2, self.circle_rad * 2)
        self.img_rect.center = img_target.center
        
        # loading the red, orange and green bar
        draw.rect(win, (255, 0, 0), self.loading_bar_red, border_radius=5) 
        if self.active:
            draw.rect(win, (255, 165, 0), self.loading_bar_green, border_radius=5)

        self.percentage = round((self.game_context.points - self.start_points) / self.points_for_inv, 2)    # calculate the percentage of the cooldown
        if not self.active:
            draw.rect(win, (0, 255, 0), (self.loading_bar_green[0], self.loading_bar_green[1], self.loading_bar_green[2] * min(1, self.percentage), self.loading_bar_green[3]), border_radius=5)
        if self.percentage >= 1:
            self.in_cooldown = False

        draw.circle(win, circle_color, self.circle_pos, self.circle_rad)
        win.blit(self.inv_img, self.img_rect)
        win.blit(self.text, (self.circle_pos[0] + self.text.get_width(), self.circle_pos[1] - self.text.get_height() // 2 - 4))