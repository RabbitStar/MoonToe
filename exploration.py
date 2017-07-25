import collections
import pickle
import random
import math

import itertools

EMPTY = 0
PLAYER_X = 1
PLAYER_O = -1
DRAW = 2

BOARD_SIZE = 7
LINE_SIZE = 4

NAMES = {0: '_', 1: 'X', -1: 'O'}

def printboard(state):
    cells = []
    print ' ',
    for i in range(BOARD_SIZE):
        print '{0}'.format(str(i).center(5)),
    print '\n'
    for i in range(BOARD_SIZE):
        print i,
        for j in range(BOARD_SIZE):
            print '{0}'.format(NAMES[state[i][j]].center(5)),
        print('\n')

def emptyboard():
    state = []
    for i in range(BOARD_SIZE):
        state.append([])
        for j in range(BOARD_SIZE):
            state[i].append(0)
    return state


def inside(i, j):
    return BOARD_SIZE > i >= 0 and BOARD_SIZE > j >= 0


def gameover(state):
    # Horizontal winning
    total_zero = 0
    for i in range(BOARD_SIZE):
        ct = {0:0, 1:0, -1:0}
        for j in range(LINE_SIZE-1):
            ct[state[i][j]] += 1
            if state[i][j] == 0:
                total_zero+=1
        for j in range(LINE_SIZE-1,BOARD_SIZE):
            if state[i][j] == 0:
                total_zero+=1
            ct[state[i][j]]+=1
            # print i,j,state[i][j],ct[state[i][j]]
            if state[i][j] != 0 and ct[state[i][j]] == LINE_SIZE:
                return state[i][j]
            ct[state[i][j-LINE_SIZE+1]]-=1

    # Vertical winning
    for j in range(BOARD_SIZE):
        ct = {0:0, 1:0, -1:0}
        for i in range(LINE_SIZE-1):
            ct[state[i][j]]+=1
        for i in range(LINE_SIZE-1,BOARD_SIZE):
            ct[state[i][j]]+=1
            if state[i][j] != 0 and ct[state[i][j]] == LINE_SIZE:
                return state[i][j]
            ct[state[i][j-LINE_SIZE+1]]-=1

    # Diagonal winning
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            ct1 = {0:0, 1:0, -1:0}
            ct2 = {0: 0, 1: 0, -1: 0}
            for k in range(LINE_SIZE):
                x,y = i+k,j+k
                if inside(x,y):
                    ct1[state[x][y]]+=1
                x,y = i+k,j-k
                if inside(x,y):
                    ct2[state[x][y]]+=1
            if ct1[1] == LINE_SIZE or ct2[1] == LINE_SIZE:
                return 1
            elif ct1[-1] == LINE_SIZE or ct2[-1] == LINE_SIZE:
                return -1

    if total_zero == 0:
        return 2
    return 0

