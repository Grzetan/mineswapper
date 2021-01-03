# mineswapper
Mineswapper game

dependencies:
pygame 
numpy
pyautogui

# Starting the game
To start the game just type "python game.py" in main directory.

# Intro to bot.py
File bot.py contains the class MinesweeperBot which given an board picks best cell.
You can use it in your projects.

# Tutorial
Tutorial (can also be found at the beggining of file):

In order for this bot to work we have to pass board variable 
every time we want to make prediction.
Board variable is a 3-dimensional array.
First two axis represent the size of an board.
The third axis has the size of 2, so the shape of board with 
size 10x15 should look like this: (10,15,2)

The first field in the third axis is the value of the individual cell
Range of values: <0,8> (8 becouse it is the maximum count of bombs around) 
This number represent the count of bombs around this particular cell
So if the first field's value in third axis is 3, we can say that 
there are 3 bombs around this cell

The second field in the third axis represents the state of cell
Range of values: <0,2>
value 0: Unrevealed cell
value 1: revealed cell
value 2: There is a flag on this cell

Bot returns a tupple of size 3
First two values are the x and y coordinates 
of the cell on the board. The third value is either True or False
True if the cell is suppose to be the flag
and False if it's save  

Let's say that bot predicted that the cell in upper left corner is save
That prediction produces this output: (0,0,False)
To make sure it's understood we will do one more.
Bot predicted that the cell in bottom right corner has 100% of being an bomb
Board size - 12x14
The output would be (11,13,True)
