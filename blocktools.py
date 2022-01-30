import io
import struct


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
	size = uint1(stream)

	if size < 0xfd:
		return size
	if size == 0xfd:
		return uint2(stream)
	if size == 0xfe:
		return uint4(stream)
	if size == 0xff:
		return uint8(stream)
	return -1

def hashStr(bytebuffer):
	return bytebuffer.hex().upper()
