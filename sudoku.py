GRID_SIZE = 9
SQUARE_SIZE = 3

import random
rand = random.Random()

class GridCell:
	def __init__(self,x,y):
		self.m_currentVal = 0
		self.m_possibleVal = [1,2,3,4,5,6,7,8,9]
		self.m_x = x
		self.m_y = y
		
	def Validate(self):	
		return 1
		possible = len(self.m_possibleVal)
		if(possible>=1 and possible<=GRID_SIZE):						
			return 1		
		print "possible ",possible
		print "x,y",self.m_x,self.m_y
		return 0
		
def TakeKnownFromPossible(known,possible):
	matches = []
	reduction = 0
	#print ""
	#print "taking known: ",known
	#print "from possible: ",possible
	#print ""
	
	for num in known:
		for pos in possible:
			if(num==pos):
				#print "match found: ",num
				matches.append(num)
	
	for match in matches:
		if(match in possible):	
			reduction+=1
			possible.remove(match)				
	return reduction
				
def CalcSquareCoord(x,y):
	cellX = (x/SQUARE_SIZE)*SQUARE_SIZE
	cellY = (y/SQUARE_SIZE)*SQUARE_SIZE
	return (cellX,cellY)	
		
class AnalyseSet:
	def __init__(self):
		self.m_items = []
	
	def SetForRow(self,grid,row):
		for i in xrange(GRID_SIZE):
			self.m_items.append(grid.m_cells[i][row])	
			
	def SetForCol(self,grid,col):
		for i in xrange(GRID_SIZE):
			self.m_items.append(grid.m_cells[col][i])		
	
	def SetForSquare(self,grid,x,y):
		for i in xrange(SQUARE_SIZE):
			for j in xrange(SQUARE_SIZE):
				self.m_items.append(grid.m_cells[x+i][y+j])						
	
	def BuildKnownList(self):
		knownList = []
		for cell in self.m_items:
			if(cell.m_currentVal != 0):
				knownList.append(cell.m_currentVal)
				
		return knownList	
		
	def Validate(self):
		vaildList = [1,2,3,4,5,6,7,8,9]
		for item in self.m_items:
			if(item.m_currentVal!=0):
				if(item.m_currentVal in vaildList):
					vaildList.remove(item.m_currentVal)
				else:
					return 0
		return 1
				
	def ReducePossible(self):
		knownList = self.BuildKnownList()		
		reduction = 0
		for cell in self.m_items:
			if(cell.m_currentVal == 0):
				reduction+=TakeKnownFromPossible(knownList,cell.m_possibleVal)
				if(len(cell.m_possibleVal)==1):
					cell.m_currentVal = cell.m_possibleVal[0]	
		return reduction
					
class AnalyseCell:
	def __init__(self):		
		self.m_grid = None
		self.m_squareAnalysis = AnalyseSet()
		self.m_rowAnalysis = AnalyseSet()
		self.m_colAnalysis = AnalyseSet()		
	
	def SetForCell(self,grid,x,y):
		self.x = x
		self.y = y
		self.m_grid = grid
		(sx,sy) = CalcSquareCoord(x,y)
		self.m_squareAnalysis.SetForSquare(self.m_grid,sx,sy)
		self.m_rowAnalysis.SetForRow(self.m_grid,y)
		self.m_colAnalysis.SetForCol(self.m_grid,x)
		self.m_cell = self.m_grid.m_cells[x][y]						
		
	def BuildKnownList(self):
		knownList = []
		knownList.extend(self.m_squareAnalysis.BuildKnownList())
		knownList.extend(self.m_rowAnalysis.BuildKnownList())
		knownList.extend(self.m_colAnalysis.BuildKnownList())
		
		return knownList
	
	def MatchingList(self,a,b):
		lenA = len(a)
		if(lenA!=len(b)):
			return 0
		
		matchCount = 0
		for itemA in a:
			for itemB in b:
				if(itemA==itemB):
					matchCount+=1
					
		if(matchCount == lenA):
			return 1
		else:
			return 0
			
			
	#if two cells in the same row/col in the same square, have identical possibilities remaining, 
	#and are the only two cells in this square to have those possibilities remaining. 
	#If that list contains only two possibilties. Then we can say that cell A must be possA or possB
	#and cell B must be whichever cell A is not. This means both possA and possB are accounted for on this
	#row/col and can be removed from the possibilties of the other cells on this row/col
	def SquareExclusionReduce(self): 		
		reductions = 0
		foundMatch = 0
		mx=0
		my=0
		matchItem = None
		if(len(self.m_cell.m_possibleVal)==2):
			for item in self.m_squareAnalysis.m_items:				
				if(item!=self.m_cell and len(item.m_possibleVal)==2):
					if(self.MatchingList(item.m_possibleVal,self.m_cell.m_possibleVal)):
						mx = item.m_x
						my = item.m_y
						matchItem = item
						foundMatch+=1
		
		
		if(foundMatch==1):
			possA = self.m_cell.m_possibleVal[0]
			possB = self.m_cell.m_possibleVal[1]
			
			if(mx==self.m_cell.m_x):# col math
				for item in self.m_colAnalysis.m_items:
					if(item!=matchItem and item!=self.m_cell and item.m_currentVal==0):
						if(possA in item.m_possibleVal):
							reductions+=1
							item.m_possibleVal.remove(possA)
						if(possB in item.m_possibleVal):
							reductions+=1
							item.m_possibleVal.remove(possB)
						
			elif(my==self.m_cell.m_y): # row match
				for item in self.m_rowAnalysis.m_items:
					if(item!=matchItem and item!=self.m_cell and item.m_currentVal==0):
						if(possA in item.m_possibleVal):
							reductions+=1
							item.m_possibleVal.remove(possA)
						if(possB in item.m_possibleVal):
							reductions+=1
							item.m_possibleVal.remove(possB)				
		
		return reductions
					
				
		
	
	def ReducePossible(self):
		reductions = 0
		if(self.m_cell.m_currentVal ==0):
			knownList = self.BuildKnownList()
			#print "Cell knownList: ",knownList
			reductions+=TakeKnownFromPossible(knownList,self.m_cell.m_possibleVal)
			if(len(self.m_cell.m_possibleVal)==1):				
				self.m_cell.m_currentVal = self.m_cell.m_possibleVal[0]		
				
		reductions+=self.SquareExclusionReduce()
		return reductions
				
