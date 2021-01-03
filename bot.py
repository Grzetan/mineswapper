# Minesweeper bot


# In order for this bot to work we have to pass board variable 
# every time we want to make prediction.
# Board variable is a 3-dimensional array.
# First two axis represent the size of an board.
# The third axis has the size of 2, so the shape of board with 
# size 10x15 should look like this: (10,15,2)

# The first field in the third axis is the value of the individual cell
# Range of values: <-1,8> (8 becouse it is the maximum count of bombs around) 
# If the value is equal to -1, that means that the cell is the bomb
# If the value is greater then -1, it is the count of bombs around this particular cell
# So if the first field's value in third axis is 3, we can say that 
# there are 3 bombs around this cell

# The second field in the third axis represents the state of cell
# Range of values: <0,2>
# value 0: Unrevealed cell
# value 1: revealed cell
# value 2: There is a flag on this cell

# Bot returns a tupple of size 3
# First two values are the x and y coordinates 
# of the cell on the board. The third value is either True or False
# True if the cell is suppose to be the flag
# and False if it's save  

# Let's say that bot predicted that the cell in upper left corner is save
# That prediction produces this output: (0,0,False)
# To make sure it's understood we will do one more.
# Bot predicted that the cell in bottom right corner has 100% of being an bomb
# Board size - 12x14
# The output would be (11,13,True)

