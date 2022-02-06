from opcode import *
from datetime import datetime

import copy
import io
import utils


class BlockHeader:

	version: int = 0
	hash_prev_blk: bytes = None
	"""
	The raw (i.e. little-endian) hashPrevBlock bytes value directly read from
	data file as defined in	https://en.bitcoin.it/wiki/Block_hashing_algorithm.
	"""
	hash_merkle_root: bytes = None
	"""
	The raw (i.e. little-endian) hashMerkleRoot bytes value directly read from
	data file as defined in	https://en.bitcoin.it/wiki/Block_hashing_algorithm.
	"""
	target_hash: int = 0
	"""
	The SHA-256 hash of a block's header must be lower than or equal to the
	current target for the block to be accepted by the network.
	The lower the target, the more difficult it is to generate a block. 
	Ref: https://en.bitcoin.it/wiki/Target.
	"""

	def __init__(self, block_reader: io.BufferedReader):
		assert isinstance(block_reader, io.BufferedReader)
		# The following is also the order of bytes of a blk*.dat file.

		self.version = utils.read_4bytes_as_uint(block_reader)
		self.hash_prev_blk = utils.read_32bytes(block_reader)
		self.hash_merkle_root = utils.read_32bytes(block_reader)
		self.timestamp = utils.read_4bytes_as_uint(block_reader)
		self.bits = utils.read_4bytes_as_uint(block_reader)
		self.nonce = utils.read_4bytes_as_uint(block_reader)
		self.target_hash = utils.get_target_hash_by_difficulty(self.bits.to_bytes(4, byteorder='little'))

	def get_bytes(self) -> bytes:
		"""
		Get original bytes of header of a block. The bytes returns by this method
		are supposed to be exactly the same as those ones stored in blk*.dat file
		"""
		# For string, such as self.prev_blk_hash,
		# the idea is that, we firstly convert strings back to bytes using
		# bytes.fromhex() and then we convert bytes from Big-Endian order back
		# to Little-Endian order with [::-1], so that the order of bytes are exactly 
		# the same as those stored in blk*.dat file

		# For integer, such as self.version, we use biult-in functions to do the same

		# Why do we need to read values one after another and then piece them
		# together? Well the initial answer is: the original blocktools repository
		# does it this way, so this project simply follow the design. But it begs 
		# the question: Can we re-design the entire algorithm to: read everything
		# in first, calculate the hash and then split the bytes into different
		# values? The answer is actually no. The reason is that, we don't know
		# the length of a transaction in advance due to the existence of 
		# variable-length integers. As a result, the current design, albeit a bit
		# awkward at the first glance, is actually not that bad.

		array = (self.version.to_bytes(4, byteorder='little') +
							self.hash_prev_blk +
							self.hash_merkle_root +
							self.timestamp.to_bytes(4, byteorder='little') +
							self.bits.to_bytes(4, byteorder='little') +
							self.nonce.to_bytes(4, byteorder='little'))
		return array


	def get_current_block_hash(self) -> bytes:
		"""
		Calculate the hash of the current block as a way to verify the validity of
		a block. The method follows the algorithm defined in 
		https://en.bitcoin.it/wiki/Block_hashing_algorithm. Usually this is done
		by the Bitcoin network instead of a parser.
		"""
		array = self.get_bytes()
		hash = utils.double_sha256(array)
		assert isinstance(hash, bytes)
		return hash


	def stdout(self):
		print(f"    Version           {self.version}")
		print(f"    Prev. Block Hash  {utils.convert_endianness(self.hash_prev_blk).hex()}")
		print(f"    Merkle Root Hash  {utils.convert_endianness(self.hash_merkle_root).hex()} (Verified)")
		# This (Verified) note is hard-coded. The real verification happens
		# in 
		print(f"    Timestamp         {self.timestamp} / 0x{self.timestamp:x} / {datetime.utcfromtimestamp(self.timestamp)} (UTC)")
		print(f"    Difficulty        {utils.difficulty(self.bits):.2f} ({self.bits} bits / 0x{self.bits:x} bits)")
		print(f"    Nonce             {self.nonce}")


