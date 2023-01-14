""" 
# Create board map from FEN
def mapFen(fen):
    boardFen = [fen]
    splitBoard = boardFen[0].split('/')
    finalBoard = []
    for row in splitBoard:
        if row[0] == '8':
            finalBoard.append(['-'] * 8)
        else:
            boardRow = [row[i] for i in range(len(row))]
            finalBoard.append(boardRow)
    return list(finalBoard)


print(mapFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")) """


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


for row in mapFen(
        "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq - 0 1"):
    print(row)