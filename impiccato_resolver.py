
################################
# IMPORT
################################
import pickle, os, time

def list_union(lista, listb):
	return list( set(lista) + set(listb) )

def list_intersect(lista, listb):
	return list(set(lista) & set(listb))

def list_difference(lista, listb):
	return list(set(listb) - set(lista))

################################
# Class WORD
################################
class impiccatoWord:
	
	word = ""
	
	def impiccatoWord(self):
		self.word = ""
	
	def init(self, w):
		self.word = w
		return self
	
	def match(self, solution):
		for pos in solution:
			if pos >= len(self.word):
				return False
			elif self.word[pos] != solution[pos]:
				return False
		return True
	
	def contains(self,list_of_char):
		for char in list_of_char:
			if char in self.word:
				return True
		return False
		
	def value(letter, db):
		if not letter in db:
			return 0
		s = []
		#maxwords
		for i in db[letter]:
			for word in db[letter][i]:
				if not word in s:
					s.append(word)
		return float(len(s)) / maxwords

################################
# Class DB
################################
class impiccatoDb:
	
	words = []
	db = {}
	
	def impiccatoDb(self):
		self.words = []
		self.db = {}
	
	def dump(self):
		res = {}
		for char in self.db.keys():
			res[char] = self.value(char)
		return res
	
	def value(self, letter):
		s = []
		for pos in self.db[letter]:
			s += self.db[letter][pos]
		# uniquify
		s = list(set(s))
		s = len(s)
		v = float(s) / len(self.words)
		return v
	
	def load(self, dbfile):
		start = time.clock()
		if not os.path.exists(dbfile):
			return False
		print "Database load from file.. "
		try:
			fp = open(dbfile,"rb")
			self.words = pickle.load(fp)
			self.db = pickle.load(fp)
			fp.close()
		except:
			os.remove(dbfile)
			raise ValueError, 'Non riesco a caricare il database!'
		print "Time length:", time.clock()-start, "sec"
		print "Database ready"
		return True
	
	def create(self, sourcefile, dbfile):
		print "Creating database.."
		start = time.clock()
		try:
			fp = open(sourcefile,"r")
			self.words = fp.read().split()
			fp.close()
		except:
			raise ValueError, 'Non riesco a caricare la word list!'
		print "Wordlist length:", len(self.words)
		# build db
		for ch in range(0,ord('z')-ord('a')+1):
			char = chr(ord('a')+ch)
			#print char
			self.db[char] = {}
		for i in range(len(self.words)):
			word = self.words[i]
			for j in range(len(word)):
				if word[j] in self.db.keys():
					if not j in self.db[ word[j] ]:
						self.db[ word[j] ][j] = []
					self.db[ word[j] ][j].append(i)
		#print db['a'][0]
		# output su file
		output = open(dbfile, 'wb')
		# Pickle the list using the highest protocol available.
		pickle.dump(self.words, output)
		pickle.dump(self.db, output)
		output.close()
		print "Time length:", time.clock()-start, "sec"
		print "Database ready"
	
	def getChars(self):
		return self.db.keys()
	
	def removeChar(self,char):
		if char in self.db:
			positions = self.db[char]
			ws = list()
			for pos in positions:
				ws = ws + self.db[char][pos]
			self.words = list_difference( self.words, ws )
			del self.db[char]
	
	def removePosition(self,char,pos):
		if char in self.db and pos in self.db[char]:
			ws = self.db[char][pos]
			self.words = list_difference( self.words, ws )
			del self.db[char][pos]

