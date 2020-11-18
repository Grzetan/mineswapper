import pygame
import sys

sys.setrecursionlimit(3000)

def create_button(win,text,color,highlight_color,text_color,cords,mouse_clicked,font,action=None):
        mouse_pos = pygame.mouse.get_pos()
        mouse_on_btn = mouse_pos[0]>cords[0] and mouse_pos[0]<cords[0]+cords[2] and mouse_pos[1]>cords[1] and mouse_pos[1]<cords[1]+cords[3]
        if mouse_on_btn:
            color = highlight_color
            if mouse_clicked and action != None:
                action()
        pygame.draw.rect(win,color,cords)
        text_ = font.render(text,1,text_color)
        win.blit(text_,(cords[0]+cords[2]//2-text_.get_width()//2, cords[1]+cords[3]//2-text_.get_height()//2))

def get_time(fps):
        sec = fps//30%60
        minutes = fps//30//60
        minutes = "0"+str(minutes) if minutes < 10 else str(minutes)
        sec = "0"+str(sec) if sec < 10 else str(sec)
        return minutes+":"+sec

def get_cells_around(cell,board_size):
        fields_to_check = [(-1,-1), (0,-1),(1,-1)
                          ,(-1,0), (1,0)
                          ,(-1,1), (0,1), (1,1)]
        cells_around = []
        for field in fields_to_check:
            x = cell[0]+field[0]
            y = cell[1]+field[1]
            if x < 0 or y < 0 or x > board_size[0]-1 or y > board_size[1]-1:
                continue
            cells_around.append((x,y))
        
        return cells_around

def exit2():
        exit()