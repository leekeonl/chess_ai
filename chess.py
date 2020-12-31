import pygame 
from pygame.locals import * 
import copy 
import pickle 
import random 
from collections import defaultdict 
from collections import Counter 
import threading 
import os 


#The Setting 
class ChessMove:
    
    def __init__(self, board, player, castling, pawndiagonal, halfmove, history ={}):
        self.board = board
        self.player = player
        self.castling = castling
        self.pawndiagonal = pawndiagonal
        self.halfmove = halfmove
        self.history = history
        
        
    def getboard(self):
        return self.board
    
    def setboard(self,board):
        self.board = board
        
    def getplayer(self):
        return self.player
    
    def setplayer(self,player):
        self.player = player
    
    def getcastling(self):
        return self.castling
    
    def setcastling(self,castling):
        self.castling = castling
    
    def getpawndiagonal(self):
        return self.pawndiagonal
    
    def setpawndiagonal(self, pawndiagonal):
        self.pawndiagonal = pawndiagonal
    
    def gethalfmove(self):
        return self.halfmove
    
    def sethalfmove(self, halfmove):
        self.halfmove = halfmove
    
    def checkRepetition(self):
        return any(value>=3 for value in self.history.itervalues())

    def gethistory(self):
        return self.history
    
    def addhistory(self,position):
        key = poskey(position)
        self.history[key] = self.history.get(key,0)+1
    
    def ChessMoveCopy(self):
        
        Copy = ChessMove(copy.deepcopy(self.board), self.player, copy.deepcopy(self.castling), self.pawndiagonal, self.halfmove)
    
        return Copy

#Shade of the piece
class Shades:
    
    def __init__(self,image,coord):
        self.image = image
        self.pos = coord
        
    def getInfo(self):
        return [self.image,self.pos]

#Display piece with GUI
class Piece:
    
    def __init__(self,pieceinfo,chess_coord):
        
        piece = pieceinfo[0]
        color = pieceinfo[1]
        
        if piece=='K':
            index = 0
        elif piece=='Q':
            index = 1
        elif piece=='B':
            index = 2
        elif piece == 'N':
            index = 3
        elif piece == 'R':
            index = 4
        elif piece == 'P':
            index = 5
        
        left_x = square_width*index
        
        if color == 'w':
            left_y = 0
        else:
            left_y = square_height
        
        self.pieceinfo = pieceinfo
        
        self.subsection = (left_x,left_y,square_width,square_height)
        self.chess_coord = chess_coord
        self.pos = (-1,-1)

    def getInfo(self):
        return [self.chess_coord, self.subsection,self.pos]
    
    def setpos(self,pos):
        self.pos = pos
        
    def getpos(self):
        return self.pos
    
    def setcoord(self,coord):
        self.chess_coord = coord
        
    def __repr__(self):
        return self.pieceinfo+'('+str(chess_coord[0])+','+str(chess_coord[1])+')'
    
#Gaming function for game such as move or restrictions for each pieces.

def printboard(board):
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == 0:
                board[i][j] == 'O'
            print(board)
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j]=='O':
                board[i][j] = 0

def Exist(board,x,y):
    #Check Empty
    if board[y][x] == 0:
        return False
    return True

def ExistPiece(board,x,y,color):
    #Check Empty
    if board[y][x] == 0:
        return False
    if board[y][x][1] == color[0]:
        return True
    return False

def filterbycolor(board,tuple_list,color):
    filtered_list = []
    for pos in tuple_list:
        x = pos[0]
        y = pos[1]
        if x>=0 and x<=7 and y>=0 and y<=7 and not ExistPiece(board,x,y,color):
            filtered_list.append(pos)
    return filtered_list

def find(board,piece):
    location_list = []
    for row in range(8):
        for col in range(8):
            if board[row][col] == piece:
                x = col
                y = row
                location_list.append((x,y))
    return location_list

def attacked(position,target_x,target_y,color):
    board = position.getboard()
    color = color[0]
    attack_list = []
    for x in range(8):
        for y in range(8):
            if board[y][x]!=0 and board[y][x][1]==color:
                attack_list.extend(possible_moves(position,x,y,True))
    return (target_x,target_y) in attack_list