class Block:
	def __init__(self, block_reader: io.BufferedReader):
		assert isinstance(block_reader, io.BufferedReader)
		self.continue_parsing = True
		self.magic_number = 0
		self.block_size = 0
		self.blockheader = ''
		self.transaction_count = 0
		self.transactions = []

		if self.has_length(block_reader, 8):	
			self.magic_number = utils.read_4bytes_as_uint(block_reader)
			self.block_size = utils.read_4bytes_as_uint(block_reader)
			# For example, after reading the magic number, the next 4 bytes from the 
			# 1st block in file blk00003.dat (hash 0000000000000a21907a50af01d3eb8bb52cc0b18edea7facf0dce4b31d8932a)
			# are 48 28 00 00:
			# step1: switch to Big-Endian order: 00 00 28 48 == 28 48
			# step2: convert 2 8 4 8 to binary: 0010 1000 0100 1000
			# steo3: convert to decimal: 2^3 + 2^6 + 2^11 + 2^13 = 10312
			# so this block's size is 10,312 bytes as confirmed by this online explorer:
			# https://www.blockchain.com/btc/block/0000000000000A21907A50AF01D3EB8BB52CC0B18EDEA7FACF0DCE4B31D8932A
		else:
			# If has_length() returns false, there is no next block in the file
			self.continue_parsing = False
			return
		
		if self.has_length(block_reader, self.block_size):
			self.set_header(block_reader)
			self.transaction_count = utils.read_bytes_as_variable_int(block_reader)
			self.transactions = []

			for i in range(0, self.transaction_count):
				transaction = Transaction(block_reader)
				transaction.seq = i 
				self.transactions.append(transaction)
		else:
			self.continue_parsing = False

		if self.get_merkle_root() != self.block_header.hash_merkle_root:
			raise ValueError("\n" + self.get_merkle_root().hex() + "\n" + self.block_header.hash_merkle_root.hex())


	def continue_parsing(self):
		return self.continue_parsing

	def getBlocksize(self):
		return self.block_size

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
		self.block_header = BlockHeader(blockchain)
		self.curr_block_hash = self.block_header.get_current_block_hash()
		if self.block_header.target_hash - int.from_bytes(self.curr_block_hash, byteorder='little') < 0:
			raise ValueError('Block hash is great than target hash.\n'
										   f'Target Hash: {self.block_header.target_hash:064x}\n'
											 f'Block Hash:  {utils.convert_endianness(self.curr_block_hash).hex()}\n'
											 f'Nonce:       {self.block_header.nonce}')

	def stdout(self):
		print("")
		print(f"  Magic No:          {hex(self.magic_number).upper()}") 
		assert hex(self.magic_number).upper() == "0XD9B4BEF9"
		# seems this is something hard-coded		
		
		print(f"  Blocksize (bytes): {self.block_size}")
		print(f"  Curr. Block Hash:  {utils.convert_endianness(self.curr_block_hash).hex()} (Derived from header)")
		print(f"  Target Hash        {self.block_header.target_hash:064x} (Derived from Difficulty)")
		print("")
		print("  ########## Block Header BEGIN ##########")
		self.block_header.stdout()
		print("  ########## Block Header END ##########\n")
		print(f"  ########## Transaction Count: {self.transaction_count} ##########\n")
		print("  ########## Transaction Data BEGIN ##########")
		for t in self.transactions:
			t.stdout()
		print("  ########## Transaction Data END ##########")
	
	def get_merkle_root(self):
		digests = []
		for t in self.transactions:
			digests.append(utils.double_sha256(t.get_bytes()))

		while True:
			digests_copy = copy.copy(digests)			

			if len(digests_copy) == 1:
				return digests_copy[0]
			if len(digests_copy) % 2 != 0:
				digests_copy.append(digests[-1])

			digests.clear()
			pos = 0
			while pos + 1 < len(digests_copy):
				digests.append(utils.double_sha256(digests_copy[pos] + digests_copy[pos+1]))
				pos += 2
			if pos == 0:
				break


