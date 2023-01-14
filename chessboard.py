from ast import Delete
from lzma import is_check_supported
from operator import length_hint
from PIL import ImageTk, Image
import tkinter as tk
import chess
from itertools import cycle

alpha = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
revAlpha = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

ai = False


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
        self.pieceMap = mapFen(startingFEN)
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
        self.drawLogs("")

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

    def squareToCoord(self, square):
        return (int(revAlpha[square[0]]), int(square[1]) - 1)

    def coordToSquare(self, coord):
        return f"{alpha[coord[0]]}{coord[1] + 1}"

    def drawLogs(self, text):
        self.logs.config(state="normal")
        self.logs.insert(tk.END, text)
        self.logs.config(state="disabled")
        self.logs.pack()

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

    # Handle player move input
    def select(self, event, i, j):  # sourcery skip: extract-method

        # If selected tile is not a piece, checks if it is a valid move
        if (i, j) in self.validMoves.values():
            # Generate uci notation of move
            curMove = self.coordToSquare(self.selected) + self.coordToSquare(
                (i, j))

            # Check for possible promotions, if possible, promote to queen
            if (chess.Move.from_uci(f"{curMove}q")) in self.validMoves:
                curMove = chess.Move.from_uci(f"{curMove}q")
            else:
                curMove = chess.Move.from_uci(curMove)

            # Assign turn variable for easier access
            #turn = f"{'White' if self.pyBoard.turn else 'Black'}"
            turn = self.pyBoard.turn

            # Display moves in log window
            if turn:
                self.drawLogs(f"  {self.pyBoard.san(curMove)}")
            else:
                moveSan = self.pyBoard.san(curMove)
                self.drawLogs(f"{' ' * (10 - len(moveSan))}{moveSan}")

            # Push move to engine
            self.pyBoard.push(curMove)
            # Clear stored move variables
            self.selected = None
            self.validMoves = {}
            # Update board visual data
            self.update(self.pyBoard.fen())
            # Checkmate message
            if self.pyBoard.is_checkmate():
                self.drawLogs(
                    f"\nGAME OVER: Checkmate by {'Black' if turn else 'White'}."
                )
            elif self.pyBoard.is_stalemate():
                self.drawLogs("\nGAME OVER: Stalemate")
        # If selected tile is a piece, generates its valid moves
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


board = ChessBoard()
board.drawboard()
board.mainloop()