def possible_moves(position,x,y,AttackSearch=False):
    
    board = position.getboard()
    player = position.getplayer()
    castling = position.getcastling()
    pawndiagonal = position.getpawndiagonal()
    
    if len(board[y][x])!=2: 
        return [] 
    piece = board[y][x][0] 
    color = board[y][x][1] 
    enemy_color = opposite(color)
    tuple_list = [] 
    
    if piece == 'P': 
        if color=='w': 
            if not Exist(board,x,y-1) and not AttackSearch:
                tuple_list.append((x,y-1))
                
                if y == 6 and not Exist(board,x,y-2):
                    tuple_list.append((x,y-2))
            
            if x!=0 and ExistPiece(board,x-1,y-1,'black'):
                tuple_list.append((x-1,y-1))
                
            if x!=7 and ExistPiece(board,x+1,y-1,'black'):
                tuple_list.append((x+1,y-1))
                
            if pawndiagonal!=-1: 
                if pawndiagonal == (x-1,y-1) or pawndiagonal == (x+1,y-1):
                    tuple_list.append(pawndiagonal)
        elif color=='b': 
            if not Exist(board,x,y+1) and not AttackSearch:
                tuple_list.append((x,y+1))
                if y == 1 and not Exist(board,x,y+2):
                    tuple_list.append((x,y+2))
            if x!=0 and ExistPiece(board,x-1,y+1,'white'):
                tuple_list.append((x-1,y+1))
            if x!=7 and ExistPiece(board,x+1,y+1,'white'):
                tuple_list.append((x+1,y+1))
            if pawndiagonal == (x-1,y+1) or pawndiagonal == (x+1,y+1):
                tuple_list.append(pawndiagonal)
        
    elif piece == 'R': 
        for i in [-1,1]:
            kx = x 
            while True: 
                kx = kx + i 
                if kx<=7 and kx>=0: 
                    if not Exist(board,kx,y):
                        tuple_list.append((kx,y))
                    else:
                        if ExistPiece(board,kx,y,enemy_color):
                            tuple_list.append((kx,y))
                        break  
                else: 
                    break
        for i in [-1,1]:
            ky = y
            while True:
                ky = ky + i 
                if ky<=7 and ky>=0: 
                    if not Exist(board,x,ky):
                        tuple_list.append((x,ky))
                    else:
                        if ExistPiece(board,x,ky,enemy_color):
                            tuple_list.append((x,ky))
                        break
                else:
                    break
        
    elif piece == 'N': 
        for dx in [-2,-1,1,2]:
            if abs(dx)==1:
                sy = 2
            else:
                sy = 1
            for dy in [-sy,+sy]:
                tuple_list.append((x+dx,y+dy))
        tuple_list = filterbycolor(board,tuple_list,color)
        
    elif piece == 'B':
        for dx in [-1,1]: 
            for dy in [-1,1]: 
                kx = x 
                ky = y
                while True: 
                    kx = kx + dx 
                    ky = ky + dy 
                    if kx<=7 and kx>=0 and ky<=7 and ky>=0:
                        if not Exist(board,kx,ky):
                            tuple_list.append((kx,ky))
                        else:
                            if ExistPiece(board,kx,ky,enemy_color):
                                tuple_list.append((kx,ky))
                            break    
                    else:
                        break
    
    elif piece == 'Q': 
        board[y][x] = 'R' + color
        list_rook = possible_moves(position,x,y,True)
        board[y][x] = 'B' + color
        list_bishop = possible_moves(position,x,y,True)
        tuple_list = list_rook + list_bishop
        board[y][x] = 'Q' + color
        
    elif piece == 'K': 
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                tuple_list.append((x+dx,y+dy))
        tuple_list = filterbycolor(board,tuple_list,color)
        if not AttackSearch:
            right = castling[player]
            
            #Kingside
            if (right[0] and board[y][7][0]=='R' and not Exist(board,x+1,y) and not Exist(board,x+2,y) and 
            not attacked(position,x,y,enemy_color) and not attacked(position,x+1,y,enemy_color) and not attacked(position,x+2,y,enemy_color)):
                tuple_list.append((x+2,y))
                
            #Queenside
            if (right[1] and board[y][0][0]=='R' and not Exist(board,x-1,y)and not Exist(board,x-2,y)and not Exist(board,x-3,y) and not attacked(position,x,y,enemy_color) and not attacked(position,x-1,y,enemy_color) and not attacked(position,x-2,y,enemy_color)):
                tuple_list.append((x-2,y)) 
                
    #Make sure the king is not under attack as a result of this move:
    if not AttackSearch:
        new_list = []
        for tupleq in tuple_list:
            x2 = tupleq[0]
            y2 = tupleq[1]
            temp_pos = position.ChessMoveCopy()
            makemove(temp_pos,x,y,x2,y2)
            if not isCheck(temp_pos,color):
                new_list.append(tupleq)
        tuple_list = new_list
    return tuple_list