class Agent(object):
    def __init__(self, player, lossval = 0):
        self.values = {}
        self.player = player
        self.epsilon = 0.1
        self.lossval = lossval
        self.prevstate = None
        self.prevvalue = 0
        self.alpha = 0.99

    def winnerval(self, winner):
        if winner == self.player:
            return 1
        elif winner == DRAW:
            return 0
        elif winner == EMPTY:
            return 0.5
        else:
            return self.lossval

    def available_moves(self,state):
        for i, j in itertools.product(range(BOARD_SIZE), range(BOARD_SIZE)):
            if state[i][j] == 0:
                yield (i, j)

    def state_formula(self, state):
        c = self.possible(state)
        if self.player == 1:
            key = (c[(1,0,3)],c[(2,0,2)],c[(3,0,1)],c[(4,0,0)],c[(0,1,3)],c[(0,2,2)],c[(0,3,1)],c[(0,4,0)])
        else:
            key = (c[(0,1,3)],c[(0,2,2)],c[(0,3,1)],c[(0,4,0)], c[(1,0,3)],c[(2,0,2)],c[(3,0,1)],c[(4,0,0)])
        return math.log(key[0]+1)+math.sqrt(key[1])+key[2]+((5*key[3])**3)-(math.log(key[4]+1)+math.sqrt(key[5])+key[6])

    def random_greedy(self,state):
        maxval = -999999999
        maxpos = None
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if state[i][j] == 0:
                    state[i][j] = self.player
                    val = self.state_formula(state)
                    state[i][j] = EMPTY
                    if val > maxval:
                        maxval = val
                        maxpos = (i, j)
        return maxpos

    def action(self,state):
        return self.random_greedy(state)

    def possible(self, state):
        line = collections.defaultdict(lambda: 0)
        line.clear()
        for i in range(BOARD_SIZE):
            ct = {0: 0, 1: 0, -1: 0}
            for j in range(LINE_SIZE - 1):
                ct[state[i][j]] += 1
            for j in range(LINE_SIZE - 1, BOARD_SIZE):
                ct[state[i][j]] += 1
                line[(ct[1],ct[-1],ct[0])] += 1
                ct[state[i][j - LINE_SIZE + 1]] -= 1

        for j in range(BOARD_SIZE):
            ct = {0: 0, 1: 0, -1: 0}
            for i in range(LINE_SIZE - 1):
                ct[state[i][j]] += 1
            for i in range(LINE_SIZE - 1, BOARD_SIZE):
                ct[state[i][j]] += 1
                line[(ct[1],ct[-1],ct[0])] += 1
                ct[state[i-LINE_SIZE+1][j]] -= 1

        for i in range(BOARD_SIZE - LINE_SIZE + 1):
            ct = {0: 0, 1: 0, -1: 0}
            for k in range(LINE_SIZE - 1):
                ct[state[i + k][k]] += 1
            inc = LINE_SIZE - 1
            while inside(i + inc, inc):
                ct[state[i + inc][inc]] += 1
                line[(ct[1],ct[-1],ct[0])] += 1
                ct[state[i + inc - LINE_SIZE + 1][inc - LINE_SIZE + 1]] -= 1
                inc += 1
            ct = {0: 0, 1: 0, -1: 0}
            if i != 0:
                for k in range(LINE_SIZE - 1):
                    ct[state[k][i + k]] += 1
                inc = LINE_SIZE - 1
                while inside(inc, i + inc):
                    ct[state[inc][i + inc]] += 1
                    line[(ct[1],ct[-1],ct[0])] += 1
                    ct[state[inc - LINE_SIZE + 1][i + inc - LINE_SIZE + 1]] -= 1
                    inc += 1

        for i in range(LINE_SIZE - 1, BOARD_SIZE):
            ct = {0: 0, 1: 0, -1: 0}
            for k in range(LINE_SIZE - 1):
                ct[state[k][i - k]] += 1
            inc = LINE_SIZE - 1
            while inside(inc, i - inc):
                ct[state[inc][i - inc]] += 1
                line[(ct[1],ct[-1],ct[0])] += 1
                ct[state[inc - LINE_SIZE + 1][i - inc + LINE_SIZE - 1]] -= 1
                inc += 1
            ct = {0: 0, 1: 0, -1: 0}
            if i != BOARD_SIZE - 1:
                for k in range(LINE_SIZE - 1):
                    ct[state[BOARD_SIZE - i - 1 + k][BOARD_SIZE - 1 - k]] += 1
                inc = LINE_SIZE - 1
                while inside(BOARD_SIZE - i - 1 + inc, BOARD_SIZE - 1 - inc):
                    ct[state[BOARD_SIZE - i - 1 + inc][BOARD_SIZE - 1 - inc]] += 1
                    line[(ct[1],ct[-1],ct[0])] += 1
                    ct[state[BOARD_SIZE - i - 1 + inc - LINE_SIZE + 1][BOARD_SIZE - 1 - inc + LINE_SIZE - 1]] -= 1
                    inc += 1
        return line

def play(agent1, agent2):
    state = emptyboard()
    for k in range(BOARD_SIZE*BOARD_SIZE):
        if k % 2 == 0:
            move = agent1.action(state)
            state[move[0]][move[1]] = agent1.player
        else:
            move = agent2.action(state)
            state[move[0]][move[1]] = agent2.player
        winner = gameover(state)
        if winner != EMPTY:
            # print winner
            return winner

    # print winner
    return winner

class Human(object):
    def __init__(self, player):
        self.player = player

    def action(self, state):
        printboard(state)
        action = raw_input('your move? ')
        move = (int(action.split(',')[0]),int(action.split(',')[1]))
        '''
        while not move in emptystate:
            action = raw_input('your move? ')
            move = (int(action.split(',')[0]), int(action.split(',')[1]))
        '''
        return move

if __name__ == '__main__':
    a1 = Agent(1, lossval=-1)
    while True:
        a2 = Human(-1)
        winner = play(a1, a2)