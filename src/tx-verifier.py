#!/usr/bin/python3

import io
import utils
from block import Block, BlockHeader

with open('../../../usb-decrypted/bitcoin/blocks/blk00001.dat', 'rb') as block_reader:
  	
	block_reader.seek(0, io.SEEK_END)
	fSize = block_reader.tell() - 80
	block_reader.seek(0, io.SEEK_SET)


	block = Block(block_reader)
	#block.stdout()
	block.transactions[1].stdout()
	print(block.transactions[1].get_bytes().hex())



