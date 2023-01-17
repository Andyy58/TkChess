from concurrent import futures
from typing import assert_type
from PIL import ImageTk, Image
import tkinter as tk
import chess
from itertools import cycle
from stockfish import Stockfish

thread_pool_executor = futures.ThreadPoolExecutor(max_workers=1)

stockfish = Stockfish(path="./stockfish-engine",
                      parameters={"UCI_LimitStrength": "true"})
stockfish.set_elo_rating(100)
stockfish.set_skill_level(1)

alpha = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
revAlpha = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

computer = True


def mapFen(fen):
    boardFen = [fen.split(" ")[0]]
    splitBoard = boardFen[0].split('/')
    finalBoard = []

    for row in splitBoard:
        newRow = []
        for tile in row:
            if tile.isdigit():
                newRow.extend(['-'] * int(tile))
            else:
                newRow.append(tile)
        finalBoard.append(newRow)
    return list(finalBoard)


class ChessBoard(tk.Tk):
    colours = ["grey", "white"]  #square colours dark then light

    def __init__(self,
                 tileCount=8,
                 startingFEN="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"):
        super().__init__()
        self.state = 'wait'
        self.tileCount = tileCount
        self.leftframe = tk.Frame(self)
        self.leftframe.grid(row=0, column=0, rowspan=10, padx=20)
        self.middleframe = tk.Frame(self)
        self.middleframe.grid(row=0, column=8, rowspan=8)
        self.canvas = tk.Canvas(
            self,
            width=1200,
            height=768,
        )
        self.canvas.grid(row=0, column=1, columnspan=8, rowspan=8)
        self.pyBoard = chess.Board()
        # Move logs and messages
        self.logs = tk.Text(self.leftframe,
                            bg="lightgrey",
                            relief=tk.SUNKEN,
                            width=40,
                            height=40)
        self.restartButton = tk.Button(self.leftframe,
                                       text="Restart",
                                       command=self.restartGame)
        self.computerPlayButton = tk.Button(self.leftframe,
                                            text="Computer play",
                                            command=self.computerPlay)
        self.defaultFEN = startingFEN
        self.pieceMap = mapFen(self.defaultFEN)
        self.selected = None
        self.validMoves = {}
        self.pieceData = {
            'b': tk.PhotoImage(file='./chesspieces/b.png'),
            'k': tk.PhotoImage(file='./chesspieces/k.png'),
            'n': tk.PhotoImage(file='./chesspieces/n.png'),
            'p': tk.PhotoImage(file='./chesspieces/p.png'),
            'q': tk.PhotoImage(file='./chesspieces/q.png'),
            'r': tk.PhotoImage(file='./chesspieces/r.png'),
            'B': tk.PhotoImage(file='./chesspieces/wb.png'),
            'K': tk.PhotoImage(file='./chesspieces/wk.png'),
            'N': tk.PhotoImage(file='./chesspieces/wn.png'),
            'P': tk.PhotoImage(file='./chesspieces/wp.png'),
            'Q': tk.PhotoImage(file='./chesspieces/wq.png'),
            'R': tk.PhotoImage(file='./chesspieces/wr.png')
        }
        self.TRects = []
        self.computerPlayButton.pack()
        self.drawLogs("")
        self.restartButton.pack()

    def create_rectangle(self, x1, y1, x2, y2, tags="", **kwargs):
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            fill = self.winfo_rgb(fill) + (alpha, )
            image = Image.new('RGBA', (x2 - x1, y2 - y1), fill)
            self.TRects.append(ImageTk.PhotoImage(image))
            self.canvas.create_image(x1,
                                     y1,
                                     image=self.TRects[-1],
                                     tags=tags,
                                     anchor='nw')
        self.canvas.create_rectangle(x1, y1, x2, y2, **kwargs)

    def drawLogs(self, text):
        self.logs.config(state="normal")
        self.logs.insert(tk.END, text)
        self.logs.config(state="disabled")
        self.logs.pack()

    def squareToCoord(self, square):
        return (int(revAlpha[square[0]]), int(square[1]) - 1)

    def coordToSquare(self, coord):
        return f"{alpha[coord[0]]}{coord[1] + 1}"

    def restartGame(self):
        self.pyBoard.reset()
        self.pieceMap = mapFen(self.defaultFEN)
        self.selected = None
        self.validMoves = {}
        self.logs.config(state="normal")
        self.logs.delete(0.0, tk.END)
        self.logs.config(state="disabled")
        self.drawboard()

    def update(self, fen):
        self.pieceMap = mapFen(fen)

    def drawboard(self):
        self.canvas.delete('all')

        for currentRow, rowPieces in enumerate(self.pieceMap):
            row = 7 - currentRow
            color = cycle(self.colours if row % 2 else self.colours[::-1])
            for col, piece in enumerate(rowPieces):
                x1 = col * 90
                y1 = (7 - row) * 90
                x2 = x1 + 90
                y2 = y1 + 90
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=next(color))

                if (col, row) in self.validMoves.values():
                    self.create_rectangle(x1,
                                          y1,
                                          x2,
                                          y2,
                                          fill='yellow',
                                          tags=f"tile{col+1}{row+1}",
                                          alpha=0.5)

                if piece != '-':
                    if self.pyBoard.is_check() and (
                        (piece == 'K' and self.pyBoard.turn) or
                        (piece == 'k' and not self.pyBoard.turn)):
                        self.create_rectangle(x1,
                                              y1,
                                              x2,
                                              y2,
                                              fill='red',
                                              alpha=0.5)
                    self.canvas.create_image(x1 + 45,
                                             y1 + 45,
                                             image=self.pieceData[piece],
                                             tags=f"tile{col+1}{row+1}",
                                             anchor=tk.CENTER)
                self.canvas.tag_bind(
                    f"tile{col+1}{row+1}",
                    "<Button-1>",
                    lambda e, i=col, j=row: self.select(e, i, j))

    def computerPlay(self):
        if computer and not self.pyBoard.turn:
            stockfish.set_fen_position(self.pyBoard.fen())
            computerMove = stockfish.get_best_move()
            self.pushMove(chess.Move.from_uci(computerMove))
            self.drawboard()

    def pushMove(self, move):
        moveSan = self.pyBoard.san(move)
        if self.pyBoard.turn:
            self.drawLogs(
                f"{self.pyBoard.fullmove_number}  {self.pyBoard.san(move)} {' ' * (10 - len(moveSan))}"
            )
        else:
            self.drawLogs(f"{moveSan} \n")
        # Push move to engine
        self.pyBoard.push(move)
        # Clear stored move variables
        self.selected = None
        self.validMoves = {}
        # Update board visual data
        self.update(self.pyBoard.fen())
        # Checkmate message
        if self.pyBoard.is_checkmate():
            self.drawLogs(
                f"\nGAME OVER: Checkmate by {'Black' if self.pyBoard.turn else 'White'}."
            )
        elif self.pyBoard.is_stalemate():
            self.drawLogs("\nGAME OVER: Stalemate")

    # Handle player move input
    def select(self, event, i, j):  # sourcery skip: extract-method
        # Assign turn variable for easier access
        turn = self.pyBoard.turn
        if not computer or turn:
            if (i, j) in self.validMoves.values():
                # Generate uci notation of move
                curMove = self.coordToSquare(
                    self.selected) + self.coordToSquare((i, j))

                # Check for possible promotions, if possible, promote to queen
                curMove = (chess.Move.from_uci(f"{curMove}q") if
                           (chess.Move.from_uci(f"{curMove}q"))
                           in self.validMoves else
                           chess.Move.from_uci(curMove))
                # Logs moves in window
                self.pushMove(curMove)
            else:
                self.selected = (i, j)
                selected = self.coordToSquare(self.selected)
                self.validMoves = {
                    a: self.squareToCoord(str(a)[2:4])
                    for a in list(
                        self.pyBoard.generate_legal_moves(from_mask=(
                            chess.BB_SQUARES[chess.parse_square(selected)])))
                }

        # Draw new board
        self.drawboard()
        #self.drawboard()
        #self.computerPlay()
        print('draw')


board = ChessBoard()
# Tests
assert (board.coordToSquare((0, 0)) == 'a1')
assert (board.coordToSquare((7, 7)) == 'h8')
assert (board.squareToCoord('a1') == (0, 0))
assert (board.squareToCoord('h8') == (7, 7))
assert_type(board.pieceMap, list)
assert_type(board.pieceMap[0], list)
assert_type(board.pieceMap[0][0], str)
assert (board.pieceMap[7][2] == 'B')

board.drawboard()
board.mainloop()