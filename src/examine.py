#!/usr/bin/python3

from blocktools import *
from block import Block, BlockHeader

import argparse
import io
import os
import sys



def parse(block_reader: io.BufferedReader, start: int, offset: int):
	assert isinstance(block_reader, io.BufferedReader)
	print('Parsing Block Chain block head, transaction etc.')
	continue_parsing = True
	counter = 0
	block_reader.seek(0, io.SEEK_END)
	# SEEK_END: seek from end and offset is 0,
	# so it just means we set the stream position to the end
	fSize = block_reader.tell() - 80 #Minus last Block header size for partial file
	block_reader.seek(0, io.SEEK_SET)
	# SEEK_SET: seek from the start of the stream position
	while continue_parsing:
		block = Block(block_reader)
		continue_parsing = block.continue_parsing
		counter += 1

		if counter <= start:
			continue

		if continue_parsing:
			print(f"#################### Blocks[{counter-1}] BEGIN ####################")
			block.toString() # print the block as well
			print(f"#################### Blocks[{counter-1}] END ####################\n")
		
		if counter >= start + offset:
			continue_parsing = False

	print('')
	print('Reached End of Field')
	print(f"Parsed {counter} blocks")

def main():

	ap = argparse.ArgumentParser()
	ap.add_argument('--file-path', dest='file-path', required=True, help="The path of blk*.dat file as used by Bitcoin Core.")
	ap.add_argument('--start', dest='start', default=0, help="Index of a block withIN the given data file.")
	ap.add_argument('--offset', dest='offset', default=-1, help="Offset from start.")
	args = vars(ap.parse_args())
	file_path = str(args['file-path'])
	start = int(args['start'])
	offset = int(args['offset'])

	if os.path.isfile(file_path) is False:
		raise FileNotFoundError(f"[{file_path}] does not exist")
	print(f"Parsing {os.path.basename(file_path)}[{start}: {start + offset}]")
	with open(file_path, 'rb') as block_reader:
		# rb: Opens the file as read-only in binary format and starts reading from
		# the beginning of the file.
		parse(block_reader, start=start, offset=offset)



if __name__ == '__main__':
  main()