class Transaction:

	def __init__(self, blockchain: io.BufferedReader):
		assert isinstance(blockchain, io.BufferedReader)
		cur_pos = blockchain.tell()
		self.version = utils.read_4bytes_as_uint(blockchain)
		self.input_count = utils.read_bytes_as_variable_int(blockchain)
		self.inputs = []
		self.seq = 1
		for i in range(0, self.input_count):
			input = txInput(blockchain)
			self.inputs.append(input)
		self.outCount = utils.read_bytes_as_variable_int(blockchain)
		self.outputs = []
		if self.outCount > 0:
			for i in range(0, self.outCount):
				output = txOutput(blockchain)
				self.outputs.append(output)	
		self.lockTime = utils.read_4bytes_as_uint(blockchain)

		
	def stdout(self):
		print(f"    ##### Transactions[{self.seq}] #####")
		print(f"      Transaction Version:     {self.version}")
		print(f"      Input Count:             {self.input_count}")
		for i in range(len(self.inputs)):
			self.inputs[i].toString(i)

		print(f"      Output Count:            {self.outCount}")
		for i in range(len(self.outputs)):
			self.outputs[i].stdout(i)
		print(f"        Lock Time:             {self.lockTime}")


	def get_bytes(self):
		"""
		Get original bytes of the transaction section of a block.
		The bytes returns by this method are supposed to be exactly the
		same as those ones stored in blk*.dat file
		"""

		# The basic idea here is the same as BlockHeader.get_bytes()


		array = (self.version.to_bytes(4, byteorder='little') + utils.get_bytes_from_variable_int(self.input_count))
		for i in range(len(self.inputs)):
			array += self.inputs[i].get_bytes()

		array += utils.get_bytes_from_variable_int(self.outCount)
		for i in range(len(self.outputs)):
			array += self.outputs[i].get_bytes()
		array += self.lockTime.to_bytes(4, byteorder='little')	
		return array


class txInput:
	
	prev_tx_hash: bytes = None
	"""
	The raw (i.e. little-endian) Previous Transaction hash bytes value directly
	read from data file as defined in	https://en.bitcoin.it/wiki/Transaction#Generation.
	"""

	def __init__(self, block_reader: io.BufferedReader):
		assert isinstance(block_reader, io.BufferedReader)
		self.prev_tx_hash = utils.read_32bytes(block_reader)
		self.txOutId = utils.read_4bytes_as_uint(block_reader)
		self.script_length = utils.read_bytes_as_variable_int(block_reader)
		self.scriptSig = block_reader.read(self.script_length)
		self.seqNo = utils.read_4bytes_as_uint(block_reader)

	def get_bytes(self):
		"""
		Get original bytes of the inputs of a transaction.
		The bytes returns by this method are supposed to be exactly the
		same as those ones stored in blk*.dat file
		"""
		# The basic idea here is the same as BlockHeader.get_bytes()	
		array = (self.prev_tx_hash +
							self.txOutId.to_bytes(4, byteorder='little') +
							utils.get_bytes_from_variable_int(self.script_length) +
							self.scriptSig +
							self.seqNo.to_bytes(4, byteorder='little'))

		return array


	def toString(self, idx):
		print(f"      ## Inputs[{idx}] ##")
		print(f"        Transaction Out Index: {self.decodeOutIdx(self.txOutId)}")
		print(f"        Script Length:         {self.script_length}")
		self.decodeScriptSig(self.scriptSig)
		print(f"        ScriptSig(hex):        {self.scriptSig.hex()}")
		
	  #	assert self.seqNo == 4294967295
		print(f"        Sequence:              {self.seqNo} (== ffffffff, not in use)")

	def decodeScriptSig(self, data):
		hexstr = utils.bytes_to_hex_string(data)
		if 0xffffffff == self.txOutId: #Coinbase
			return hexstr
		scriptLen = int(hexstr[0:2],16)
		scriptLen *= 2
		script = hexstr[2:2+scriptLen] 
		print(f"        Script:                {script}")
		if SIGHASH_ALL != int(hexstr[scriptLen:scriptLen+2],16): # should be 0x01
			print("\t Script op_code is not SIGHASH_ALL")
			return hexstr
		else: 
			pubkey = hexstr[2+scriptLen+2:] # very critical change
			print(f"        Pubkey:                {pubkey} (Addr: {utils.Pubkey2Address.PubkeyToAddress(pubkey)})")