def makemove(position,x,y,x2,y2):
    board = position.getboard()
    piece = board[y][x][0]
    color = board[y][x][1]
    
    player = position.getplayer()
    castling = position.getcastling()
    pawndiagonal = position.getpawndiagonal()
    halfmove = position.gethalfmove()

    if Exist(board,x2,y2) or piece=='P':
        halfmove = 0
    else:
        halfmove += 1

    #Make the move:
    board[y2][x2] = board[y][x]
    board[y][x] = 0
    
    #Special piece requirements:
    #King:
    if piece == 'K':
        castling[player] = [False,False]
        if abs(x2-x) == 2:
            if color=='w':
                l = 7
            else:
                l = 0
            
            if x2>x:
                    board[l][5] = 'R'+color
                    board[l][7] = 0
            else:
                    board[l][3] = 'R'+color
                    board[l][0] = 0
    #Rook:
    if piece=='R':
        if x==0 and y==0:
            castling[1][1] = False
        elif x==7 and y==0:
            castling[1][0] = False
        elif x==0 and y==7:
            castling[0][1] = False
        elif x==7 and y==7:
            castling[0][0] = False
    #Pawn:
    if piece == 'P':
        if pawndiagonal == (x2,y2):
            if color=='w':
                board[y2+1][x2] = 0
            else:
                board[y2-1][x2] = 0
        if abs(y2-y)==2:
            pawndiagonal = (x,(y+y2)/2)
        else:
            pawndiagonal = -1

        if y2==0:
            board[y2][x2] = 'Qw'
        elif y2 == 7:
            board[y2][x2] = 'Qb'
            
    else:
        pawndiagonal = -1

    player = 1 - player       
    position.setplayer(player)
    position.setcastling(castling)
    position.setpawndiagonal(pawndiagonal)
    position.sethalfmove(halfmove)
    
def opposite(color):
    color = color[0]
    if color == 'w':
        oppcolor = 'b'
    else:
        oppcolor = 'w'
    return oppcolor

def isCheck(position,color):
    board = position.getboard()
    color = color[0]
    enemy = opposite(color)
    piece = 'K' + color
    x,y = find(board,piece)[0]
    return attacked(position,x,y,enemy)

def isCheckmate(position,color=-1):
    
    if color==-1:
        return isCheckmate(position,'white') or isCheckmate(position,'b')
    color = color[0]
    if isCheck(position,color) and allMoves(position,color)==[]:
            return True
    return False

def isStalemate(position):
    player = position.getplayer()
    if player==0:
        color = 'w'
    else:
        color = 'b'
    if not isCheck(position,color) and allMoves(position,color)==[]:
        return True
    return False

def getallpieces(position,color):
    board = position.getboard()
    listofpos = []
    for j in range(8):
        for i in range(8):
            if ExistPiece(board,i,j,color):
                listofpos.append((i,j))
    return listofpos

def allMoves(position, color):
    if color==1:
        color = 'white'
    elif color ==-1:
        color = 'black'
    color = color[0]
    listofpieces = getallpieces(position,color)
    moves = []
    for pos in listofpieces:
        targets = possible_moves(position,pos[0],pos[1])
        for target in targets:
             moves.append([pos,target])
    return moves

def poskey(position):
    board = position.getboard()
    boardTuple = []
    for row in board:
        boardTuple.append(tuple(row))
    boardTuple = tuple(boardTuple)
    rights = position.getcastling()
    tuplerights = (tuple(rights[0]),tuple(rights[1]))
    key = (boardTuple,position.getplayer(), tuplerights)
    return key










#GUI Functions that shows visual for user interface
def chess_coord_to_pixels(chess_coord):
    x,y = chess_coord

    if isAI:
        if AIPlayer==0:
            return ((7-x)*square_width, (7-y)*square_height)
        else:
            return (x*square_width, y*square_height)

    if not isFlip or player==0 ^ isTransition:
        return (x*square_width, y*square_height)
    else:
        return ((7-x)*square_width, (7-y)*square_height)
    
def pixel_coord_to_chess(pixel_coord):
    x,y = pixel_coord[0]/square_width, pixel_coord[1]/square_height
    if isAI:
        if AIPlayer==0:
            return (7-x,7-y)
        else:
            return (x,y)
    if not isFlip or player==0 ^ isTransition:
        return (x,y)
    else:
        return (7-x,7-y)
    
def getPiece(chess_coord):
    for piece in listofWhitePieces+listofBlackPieces:
        if piece.getInfo()[0] == chess_coord:
            return piece
        
