import requests
import re

class Game(object):
    url = 'https://rota.praetorian.com/rota/service/play.php'
    session = requests.Session()
    board = '---------'
    wins = 0
    fails = 0
    rounds = 0
    moves = 0
    hash = ''
    gaming = False
    currentGame = []

    def __init__(self):
        self.handle(self.session.get(self.url+"?request=new&email=xxx@xxx.xxx").json())

    def handle(self, req):
        if req.get('status', '') != 'success':
            print('Failed' + req)
            raise Exception('Failed Request')
        data = req.get('data', [])
        if self.rounds >= 50:
            self.hash = data['hash']
            print(self.hash)
            exit()
        try:
            self.board = data['board']
        except:
            self.hash = data['hash']
            print(str(self.hash))
            exit()
        self.wins, self.fails, self.moves, self.rounds = data['player_wins'], data['computer_wins'], data['moves'], data['games_won']
        if self.moves > 30:
            self.next()
            self.gaming = False
        if self.fails > 0:
            print('Failed!')
            exit()
    
    def place(self, x):
        self.handle(self.session.get(self.url+"?request=place&location=" + str(x)).json())
    
    def move(self, x, y):
        self.handle(self.session.get(self.url+"?request=move&from=" + str(x) + "&to=" + str(y)).json())

    def status(self):
        self.handle(self.session.get(self.url+"?request=status").json())

    def next(self):
        self.handle(self.session.get(self.url+"?request=next").json())
    
    def clock(self, loc):
        if loc <= 0:
            exit()
        dic = {1:2, 2:3, 3:6, 4:1, 5:5, 6:9, 7:4, 8:7, 9:8}
        return dic[loc]

    def cclock(self, loc):
        if loc <= 0:
            exit()
        dic = {1:4, 2:1, 3:2, 4:7, 5:5, 6:3, 7:8, 8:9, 9:6}
        return dic[loc]
    
    def movable(self, loc):
        return self.board[loc-1] == '-'

    def __str__(self):
        t = re.findall('.{3}', self.board)
        s = ''
        for i in t:
            s += i+'\n'
        return s

    def winCross(self, char, move):
        if (self.board[5-1] != char and move[1] != 5) or move[0] == 5:
            return False
        index = [(i+1) for i, c in enumerate(self.board) if c == char]
        if move[0] != 0:
            index.remove(move[0])
        index.append(move[1])
        return sum(index) == 15

    def winEdge(self, char, move):
        locs = [(i+1) for i, c in enumerate(self.board) if c == char]
        if move[0] != 0:
            locs.remove(move[0])
        locs.append(move[1])
        if 5 in locs:
            return False
        for loc in locs:
            c, cc = self.clock(loc), self.cclock(loc)
            if (c in locs) and (self.clock(c) in locs):
                return True
            if (cc in locs) and (self.cclock(cc) in locs):
                return True
        return False

    def checkWin(self, char):
        for loc in range(1, 10):
            if not self.movable(loc):
                continue
            if self.winCross(char, (0, loc)):
                return loc
            if self.winEdge(char, (0, loc)):
                return loc
        return 0
    
    def start(self):
        self.gaming = True
        self.currentGame.append(str(self))
        if 'c' in self.board:
            loc = self.board.index('c') + 1
            if loc == 5:
                self.place(8)
            else:
                self.place(self.cclock(loc))
        else:
            self.place(8)
        self.currentGame.append(str(self))
        loc = self.checkWin('c')
        if loc == 0:
            for i in range(1, 10):
                if self.board[i-1] == 'c':
                    if i == 5:
                        loc = 10 - (self.board.index('p') + 1)
                        self.place(loc)
                        break
                    c, cc = self.clock(i), self.cclock(i)
                    if self.movable(c) and not self.nearPiece('p', 0, c):
                        self.place(c)
                        break
                    if self.movable(cc) and not self.nearPiece('p', 0, cc):
                        self.place(cc)
                        break
        else:
            self.place(loc)
        self.currentGame.append(str(self))
        loc = 0
        if self.board.count('c') == 2:
            loc = self.checkWin('c')
        else:
            computerWinMoves = self.winMoves('c')
            computerPossibleMoves = self.possibleMoves('c')
            for possibleMove in computerPossibleMoves:
                if (possibleMove in computerWinMoves):
                    loc = possibleMove[1]
                    if self.movable(loc):
                        continue
        if loc == 0:
            prev = self.board.index('c') + 1
            while True:
                if prev == 5:
                    prev = 8
                c = self.clock(prev)
                if self.movable(c) and not self.nearPiece('p', 0, c):
                    self.place(c)
                    break
                prev = c
        else:
            self.place(loc)
        self.currentGame.append(str(self))
        if self.board.count('c') != 3:
            raise Exception("Not enough pieces placed")
        
    def possibleMoves(self, char):
        moves = []
        locs = [(i + 1) for i, c in enumerate(self.board) if c == char]
        for loc in locs:
            if loc == 5:
                for i in range(1, 10):
                    if i == 5:
                        continue
                    if self.movable(i):
                        moves.append((loc, i))
            else:
                c, cc = self.clock(loc), self.cclock(loc)
                middle = 5
                if self.movable(c):
                    moves.append((loc, c))
                if self.movable(cc):
                    moves.append((loc, cc))
                if self.movable(middle):
                    moves.append((loc, middle))
        return moves

    def winMoves(self, char):
        moves = []
        locs = [(i + 1) for i, c in enumerate(self.board) if c == char]
        for loc in locs:
            if loc == 5:
                for i in range(1, 10):
                    if i == 5:
                        continue
                    if self.winCross(char, (loc, i)) or self.winEdge(char, (loc, i)):
                        moves.append((loc, i))
            else:
                c, cc = self.clock(loc), self.cclock(loc)
                middle = 5
                if self.winCross(char, (loc, c)) or self.winEdge(char, (loc, c)):
                    moves.append((loc, c))
                if self.winCross(char, (loc, cc)) or self.winEdge(char, (loc, cc)):
                    moves.append((loc, cc))
                if self.winCross(char, (loc, middle)) or self.winEdge(char, (loc, middle)):
                    moves.append((loc, middle))
        return moves

    def nearPiece(self, char, current_loc, loc):
        if loc == 5:
            return True
        c, cc = self.clock(loc), self.cclock(loc)
        if c == current_loc:
            return self.board[cc - 1] == char
        if cc == current_loc:
            return self.board[c - 1] == char
        return (self.board[c - 1] == char) or (self.board[cc - 1] == char)

    def defense(self):
        self.currentGame.append(str(self))
        playerMoves = self.possibleMoves('p')
        computerMoves = self.winMoves('c')
        for move in playerMoves:
            if self.winEdge('p', move) or self.winCross('p', move):
                print("Win!")
                self.move(move[0], move[1])
                return
        playLocs = [(i + 1) for i, c in enumerate(self.board) if c == 'p']
        for computerMove in computerMoves[:]:
            if computerMove[1] in playLocs:
                computerMoves.remove(computerMove)
                for playerMove in playerMoves[:]:
                    if playerMove[0] == computerMove[1]:
                        playerMoves.remove(playerMove)
        compWinLocs = []
        for move in computerMoves:
            compWinLocs.append(move[1])
        compWinLocs = list(set(compWinLocs))

        if len(compWinLocs) > 1:
            print("Failed, computer win")
            exit(1)
        if compWinLocs:
            for move in playerMoves:
                if move[1] == compWinLocs[0]:
                    self.move(move[0], move[1])
                    return
        else:
            for move in playerMoves:
                if move[0] == 5:
                    for i in range(1, 10):
                        if i == 5:
                            continue
                        if not self.nearPiece('p', move[0], i) and (move[1] == i):
                            self.move(move[0], move[1])
                            return
            for move in playerMoves:
                    if move[1] == 5:
                        continue
                    if not self.nearPiece('p', move[0], move[1]):
                        self.move(move[0], move[1])
                        return

game = Game()
while game.rounds < 50:
    game.currentGame = []
    print(game.rounds)
    game.start()
    while game.gaming:
        game.defense()
