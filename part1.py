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


class KeywordSearch:
	def __init__(self:object) -> object:
		self.__lines = []
		self.__dict = {}
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
	def build(self:object, filePath:str) -> bool:
		# Initialization #
		if isinstance(filePath, str):
			content = self.__getTxt(filePath)
			if content is None:
				print("Cannot read the file \"{0}\". ".format(filePath))
				return False
			else:
				lines = content.splitlines()
				self.__lines = lines
				del content
		else:
			print("Please pass the file path as a ``str`` object. ")
			return False
		
		# Construction #
		d = self.__dict
		d.clear()
		for i, line in enumerate(lines):
			if "\ttags: " in line:
				tags = line[line.index("\ttags: ") + 7:].split(",")
				for tag in tags:
					d.setdefault(tag, set()).add(i)
		print("\nnumber of keywords: {0}\n\nfrequencies:".format(len(d)), end = "")
		for tag in sorted(d.keys()):
			print(" [{0}: {1}]".format(tag, len(d[tag])), end = "")
		print("\n")
		return True
	def kwSearchRaw(self:object, keywords:list) -> int:
		if isinstance(keywords, (tuple, list, set)):
			lines, d, results = self.__lines, self.__dict, []
			startTime = time()
			for idx, line in enumerate(lines):
				if "\ttags: " in line:
					tags = line[line.index("\ttags: ") + 7:].split(",")
					for keyword in keywords:
						if keyword not in tags:
							break # at least one of the keywords cannot be found in the tags
					else: # the loop ends naturally
						results.append(idx)
			endTime = time()
			print("kwSearchRaw: {0} result(s), cost = {1:.9f} second(s)".format(len(results), endTime - startTime))
			for idx in results:
				print(lines[idx])
			print()
			return len(results)
		else:
			return -1
	def kwSearchIF(self:object, keywords:list) -> int:
		if isinstance(keywords, (tuple, list, set)):
			lines, d = self.__lines, self.__dict
			startTime = time()
			if keywords:
				idx, length, s = 1, len(keywords), (d[keywords[0]] if keywords[0] in d else set())
				while idx < length and s: # to speed up
					if keywords[idx] in d: # avoid bugs
						s = s.intersection(d[keywords[idx]])
						idx += 1
					else:
						s.clear()
						break
				results = sorted(s)
			else:
				results = list(range(len(lines)))
			endTime = time()
			print("kwSearchIF: {0} result(s), cost = {1:.9f} second(s)".format(len(results), endTime - startTime))
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

def main() -> int: # organic "late night"
	if len(argv) < 2:
		print("Please provide the keywords for searching via the command line. ")
		preExit()
		return EOF
	filePath = "Restaurants_London_England.tsv"
	keywordSearch = KeywordSearch()
	if not keywordSearch.build(filePath):
		preExit()
		return EOF
	flagRaw, flagIF = keywordSearch.kwSearchRaw(argv[1:]), keywordSearch.kwSearchIF(argv[1:])
	preExit()
	return EXIT_SUCCESS if flagRaw >= 1 and flagIF >= 1 and flagRaw == flagIF else EXIT_FAILURE



if __name__ == "__main__":
	exit(main())