from blocktools import *
from opcode import *
from datetime import datetime

import io
import time

class BlockHeader:
	def __init__(self, blockchain):
		self.version = uint4(blockchain)
		self.previous_block_hash = hash32(blockchain)
		self.merkleHash = hash32(blockchain)
		# the Merkle root is the hash of all the hashes of all the transactions in the block. 
		self.time = uint4(blockchain)
		self.bits = uint4(blockchain)
		self.nonce = uint4(blockchain)
	def toString(self):
		print(f"    Version               {self.version}")
		print(f"    Previous Block Hash   {hashStr(self.previous_block_hash)}")
		print(f"    Merkle Root           {hashStr(self.merkleHash)}")
		print(f"    Time stamp            {self.decodeTime(self.time)}")
		print(f"    Difficulty            {difficulty(self.bits):.2f} ({self.bits} bits)")
		print(f"    Nonce                 {self.nonce}")
	def decodeTime(self, time):
		utc_time = datetime.utcfromtimestamp(time)
		return utc_time.strftime("%Y-%m-%d %H:%M:%S.%f+00:00 (UTC)")

class Block:
	def __init__(self, blockchain: io.BufferedReader):
		assert isinstance(blockchain, io.BufferedReader)
		self.continue_parsing = True
		self.magicNum = 0
		self.blocksize = 0
		self.blockheader = ''
		self.transaction_count = 0
		self.transactions = []

		if self.has_length(blockchain, 8):	
			self.magicNum = uint4(blockchain)
			# If you unpack bytes F9 BE in dat file you get the magic number 0XD9B4BEF9
			# magic number is also used to confirm the start of a block
			self.blocksize = uint4(blockchain)
		else:
			# If has_length() returns false, there is no next block in the file
			self.continue_parsing = False
			return
		
		if self.has_length(blockchain, self.blocksize):
			self.set_header(blockchain)
			self.transaction_count = varint(blockchain)
			self.transactions = []

			for i in range(0, self.transaction_count):
				transaction = Transaction(blockchain)
				transaction.seq = i 
				self.transactions.append(transaction)
		else:
			self.continue_parsing = False
						

	def continue_parsing(self):
		return self.continue_parsing

	def getBlocksize(self):
		return self.blocksize

	def has_length(self, blockchain, size):
		cur_pos = blockchain.tell()
		# tell(): Return the current stream position as an opaque number.
		# The number does not usually represent a number of bytes in the underlying binary storage.

		blockchain.seek(0, io.SEEK_END)		
		file_size = blockchain.tell()
		blockchain.seek(cur_pos, io.SEEK_SET)

		# if means that if the remaining size is too small,
		# the method returns False
		temp_block_size = file_size - cur_pos
		if temp_block_size < size:
			return False
		return True

	def set_header(self, blockchain):
		self.blockHeader = BlockHeader(blockchain)

	def toString(self):
		print("")
		print(f"  Magic No: \t\t\t{hex(self.magicNum).upper()}") 
		assert hex(self.magicNum).upper() == "0XD9B4BEF9"
		# seems this is something hard-coded		
		print(f"  Blocksize (bytes): \t{self.blocksize}")
		print("")
		print("  ########## Block Header BEGIN ##########")
		self.blockHeader.toString()
		print("  ########## Block Header END ##########\n")
		print(f"  ########## Transaction Count: {self.transaction_count} ##########\n")
		print("  ########## Transaction Data BEGIN ##########")
		for t in self.transactions:
			t.toString()
		print("  ########## Transaction Data END ##########")


class Transaction:
	def __init__(self, blockchain: io.BufferedReader):
		assert isinstance(blockchain, io.BufferedReader)
		cur_pos = blockchain.tell()
		self.version = uint4(blockchain)
		self.input_count = varint(blockchain)
		self.inputs = []
		self.seq = 1
		for i in range(0, self.input_count):
			input = txInput(blockchain)
			self.inputs.append(input)
		self.outCount = varint(blockchain)
		self.outputs = []
		if self.outCount > 0:
			for i in range(0, self.outCount):
				output = txOutput(blockchain)
				self.outputs.append(output)	
		self.lockTime = uint4(blockchain)

		
	def toString(self):
		print(f"    ##### Transactions[{self.seq}] #####")
		print(f"      Transaction Version:\t {self.version}")
		print(f"      Input Count:\t\t {self.input_count}")
		for i in self.inputs:
			i.toString()

		print(f"      Output Count:\t {self.outCount}")
		for o in self.outputs:
			o.toString()
		print(f"        Lock Time:\t {self.lockTime}")

