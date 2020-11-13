import pygame
import numpy as np
import sys

sys.setrecursionlimit(2000)

pygame.init()

W,H = 640, 720
WIN = pygame.display.set_mode((W,H))
CLOCK = pygame.time.Clock()
FPS = 30

def game(board_size):
    run = True
    run2 = True
    FPS_COUNTER = 0
    game_started = False
    current_cell = None
    mines_number = 40
    flag_used = 0
    cell_font = pygame.font.SysFont('comicsans',25)
    menu_font = pygame.font.SysFont('comicsans',50)
    btn_font = pygame.font.SysFont('comicsans',40)
    main_color = (2, 123, 206)
    text_color = (255,255,255)
    game_end_color = (2, 123, 206)
    background_color = (4, 150, 255)
    cell_color = (0, 72, 124)

    board = np.zeros((board_size[0],board_size[1],2))
    menu_height = 150
    inner_padding = 2
    cell_size = 25
    x_align = int((W - board_size[1]*(cell_size+2*inner_padding)) / 2)
    y_align = int((H - board_size[0]*(cell_size+2*inner_padding) + menu_height) / 2) 

    flag_image = pygame.image.load('flag.png')
    flag_image_resized = pygame.transform.scale(flag_image,(cell_size,cell_size))

    def get_cells_around(cell):
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

    def reveal_empty_cells(cell):
        nonlocal board
        cells_ard = get_cells_around(cell)
        for cell in cells_ard:
            if board[cell[0],cell[1],0] == 0 and board[cell[0],cell[1],1] == 0:
                board[cell[0],cell[1],1] = 1
                reveal_empty_cells(cell)
                for cell2 in get_cells_around(cell):
                    board[cell2[0],cell2[1],1] = 1
        
        check_for_win()

    def get_time(fps):
        sec = fps//30%60
        minutes = fps//30//60
        minutes = "0"+str(minutes) if minutes < 10 else str(minutes)
        sec = "0"+str(sec) if sec < 10 else str(sec)
        return minutes+":"+sec

    def create_button(win,text,color,highlight_color,cords,mouse_clicked,action=None):
        mouse_pos = pygame.mouse.get_pos()
        mouse_on_btn = mouse_pos[0]>cords[0] and mouse_pos[0]<cords[0]+cords[2] and mouse_pos[1]>cords[1] and mouse_pos[1]<cords[1]+cords[3]
        if mouse_on_btn:
            color = highlight_color
            if mouse_clicked and action != None:
                action()
        pygame.draw.rect(win,color,cords)
        text_ = btn_font.render(text,1,text_color)
        WIN.blit(text_,(W//2-text_.get_width()//2, cords[1]+cords[3]//2-text_.get_height()//2))

    def check_for_win():
        revealed = 0
        for i in range(board_size[0]):
            for j in range(board_size[1]):
                if board[i,j,1] == 1:
                    revealed += 1
        
        if revealed >= board_size[0]*board_size[1] - mines_number:
            end_game("Victory")

    def reset_board():
        nonlocal board
        nonlocal FPS_COUNTER
        nonlocal flag_used
        nonlocal run2
        nonlocal game_started

        game_started = False
        run2 = False
        FPS_COUNTER = 0
        flag_used = 0
        board = np.zeros((board_size[0],board_size[1],2))

    def exit2():
        exit()

    def end_game(title):
        nonlocal run2
        run2 = True
        mouse_clicked = False

        def events2():
            nonlocal run2
            nonlocal run
            nonlocal mouse_clicked
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run2 = False
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_clicked=True
        
        def refresh_window():
            pygame.draw.rect(WIN, game_end_color, (W//2-200,H//2-300,400,600))

            text = menu_font.render(title,1,text_color)
            WIN.blit(text,(W//2-text.get_width()//2,H//2-300+50))

            text = menu_font.render("Time: " + get_time(FPS_COUNTER),1,text_color)
            WIN.blit(text, (W//2-text.get_width()//2,H//2-300+150))

            create_button(WIN, "Play again",(0,255,0),(0,190,0),(W//2-150,H//2-300+230,300,80),mouse_clicked,reset_board)
            create_button(WIN, "Exit",(255,0,0),(190,0,0),(W//2-150,H//2-300+370,300,80),mouse_clicked,exit2)

            pygame.display.update()

        while run2:
            mouse_clicked = False
            events2()
            refresh_window()

    def start_game(current_cell):
        nonlocal board
        board[current_cell[0],current_cell[1]] = 1
        mines = []
        for i in range(mines_number):
            mine_x = np.random.randint(0,board_size[0])
            mine_y = np.random.randint(0,board_size[1])
            while (mine_x,mine_y) == current_cell or (mine_x,mine_y) in get_cells_around(current_cell) or (mine_x,mine_y) in mines:
                mine_x = np.random.randint(0,board_size[0])
                mine_y = np.random.randint(0,board_size[1])
            mines.append((mine_x,mine_y))
            board[mine_x,mine_y,0] = -1

        for i in range(board_size[0]):
            for j in range(board_size[1]):
                mines_around = 0
                if board[i,j,0] != -1:
                    for cell in get_cells_around((i,j)):
                        if board[cell[0],cell[1],0] == -1:
                            mines_around += 1
                    board[i,j,0] = mines_around

        reveal_empty_cells(current_cell)

        for cell in get_cells_around(current_cell):
            board[cell[0],cell[1],1] = 1

    def events():
        nonlocal run
        nonlocal game_started
        nonlocal board
        nonlocal flag_used

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if current_cell is not None:
                    if not game_started and event.button == 1:
                        start_game(current_cell)
                        game_started = True
                    elif board[current_cell[0],current_cell[1],1] != 1:
                        if event.button == 1 and board[current_cell[0],current_cell[1],1] != 2:
                            board[current_cell[0],current_cell[1],1] = 1
                            if board[current_cell[0],current_cell[1],0] == 0:
                                reveal_empty_cells(current_cell)
                            elif board[current_cell[0],current_cell[1],0] == -1:
                                end_game("Game over")
                            check_for_win()
                        elif event.button == 1:
                            board[current_cell[0],current_cell[1],1] = 0
                            flag_used -= 1
                        elif event.button == 3 and game_started:
                            if board[current_cell[0],current_cell[1],1] == 2:
                                board[current_cell[0],current_cell[1],1] = 0
                                flag_used -= 1
                            elif flag_used < mines_number:
                                board[current_cell[0],current_cell[1],1] = 2
                                flag_used += 1

    def step(board):
        nonlocal current_cell
        current_cell = None
        WIN.fill(background_color)
        pygame.draw.rect(WIN, cell_color, (0,menu_height,W,3))
        #game
        mouse_pos = pygame.mouse.get_pos()
        for i in range(board.shape[0]):
            for j in range(board.shape[1]):
                x = j*(cell_size + 2*inner_padding) + x_align
                y = i*(cell_size + 2*inner_padding) + y_align
                color = (255,255,255)
                if mouse_pos[0] in list(range(x,x+cell_size)) and mouse_pos[1] in list(range(y,y+cell_size)):
                    color=(190,190,190)
                    current_cell = (i,j)
                if board[i,j,1] == 1:
                    color = cell_color

                pygame.draw.rect(WIN, color, (x,y,cell_size,cell_size))

                if board[i,j,1] == 2:
                    WIN.blit(flag_image_resized,(x,y))

                if board[i,j,1] == 1 and board[i,j,0] != 0:
                    text = cell_font.render(str(int(board[i,j,0])),1,text_color)
                    x = x+(cell_size-text.get_width())//2
                    y = y+(cell_size-text.get_height())//2
                    WIN.blit(text, (x,y))
        #flags
        text = menu_font.render(str(mines_number-flag_used),1,text_color)
        WIN.blit(text,(W//4,menu_height//2-text.get_height()//2))
        WIN.blit(flag_image,(W//4-flag_image.get_width(),menu_height//2-text.get_height()//2))
        #clock
        text = menu_font.render(get_time(FPS_COUNTER),1,text_color)
        WIN.blit(text,(3*W//4-text.get_width()//2, menu_height//2-text.get_height()//2))
        pygame.display.update()

    while run:
        CLOCK.tick(FPS)
        events()
        step(board)
        FPS_COUNTER = FPS_COUNTER+1 if game_started else 0

game((15,19))