class Grid:
	def __init__(self):		
		self.m_cells = []
		for i in xrange(GRID_SIZE):
			self.m_cells.append([])
			for j in xrange(GRID_SIZE):
				self.m_cells[i].append(GridCell(i,j))
		
		self.m_alternateGrid = []		
	
	#Validation code		
	def ValidateByCell(self):		
		for i in xrange(GRID_SIZE):
			for j in xrange(GRID_SIZE):
				if(self.m_cells[i][j].Validate()==0):										
					return 0
				analyser = AnalyseSet()
				(sx,sy) = CalcSquareCoord(i,j)
				analyser.SetForSquare(self,sx,sy)
				if(analyser.Validate()==0):
					return 0				
		return 1
	
	def ValidateRows(self):
		for i in xrange(GRID_SIZE):
			analyser = AnalyseSet()
			analyser.SetForRow(self,i)
			if(analyser.Validate()==0):
				return 0
		return 1
		
	def ValidateCols(self):
		for i in xrange(GRID_SIZE):
			analyser = AnalyseSet()
			analyser.SetForCol(self,i)
			if(analyser.Validate()==0):
				return 0
		return 1
					
	def ValidatePuzzle(self):
		if(self.ValidateRows()==0):	
			return 0
		if(self.ValidateCols()==0):			
			return 0
		if(self.ValidateByCell()==0):						
			return 0
		
		return 1
	
	#Guestimation of alternates	
	def GenAlternate(self):
		self.m_alternateGrid = []
		smallPos = 99
		smX = -1
		smY = -1
		for i in xrange(GRID_SIZE):
			for j in xrange(GRID_SIZE):
				if(self.m_cells[i][j].m_currentVal==0 and len(self.m_cells[i][j].m_possibleVal)<smallPos):
					smX = i
					smY = j
					smallPos = len(self.m_cells[i][j].m_possibleVal)
		
		
		
		
		
		possibles = []
		for item in self.m_cells[smX][smY].m_possibleVal:
			possibles.append(item)			
		
		
		for item in possibles:
			self.m_alternateGrid.append(Grid())			
			
		#print "possibles ",possibles
		for i in xrange(len(possibles)):
			self.m_alternateGrid[i].SetGrid(self.GetSetupFromCurrent())						
			self.m_alternateGrid[i].m_cells[smX][smY].m_currentVal = possibles[i]
			self.m_alternateGrid[i].m_cells[smX][smY].m_possibleVal = [possibles[i]]
			#print "Set possible grid at ",smX," ",smY," with possible ",possibles[i]
		#asrt =1/0
		
		
			
	
	#Solver code	
	def CheckSolved(self):
		for i in xrange(GRID_SIZE):
			for j in xrange(GRID_SIZE):
				if(self.m_cells[i][j].m_currentVal==0):
					return 0
		return 1
		
	def ScanRow(self,row):
		analyser = AnalyseSet()
		analyser.SetForRow(self,row)
		return analyser.ReducePossible()
		
	def ScanCol(self,col):
		analyser = AnalyseSet()
		analyser.SetForCol(self,col)
		return analyser.ReducePossible()
		
	def ScanRowsAndCols(self):
		#print "Row and Col pass"
		reduction = 0
		for i in xrange(GRID_SIZE):
			reduction+=self.ScanCol(i)
			reduction+=self.ScanRow(i)
		return reduction	
			
	def ScanCell(self,x,y):
		analyser = AnalyseCell()
		analyser.SetForCell(self,x,y)
		return analyser.ReducePossible()		
	
	def ScanCells(self):
		reduction = 0
		#print "Cell by Cell pass"
		for i in xrange(GRID_SIZE):
			for j in xrange(GRID_SIZE):
				analyser = AnalyseCell()
				analyser.SetForCell(self,i,j)
				reduction+=analyser.ReducePossible()
		return reduction
		
	def Solve(self,prevSolvePasses=0):									
		solvePasses = prevSolvePasses
		lastPassReduction = 1
		while(self.CheckSolved()==0):	
			reductionForPass = 0					
			reductionForPass+=self.ScanCells()
			reductionForPass+=self.ScanRowsAndCols()
			solvePasses+=1		
			
			
			if(self.ValidatePuzzle()==0):				
				return (0,self.GetSetupFromCurrent(),solvePasses) # failed, return broken case
			
			if(reductionForPass==0 and lastPassReduction==0):				
				self.GenAlternate()
				for altGrid in self.m_alternateGrid:
					altSolvePasses = 0
					(solved,solution,altSolvePasses) = altGrid.Solve(solvePasses)
					solvePasses+=altSolvePasses
					if(solved==1):
						self.SetGrid(solution)
						return (1,self.GetSetupFromCurrent(),solvePasses) # solved return solution
				return (0,self.GetSetupFromCurrent(),solvePasses) # all bad branches (this must be an alternate grid that was bad)
			else:
				lastPassReduction = reductionForPass
		
		print "Solved in ",solvePasses," passes\n"
		return (1,self.GetSetupFromCurrent(),solvePasses) # solved return solution
		
		
		
		
	def SetItem(self,x,y,val):
		self.m_cells[x][y].m_currentVal = val		
		
	def Print(self):		
		for i in xrange(GRID_SIZE):		
			rowStr = ""
			for j in xrange(GRID_SIZE):				
				rowStr+=str(self.m_cells[i][j].m_currentVal)
				if((j+1)%SQUARE_SIZE==0):
					rowStr+=" "
			print rowStr
			if((i+1)%SQUARE_SIZE==0):
				print " "
	
	def SetGrid(self,setup):
		for i in xrange(GRID_SIZE):
			for j in xrange(GRID_SIZE):
				self.m_cells[i][j].m_currentVal = setup[i][j]
				if(setup[i][j]!=0):
					self.m_cells[i][j].m_possibleVal = [setup[i][j]]
		self.ValidatePuzzle()
	
	def GetSetupFromCurrent(self):
		setup = []
		for i in xrange(GRID_SIZE):
			setup.append([])
			for j in xrange(GRID_SIZE):
				setup[i].append(self.m_cells[i][j].m_currentVal)
		
		return setup
		
				
		
		
