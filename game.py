import pygame
import numpy as np
import pyautogui
import threading
from pygame._sdl2.video import Window
import sys
import os
from utils import *
import time
import math
from bot import MinesweeperBot

class Minesweeper(object):

    def __init__(self,board_size,win_size=(640,720),FPS=30,mines_number=40):
        pygame.init()

        #Board variable is an array (size - board_size[0] x board_size[1] x 2)
        #First axis:
        #value -1 - Bomb
        #value >= 0 - numer of mines around

        #Second axis:
        #value 0 - unrevealed field
        #value 1 - revealed field
        #value 2 - flag

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
        self.main_window = Window.from_display_module()
        self.mouse_clicked = False
        self.ai = MinesweeperBot()

        self.board_size = board_size
        self.board = np.zeros((board_size[0],board_size[1],2))
        self.probs = np.full(board_size,None)
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

    def mouse_on_cell(self,cell,flag=False):
        win_pos = self.main_window.position
        cell_x = win_pos[0] + self.x_align + cell[0]*(self.cell_size+2*self.inner_padding) + (self.cell_size+2*self.inner_padding)//2
        cell_y = win_pos[1] + self.y_align + cell[1]*(self.cell_size+2*self.inner_padding) + (self.cell_size+2*self.inner_padding)//2
        pyautogui.moveTo(cell_x,cell_y,0,pyautogui.easeInOutQuad)
        button = 'right' if flag else 'left'
        pyautogui.click(button=button)

    def check_for_win(self):
        revealed = 0
        for i in range(self.board_size[0]):
            for j in range(self.board_size[1]):
                if self.board[i,j,1] == 1:
                    revealed += 1
        
        if revealed >= self.board_size[0]*self.board_size[1] - self.mines_number:
            end_game(self.WIN,self.btn_font,self.menu_font,self.game_end_color,self.text_color,self.FPS_COUNTER,"Victory",(self.W,self.H))

    def pause(self):
        end_game(self.WIN,self.btn_font,self.menu_font,self.game_end_color,self.text_color,self.FPS_COUNTER,"Paused",(self.W,self.H))

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
        self.mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit2()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_clicked = True
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

    def keys(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.pause()

    def find_best_cell(self):
        #Find cells with 100% probability of being a bomb or not being a bomb
        for i in range(self.board_size[0]):
                for j in range(self.board_size[1]):
                    if self.board[i,j,1] == 1 and self.board[i,j,0] > 0:
                        bombs_ard = self.board[i,j,0]
                        cells_ard = []

                        for cell in get_cells_around((i,j),self.board_size):
                            if self.board[cell[0],cell[1],1] == 0:
                                cells_ard.append(cell)
                            elif self.board[cell[0],cell[1],1] == 2:
                                bombs_ard -= 1
                        
                        for cell in cells_ard:
                            prob = bombs_ard / len(cells_ard)

                            if prob == 1:
                                return cell[1],cell[0],True
                            elif prob == 0:
                                return cell[1],cell[0],False  

        #If upper algorith fails group border cells for the tank solver
        border_groups = []
        border_cells = []

        for i in range(self.board_size[0]):
            for j in range(self.board_size[1]):
                if self.board[i,j,1] == 0:
                    cells_ard = [cell for cell in get_cells_around((i,j),self.board_size) if self.board[cell[0],cell[1],1] == 1]
                    if len(cells_ard) >= 1:
                        border_cells.append((i,j))

        for border_cell in border_cells:
            revealed_ard = [cell for cell in get_cells_around(border_cell,self.board_size) if self.board[cell[0],cell[1],1] == 1]
            unrevealed_ard = [cell for cell2 in revealed_ard for cell in get_cells_around(cell2,self.board_size) if self.board[cell[0],cell[1],1] == 0]
            valid_gropus = []
            for k,border_group_cells in enumerate(border_groups):
                if common_member(border_group_cells,unrevealed_ard):
                    valid_gropus.append(k)
            
            if len(valid_gropus) == 1:
                border_groups[valid_gropus[0]].append(border_cell)
            elif len(valid_gropus) == 0:
                border_groups.append([border_cell])
            else:
                merged_group = [cell for i,group in enumerate(border_groups) for cell in group if i in valid_gropus]
                merged_group.append(border_cell)
                border_groups = [elem for i,elem in enumerate(border_groups) if i not in valid_gropus]
                border_groups.append(merged_group)

        # cut_border_groups = []
        # for grp in border_groups:
        #     if len(grp) > 17:
        #         chunks = math.ceil(len(grp) / 17)
        #         new_grp_len = round(len(grp) / chunks)
        #         for i in range(chunks):
        #             if i+1 == chunks:
        #                 cut_border_groups.append(grp[i*new_grp_len:])
        #             else:
        #                 cut_border_groups.append(grp[i*new_grp_len:(i+1)*new_grp_len])
        #     else:
        #         cut_border_groups.append(grp)

        # border_groups = cut_border_groups[:]
        
        border_groups.sort(key=len)
        grp_probs = []

        for grp in border_groups:
            for i,cell in enumerate(grp):
                self.probs[cell[0],cell[1]] = i

        for group in border_groups:

            #genenrate all posible arangements of bombs
            start = time.time()
            all_arangements = generate_bomb_arangements(group)
            end = time.time()
            g_time = end-start

            revealed = [cell for cell2 in group for cell in get_cells_around(cell2,self.board_size) if self.board[cell[0],cell[1],1] == 1]
            #get number of bombs around for revealed cell having in mind flags
            bombs_ard = []
            for cell in revealed:
                bombs = self.board[cell[0],cell[1],0]
                for cell2 in get_cells_around(cell,self.board_size):
                    if self.board[cell2[0],cell2[1],1] == 2:
                            bombs -= 1 
                bombs_ard.append(bombs)
            #make an array (len the same as revealed) with group's element
            # near every revealed cell 
            grp_members_ard_revealed = []
            for cell in revealed:
                arr = []
                for cell2 in get_cells_around(cell,self.board_size):
                    if cell2 in group:
                        arr.append(cell2)
                grp_members_ard_revealed.append(arr)
            print(len(grp_members_ard_revealed),len(group))
            input()
            #Filter arangements
            start = time.time()
            valid_arangements_index = []
            for j,arangement in enumerate(all_arangements):
                valid = True
                for i in range(len(revealed)):
                    #count nr of bombs in current arangement
                    bombs_ard_in_arangement = 0
                    for cell in grp_members_ard_revealed[i]:
                        bombs_ard_in_arangement += arangement[group.index(cell)]

                    if bombs_ard_in_arangement != bombs_ard[i]:
                        valid = False
                        break

                if valid:
                    valid_arangements_index.append(j)
            end = time.time()
            f_time = end-start
            if len(group) > 12:
                graph(g_time,f_time,len(group))
            #calculate the probability of every cell being a bomb
            arangements = np.array([a for i,a in enumerate(all_arangements) if i in valid_arangements_index])
            probs = np.full((len(group),1),None)
            for i,cell in enumerate(group):
                is_bomb = np.count_nonzero(arangements[:,i] == 1)
                prob = is_bomb / len(arangements)
                #If cell is certain to be a bomb or not beeing a bomb - return
                if prob == 1:
                    return cell[1],cell[0],True
                elif prob == 0:
                    return cell[1],cell[0],False
                probs[i] = prob

            grp_probs.append(probs)

        #choose cell with the lowest probability of being a bomb
        # probs = np.array(grp_probs)
        # index = np.unravel_index(probs.argmin(), probs.shape)
        # cell = border_groups[index[0],index[1]] 
        # print(cell)
        # input()

    def ai_move(self):
        if self.game_started:
            x,y,flag = self.ai(self.board)
            # x,y,flag = self.find_best_cell()
        else:
            x = np.random.randint(self.board_size[1])
            y = np.random.randint(self.board_size[0])
            flag = False

        self.mouse_on_cell((x,y),flag)
        sys.exit()

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
                    x1 = x+(self.cell_size-text.get_width())//2
                    y1 = y+(self.cell_size-text.get_height())//2
                    self.WIN.blit(text, (x1,y1))

                if self.probs[i,j] is not None and self.board[i,j,1] == 0:
                    text = self.cell_font.render(str(round(self.probs[i,j],2)),1,(255,0,0))
                    x1 = x+(self.cell_size-text.get_width())//2
                    y1 = y+(self.cell_size-text.get_height())//2
                    self.WIN.blit(text,(x1,y1))
        
        #flags
        text = self.menu_font.render(str(self.mines_number-self.flag_used),1,self.text_color)
        self.WIN.blit(text,(self.W//6,self.menu_height//2-text.get_height()//2))
        self.WIN.blit(self.flag_image,(self.W//6-self.flag_image.get_width(),self.menu_height//2-self.flag_image.get_height()//2))
        #clock
        text = self.menu_font.render(get_time(self.FPS_COUNTER),1,self.text_color)
        self.WIN.blit(text,(3*self.W//6-text.get_width()//2, self.menu_height//2-text.get_height()//2))
        #pause
        create_button(self.WIN, "||",(80,80,80),(120,120,120),(0,0,0),(5*self.W//6-25,self.menu_height//2-25,50,50),self.mouse_clicked,self.btn_font,action=self.pause)
        pygame.display.update()

    def play_ai(self):
        self.game_started = False
        self.board = np.zeros((self.board_size[0],self.board_size[1],2))
        self.flag_used = 0
        self.probs = np.full(self.board_size,None)
        self.FPS_COUNTER = 0

        thread = threading.Thread(target=self.ai_move)
        thread.daemon = True

        while self.run:
            pygame.event.pump()
            self.CLOCK.tick(self.FPS)
            self.events()
            self.keys()
            self.step()
            self.FPS_COUNTER = self.FPS_COUNTER+1 if self.game_started else 0
            if not thread.is_alive():
                thread = threading.Thread(target=self.ai_move)
                thread.daemon = True
                thread.start()
                

    def play(self):
        self.game_started = False
        self.board = np.zeros((self.board_size[0],self.board_size[1],2))
        self.flag_used = 0
        self.FPS_COUNTER = 0

        if self.first_launch:
            self.step()
            self.first_launch = False
            end_game(self.WIN,self.btn_font,self.menu_font,self.game_end_color,self.text_color,self.FPS_COUNTER,"Minesweeper",(self.W,self.H))

        while self.run:
            self.CLOCK.tick(self.FPS)
            self.events()
            self.keys()
            self.step()
            self.FPS_COUNTER = self.FPS_COUNTER+1 if self.game_started else 0

def end_game(WIN, btn_font,menu_font,game_end_color,text_color,FPS_COUNTER,title,win_size):
        run = True
        mouse_clicked = False
        W,H = win_size

        def resume():
            nonlocal run
            run = False

        def main_menu():
            game.first_launch = True
            game.play()

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

            if title == 'Paused':
                create_button(WIN, "Continue",(0,255,255),(0,190,190),(20,20,20),(W//2-150,H//2-300+230,300,80),mouse_clicked,btn_font,resume)
                create_button(WIN,"Menu (reset game)",(0,255,255),(0,190,190),(20,20,20),(W//2-150,H//2-300+350,300,80),mouse_clicked,btn_font,main_menu)
                create_button(WIN, "Exit",(255,0,0),(190,0,0),text_color,(W//2-150,H//2-300+470,300,80),mouse_clicked,btn_font,exit2)
            else:
                create_button(WIN, "Play",(0,255,255),(0,190,190),(20,20,20),(W//2-150,H//2-300+230,300,80),mouse_clicked,btn_font,game.play)
                create_button(WIN,"Watch AI play",(0,255,255),(0,190,190),(20,20,20),(W//2-150,H//2-300+350,300,80),mouse_clicked,btn_font,game.play_ai)
                create_button(WIN, "Exit",(255,0,0),(190,0,0),text_color,(W//2-150,H//2-300+470,300,80),mouse_clicked,btn_font,exit2)
             
            pygame.display.update()

        while run:
            mouse_clicked = False
            events2()
            refresh_window()

game = Minesweeper((15,19),mines_number=40)
game.play()