def createPieces(board):
    listofWhitePieces = []
    listofBlackPieces = []
    for i in range(8):
        for k in range(8):
            if board[i][k]!=0:
                p = Piece(board[i][k],(k,i))
                if board[i][k][1]=='w':
                    listofWhitePieces.append(p)
                else:
                    listofBlackPieces.append(p)
    return [listofWhitePieces,listofBlackPieces]

def createShades(tuple_list):
    global listofShades

    listofShades = []
    if isTransition:

        return
    
    if isDraw:

        coord = find(board,'Kw')[0]
        shade = Shades(circle_image_yellow,coord)
        listofShades.append(shade)
        coord = find(board,'Kb')[0]
        shade = Shades(circle_image_yellow,coord)
        listofShades.append(shade)

        return
    
    if chessEnded:
        coord = find(board,'K'+winner)[0]
        shade = Shades(circle_image_green_big,coord)
        listofShades.append(shade)
        
    if isCheck(position,'white'):
        coord = find(board,'Kw')[0]
        shade = Shades(circle_image_red,coord)
        listofShades.append(shade)
        
    if isCheck(position,'black'):
        coord = find(board,'Kb')[0]
        shade = Shades(circle_image_red,coord)
        listofShades.append(shade)
        
    for pos in tuple_list:

        if Exist(board,pos[0],pos[1]):
            img = circle_image_capture
        else:
            img = circle_image_green
        shade = Shades(img,pos)

        listofShades.append(shade)
        
def drawBoard():

    screen.blit(background,(0,0))

    if player==1:
        order = [listofWhitePieces,listofBlackPieces]
    else:
        order = [listofBlackPieces,listofWhitePieces]
    if isTransition:

        order = list(reversed(order))

    if isDraw or chessEnded or isAIThink:

        for shade in listofShades:
            img,chess_coord = shade.getInfo()
            pixel_coord = chess_coord_to_pixels(chess_coord)
            screen.blit(img,pixel_coord)

    if prevMove[0]!=-1 and not isTransition:
        x,y,x2,y2 = prevMove
        screen.blit(yellowbox_image,chess_coord_to_pixels((x,y)))
        screen.blit(yellowbox_image,chess_coord_to_pixels((x2,y2)))

    for piece in order[0]:
        
        chess_coord,subsection,pos = piece.getInfo()
        pixel_coord = chess_coord_to_pixels(chess_coord)
        if pos==(-1,-1):
            screen.blit(pieces_image,pixel_coord,subsection)
        else:
            screen.blit(pieces_image,pos,subsection)

    if not (isDraw or chessEnded or isAIThink):
        for shade in listofShades:
            img,chess_coord = shade.getInfo()
            pixel_coord = chess_coord_to_pixels(chess_coord)
            screen.blit(img,pixel_coord)
    for piece in order[1]:
        chess_coord,subsection,pos = piece.getInfo()
        pixel_coord = chess_coord_to_pixels(chess_coord)
        if pos==(-1,-1):
            screen.blit(pieces_image,pixel_coord,subsection)
        else:
            screen.blit(pieces_image,pos,subsection)






#AI functions that helps to do user vs computer

def negamax(position,depth,alpha,beta,colorsign,bestMoveReturn,root=True):
    if root:
        key = poskey(position)
        if key in openings:
            bestMoveReturn[:] = random.choice(openings[key])
            return
    global searched
    if depth==0:
        return colorsign*evaluate(position)
    moves = allMoves(position, colorsign)
    if moves==[]:
        return colorsign*evaluate(position)
    if root:
        bestMove = moves[0]
    bestValue = -100000
    
    for move in moves:
        newpos = position.ChessMoveCopy()
        makemove(newpos,move[0][0],move[0][1],move[1][0],move[1][1])
        key = poskey(newpos)

        if key in searched:
            value = searched[key]
        else:
            value = -negamax(newpos,depth-1, -beta,-alpha,-colorsign,[],False)
            searched[key] = value
        if value>bestValue:
            bestValue = value
            if root:
                bestMove = move
        alpha = max(alpha,value)
        if alpha>=beta:
            break

    if root:
        searched = {}
        bestMoveReturn[:] = bestMove
        return
    return bestValue