def Test():
	grid = Grid()
	
	puzzle = [	[3,0,0,9,6,0,0,0,0],
				[1,4,0,0,0,5,0,9,0],
				[0,0,5,0,0,0,0,0,8],
				[0,0,0,0,5,0,0,2,0],
				[0,0,3,8,0,0,0,1,9],
				[0,0,0,6,4,0,0,3,0],
				[0,0,0,0,0,0,0,0,1],
				[8,0,0,0,2,0,0,0,0],
				[0,0,1,0,0,3,0,0,4]
				]
				
	grid.SetGrid(puzzle)
	
	
	
	print "Check Puzzle"
	grid.Print()	
	print "Solving..."
	(solved,solution,solvePasses) = grid.Solve()
	if(solved==1):		
		grid.Print()
	
	#puzzle = [	[3,0,0,9,6,0,0,0,0],
	#			[1,4,0,0,0,5,0,9,0],
	#			[0,0,5,0,0,0,0,0,8],
	#			[0,0,0,0,5,0,0,2,0],
	#			[0,0,3,8,0,0,0,1,9],
	#			[0,0,0,6,4,0,0,3,0],
	#			[0,0,0,0,0,0,0,0,1],
	#			[8,0,0,0,2,0,0,0,0],
	#			[0,0,1,0,0,3,0,0,4]
	#			]
	#			
	#grid.SetGrid(puzzle)
	#grid.Print()
	#print "Valid Puzzle: ",grid.ValidatePuzzle()
	
Test()