#!/usr/bin/python3

from blocktools import *
from block import Block, BlockHeader

import io
import sys



def parse(blockchain: io.BufferedReader, block_no: int):
	assert isinstance(blockchain, io.BufferedReader)
	print('Parsing Block Chain block head, transaction etc.')
	continue_parsing = True
	counter = 0
	blockchain.seek(0, io.SEEK_END)
	# SEEK_END: seek from end and offset is 0,
	# so it just means we set the stream position to the end
	fSize = blockchain.tell() - 80 #Minus last Block header size for partial file
	blockchain.seek(0, io.SEEK_SET)
	# SEEK_SET: seek from the start of the stream position
	while continue_parsing:	
		block = Block(blockchain)
		continue_parsing = block.continue_parsing
		counter += 1
		print(f"#################### Block counter No. {counter} BEGIN" \
		      f"/第{counter}号区块开始 ####################")
		if continue_parsing:
			block.toString() # print the block as well
		
		print(f"#################### Block counter No. {counter} END" \
		      f"/第{counter}号区块结束 ####################\n")
		if counter >= block_no and block_no != 0xFF:
			continue_parsing = False

	print('')
	print('Reached End of Field')
	print(f"Parsed {counter} blocks")

def main():
	if len(sys.argv) < 2:
		print('Usage: sight.py filename [N]')
	else:
		block_no = 0xFF #255
		if(len(sys.argv) == 3):
			block_no = int(sys.argv[2])
			print(f"Parsing {block_no} blocks")
		with open(sys.argv[1], 'rb') as blockchain:
			parse(blockchain, block_no)



if __name__ == '__main__':
  main()