################################
# Class GAME
################################
class impiccatoGame:
	
	secret_word = ""
	solution = {}
	possible_word = []
	guessed = []
	missing = []
	guess_count = 0
	db = None
	
	def impiccatoGame(self):
		self.solution = {}
		self.guessed = []
		self.missing = []
		self.possible_word = []
	
	def init(self, secret_word, db, guess_count=10):
		self.secret_word = secret_word.lower()
		self.guess_count = guess_count
		self.db = db
	
	def getSolution(self):
		ris = ""
		if self.solution:
			for i in range(max(self.solution.keys())):
				if i in self.solution.keys():
					ris += self.solution[i]
				else:
					ris += "_"
			#return "".join(self.solution.values()).lower()
		return ris
	
	def lose(self):
		return self.guess_count <= 0 or len(self.missing) >= len(self.db.getChars())
	
	def win(self):
		return self.getSolution() == self.secret_word
	
	def guess(self,letter):
		letter = letter.lower()
		word = self.secret_word
		ris = []
		if letter in word:
			for i in range(len(word)):
				if letter == word[i]:
					ris.append(i)
		self.guessed.append(letter)
		if not ris:
			self.missing.append(letter)
			self.guess_count -= 1
		return ris
	
	def getNextLetter(self):
		maxletter = None
		maxcount = 0
		for char in self.db.getChars():
			nval = self.db.value(char)
			if nval > maxcount and not char in self.guessed:
				maxcount = nval
				maxletter = char
		if not maxletter:
			#raise ValueError, "Guessed all possible character!"
			return False, 0
		else:
			return maxletter, maxcount
	
	def getChars(self):
			return self.db.getChars()
	
	def getPositions(self,char):
		return self.db.db[char]
	
	def getWords(self,char,pos):
		return self.getPositions(char)[pos]
	
	def run(self):
		while not self.win() and not self.lose():
			print "-------------------------"
			
			# estrazione lettera
			(maxletter, maxcount) = self.getNextLetter()
			print "Scelgo:", maxletter, maxcount
			
			if not maxletter:
				raise ValueError, "Ho finito le lettere! =("
			
			# guess della lettera scelta
			res = self.guess(maxletter)
			print "Risultato:", res
			
			# gestione solution e lista delle possible_words in
			# base al risultato
			if res:
				for pos in res:
					#print len(solution), pos
					self.solution[pos] = maxletter
					if not self.possible_word:
						self.possible_word = self.getWords(maxletter,pos)
					else:
						self.possible_word = list_intersect(self.possible_word,self.getWords(maxletter,pos))
			elif self.possible_word:
				for pos in self.getPositions(maxletter):
					words = self.getWords(maxletter,pos)
					self.possible_word = list_difference(self.possible_word, words)
			
			# output
			print 'Solution:', self.getSolution(), 'Guess_count:', self.guess_count
			
			# rebuilding db
			start = time.clock()
			print "Rebuilding database.."
			if not res:
				# tolgo la lettera dal dizionario
				# e aggiorna lo stato interno
				self.db.removeChar(maxletter)
			else:
				# tolgo la pos della lettera che viene
				# trovata ma non in quella pos =)
				poss = {}
				for pos in self.getPositions(maxletter):
					if not pos in res:
						#self.db.removePosition(maxletter,pos)
						True
					else:
						#self.db.db[maxletter][pos] = 
						poss[pos] = list_intersect(self.db.db[maxletter][pos],self.possible_word)
				self.db.db[maxletter] = poss
				# aggiorno gli elenchi delle word per le letter non ancora guessed
				for char in self.getChars():
					if not char in self.guessed:
						ndb = {}
						for pos in self.getPositions(char):
							nlist = list_intersect( self.getWords(char,pos), self.possible_word )
							if nlist:
								ndb[pos] = nlist
						self.db.db[char] = ndb
			# next cycle
			print "Finished", time.clock()-start, "sec"
			print self.db.dump()
				

if __name__ == "__main__":
    
    sourcefile = "/script/wordlist-ita.txt"
    dbfile = "/script/wordlist-ita.pkl"
    
    secret_word = "casa"
    #print guess('a')
    #print guess('u')
    
    # Creating database impiccatoDb
    db = impiccatoDb()
    db2 = db.load(dbfile)
    if not db2:
    	db.create(sourcefile,dbfile)
    print db.dump()
    
    game = impiccatoGame()
    game.init(secret_word,db,10)
    game.run()
    
