import io
import struct
from hashlib import *
import base58

class Pubkey2Address:
	@staticmethod
	def SHA256D(bstr):
			return sha256(sha256(bstr).digest()).digest()

	@staticmethod
	def ConvertPKHToAddress(prefix, addr):
			data = prefix + addr
			return base58.b58encode(data + Pubkey2Address.SHA256D(data)[:4])

	@staticmethod
	def PubkeyToAddress(pubkey_hex):
			pubkey = bytearray.fromhex(pubkey_hex)
			round1 = sha256(pubkey).digest()
			h = new('ripemd160')
			h.update(round1)
			pubkey_hash = h.digest()
			return Pubkey2Address.ConvertPKHToAddress(b'\x00', pubkey_hash)


def nbits(num):
  # Convert integer to hex
  hexstr = format(num, 'x')
  first_byte, last_bytes = hexstr[0:2], hexstr[2:]
  # convert bytes back to int
  first, last = int(first_byte, 16), int(last_bytes, 16)
  return last * 256 ** (first - 3)

def difficulty(num):
  # Difficulty of genesis block / current
  return 0x00ffff0000000000000000000000000000000000000000000000000000 / nbits(num)


def uint1(stream):
	return ord(stream.read(1))

def uint2(stream):
	return struct.unpack('H', stream.read(2))[0]

def uint4(stream: io.BufferedReader):
	assert isinstance(stream, io.BufferedReader)
	return struct.unpack('I', stream.read(4))[0]
	# format string 'I' means unsigned int
	# io.BufferedReader.read(): Read and return size bytes, or...
	# So here we read 4 bytes from the stream and treat it as an unsigned integer.

def uint8(stream):
	return struct.unpack('Q', stream.read(8))[0]

def hash32(stream):
	return stream.read(32)[::-1]

def time(stream):
	time = uint4(stream)
	return time

def varint(stream):
	# seems the rule is like this:
	# * If the number < 253 (0xFD), store it in 1 byte, left-padded with zeros.
  # * If the number fits in 16 bits (but is greater than 252), store it in 3 
	#   bytes: a 1-byte value 253 (0xFD) followed by the 2 byte little-endian number.
  # * If the number fits in 32 bits (but not 8 or 16), store it in 5 bytes: 
	#   a 1-byte value 254 (0xFE) followed by the 4 byte little-endian number
	# * If the number fits in 64 bits (but not 8, 16, or 32), store it in 9 bytes:
	#   a 1-byte value 255 (0xFF) followed by the 8 byte little-endian number
	# reference: https://reference.cash/protocol/formats/variable-length-integer
	size = uint1(stream)

	if size < 0xfd: # decimal 253, binary 11111101
		return size
	if size == 0xfd: # decimal 253, binary 11111101
		return uint2(stream)
	if size == 0xfe: # decimal 254, binary 11111110
		return uint4(stream)
	if size == 0xff: # decimal 255, binary 11111111
		return uint8(stream)
	raise ValueError('Datafile seems corrupt')


def hashStr(bytebuffer):
	return bytebuffer.hex().upper()