def evaluate(position):
    if isCheckmate(position,'white'):
        return -20000
    if isCheckmate(position,'black'):
        return 20000
    #Get the board:
    board = position.getboard()

    flatboard = [x for row in board for x in row]

    c = Counter(flatboard)
    Qw = c['Qw']
    Qb = c['Qb']
    Rw = c['Rw']
    Rb = c['Rb']
    Bw = c['Bw']
    Bb = c['Bb']
    Nw = c['Nw']
    Nb = c['Nb']
    Pw = c['Pw']
    Pb = c['Pb']

    whiteMaterial = 9*Qw + 5*Rw + 3*Nw + 3*Bw + 1*Pw
    blackMaterial = 9*Qb + 5*Rb + 3*Nb + 3*Bb + 1*Pb
    numofmoves = len(position.gethistory())
    gamephase = 'opening'
    if numofmoves>40 or (whiteMaterial<14 and blackMaterial<14):
        gamephase = 'ending'

    Dw = doubledPawns(board,'white')
    Db = doubledPawns(board,'black')
    Sw = blockedPawns(board,'white')
    Sb = blockedPawns(board,'black')
    Iw = isolatedPawns(board,'white')
    Ib = isolatedPawns(board,'black')

    evaluation1 = 900*(Qw - Qb) + 500*(Rw - Rb) +330*(Bw-Bb)+320*(Nw - Nb) +100*(Pw - Pb) +-30*(Dw-Db + Sw-Sb + Iw- Ib)

    evaluation2 = pieceSquareTable(flatboard,gamephase)

    evaluation = evaluation1 + evaluation2

    return evaluation

def pieceSquareTable(flatboard,gamephase):

    score = 0

    for i in range(64):
        if flatboard[i]==0:

            continue

        piece = flatboard[i][0]
        color = flatboard[i][1]
        sign = +1

        if color=='b':
            i = (7-i/8)*8 + i%8
            sign = -1
        #Adjust score:
        if piece=='P':
            score += sign*pawn_table[i]
        elif piece=='N':
            score+= sign*knight_table[i]
        elif piece=='B':
            score+=sign*bishop_table[i]
        elif piece=='R':
            score+=sign*rook_table[i]
        elif piece=='Q':
            score+=sign*queen_table[i]
        elif piece=='K':
            if gamephase=='opening':
                score+=sign*king_table[i]
            else:
                score+=sign*king_endgame_table[i]
    return score  

def doubledPawns(board,color):
    color = color[0]

    listofpawns = find(board,'P'+color)

    repeats = 0
    temp = []
    for pawnpos in listofpawns:
        if pawnpos[0] in temp:
            repeats = repeats + 1
        else:
            temp.append(pawnpos[0])
    return repeats

def blockedPawns(board,color):
    color = color[0]
    listofpawns = find(board,'P'+color)
    blocked = 0
    for pawnpos in listofpawns:
        if ((color=='w' and ExistPiece(board,pawnpos[0],pawnpos[1]-1,'black')) or (color=='b' and ExistPiece(board,pawnpos[0],pawnpos[1]+1, 'white'))):
            blocked = blocked + 1
    return blocked

def isolatedPawns(board,color):
    color = color[0]
    listofpawns = find(board,'P'+color)

    xlist = [x for (x,y) in listofpawns]
    isolated = 0
    for x in xlist:
        if x!=0 and x!=7:

            if x-1 not in xlist and x+1 not in xlist:
                isolated+=1
        elif x==0 and 1 not in xlist:

            isolated+=1
        elif x==7 and 6 not in xlist:

            isolated+=1
    return isolated

#main function

#Initialize the board:
board = [ ['Rb', 'Nb', 'Bb', 'Qb', 'Kb', 'Bb', 'Nb', 'Rb'], #8
          ['Pb', 'Pb', 'Pb', 'Pb', 'Pb', 'Pb', 'Pb', 'Pb'], #7
          [  0,    0,    0,    0,    0,    0,    0,    0],  #6
          [  0,    0,    0,    0,    0,    0,    0,    0],  #5
          [  0,    0,    0,    0,    0,    0,    0,    0],  #4
          [  0,    0,    0,    0,    0,    0,    0,    0],  #3
          ['Pw', 'Pw', 'Pw',  'Pw', 'Pw', 'Pw', 'Pw', 'Pw'], #2
          ['Rw', 'Nw', 'Bw',  'Qw', 'Kw', 'Bw', 'Nw', 'Rw'] ]#1
          # a      b     c     d     e     f     g     h


player = 0 
castling = [[True, True],[True, True]]
pawndiagonal = -1
halfmove = 0 
position = ChessMove(board,player,castling,pawndiagonal ,halfmove)

pawn_table = [  0,  0,  0,  0,  0,  0,  0,  0,
50, 50, 50, 50, 50, 50, 50, 50,
10, 10, 20, 30, 30, 20, 10, 10,
 5,  5, 10, 25, 25, 10,  5,  5,
 0,  0,  0, 20, 20,  0,  0,  0,
 5, -5,-10,  0,  0,-10, -5,  5,
 5, 10, 10,-20,-20, 10, 10,  5,
 0,  0,  0,  0,  0,  0,  0,  0]
