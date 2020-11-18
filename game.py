import pygame
import numpy as np
import sys
from utils import *

class Minesweeper(object):

    def __init__(self,board_size,win_size=(640,720),FPS=30,mines_number=40):
        pygame.init()

        self.W, self.H = win_size
        self.WIN = pygame.display.set_mode((self.W,self.H))
        self.CLOCK = pygame.time.Clock()
        self.FPS = FPS
        self.run = True
        self.FPS_COUNTER = 0
        self.game_started = False
        self.first_launch = True
        self.current_cell = None
        self.mines_number = mines_number
        self.flag_used = 0
        self.cell_size = 25
        self.cell_font = pygame.font.SysFont('comicsans',self.cell_size)
        self.menu_font = pygame.font.SysFont('comicsans',50)
        self.btn_font = pygame.font.SysFont('comicsans',40)
        self.main_color = (2, 123, 206)
        self.text_color = (255,255,255)
        self.game_end_color = (2, 123, 206)
        self.background_color = (4, 150, 255)
        self.cell_color = (0, 72, 124)

        self.board_size = board_size
        self.board = np.zeros((board_size[0],board_size[1],2))
        self.menu_height = 150
        self.inner_padding = 2
        self.x_align = int((self.W - self.board_size[1]*(self.cell_size+2*self.inner_padding)) / 2)
        self.y_align = int((self.H - self.board_size[0]*(self.cell_size+2*self.inner_padding) + self.menu_height) / 2) 

        self.flag_image = pygame.image.load('flag.png')
        self.flag_image_resized = pygame.transform.scale(self.flag_image,(self.cell_size,self.cell_size))

    def reveal_empty_cells(self,cell):
        cells_ard = get_cells_around(cell,self.board_size)
        for cell in cells_ard:
            if self.board[cell[0],cell[1],0] == 0 and self.board[cell[0],cell[1],1] == 0:
                self.board[cell[0],cell[1],1] = 1
                self.reveal_empty_cells(cell)
            self.board[cell[0],cell[1],1] = 1

        self.check_for_win()

    def check_for_win(self):
        revealed = 0
        for i in range(self.board_size[0]):
            for j in range(self.board_size[1]):
                if self.board[i,j,1] == 1:
                    revealed += 1
        
        if revealed >= self.board_size[0]*self.board_size[1] - self.mines_number:
            end_game(self.WIN,self.btn_font,self.menu_font,self.game_end_color,self.text_color,self.FPS_COUNTER,"Victory",(self.W,self.H))

    def reset_board(self):
        self.game_started = False
        self.FPS_COUNTER = 0
        self.flag_used = 0
        self.board = np.zeros((self.board_size[0],self.board_size[1],2))

    def start_game(self,current_cell):
        self.board[current_cell[0],current_cell[1]] = 1
        mines = []
        for i in range(self.mines_number):
            mine_x = np.random.randint(0,self.board_size[0])
            mine_y = np.random.randint(0,self.board_size[1])
            while (mine_x,mine_y) == current_cell or (mine_x,mine_y) in get_cells_around(current_cell,self.board_size) or (mine_x,mine_y) in mines:
                mine_x = np.random.randint(0,self.board_size[0])
                mine_y = np.random.randint(0,self.board_size[1])
            mines.append((mine_x,mine_y))
            self.board[mine_x,mine_y,0] = -1

        for i in range(self.board_size[0]):
            for j in range(self.board_size[1]):
                mines_around = 0
                if self.board[i,j,0] != -1:
                    for cell in get_cells_around((i,j),self.board_size):
                        if self.board[cell[0],cell[1],0] == -1:
                            mines_around += 1
                    self.board[i,j,0] = mines_around

        self.reveal_empty_cells(self.current_cell)

        for cell in get_cells_around(self.current_cell,self.board_size):
            self.board[cell[0],cell[1],1] = 1

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit2()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.current_cell is not None:
                    if not self.game_started and event.button == 1:
                        self.start_game(self.current_cell)
                        self.game_started = True
                    elif self.board[self.current_cell[0],self.current_cell[1],1] != 1:
                        if event.button == 1 and self.board[self.current_cell[0],self.current_cell[1],1] != 2:
                            self.board[self.current_cell[0],self.current_cell[1],1] = 1
                            if self.board[self.current_cell[0],self.current_cell[1],0] == 0:
                                self.reveal_empty_cells(self.current_cell)
                            elif self.board[self.current_cell[0],self.current_cell[1],0] == -1:
                                end_game(self.WIN,self.btn_font,self.menu_font,self.game_end_color,self.text_color,self.FPS_COUNTER,"Game over",(self.W,self.H))
                            self.check_for_win()
                        elif event.button == 1:
                            self.board[self.current_cell[0],self.current_cell[1],1] = 0
                            self.flag_used -= 1
                        elif event.button == 3 and self.game_started:
                            if self.board[self.current_cell[0],self.current_cell[1],1] == 2:
                                self.board[self.current_cell[0],self.current_cell[1],1] = 0
                                self.flag_used -= 1
                            elif self.flag_used < self.mines_number:
                                self.board[self.current_cell[0],self.current_cell[1],1] = 2
                                self.flag_used += 1

    def step(self):
        self.current_cell = None
        self.WIN.fill(self.background_color)
        pygame.draw.rect(self.WIN, self.cell_color, (0,self.menu_height,self.W,3))
        #game
        mouse_pos = pygame.mouse.get_pos()
        for i in range(self.board.shape[0]):
            for j in range(self.board.shape[1]):
                x = j*(self.cell_size + 2*self.inner_padding) + self.x_align
                y = i*(self.cell_size + 2*self.inner_padding) + self.y_align
                color = (255,255,255)
                if mouse_pos[0] in list(range(x,x+self.cell_size)) and mouse_pos[1] in list(range(y,y+self.cell_size)):
                    color=(190,190,190)
                    self.current_cell = (i,j)
                if self.board[i,j,1] == 1:
                    color = self.cell_color

                pygame.draw.rect(self.WIN, color, (x,y,self.cell_size,self.cell_size))

                if self.board[i,j,1] == 2:
                    self.WIN.blit(self.flag_image_resized,(x,y))

                if self.board[i,j,1] == 1 and self.board[i,j,0] != 0:
                    text = self.cell_font.render(str(int(self.board[i,j,0])),1,self.text_color)
                    x = x+(self.cell_size-text.get_width())//2
                    y = y+(self.cell_size-text.get_height())//2
                    self.WIN.blit(text, (x,y))
        #flags
        text = self.menu_font.render(str(self.mines_number-self.flag_used),1,self.text_color)
        self.WIN.blit(text,(self.W//4,self.menu_height//2-text.get_height()//2))
        self.WIN.blit(self.flag_image,(self.W//4-self.flag_image.get_width(),self.menu_height//2-text.get_height()//2))
        #clock
        text = self.menu_font.render(get_time(self.FPS_COUNTER),1,self.text_color)
        self.WIN.blit(text,(3*self.W//4-text.get_width()//2, self.menu_height//2-text.get_height()//2))
        pygame.display.update()

    def play_ai(self):
        self.game_started = False
        self.board = np.zeros((self.board_size[0],self.board_size[1],2))
        self.flag_used = 0
        self.FPS_COUNTER = 0

        while self.run:
            self.CLOCK.tick(self.FPS)
            self.events()
            self.step()
            self.FPS_COUNTER = self.FPS_COUNTER+1 if self.game_started else 0

    def play(self):
        self.game_started = False
        self.board = np.zeros((self.board_size[0],self.board_size[1],2))
        self.flag_used = 0
        self.FPS_COUNTER = 0

        if self.first_launch:
            self.step()
            self.first_launch = False
            end_game(self.WIN,self.btn_font,self.menu_font,self.game_end_color,self.text_color,self.FPS_COUNTER,"Welcome",(self.W,self.H))

        while self.run:
            self.CLOCK.tick(self.FPS)
            self.events()
            self.step()
            self.FPS_COUNTER = self.FPS_COUNTER+1 if self.game_started else 0

def end_game(WIN, btn_font,menu_font,game_end_color,text_color,FPS_COUNTER,title,win_size):
        run = True
        mouse_clicked = False
        W,H = win_size

        def events2():
            nonlocal mouse_clicked
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit2()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_clicked=True
        
        def refresh_window():
            pygame.draw.rect(WIN, game_end_color, (W//2-200,H//2-300,400,600))

            text = menu_font.render(title,1,text_color)
            WIN.blit(text,(W//2-text.get_width()//2,H//2-300+50))

            if FPS_COUNTER != 0:
                text = menu_font.render("Time: " + get_time(FPS_COUNTER),1,text_color)
                WIN.blit(text, (W//2-text.get_width()//2,H//2-300+150))

            create_button(WIN, "Play",(0,255,255),(0,190,190),(20,20,20),(W//2-150,H//2-300+230,300,80),mouse_clicked,btn_font,game.play)
            create_button(WIN,"Watch AI play",(0,255,255),(0,190,190),(20,20,20),(W//2-150,H//2-300+350,300,80),mouse_clicked,btn_font,game.play_ai)
            create_button(WIN, "Exit",(255,0,0),(190,0,0),text_color,(W//2-150,H//2-300+470,300,80),mouse_clicked,btn_font,exit2)

            pygame.display.update()

        while run:
            mouse_clicked = False
            events2()
            refresh_window()

game = Minesweeper((15,19))
game.play()