class txInput:
	def __init__(self, blockchain: io.BufferedReader):
		assert isinstance(blockchain, io.BufferedReader)
		self.prev_transaction_hash = hash32(blockchain)
		self.txOutId = uint4(blockchain)
		self.script_length = varint(blockchain)
		self.scriptSig = blockchain.read(self.script_length)
		self.seqNo = uint4(blockchain)

	def toString(self):
#		print "\tPrev. Tx Hash:\t %s" % hashStr(self.prevhash)
		print(f"        Transaction Out Index:\t{self.decodeOutIdx(self.txOutId)}")
		print(f"        Script Length:\t {self.script_length}")
	#	print(f"\tScriptSig:\t {self.scriptSig}") 
	#	print(f"\tScriptSig:\t {self.scriptSig.decode('utf8')}") 
		self.decodeScriptSig(self.scriptSig)
		assert self.seqNo == 4294967295
		print(f"        Sequence:\t {self.seqNo} (== ffffffff, not in use)")

	def decodeScriptSig(self,data):
		hexstr = hashStr(data)
		if 0xffffffff == self.txOutId: #Coinbase
			return hexstr
		scriptLen = int(hexstr[0:2],16)
		scriptLen *= 2
		script = hexstr[2:2+scriptLen] 
		print(f"        Script:\t\t {script}")
		if SIGHASH_ALL != int(hexstr[scriptLen:scriptLen+2],16): # should be 0x01
			print("\t Script op_code is not SIGHASH_ALL")
			return hexstr
		else: 
			pubkey = hexstr[2+scriptLen+2:2+scriptLen+2+66]
			print("        InPubkey:\t " + pubkey)
#		return hexstr

	def decodeOutIdx(self,idx):
		s = ""
		if(idx == 0xffffffff):
			s = " Coinbase with special index"
			print("        Coinbase Text:\t%s" % hashStr(self.prev_transaction_hash))
		else: 
			print("        Prev. Transaction Hash:\t%s" % hashStr(self.prev_transaction_hash))
		return f"{int(idx)} {s}"
		

class txOutput:
	def __init__(self, blockchain):	
		self.value = uint8(blockchain)
		self.scriptLen = varint(blockchain)
		self.pubkey = blockchain.read(self.scriptLen)

	def toString(self):
		print("        Value:\t\t %d" % self.value + " Satoshi")
		print("        Script Len:\t %d" % self.scriptLen)
		print("        ScriptPubkey:\t %s" % self.decodeScriptPubkey(self.pubkey))
	def decodeScriptPubkey(self,data):
		hexstr = hashStr(data)
		op_idx = int(hexstr[0:2], base=16)
		try: 
			op_code1 = OPCODE_NAMES[op_idx]
		except KeyError: #Obselete pay to pubkey directly 
			print(f"        OP_CODE {op_idx} is probably obselete pay to address")
			keylen = op_idx
			op_codeTail = OPCODE_NAMES[int(hexstr[2+keylen*2:2+keylen*2+2],16)]
			print("        Pubkey OP_CODE:\t " "None " + "Bytes:%d " % keylen +\
					"tail_op_code:" +  op_codeTail + " " )
			print("        Pure Pubkey:\t   %s" % hexstr[2:2+keylen*2])
			return hexstr
		if op_code1 == "OP_DUP":  #P2PKHA pay to pubkey hash mode
			op_code2 = OPCODE_NAMES[int(hexstr[2:4],16)] + " "
			keylen = int(hexstr[4:6],16) 
			op_codeTail2nd = OPCODE_NAMES[int(hexstr[6+keylen*2:6+keylen*2+2],16)]
			op_codeTailLast = OPCODE_NAMES[int(hexstr[6+keylen*2+2:6+keylen*2+4],16)]
			print(" \tPubkey OP_CODE:\t " + op_code1 + " " + op_code2 + " " + "Bytes:%d " % keylen +\
					"tail_op_code:" +  op_codeTail2nd + " " + op_codeTailLast)
			print("\tPubkeyHash:\t       %s" % hexstr[6:6+keylen*2])
			return hexstr	
		elif op_code1 == "OP_HASH160": #P2SHA pay to script hash 
			keylen = int(hexstr[2:4],16) 
			op_codeTail = OPCODE_NAMES[int(hexstr[4+keylen*2:4+keylen*2+2],16)]
			print(" \tPubkey OP_CODE:\t " + op_code1 + " " + " " + "Bytes:%d " % keylen +\
					"tail_op_code:" +  op_codeTail + " " )
			print("\tPure Pubkey:\t     %s" % hexstr[4:4+keylen*2])
			return hexstr
		else: #TODO extend for multi-signature parsing 
			print("\t Need to extend multi-signatuer parsing %x" % int(hexstr[0:2],16) + op_code1)
			return hexstr
		