class MinesweeperBot():
    def __init__(self):
        self.board_size = None
        self.board = None

    def graph(self,t1,t2,len1):
        with open('graph.txt','a') as f:
            f.write(f"generate ttime - {t1}\nfiltering time - {t2}\nlen - {len1}\n\n")
            f.close()

    def common_member(self,a,b):
        a_set = set(a) 
        b_set = set(b) 
        if (a_set & b_set): 
            return True 
        else: 
            return False

    def get_cells_around(self,cell):
        fields_to_check = [(-1,-1), (0,-1),(1,-1)
                          ,(-1,0), (1,0)
                          ,(-1,1), (0,1), (1,1)]
        cells_around = []
        #Iterate through every field to check
        for field in fields_to_check:
            #Get an addres of cell to check
            x = cell[0]+field[0]
            y = cell[1]+field[1]
            #Check if it fits in board's boundaries
            if x < 0 or y < 0 or x > self.board_size[1]-1 or y > self.board_size[0]-1:
                continue
            cells_around.append((x,y))

        return cells_around

    def generate_bomb_arangements(self, grp_len):
        if grp_len == 1:
            #Combination for group with only 1 element has length of 2
            #This one and only cell is either a bomb or it's not
            combination = [[0],[1]]
        else:
            #Get combination for group i field smaller
            combination_ = self.generate_bomb_arangements(grp_len-1)
            #Double this combination adding a posibility of current cell being a bomb and not being a bomb
            combination = []
            for i in range(2):
                for c in combination_:
                    bufor = c[:]
                    bufor.append(i)
                    combination.append(bufor)
        return combination

    def simple_argorithm(self):
        #Iterate through every cell on the board
        for y,col in enumerate(self.board):
            for x,cell_data in enumerate(col):
                if cell_data[0] > 0 and cell_data[1] == 1:
                    bombs_ard = cell_data[0]
                    cells_ard = self.get_cells_around((x,y))
                    indexes = [] #indexes of uncovered cell around
                    for i,cell in enumerate(cells_ard):
                        if self.board[cell[1],cell[0],1] == 0:
                            indexes.append(i)
                        elif self.board[cell[1],cell[0],1] == 2:
                            #If there is a flag around subctract 1 from bombs_ard
                            bombs_ard -= 1 
                    #Filter cells around so we can seperate uncovered fields
                    cells_ard = [cell for j,cell in enumerate(cells_ard) if j in indexes]
                    for cell in cells_ard:
                        #Calculate probability of being a bomb for each uncovered cell around
                        prob = bombs_ard / len(cells_ard)
                        #If there is 100% or 0% of cell being a bomb, return the result
                        if prob == 1:
                            return cell[0],cell[1],True
                        elif prob == 0:
                            return cell[0],cell[1],False
        return False

    def tank_solver(self):
        #Make a list of unrevealed border cells
        border_cells = []
        for y in range(self.board_size[0]):
            for x in range(self.board_size[1]):
                if self.board[y,x,1] == 0:
                    #Get all revealed cells around
                    revealed_cells_ard = [cell for cell in self.get_cells_around((x,y)) if self.board[cell[1],cell[0],1] == 1]
                    #If there is at least one, append cell to border cells
                    if len(revealed_cells_ard) > 0:
                        border_cells.append((x,y))
        #Segregate border cell into groups
        #One group has nothing to do with any other group
        border_groups = []
        for border_cell in border_cells:
            #Get revealed cells around
            revealed_ard = [cell for cell in self.get_cells_around(border_cell) if self.board[cell[1],cell[0],1] == 1]
            #Get every unrevealed cell around every revealed cell
            unrevealed_ard = [cell for cell2 in revealed_ard for cell in self.get_cells_around(cell2) if self.board[cell[1],cell[0],1] == 0]
            valid = []#Indexes of groups valid for cell
            for i,grp in enumerate(border_groups):
                #If we have at least one common member in group and unrevealed_ard, append to valid
                if self.common_member(grp, unrevealed_ard):
                    valid.append(i)
                    continue
            #If there is only one valid group, append the cell to it
            if len(valid) == 1:
                border_groups[valid[0]].append(border_cell)
            #If there are two or more, merge those groups and append cell to the new group
            elif len(valid) > 1:
                merged_group = [cell for i,grp2 in enumerate(border_groups) for cell in grp2 if i in valid]
                merged_group.append(border_cell)
                #Remove merged groups 
                border_groups = [grp2 for i,grp2 in enumerate(border_groups) if i not in valid]
                #Append new group
                border_groups.append(merged_group)
            #If there is no valid group, create new group
            elif len(valid) == 0:
                border_groups.append([border_cell])

        #Sort border groups by length
        border_groups.sort(key=len)
        #Array for probs
        probs = []

        for grp in border_groups:
            #If group is too big break out of the loop
            if len(grp) > 19:
                break
            #Generate all posible arangements of bombs
            all_arangements = self.generate_bomb_arangements(len(grp))
            #Get every revealed cell around every cell in the group
            revealed = [cell for cell2 in grp for cell in self.get_cells_around(cell2) if self.board[cell[1],cell[0],1] == 1]
            #Make an array with bombs around every revealed cell having in mind flags
            bombs_ard = []
            for i,cell in enumerate(revealed):
                #Get number of bombs ard
                bombs = self.board[cell[1],cell[0],0]
                for cell2 in self.get_cells_around(cell):
                    #If any of cells around is a flag, reduce bombs variable
                    if self.board[cell2[1],cell2[0],1] == 2:
                        bombs -= 1
                bombs_ard.append(bombs)
            #Make an array with group members around every revealed cell
            grp_members_ard_revealed = []
            for cell in revealed:
                arr = []
                #Iterate through cells ard and add those which are group members
                for cell2 in self.get_cells_around(cell):
                    if cell2 in grp:
                        arr.append(cell2)
                #Add to main array the result
                grp_members_ard_revealed.append(arr)
           #Filter arangements so we get only the valid ones
            valid_arangements_index = []
            for j,arg in enumerate(all_arangements):
                #Check if there is a required number of bombs around every revealed cell in arangement
                for i,cell in enumerate(revealed):
                    #Count bombs ard in arangement
                    bombs_ard_in_arangement = 0
                    for cell in grp_members_ard_revealed[i]:
                        bombs_ard_in_arangement += arg[grp.index(cell)]
                    #Check if number of bombs is valid, if not go to next arangement
                    if bombs_ard_in_arangement != bombs_ard[i]:
                        break
                    #If arangement is valid, append it's index to valid arangements
                    valid_arangements_index.append(j)
            #Calculate probability of every cell in the group being a bomb
            for i,cell in enumerate(grp):
                #Count how many times cell is an bomb in all arangments
                is_bomb = 0
                for j in valid_arangements_index:
                    is_bomb += all_arangements[j][i]
                prob = is_bomb / len(valid_arangements_index)
                #If we are certain about cell being a bomb or not, return 
                if prob == 1:
                    return cell[0],cell[1],True
                elif prob == 0:
                    return cell[0],cell[1],False
                #Append prob to array 
                probs.append((prob,cell))
        #If tanksolver is not certain about any cell, return one with
        #the lowest probability of being a bomb

        minimum = 1 #Variable for storing lowest prob
        cell = None
        for prob in probs:
            if prob[0] < minimum:
                minimum = prob[0]
                cell = prob[1]
        #If every group was too big, just pick first border cell
        if cell is None:
            cell = border_cells[0]
        #return the result
        return cell[0],cell[1],False


    def __call__(self,board):
        self.board = board
        self.board_size = board.shape[:2]
        #Run simple algorithm, if it finds cell, return it
        result = self.simple_argorithm()
        if result:
            return result
        #Run tanksolver
        result = self.tank_solver()
        return result