knight_table = [-50,-40,-30,-30,-30,-30,-40,-50,
-40,-20,  0,  0,  0,  0,-20,-40,
-30,  0, 10, 15, 15, 10,  0,-30,
-30,  5, 15, 20, 20, 15,  5,-30,
-30,  0, 15, 20, 20, 15,  0,-30,
-30,  5, 10, 15, 15, 10,  5,-30,
-40,-20,  0,  5,  5,  0,-20,-40,
-50,-90,-30,-30,-30,-30,-90,-50]
bishop_table = [-20,-10,-10,-10,-10,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  0,  5, 10, 10,  5,  0,-10,
-10,  5,  5, 10, 10,  5,  5,-10,
-10,  0, 10, 10, 10, 10,  0,-10,
-10, 10, 10, 10, 10, 10, 10,-10,
-10,  5,  0,  0,  0,  0,  5,-10,
-20,-10,-90,-10,-10,-90,-10,-20]
rook_table = [0,  0,  0,  0,  0,  0,  0,  0,
  5, 10, 10, 10, 10, 10, 10,  5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
  0,  0,  0,  5,  5,  0,  0,  0]
queen_table = [-20,-10,-10, -5, -5,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  0,  5,  5,  5,  5,  0,-10,
 -5,  0,  5,  5,  5,  5,  0, -5,
  0,  0,  5,  5,  5,  5,  0, -5,
-10,  5,  5,  5,  5,  5,  0,-10,
-10,  0,  5,  0,  0,  0,  0,-10,
-20,-10,-10, 70, -5,-10,-10,-20]
king_table = [-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-20,-30,-30,-40,-40,-30,-30,-20,
-10,-20,-20,-20,-20,-20,-20,-10,
 20, 20,  0,  0,  0,  0, 20, 20,
 20, 30, 10,  0,  0, 10, 30, 20]
king_endgame_table = [-50,-40,-30,-20,-20,-30,-40,-50,
-30,-20,-10,  0,  0,-10,-20,-30,
-30,-10, 20, 30, 30, 20,-10,-30,
-30,-10, 30, 40, 40, 30,-10,-30,
-30,-10, 30, 40, 40, 30,-10,-30,
-30,-10, 20, 30, 30, 20,-10,-30,
-30,-30,  0,  0,  0,  0,-30,-30,
-50,-30,-30,-30,-30,-30,-30,-50]

#Make the GUI:
#Start pygame
pygame.init()

screen = pygame.display.set_mode((600,600))

background = pygame.image.load(os.path.join('Media','board.png')).convert()


pieces_image = pygame.image.load(os.path.join('Media','Chess_Pieces_Sprite.png')).convert_alpha()
circle_image_green = pygame.image.load(os.path.join('Media','green_circle_small.png')).convert_alpha()
circle_image_capture = pygame.image.load(os.path.join('Media','green_circle_neg.png')).convert_alpha()
circle_image_red = pygame.image.load(os.path.join('Media','red_circle_big.png')).convert_alpha()
greenbox_image = pygame.image.load(os.path.join('Media','green_box.png')).convert_alpha()
circle_image_yellow = pygame.image.load(os.path.join('Media','yellow_circle_big.png')).convert_alpha()
circle_image_green_big = pygame.image.load(os.path.join('Media','green_circle_big.png')).convert_alpha()
yellowbox_image = pygame.image.load(os.path.join('Media','yellow_box.png')).convert_alpha()


withfriend_pic = pygame.image.load(os.path.join('Media','withfriend.png')).convert_alpha()
withAI_pic = pygame.image.load(os.path.join('Media','withAI.png')).convert_alpha()
playwhite_pic = pygame.image.load(os.path.join('Media','playWhite.png')).convert_alpha()
playblack_pic = pygame.image.load(os.path.join('Media','playBlack.png')).convert_alpha()
flipEnabled_pic = pygame.image.load(os.path.join('Media','flipEnabled.png')).convert_alpha()
flipDisabled_pic = pygame.image.load(os.path.join('Media','flipDisabled.png')).convert_alpha()


size_of_bg = background.get_rect().size

square_width = size_of_bg[0]/8
square_height = size_of_bg[1]/8



