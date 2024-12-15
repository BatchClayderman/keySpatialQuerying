import os
from sys import argv, exit
from time import time, sleep
try:
	os.chdir(os.path.abspath(os.path.dirname(__file__)))
except:
	pass
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EOF = (-1)


class LocationSearch:
	def __init__(self:object) -> object:
		self.__lines = []
		self.__cells = []
		self.__gridSize = 0 # flag
		self.__xLB = None
		self.__xUB = None
		self.__yLB = None
		self.__yUB = None
		self.__xSize = None
		self.__ySize = None
	def __getTxt(self:object, filePath:str, index:int = 0) -> str: # get .txt content
		coding = ("utf-8", "gbk", "utf-16") # codings
		if 0 <= index < len(coding): # in the range
			try:
				with open(filePath, "r", encoding = coding[index]) as f:
					content = f.read()
				return content[1:] if content.startswith("\ufeff") else content # if utf-8 with BOM, remove BOM
			except (UnicodeError, UnicodeDecodeError):
				return getTxt(filePath, index + 1) # recursion
			except:
				return None
		else:
			return None # out of range
	def build(self:object, filePath:str, gridSize:int = 50) -> bool:
		# Initialization #
		if isinstance(filePath, str) and isinstance(gridSize, int) and gridSize >= 1:
			content = self.__getTxt(filePath)
			if content is None:
				print("Cannot read the file \"{0}\". ".format(filePath))
				return False # do not set the gridSize to 0 (set the flag to False) since no modifications are made in the lines and the cells
			else:
				lines = content.splitlines()
				self.__lines = lines
				del content
		else:
			print("Please pass the file path as a ``str`` object and the grid size as a positive integer. ")
			return False
		
		
		# Tuples #
		tuples = []
		for i, line in enumerate(lines):
			if "\tlocation: " in line and "\ttags: " in line:
				values = line[line.index("\tlocation: ") + 11:line.index("\ttags: ")].split(",")
				if 2 == len(values):
					try:
						tuples.append((i, float(values[0]), float(values[1])))
					except:
						pass
		if not tuples:
			self.__gridSize = 0 # set the flag to False to indicate that the object is not ready
			return False
		
		# Bounds #
		xLB, xUB, yLB, yUB = min(tuples, key = lambda t:t[1])[1], max(tuples, key = lambda t:t[1])[1], min(tuples, key = lambda t:t[2])[2], max(tuples, key = lambda t:t[2])[2]
		xDelta, yDelta = xUB - xLB, yUB - yLB
		print("bounds: {0} {1} {2} {3}".format(xLB, xUB, yLB, yUB))
		print("widths: {0} {1}".format(xDelta, yDelta))
		
		# Cells #
		self.__cells = [[[] for j in range(gridSize)] for i in range(gridSize)]
		cells = self.__cells # to speed up
		xSize, ySize = xDelta / gridSize, yDelta / gridSize
		for t in tuples:
			cells[min(gridSize - 1, int((t[1] - xLB) / xSize))][min(gridSize - 1, int((t[2] - yLB) / ySize))].append(t)
		for i in range(gridSize):
			for j in range(gridSize):
				if cells[i][j]:
					print("{0} {1} {2}".format(i, j, len(cells[i][j])))
		print()
		# print("grid[5][36] = {0}\n".format([t[0] for t in cells[5][36]])) # for debug purposes
		
		# Variables #
		self.__gridSize, self.__xLB, self.__xUB, self.__yLB, self.__yUB, self.__xSize, self.__ySize = gridSize, xLB, xUB, yLB, yUB, xSize, ySize
		return True
	def spaSearchRaw(self:object, xLow:float, xHigh:float, yLow:float, yHigh:float) -> int:
		if isinstance(xLow, float) and isinstance(xHigh, float) and isinstance(yLow, float) and isinstance(yHigh, float) and self.__gridSize >= 1:
			lines, results = self.__lines, []
			startTime = time()
			for idx, line in enumerate(lines):
				if "\tlocation: " in line and "\ttags: " in line:
					values = line[line.index("\tlocation: ") + 11:line.index("\ttags: ")].split(",")
					if 2 == len(values):
						try:
							x, y = float(values[0]), float(values[1])
						except:
							continue
						if xLow <= x <= xHigh and yLow <= y <= yHigh:
							results.append(idx)
			endTime = time()
			print("spaSearchRaw: {0} result(s), cost = {1:.9f} second(s)".format(len(results), endTime - startTime))
			for idx in results:
				print(lines[idx])
			print()
			return len(results)
		else:
			return -1
	def spaSearchGrid(self:object, xLow:float, xHigh:float, yLow:float, yHigh:float) -> int:
		if isinstance(xLow, float) and isinstance(xHigh, float) and isinstance(yLow, float) and isinstance(yHigh, float) and self.__gridSize >= 1:
			lines, cells, results, gridSize, xLB, xUB, yLB, yUB, xSize, ySize = self.__lines, self.__cells, [], self.__gridSize, self.__xLB, self.__xUB, self.__yLB, self.__yUB, self.__xSize, self.__ySize
			startTime = time()
			xLowIdx = int((xLow - xLB) / xSize) if xLB < xLow < xUB else (-1 if xLow <= xLB else gridSize)
			xHighIdx = int((xHigh - xLB) / xSize) if xLB < xHigh < xUB else (-1 if xHigh <= xLB else gridSize)
			yLowIdx = int((yLow - yLB) / ySize) if yLB < yLow < yUB else (-1 if yLow <= yLB else gridSize)
			yHighIdx = int((yHigh - yLB) / ySize) if yLB < yHigh < yUB else (-1 if yHigh <= yLB else gridSize)
			# print("The four boundary values locate at ({0}, {1}, {2}, {3}) of the grid. ".format(xLowIdx, xHighIdx, yLowIdx, yHighIdx)) # for debug purposes
			if 0 <= yHighIdx < gridSize: # the upper side (from left to right and exclude the rightmost cell)
				for i in range(max(0, xLowIdx), min(xHighIdx, gridSize - 1)):
					# print("The program is accessing grid[{0}][{1}]. ".format(i, yHighIdx)) # for debug purposes
					for t in cells[i][yHighIdx]:
						if xLow <= t[1] <= xHigh and yLow <= t[2] <= yHigh:
							results.append(t[0])
			if 0 <= xHighIdx < gridSize: # the right side (from up to bottom and exclude the bottom cell)
				for j in range(min(yHighIdx, gridSize - 1), max(0, yLowIdx), -1):
					# print("The program is accessing grid[{0}][{1}]. ".format(xHighIdx, j)) # for debug purposes
					for t in cells[xHighIdx][j]:
						if xLow <= t[1] <= xHigh and yLow <= t[2] <= yHigh:
							results.append(t[0])
			if 0 <= yLowIdx < gridSize: # the lower side (from right to left and exclude the leftmost cell)
				for i in range(min(xHighIdx, gridSize - 1), max(0, xLowIdx), -1):
					# print("The program is accessing grid[{0}][{1}]. ".format(i, yLowIdx)) # for debug purposes
					for t in cells[i][yLowIdx]:
						if xLow <= t[1] <= xHigh and yLow <= t[2] <= yHigh:
							results.append(t[0])
			if 0 <= xLowIdx < gridSize: # the left side (from bottom to up and exclude the top cell)
				for j in range(max(0, yLowIdx), min(yHighIdx, gridSize - 1)):
					# print("The program is accessing grid[{0}][{1}]. ".format(xLowIdx, j)) # for debug purposes
					for t in cells[xLowIdx][j]:
						if xLow <= t[1] <= xHigh and yLow <= t[2] <= yHigh:
							results.append(t[0])
			for i in range(xLowIdx + 1, xHighIdx): # all the points in the cells within but not on the four sides must be within the given range
				for j in range(yLowIdx + 1, yHighIdx):
					# print("The program is accessing grid[{0}][{1}]. ".format(i, j)) # for debug purposes
					for t in cells[i][j]:
						results.append(t[0])
			results.sort()
			endTime = time()
			print("spaSearchGrid: {0} result(s), cost = {1:.9f} second(s)".format(len(results), endTime - startTime))
			for idx in results:
				print(lines[idx])
			print()
			return len(results)
		else:
			return -1