#		return hexstr

	def decodeOutIdx(self,idx):
		s = ""
		if(idx == 0xffffffff):
			s = " Coinbase with special index"
			print(f"        Coinbase Text:         {utils.convert_endianness(self.prev_tx_hash).hex()}")
		else: 
			print(f"        Prev. Tx Hash:         {utils.convert_endianness(self.prev_tx_hash).hex()}")
		return f"{int(idx)} {s}"
		

class txOutput:
	def __init__(self, blockchain):	
		self.value = utils.uint8(blockchain)
		self.scriptLen = utils.read_bytes_as_variable_int(blockchain)
		self.pubkey = blockchain.read(self.scriptLen)

	def get_bytes(self):
		array = (self.value.to_bytes(8, byteorder='little')+
						 utils.get_bytes_from_variable_int(self.scriptLen) +
						 self.pubkey)

		return array


	def stdout(self, idx):
		print(f"      ## Outputs[{idx}] ##")
		print(f"        Value:                 {self.value:,} Satoshi ({self.value / 100_000_000} Bitcoin)")
		print(f"        Script Len:            {self.scriptLen}")
		print(f"        ScriptPubkey(hex):     {self.decodeScriptPubkey(self.pubkey)}")


	def decodeScriptPubkey(self,data):
		hexstr = utils.bytes_to_hex_string(data)
		op_idx = int(hexstr[0:2], base=16)
		try: 
			op_code1 = OPCODE_NAMES[op_idx]
		except KeyError: #Obselete pay to pubkey directly 
			print(f"        OP_CODE {op_idx} is probably obselete pay to address")
			keylen = op_idx
			op_codeTail = OPCODE_NAMES[int(hexstr[2+keylen*2:2+keylen*2+2],16)]
			print("        Pubkey OP_CODE:\t " "None " + "Bytes:%d " % keylen +\
					"tail_op_code:" +  op_codeTail + " " )
			print("        Pure Pubkey:        %s" % hexstr[2:2+keylen*2])
			return hexstr
		if op_code1 == "OP_DUP":  #P2PKHA pay to pubkey hash mode
			print("        Transaction Type:      Pay-to-PubkeyHash (P2PKH)")
			op_code2 = OPCODE_NAMES[int(hexstr[2:4],16)]
			keylen = int(hexstr[4:6],16) 
			op_codeTail2nd = OPCODE_NAMES[int(hexstr[6+keylen*2:6+keylen*2+2],16)]
			op_codeTailLast = OPCODE_NAMES[int(hexstr[6+keylen*2+2:6+keylen*2+4],16)]
			print(f"        PubkeyHash:            {hexstr[6:6+keylen*2]}")
			print(f"        Assembly:              {op_code1} {op_code2} <PubkeyHash> {op_codeTail2nd} {op_codeTailLast}")
			return hexstr	
		elif op_code1 == "OP_HASH160": #P2SHA pay to script hash 
			keylen = int(hexstr[2:4],16) 
			op_codeTail = OPCODE_NAMES[int(hexstr[4+keylen*2:4+keylen*2+2],16)]
			print("         Pubkey OP_CODE:\t " + op_code1 + " " + " " + "Bytes:%d " % keylen +\
					"tail_op_code:" +  op_codeTail + " " )
			print("        Pure Pubkey:          %s" % hexstr[4:4+keylen*2])
			return hexstr
		else: #TODO extend for multi-signature parsing 
			print("\t Need to extend multi-signatuer parsing %x" % int(hexstr[0:2],16) + op_code1)
			return hexstr
		