pieces_image = pygame.transform.scale(pieces_image,(square_width*6,square_height*2))
circle_image_green = pygame.transform.scale(circle_image_green,(square_width, square_height))
circle_image_capture = pygame.transform.scale(circle_image_capture,(square_width, square_height))
circle_image_red = pygame.transform.scale(circle_image_red,(square_width, square_height))
greenbox_image = pygame.transform.scale(greenbox_image,(square_width, square_height))
yellowbox_image = pygame.transform.scale(yellowbox_image,(square_width, square_height))
circle_image_yellow = pygame.transform.scale(circle_image_yellow,(square_width, square_height))
circle_image_green_big = pygame.transform.scale(circle_image_green_big,(square_width, square_height))
withfriend_pic = pygame.transform.scale(withfriend_pic,(square_width*4,square_height*4))
withAI_pic = pygame.transform.scale(withAI_pic,(square_width*4,square_height*4))
playwhite_pic = pygame.transform.scale(playwhite_pic,(square_width*4,square_height*4))
playblack_pic = pygame.transform.scale(playblack_pic,(square_width*4,square_height*4))
flipEnabled_pic = pygame.transform.scale(flipEnabled_pic,(square_width*4,square_height*4))
flipDisabled_pic = pygame.transform.scale(flipDisabled_pic, (square_width*4,square_height*4))


screen = pygame.display.set_mode(size_of_bg)
pygame.display.set_caption('Shallow Green')
screen.blit(background,(0,0))


listofWhitePieces,listofBlackPieces = createPieces(board)

listofShades = []

clock = pygame.time.Clock() 
isDown = False 
isClicked = False 
isTransition = False 
isDraw = False
chessEnded = False 
isRecord = False 
isAIThink = False 
openings = defaultdict(list)

try:
    file_handle = open('openingTable.txt','r+')
    openings = pickle.loads(file_handle.read())
except:
    if isRecord:
        file_handle = open('openingTable.txt','w')

searched = {} 

prevMove = [-1,-1,-1,-1] 
ax,ay=0,0
numm = 0


isMenu = True
isAI = -1
isFlip = -1
AIPlayer = -1

gameEnded = False

