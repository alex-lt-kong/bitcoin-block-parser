from blocktools import *
from opcode import *
from datetime import datetime

import binascii
import hashlib
import io
import time

class BlockHeader:

	def __init__(self, block_reader):
		# The following is also the order of bytes of a blk*.dat file.
		self.version = read_4bytes_as_uint(block_reader)
		self.prev_blk_hash = bytes_to_hex_string(read_32bytes(block_reader,
		 																											to_big_endian=True))
		self.merkle_root = bytes_to_hex_string(read_32bytes(block_reader, 
																												to_big_endian=True))
		# the Merkle root is the hash of all the hashes of all the transactions in the block. 
		self.timestamp = read_4bytes_as_uint(block_reader)
		self.bits = read_4bytes_as_uint(block_reader)
		self.nonce = read_4bytes_as_uint(block_reader)

	def get_current_block_hash(self, ):
		# The idea is that, we firstly convert strings back to bytes using
		# bytes.fromhex() and then we convert bytes from Big-Endian order back
		# to Little-Endian order with [::-1], so that the order of bytes are exactly 
		# the same as those stored in blk*.dat file

		assert self.version == 1 or self.version == 2
		
		header = (bytes.fromhex(f"0000000{self.version}")[::-1]+
							bytes.fromhex(self.prev_blk_hash)[::-1]+
							bytes.fromhex(self.merkle_root)[::-1]+
							self.timestamp.to_bytes(4, byteorder='little')+ # 4 bytes out, 4 bytes in
							self.bits.to_bytes(4, byteorder='little')+			# Little-Endian out, Little-Endian in
							self.nonce.to_bytes(4, byteorder='little'))

		hash = hashlib.sha256(hashlib.sha256(header).digest()).digest()
		return bytes_to_hex_string(hash, switch_endianness=True)


	def toString(self):
		print(f"    Version           {self.version}")
		print(f"    Prev. Block Hash  {self.prev_blk_hash}")
		print(f"    Merkle Root       {self.merkle_root}") 
		print(f"    Timestamp         {self.timestamp} / 0x{self.timestamp:x} / {datetime.utcfromtimestamp(self.timestamp)} (UTC)")
		print(f"    Difficulty        {difficulty(self.bits):.2f} ({self.bits} bits / 0x{self.bits:x} bits)")
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
			self.magic_number = read_4bytes_as_uint(block_reader)
			self.block_size = read_4bytes_as_uint(block_reader)
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
			self.transaction_count = varint(block_reader)
			self.transactions = []

			for i in range(0, self.transaction_count):
				transaction = Transaction(block_reader)
				transaction.seq = i 
				self.transactions.append(transaction)
		else:
			self.continue_parsing = False
						

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

	def toString(self):
		print("")
		print(f"  Magic No:          {hex(self.magic_number).upper()}") 
		assert hex(self.magic_number).upper() == "0XD9B4BEF9"
		# seems this is something hard-coded		
		print(f"  Blocksize (bytes): {self.block_size}")
		print(f"  Curr. Block Hash:  {self.block_header.get_current_block_hash()} (Calculated)")
		print("")
		print("  ########## Block Header BEGIN ##########")
		self.block_header.toString()
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
		self.version = read_4bytes_as_uint(blockchain)
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
		self.lockTime = read_4bytes_as_uint(blockchain)

		
	def toString(self):
		print(f"    ##### Transactions[{self.seq}] #####")
		print(f"      Transaction Version:     {self.version}")
		print(f"      Input Count:             {self.input_count}")
		for i in range(len(self.inputs)):
			self.inputs[i].toString(i)

		print(f"      Output Count:\t {self.outCount}")
		for i in range(len(self.outputs)):
			self.outputs[i].toString(i)
		print(f"        Lock Time:\t {self.lockTime}")

class txInput:
	def __init__(self, blockchain: io.BufferedReader):
		assert isinstance(blockchain, io.BufferedReader)
		self.prev_transaction_hash = read_32bytes(blockchain)
		self.txOutId = read_4bytes_as_uint(blockchain)
		self.script_length = varint(blockchain)
		self.scriptSig = blockchain.read(self.script_length)
		self.seqNo = read_4bytes_as_uint(blockchain)

	def toString(self, idx):
		print(f"      ## Inputs[{idx}] ##")
		print(f"        Transaction Out Index: {self.decodeOutIdx(self.txOutId)}")
		print(f"        Script Length:         {self.script_length}")
		self.decodeScriptSig(self.scriptSig)
		print(f"        ScriptSig(hex):        {self.scriptSig.hex()}")
		
	  #	assert self.seqNo == 4294967295
		print(f"        Sequence:              {self.seqNo} (== ffffffff, not in use)")

	def decodeScriptSig(self, data):
		hexstr = bytes_to_hex_string(data)
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
			print(f"        Pubkey:              {pubkey} (Addr: {Pubkey2Address.PubkeyToAddress(pubkey)})")
#		return hexstr

	def decodeOutIdx(self,idx):
		s = ""
		if(idx == 0xffffffff):
			s = " Coinbase with special index"
			print(f"        Coinbase Text:         {bytes_to_hex_string(self.prev_transaction_hash)}")
		else: 
			print(f"        Prev. Tx Hash:         {bytes_to_hex_string(self.prev_transaction_hash)}")
		return f"{int(idx)} {s}"
		

class txOutput:
	def __init__(self, blockchain):	
		self.value = uint8(blockchain)
		self.scriptLen = varint(blockchain)
		self.pubkey = blockchain.read(self.scriptLen)

	def toString(self, idx):
		print(f"      ## Outputs[{idx}] ##")
		print(f"        Value:                 {self.value:,} Satoshi ({self.value / 100_000_000} Bitcoin)")
		print(f"        Script Len:            {self.scriptLen}")
		print(f"        ScriptPubkey(hex):     {self.decodeScriptPubkey(self.pubkey)}")
	def decodeScriptPubkey(self,data):
		hexstr = bytes_to_hex_string(data)
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
			print("        Pure Pubkey:\t     %s" % hexstr[4:4+keylen*2])
			return hexstr
		else: #TODO extend for multi-signature parsing 
			print("\t Need to extend multi-signatuer parsing %x" % int(hexstr[0:2],16) + op_code1)
			return hexstr
		
