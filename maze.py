import random
def gridDimensions():
    row, col = 15, 15
    spacing = 100
    zcoord = 0
    return (row, col, spacing, zcoord)

def makePointGrid():
    numRow, numCol,  spacing, zcoord = gridDimensions()
    ptGrid = []
    for row in range(numRow): 
            ptGrid += [[0]*numCol]
    ptGrid = fillGrid(ptGrid, spacing, zcoord)
    return ptGrid

def fillGrid(ptGrid, spacing, zcoord):
    for row in range(len(ptGrid)):
        for col in range(len(ptGrid[row])):
            ptGrid[row][col] = (col*spacing, (len(ptGrid[row])-1-row)*spacing, zcoord)
    return ptGrid

def makeMaze():
    numRow, numCol, spacing, zcoord = gridDimensions()
    boarders = 2
    cells = [[[1 for elem in range(boarders)] 
        for col in range(numCol)]
        for row in range(numRow)]
    lst = makeLst(numRow, numCol)
    cells = fill(cells, lst, [], [])
    cells = boarder(cells)
    return cells

def boarder(cells):
    for row in range(len(cells)):
        for col in range(len(cells[row])):
            #walls going in order: (right, down)
            if row == 0:
                cells[row][col][0] = 1
            if col == 0:
                cells[row][col][1] = 1
            if col == len(cells[row])-1:
                cells[row][col][0] = 0
            if row == len(cells)-1:
                cells[row][col][1] = 0
                if (row, col) != (len(cells)-1, len(cells[0])-1):
                    cells[row][col][0] = 1
    return cells

def makeLst(numRow, numCol):
    lst = []
    for row in range(numRow-1):
        lst += [[0]*(numCol-1)]

    for row in range(len(lst)):
        for col in range(len(lst[row])):
            lst[row][col] = (row, col)
    return lst

def  fill(cells, lst, mazeLst, optionsLst, depth = 0):
        if mazeLst == []:
            row = random.randint(0,len(lst)-1)
            col = random.randint(0,len(lst[row])-1)
            #choose a random cell in the grid and add to mazeLst
            pt = lst[row][col]
        elif optionsLst == []:
            return cells
        else: 
            index = random.randint(0, len(optionsLst)-1)
            pt = optionsLst[index]
            optionsLst.pop(index)
        mazeLst += [pt]
        dtns = {'n':(-1,0), 's':(1,0), 'e':(0,1), 'w':(0,-1)}
        count = 0
        neighbor = []
        for dirc in dtns: 
                #find all neighbor cells that are in bounds
                newRow = dtns[dirc][0] + pt[0]
                newCol = dtns[dirc][1] + pt[1]
                if newRow >= 0 and newRow < len(cells)\
                    and newCol >= 0 and newCol < len(cells[0]):
                    if (newRow, newCol) not in optionsLst and (newRow, newCol) not in mazeLst \
                        and newRow != len(cells)-1 and newCol != len(cells[0])-1:
                        optionsLst += [(newRow, newCol)]
                    if (newRow, newCol) in mazeLst:
                        neighbor += [dirc]
                        count += 1
        if count > 0:
            #get rid of the connecting wall
            if neighbor[0] == 'n':
                cells[pt[0]][pt[1]][0] = 0
            if neighbor[0] == 's':
                cells[pt[0]+1][pt[1]][0] = 0
            if neighbor[0] == 'e':
                cells[pt[0]][pt[1]+1][1] = 0
            if neighbor[0] == 'w':
                cells[pt[0]][pt[1]][1] = 0
        result = fill(cells, lst, mazeLst, optionsLst, depth +1)
        return result









    

