from random import randint, choice
from data_structs import Info, Support
from pygame import draw, image, transform


class Portals:
    def __init__(self, game_context):
        self.game_context = game_context

        self.portal_list = []
        self.portal_count = 5  # 2 for a 20x20 maze, 4 for a 20x30 maze
        self.portal_scale = 1.1
        self.portal_offset = Info.cell_size * (1 - self.portal_scale) / 2
        self.tp_images = [(170, 83, 170), (64, 140, 194), (180, 120, 40), (127, 186, 132), (200, 115, 115), (163, 191, 105), (90, 90, 160)]
        self.portal_imgs = [image.load(f"images/portal{i}.tiff") for i in range(1, 6)]
        self.portal_imgs = [transform.smoothscale(portal_img, (Info.cell_size * self.portal_scale, Info.cell_size * self.portal_scale)) for portal_img in self.portal_imgs]
        self.disabled_portal_imgs = [] 

        self.add_multiple_portals(self.portal_count)


    
    def add_portal(self):
        lucky_block_cells = self.game_context.lucky_blocks.values()
        tp1 = tp2 = 0
        while tp1 == tp2 or (tp1 == self.game_context.end_cell or tp2 == self.game_context.end_cell) or tp1 == tp2 or (tp1 == self.game_context.cell or tp2 == self.game_context.cell) or\
              tp1 in lucky_block_cells or tp2 in lucky_block_cells or\
                not all(tp1 != tp and tp2 != tp for portal in self.portal_list for tp in portal[0:2]):   # make sure the two portals are not the same and not generating on a lucky block
            tp1 = [randint(0, Info.rows - 1), randint(0, Info.cols - 1)]
            tp2 = [randint(0, Info.rows - 1), randint(0, Info.cols - 1)]
        while True:   # get an unused image for the portal
            random_portal = choice(self.portal_imgs)     # random choice -> choice is from the random module
            if random_portal not in self.disabled_portal_imgs:
                break
        self.disabled_portal_imgs.append(random_portal)
        self.portal_list.append((tp1, tp2, random_portal))


    def add_multiple_portals(self, portal_num):
        for _ in range(portal_num):
            self.add_portal()   # also check for adding a new portals during the move animation


    def delete_portal(self, delete_index, do_not_delete_color=False):
        if not do_not_delete_color:
            portal_to_delete = self.portal_list[delete_index][2]
            self.disabled_portal_imgs.remove(portal_to_delete)  # remove the image of the disabled portal out of the used images list
        
        del self.portal_list[delete_index]  # delete the portal on the old cell


    def check_for_portal(self, cell):
        for index, (tp1, tp2, _) in enumerate(self.portal_list):
            if cell  == tp1 or cell == tp2:
                teleport_destination = tp2 if cell == tp1 else tp1
                return index, teleport_destination, True
        return None, None, False
 

    def draw(self, win):
        for tp1, tp2, img in self.portal_list:
            win.blit(img, (Support.get_pygame_coords(tp1, "col") + self.portal_offset, Support.get_pygame_coords(tp1, "row") + self.portal_offset))
            win.blit(img, (Support.get_pygame_coords(tp2, "col") + self.portal_offset, Support.get_pygame_coords(tp2, "row") + self.portal_offset))

            # draw.rect(win, color, (Support.get_pygame_coords(tp1, "col"), Support.get_pygame_coords(tp1, "row"), Info.cell_size, Info.cell_size))
            # draw.rect(win, color, (Support.get_pygame_coords(tp2, "col"), Support.get_pygame_coords(tp2, "row"), Info.cell_size, Info.cell_size))