#########################INFINITE LOOP#####################################
#The program remains in this loop until the user quits the application
while not gameEnded:
    if isMenu:

        screen.blit(background,(0,0))
        if isAI==-1:
            screen.blit(withfriend_pic,(0,square_height*2))
            screen.blit(withAI_pic,(square_width*4,square_height*2))
            
        elif isAI==True:
            screen.blit(playwhite_pic,(0,square_height*2))
            screen.blit(playblack_pic,(square_width*4,square_height*2))
            
        elif isAI==False:
            screen.blit(flipDisabled_pic,(0,square_height*2))
            screen.blit(flipEnabled_pic,(square_width*4,square_height*2))
        if isFlip!=-1:

            drawBoard()

            isMenu = False

            if isAI and AIPlayer==0:
                colorsign=1
                bestMoveReturn = []
                move_thread = threading.Thread(target = negamax, args = (position,3,-1000000,1000000,colorsign,bestMoveReturn))
                move_thread.start()
                isAIThink = True
            continue
        for event in pygame.event.get():

            if event.type==QUIT:

                gameEnded = True
                break
            if event.type == MOUSEBUTTONUP:

                pos = pygame.mouse.get_pos()

                if (pos[0]<square_width*4 and pos[1]>square_height*2 and pos[1]<square_height*6):

                    if isAI == -1:
                        isAI = False
                    elif isAI==True:
                        AIPlayer = 1
                        isFlip = False
                    elif isAI==False:
                        isFlip = False
                elif (pos[0]>square_width*4 and pos[1]>square_height*2 and pos[1]<square_height*6):

                    if isAI == -1:
                        isAI = True
                    elif isAI==True:
                        AIPlayer = 0
                        isFlip = False
                    elif isAI==False:
                        isFlip=True


        pygame.display.update()


        clock.tick(60)
        continue

    numm+=1
    if isAIThink and numm%6==0:
        ax+=1
        if ax==8:
            ay+=1
            ax=0
        if ay==8:
            ax,ay=0,0
        if ax%4==0:
            createShades([])

        if AIPlayer==0:
            listofShades.append(Shades(greenbox_image,(7-ax,7-ay)))
        else:
            listofShades.append(Shades(greenbox_image,(ax,ay)))
    
    for event in pygame.event.get():

        if event.type==QUIT:
            gameEnded = True
        
            break

        if chessEnded or isTransition or isAIThink:
            continue

        if not isDown and event.type == MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            chess_coord = pixel_coord_to_chess(pos)
            x = chess_coord[0]
            y = chess_coord[1]

            if not ExistPiece(board,x,y,'wb'[player]):
                continue

            dragPiece = getPiece(chess_coord)

            tuple_list = possible_moves(position,x,y)

            createShades(tuple_list)

            if ((dragPiece.pieceinfo[0]=='K') and
                (isCheck(position,'white') or isCheck(position,'black'))):
                None
            else:
                listofShades.append(Shades(greenbox_image,(x,y)))
            isDown = True       
        if (isDown or isClicked) and event.type == MOUSEBUTTONUP:

            isDown = False

            dragPiece.setpos((-1,-1))

            pos = pygame.mouse.get_pos()
            chess_coord = pixel_coord_to_chess(pos)
            x2 = chess_coord[0]
            y2 = chess_coord[1]

            isTransition = False
            if (x,y)==(x2,y2): 

                if not isClicked:

                    isClicked = True
                    prevPos = (x,y) 
                else: 
                    x,y = prevPos
                    if (x,y)==(x2,y2):
                        isClicked = False

                        createShades([])
                    else:

                        if ExistPiece(board,x2,y2,'wb'[player]):
                            isClicked = True
                            prevPos = (x2,y2) 
                        else:

                            isClicked = False
                            #Destory all shades
                            createShades([])
                            isTransition = True 
                            

            if not (x2,y2) in tuple_list:
                #Move was invalid
                isTransition = False
                continue

            if isRecord:
                key = poskey(position)
                if [(x,y),(x2,y2)] not in openings[key]: 
                    openings[key].append([(x,y),(x2,y2)])
                
            #Make the move:
            makemove(position,x,y,x2,y2)
            prevMove = [x,y,x2,y2]

            player = position.getplayer()

            position.addhistory(position)

            halfmove = position.gethalfmove()
            if halfmove>=100 or isStalemate(position) or position.checkRepetition():

                isDraw = True
                chessEnded = True

            if isCheckmate(position,'white'):
                winner = 'b'
                chessEnded = True
            if isCheckmate(position,'black'):
                winner = 'w'
                chessEnded = True

            if isAI and not chessEnded:
                if player==0:
                    colorsign = 1
                else:
                    colorsign = -1
                bestMoveReturn = []
                move_thread = threading.Thread(target = negamax, args = (position,3,-1000000,1000000,colorsign,bestMoveReturn))
                move_thread.start()
                isAIThink = True
            #Move the piece to its new destination:
            dragPiece.setcoord((x2,y2))
            if not isTransition:
                listofWhitePieces,listofBlackPieces = createPieces(board)
            else:
                movingPiece = dragPiece
                origin = chess_coord_to_pixels((x,y))
                destiny = chess_coord_to_pixels((x2,y2))
                movingPiece.setpos(origin)
                step = (destiny[0]-origin[0],destiny[1]-origin[1])
            

            createShades([])

    if isTransition:
        p,q = movingPiece.getpos()
        dx2,dy2 = destiny
        n= 30.0
        if abs(p-dx2)<=abs(step[0]/n) and abs(q-dy2)<=abs(step[1]/n):

            movingPiece.setpos((-1,-1))
            listofWhitePieces,listofBlackPieces = createPieces(board)
            isTransition = False
            createShades([])
        else:

            movingPiece.setpos((p+step[0]/n,q+step[1]/n))

    if isDown:
        m,k = pygame.mouse.get_pos()
        dragPiece.setpos((m-square_width/2,k-square_height/2))

    if isAIThink and not isTransition:
        if not move_thread.isAlive():
            isAIThink = False
            createShades([])
            [x,y],[x2,y2] = bestMoveReturn
            makemove(position,x,y,x2,y2)
            prevMove = [x,y,x2,y2]
            player = position.getplayer()
            halfmove = position.gethalfmove()
            position.addhistory(position)
            if halfmove>=100 or isStalemate(position) or position.checkRepetition():
                isDraw = True
                chessEnded = True
            if isCheckmate(position,'white'):
                winner = 'b'
                chessEnded = True
            if isCheckmate(position,'black'):
                winner = 'w'
                chessEnded = True

            isTransition = True
            movingPiece = getPiece((x,y))
            origin = chess_coord_to_pixels((x,y))
            destiny = chess_coord_to_pixels((x2,y2))
            movingPiece.setpos(origin)
            step = (destiny[0]-origin[0],destiny[1]-origin[1])

    #Update positions of all images:
    drawBoard()
    #Update the display:
    pygame.display.update()

    #Run at specific fps:
    clock.tick(60)

#Out of loop. Quit pygame:
pygame.quit()

if isRecord:
    file_handle.seek(0)
    pickle.dump(openings,file_handle)
    file_handle.truncate()
    file_handle.close()