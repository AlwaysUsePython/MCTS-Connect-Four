# This program is creating a template for a monte carlo tree

# Things that includes:

# - game states, i.e. the nodes of the tree
# - the tree itself

import random
import numpy as np


# Things a game state needs:
# - the literal game state (board)
# - whose turn it is
# - pointer to the parent (if it exists)
# - pointers to the children (if they exist)
# - a total score
# - a counter to keep track of the number of visits
# - a method to calculate UCBI
# - a method that expands a node
# - a method that finds highestUCBI

# note: what is UCBI? It's a way to balance between exploration and exploitation.
# Exploitation side is the average value (self.total/self.visits)
# Exploration side is 2 * √(ln(visits to parent)/visits to child)
# UCBI is sum of Exploitation value + Exploration value
class GameState:

    def __init__(self, board, player = None):
        self.board = board
        self.total = 0
        self.visits = 0
        self.player = player

        self.parent = None
        self.children = []
        self.leaf = False

        if hasWon(self.board, userPlayer):
            self.total = -50
            self.visits = 0
            self.leaf = True
        elif hasWon(self.board, getNextPlayer(userPlayer)):
            self.total = 50
            self.visits = 0
            self.leaf = True


    def setParent(self, parentState):
        self.parent = parentState
        self.player = getNextPlayer(parentState.player)
        parentState.addChild(self)
        if hasWon(self.board, userPlayer):
            self.total = -50
            self.visits = 0
            self.leaf = True
        elif hasWon(self.board, getNextPlayer(userPlayer)):
            self.total = 50
            self.visits = 0
            self.leaf = True

    def addChild(self, childState):
        self.children.append(childState)

    def roll(self):
        if self.leaf:
            self.visits = -1
            return self.total
        return simulate(self.board, getNextPlayer(self.player))

    def addToTotal(self, newValue):
        self.total += newValue

        # now we have to update the parent as well
        # to do this, we'll use a bit of recursion!

        # base case:
        if self.parent == None:
            return
        # recursive step:
        else:
            self.parent.addToTotal(newValue)

    def addVisit(self):
        self.visits += 1

        # same as above
        # base case:
        if self.parent == None:
            return
        # recursive step:
        else:
            self.parent.addVisit()

    def calculateUCBI(self):

        if self.visits == np.Infinity:
            return np.Infinity

        # Formula:
        # average value + 10*√(ln(visits to parent)/visits to child)

        # THINGS THAT CAN BE 0
        # - self.visits -> return infinity because we have a fully unexplored branch
        # - self.parent -> CANNOT BE NONE because then this would never get called!
        # - self.total -> doesn't cause 0 division errors so we don't care

        if self.visits == 0:
            if self.player != userPlayer:
                return -np.Infinity
            return np.Infinity

        else:
            try:
                exploitationValue = self.total / self.visits
            except:
                exploitationValue = self.total // (self.visits)

            # NOTE: np.log is actually ln(), np.log10 is standard log()
            explorationValue = 50 * np.sqrt(np.log(self.parent.visits)/self.visits)

            if self.player != userPlayer:
                explorationValue *= -1

            try:
                return exploitationValue + explorationValue
            except:
                return 1 * 10**200


    def getChildrenUCBIs(self):
        childScores = []

        for child in self.children:
            childScores.append(child.calculateUCBI())

        return childScores

    def findHighestUCBILeaf(self):

        # base case:
        if self.visits == 0 and self.parent != None:
            return self

        # recursive step(s):
        if self.children == []:
            self.expand()
            try:
                return self.children[0]
            except:
                return self

        else:
            UCBIs = self.getChildrenUCBIs()
            favoriteChild = 0

            if self.player != userPlayer:
                max = UCBIs[0]

                for childNum in range(len(UCBIs)):
                    if UCBIs[childNum] > max:
                        favoriteChild = childNum
                        max = UCBIs[childNum]

            else:
                min = UCBIs[0]

                for childNum in range(len(UCBIs)):
                    if UCBIs[childNum] < min:
                        favoriteChild = childNum
                        min = UCBIs[childNum]

            return self.children[favoriteChild].findHighestUCBILeaf()


    def expand(self):
        nextMoves = getNextMoves(self.board, self.player)

        for nextState in nextMoves:
            newState = GameState(getBoardCopy(nextState))
            newState.setParent(self)

# Things a MCTree needs:
# - root node -> this will point to all the other nodes
# - iterate() function that updates the values
# - makeChoice(x) function that iterates x times and picks out the best branch

# note: to write this, we need to assume that a few game-specific functions exist

class MCTree:

    def __init__(self, start):

        # note: this root is likely going to be a part of a different tree. So we can't just reuse it – we need to reset the total and visits
        self.root = start #GameState(start.board, start.player)
        self.root.expand()

        """print("ROOT")
        printBoard(self.root.board)"""

    def iterate(self):
        leafToUpdate = self.root.findHighestUCBILeaf()

        score = leafToUpdate.roll()

        leafToUpdate.addToTotal(score)
        leafToUpdate.addVisit()

    def makeChoice(self, iterations):
        for iteration in range(iterations):
            self.iterate()

        childScores = []

        for child in self.root.children:
            try:
                childScores.append(child.total / child.visits)
            except:
                childScores.append(child.total)

        approved = 0
        try:
            max = childScores[0]

            for item in range(len(childScores)):
                if childScores[item] > max:
                    approved = item
                    max = childScores[item]
            #print(approved)
            return [self.root.children[approved].board, max]

        except:
            #print("except")
            return [self.root.children[0].board, 50]



