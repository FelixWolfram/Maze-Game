from os import system
from pygame import draw
from data_structs import Info, Cell, Support
from random import randint
from lucky_blocks import LuckyBlockFactory, LuckyBlock


class Labyrinth:
    def __init__(self, lucky_blocks):
        self.labyrinth = [[Cell(j, i) for i in range(Info.cols)] for j in range(Info.rows)]
        self.cell_color = (125, 175, 100)
        self.wall_color = (30, 30, 30)
        self.end_color = (100, 40, 55)
            
        self.start_cell = [randint(0, Info.rows - 1), randint(0, Info.cols - 1)]
        self.deepest_recursion = 0
        self.deepest_recursion_cell = None
        self.lucky_block_count = 10
        self.lucky_blocks = lucky_blocks

        self.generate_maze(self.start_cell[0], self.start_cell[1], 0)
        self.end_cell = self.deepest_recursion_cell


    def draw(self, win):
        for row in range(Info.rows):
            for col in range(Info.cols):
                # drawing the walls and coloring the end cell
                # IMPORTENT TO REMEBER: for pygame coordinates the x-axis (our y-coordinate) goes first, then the y-axis (our x-coordinate) -> COORDINATES ARE SWAPPED
                if row == self.deepest_recursion_cell[0] and col == self.deepest_recursion_cell[1]:
                    draw.rect(win, self.end_color, (col * Info.cell_size + (col + 1) * Info.wall_width, row * Info.cell_size + (row + 1) * Info.wall_width, 
                                                     Info.cell_size, Info.cell_size))
                if self.labyrinth[row][col].walls["top"]:
                    draw.rect(win, self.wall_color, (col * Info.cell_size + col * Info.wall_width, row * Info.cell_size + row * Info.wall_width, 
                                                     Info.cell_size + 2 * Info.wall_width, Info.wall_width))
                if self.labyrinth[row][col].walls["bottom"]:
                    draw.rect(win, self.wall_color, (col * Info.cell_size + col * Info.wall_width, row * Info.cell_size + (row + 1) * Info.wall_width + Info.cell_size, 
                                                     Info.cell_size + 2 * Info.wall_width, Info.wall_width))
                if self.labyrinth[row][col].walls["left"]:
                    draw.rect(win, self.wall_color, (col * Info.cell_size + col * Info.wall_width, row * Info.cell_size + row * Info.wall_width, 
                                                     Info.wall_width, Info.cell_size + 2 * Info.wall_width))
                if self.labyrinth[row][col].walls["right"]:
                    draw.rect(win, self.wall_color, (col * Info.cell_size + (col + 1) * Info.wall_width + Info.cell_size, row * Info.cell_size + row * Info.wall_width, 
                                                     Info.wall_width, Info.cell_size + 2 * Info.wall_width))
                if [row, col] in self.lucky_blocks.values():
                    draw.rect(win, LuckyBlock.background_color, (Support.get_pygame_coords([row, col], "col"), Support.get_pygame_coords([row, col], "row"), Info.cell_size, Info.cell_size))
                    

    def generate_maze(self, x , y, recursion):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # right, left, bottom, top

        while True:
            valid_directs = []  # get all the valid directions we can go to
            for direct_x, direct_y in directions:
                nx, ny = x + direct_x, y + direct_y
                if (0 <= nx < Info.rows and 0 <= ny < Info.cols) and not self.labyrinth[nx][ny].visited: # if we are checking a valid cell which has not been visited yet
                    valid_directs.append((nx, ny))

            if valid_directs:   
                self.labyrinth[x][y].visited = True
                go_direct_x, go_direct_y = valid_directs[randint(0, len(valid_directs) - 1)]   # pick a random valid direction
                
                self.remove_wall(x, y, go_direct_x, go_direct_y)        # remove the wall between the current cell and the next cell
                self.generate_maze(go_direct_x, go_direct_y, recursion + 1)    # take the next cell as the current cell and do the same until there are no valid directions left
            else:   # if there are no valid directions left
                self.labyrinth[x][y].visited = True
                if recursion > self.deepest_recursion:  
                    self.deepest_recursion = recursion
                    self.deepest_recursion_cell = [x, y]    # save the cell with the deepest recursion to take it as the end_cell at the end
                break   # go back to the previous cell to check for valid directions there
        

    def remove_wall(self, x, y, go_direct_x, go_direct_y):
        if go_direct_x > x:     # if the next cell is below the current cell
            self.labyrinth[x][y].walls["bottom"] = False
            self.labyrinth[go_direct_x][go_direct_y].walls["top"] = False
        elif go_direct_x < x:   # if the next cell is above the current cell
            self.labyrinth[x][y].walls["top"] = False
            self.labyrinth[go_direct_x][go_direct_y].walls["bottom"] = False
        elif go_direct_y > y:   # if the next cell is to the right of the current cell
            self.labyrinth[x][y].walls["right"] = False
            self.labyrinth[go_direct_x][go_direct_y].walls["left"] = False
        elif go_direct_y < y:   # if the next cell is to the left of the current cell
            self.labyrinth[x][y].walls["left"] = False
            self.labyrinth[go_direct_x][go_direct_y].walls["right"] = False


    def add_lucky_blocks(self, portals):
        for _ in range(self.lucky_block_count):
            while True:
                row, col = randint(0, Info.rows - 1), randint(0, Info.cols - 1) # generate random values for the lucky blocks
                if [row, col] != self.start_cell and [row, col] != self.end_cell and [row, col] not in self.lucky_blocks.values() and all([row, col] != tp for portal in portals for tp in portal[0:2]):
                    self.lucky_blocks[LuckyBlockFactory.get_lucky_block([row, col], self.remove_wall, self.end_cell, portals, self.lucky_blocks.values())] = [row, col]  # add the lucky block with the adjacent cell to the dictionary
                    break

    
    def add_portals(self, add_portal, portal_count):
        for _ in range(portal_count):
            add_portal(self.lucky_blocks.values(), self.start_cell)   # also check for adding a new portals during the move animation



if __name__ == "__main__":
    import pygame

    pygame.init()
    pygame.display.set_caption("Maze Game")
    win = pygame.display.set_mode((Info.win_width, Info.win_height))

    labyrinth = Labyrinth()
    print(labyrinth.deepest_recursion, labyrinth.deepest_recursion_cell)
    print(labyrinth.start_cell)
    run = True
    while run:
        pygame.time.Clock().tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        labyrinth.draw(win)
        pygame.display.update()