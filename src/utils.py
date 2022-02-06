import io
import struct
from hashlib import *
import base58
import hashlib

# * Native byte order is big-endian or little-endian, depending on the host system.
#   For example, Intel x86 and AMD64 (x86-64) are little-endian;
#   Motorola 68000 and PowerPC G5 are big-endian;
#   ARM and Intel Itanium feature switchable endianness (bi-endian).
#   Use sys.byteorder to check the endianness of your system.




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

def double_sha256(array: bytes):
	assert isinstance(array, bytes)
	return hashlib.sha256(hashlib.sha256(array).digest()).digest()

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


def read_2bytes_as_uint(reader):
	res = struct.unpack('<H', reader.read(2))[0]
	return res

def read_4bytes_as_uint(reader: io.BufferedReader) -> int:
	assert isinstance(reader, io.BufferedReader)
	res = struct.unpack('<I', reader.read(4))[0]

	# format string 'I' means unsigned int and '<' means read bytes following
	# little-endian byte order.
	# So there we io.BufferedReader.read() 4 bytes from the stream 
	# and then interpret the bytes into an unsigned integer using little-endian
	# byte order.
	# For example, if the underlying bytes are F9BEB4X9 on the filesystem
  # this function returns integer 3652501241 / 0xd9b4bef9

	assert isinstance(res, int)
	# Python does not have signed and unsigned integers as data types. However,
	# In Python, value of an integer is not restricted by the number of bits and
	# can expand to the limit of the available memory.
	return res

def uint8(stream):
	return struct.unpack('Q', stream.read(8))[0]

def read_32bytes(reader, to_big_endian=False):
	assert isinstance(reader, io.BufferedReader)
	# My understanding is that Bitcoin Core stores data in little-endian order,
	# slice syntax: array[ <first element to include> : <first element to exclude> : <step>]
	# so if we want Big Endian, we use step=-1
	array = reader.read(32)[::-1 if to_big_endian else 1]
	assert isinstance(array, bytes)
	return array

def read_bytes_as_variable_int(reader: io.BufferedReader):
	assert isinstance(reader, io.BufferedReader)
	# seems the rule is like this:
	# * If the number < 253 (0xFD), store it in 1 byte, left-padded with zeros.
  # * If the number fits in 16 bits (but is greater than 252), store it in 3 
	#   bytes: a 1-byte value 253 (0xFD) followed by the 2 byte little-endian number.
  # * If the number fits in 32 bits (but not 8 or 16), store it in 5 bytes: 
	#   a 1-byte value 254 (0xFE) followed by the 4 byte little-endian number
	# * If the number fits in 64 bits (but not 8, 16, or 32), store it in 9 bytes:
	#   a 1-byte value 255 (0xFF) followed by the 8 byte little-endian number
	# reference: https://reference.cash/protocol/formats/variable-length-integer
	size = ord(reader.read(1))

	if size < 0xfd: # decimal 253, binary 11111101
		return size
	if size == 0xfd: # decimal 253, binary 11111101
		return read_2bytes_as_uint(reader)
	if size == 0xfe: # decimal 254, binary 11111110
		return read_4bytes_as_uint(reader)
	if size == 0xff: # decimal 255, binary 11111111
		return uint8(reader)
	raise ValueError('Datafile seems corrupt')


def bytes_to_hex_string(array: bytes, switch_endianness=False) -> str:
	assert isinstance(array, bytes)
	return array[::-1 if switch_endianness else 1].hex().upper()
	# array[ <first element to include> : <first element to exclude> : <step>]
	# step=-1 basically means we reverse the order of the bytes.


def get_bytes_from_variable_int(varint: int) -> bytes:
	'''
	The reverse of read_bytes_as_variable_int(): we get the bytes representation
	of a variable-length integer
	'''

	if varint < 0xfd:
		varint_bytes = varint.to_bytes(1, byteorder='little')
	elif varint < 2**16: # Not quite sure if there should be < or <= ...
		varint_bytes = (0xfd).to_bytes(1, byteorder='little') + struct.pack("<H", varint)
	elif varint < 2**32:
		varint_bytes = (0xfe).to_bytes(1, byteorder='little') + struct.pack("<I", varint) 
	elif varint < 2**64:
		varint_bytes = (0xff).to_bytes(1, byteorder='little') + struct.pack("Q", varint)
	else:
		raise ValueError(f'{varint} seems invalid for the purpose of Bitcoin')
	return varint_bytes

def get_target_hash_by_difficulty(difficulty: bytes) -> int:
	"""
	Calculate target hash given Difficulty as Little-Endian bytes. A valid
	hash generated from a given nonce should always smaller than the target hash.
	The formula	is directly from the semi-official Bitcoin Wiki:
	https://en.bitcoin.it/wiki/Difficulty#How_is_difficulty_stored_in_blocks.3F
	"""
	assert isinstance(difficulty, bytes) and len(difficulty) == 4
	exponent = difficulty[3]
	coef = int.from_bytes(difficulty[0:3], byteorder='little')
	res = coef * 2**(8*(exponent - 3))
	assert isinstance(res, int)
	return res

def convert_endianness(array: bytes):
	"""
	Switch between big-endian order and little-endian order. 
	Bitcoin stores bytes in little-endian byte order but we human beings are 
	more comfortable with big-endian one. Therefore, we convert the endianness
	before showing values to users.
	Note that bytes objects are immutable
	"""
	assert isinstance(array, bytes)
	return array[::-1]