board = [
    list("_______"),
    list("_______"),
    list("_______"),
    list("_______"),
    list("_______"),
    list("_______"),
]

# This way we can toggle who's playing first
turn = "R"
userPlayer = "Y"

# copying the board to avoid pointer errors
def getBoardCopy(board):
    boardCopy = []

    for row in board:
        boardCopy.append(row.copy())

    return boardCopy

# boolean to detect whether or not moves can be made
def hasMovesLeft(board):
    for row in range(6):
        for col in range(7):
            if board[row][col] == '_':
                return True
    return False

# makes a move given a specified column
# NOTE: THERE IS NO CODE HERE TO CATCH ILLEGAL MOVES
def makeMove(currentBoard, col, symbol):
    firstEmptyRow = 0

    while currentBoard[firstEmptyRow+1][col] == "_":
        firstEmptyRow += 1

        # make sure we don't go off the board
        if firstEmptyRow == 5:
            break

    currentBoard[firstEmptyRow][col] = symbol

    return currentBoard

# Returns a list of the GAME STATES of all the possible next moves
def getNextMoves(currentBoard, player):
    nextMoves = []

    for col in range(7):
        if currentBoard[0][col] == "_":
            boardCopy = getBoardCopy(currentBoard)
            boardCopy = makeMove(boardCopy, col, player)
            nextMoves.append(boardCopy)

    return nextMoves

# Returns a boolean to tell if the player has won
# NOTE: WILL NOT TELL IF OPPONENT HAS WON, HOWEVER SHOULD NEVER GET TO THAT STATE
def hasWon(board, player):

    # 1) Check for horizontal connect 4
    for startRow in range(6):
        for startCol in range(4):
            if board[startRow][startCol] == player and board[startRow][startCol + 1] == player and board[startRow][startCol + 2] == player and board[startRow][startCol + 3] == player:
                return True

    # 2) Check for vertical connect 4
    for startRow in range(3):
        for startCol in range(7):
            if board[startRow][startCol] == player and board[startRow + 1][startCol] == player and board[startRow + 2][startCol] == player and board[startRow + 3][startCol] == player:
                return True

    # 3) Check for diagonal up connect 4
    for startRow in range(3, 6):
        for startCol in range(4):
            if board[startRow][startCol] == player and board[startRow - 1][startCol + 1] == player and board[startRow - 2][startCol + 2] == player and board[startRow - 3][startCol + 3] == player:
                return True

    # 4) Check for diagonal down connect 4
    for startRow in range(3):
        for startCol in range(4):
            if board[startRow][startCol] == player and board[startRow + 1][startCol + 1] == player and board[startRow + 2][startCol + 2] == player and board[startRow + 3][startCol + 3] == player:
                return True

# Takes in the currentPlayer, returns the next player
def getNextPlayer(currentPlayer):
    if currentPlayer == 'R':
        return 'Y'

    return 'R'

# Plays MC Simulation
# takes in a board and a player, returns a score (positive if the computer won, negative otherwise)
def simulate(currentBoard, player):
    currentPlayer = getNextPlayer(player)
    boardCopy = getBoardCopy(currentBoard)

    if hasWon(currentBoard, userPlayer):
        return -50
    elif hasWon(currentBoard, getNextPlayer(userPlayer)):
        return 50

    simulationMoves = []
    nextMoves = getNextMoves(boardCopy, currentPlayer)


    while nextMoves != []:
        roll = random.randint(1, len(nextMoves)) - 1
        boardCopy = nextMoves[roll]

        simulationMoves.append(boardCopy)

        if hasWon(boardCopy, currentPlayer):
            break

        currentPlayer = getNextPlayer(currentPlayer)
        nextMoves = getNextMoves(boardCopy, currentPlayer)

    if hasWon(boardCopy, userPlayer):
        score = -50
    elif hasWon(boardCopy, getNextPlayer(userPlayer)):
        score = 50
    else:
        score = 0

    return score

# prints the board
def printBoard(board):
    print(" 0  1  2  3  4  5  6")

    for row in range(6):
        for col in range(7):
            if board[row][col] == "R":
                print("🔴", end = " ")
            elif board[row][col] == "Y":
                print("🟡", end = " ")
            else:
                print("⚪", end = " ")
        print()

# Takes in input from the player and makes the move on the board
def getPlayerMove(board, currentPlayer):
    isMoveValid = False
    while isMoveValid == False:
        print('')
        userMove = input('column? ')
        userChoice = int(userMove)

        if board[0][userChoice] == '_':
            isMoveValid = True

    board = makeMove(board, userChoice, currentPlayer)
    return board


printBoard(board)

keepPlaying = True

while keepPlaying:
    while hasMovesLeft(board):
        if turn == userPlayer:
            board = getPlayerMove(board, turn)
        else:
            tree = MCTree(GameState(board, turn))
            move = tree.makeChoice(5000)
            board = move[0]
            if abs(move[1]) < 30:
                print("evaluation:", move[1])
            elif move[1] < 0:
                print("Uh oh... I think I'm gonna lose :(")
            else:
                print("GG's. Just concede now.")

        print('')
        printBoard(board)

        if hasWon(board, turn):
            print('Player ' + turn + ' has won!')
            break

        turn = getNextPlayer(turn)

    print()
    print("new game! switch colors")
    print()
    userPlayer = getNextPlayer(userPlayer)
    turn = "R"

    board = [
        list("_______"),
        list("_______"),
        list("_______"),
        list("_______"),
        list("_______"),
        list("_______"),
    ]

    gameOver = False

    printBoard(board)
