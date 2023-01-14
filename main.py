import chess

alpha = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h'}
revAlpha = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

board = chess.Board()

moveCounter = 1
""" while True:
    print(
        f"Move {moveCounter}: {'White to move' if ((moveCounter % 2) == 1) else 'Black to move'}"
    )
    print(board)
    if board.is_checkmate():
        print(f"{'Black wins' if ((moveCounter % 2) == 1) else 'White wins'}")
        break
    moveFrom = input("move from: ")
    moveTo = input("move to: ")
    move = chess.Move.from_uci(moveFrom + moveTo)
    print(moveFrom)
    if move in list(
            board.generate_legal_moves(
                from_mask=(chess.BB_SQUARES[chess.parse_square(moveFrom)]))):
        board.push(move)
        moveCounter += 1 """


def squareToCoord(square):
    return (int(revAlpha[square[0]]), int(square[1]) - 1)


print(squareToCoord('a2'))


def coordToSquare(coord):
    return f"{alpha[coord[0]]}{coord[1]}"