def preExit(countdownTime:int = 5) -> None:
		try:
			cntTime = int(countdownTime)
			length = len(str(cntTime))
		except:
			print("Program ended. ")
			return
		print()
		while cntTime > 0:
			print("\rProgram ended, exiting in {{0:>{0}}} second(s). ".format(length).format(cntTime), end = "")
			try:
				sleep(1)
			except:
				print("\rProgram ended, exiting in {{0:>{0}}} second(s). ".format(length).format(0))
				return
			cntTime -= 1
		print("\rProgram ended, exiting in {{0:>{0}}} second(s). ".format(length).format(cntTime))

def main() -> int:
	if len(argv) == 5: # 51 51.20 -0.5 0
		try:
			xLow, xHigh, yLow, yHigh = float(argv[1]), float(argv[2]), float(argv[3]), float(argv[4])
		except:
			print("Please provide the four boundary values in the form of ``xLow xHigh yLow yHigh`` correctly. ")
			preExit()
			return EOF
	else:
		print("Please provide the locations for searching via the command line. ")
		preExit()
		return EOF
	filePath = "Restaurants_London_England.tsv"
	locationSearch = LocationSearch()
	if not locationSearch.build(filePath):
		preExit()
		return EOF
	flagRaw, flagGrid = locationSearch.spaSearchRaw(xLow, xHigh, yLow, yHigh), locationSearch.spaSearchGrid(xLow, xHigh, yLow, yHigh)
	preExit()
	return EXIT_SUCCESS if flagRaw >= 1 and flagGrid >= 1 and flagRaw == flagGrid else EXIT_FAILURE



if __name__ == "__main__":
	exit(main())