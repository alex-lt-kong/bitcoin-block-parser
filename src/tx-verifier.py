#!/usr/bin/python3

import io
import utils
from block import Block, BlockHeader

with open('../../../usb-decrypted/bitcoin/blocks/blk00001.dat', 'rb') as block_reader:
  	
	block_reader.seek(0, io.SEEK_END)
	fSize = block_reader.tell() - 80
	block_reader.seek(0, io.SEEK_SET)


	block = Block(block_reader)

block.transactions[1].stdout()
print(block.transactions[1].get_bytes().hex())

raw_bytes = block.transactions[1].get_bytes()

# The following cryptic code implements this step-to-step guide on
# transaction verification:
# https://bitcoin.stackexchange.com/questions/72657/signature-verification-in-python-using-compressed-public-key
part_one = 4 + 1 + 32 + 4
# 4: Version
# 1: Input Count
# 32: Prev. hash
# 4: Output Index
target_bytes = raw_bytes[:part_one]
print(f"target_bytes.hex(): {target_bytes.hex()}")

target_bytes += bytes.fromhex('1976a914b0d7b19af5aee9a07ef6a147a0ec6a4e1fdf9e7188ac')
print(f"target_bytes.hex(): {target_bytes.hex()}")

target_bytes += raw_bytes[part_one + 1 + raw_bytes[part_one]:]
print(f"target_bytes.hex(): {target_bytes.hex()}")

target_bytes += bytes.fromhex('01000000')
import hashlib
import binascii
hashval = binascii.hexlify(hashlib.sha256(target_bytes).digest())
txn_sha256 = bytes.decode(hashval)
print("txn_sha256 = %s" % (txn_sha256))

import ecdsa

sig_b = bytes.fromhex(block.transactions[1].inputs[0].signature)
txn_sha256_b = bytes.fromhex(txn_sha256)
vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(block.transactions[1].inputs[0].pubkey),curve=ecdsa.SECP256k1)
if vk.verify(sig_b, txn_sha256_b, hashlib.sha256) == True: # True
        print("Signature is Valid")
else:
        print("Signature is not Valid")


#0100000001959af1e21ddcb1fe07a2c8de6c28a1645a3d586c8aa4541b697791f27548ffa3000000001976a914b0d7b19af5aee9a07ef6a147a0ec6a4e1fdf9e7188acffffffff02809dc29c000000001976a9148fb7de32f84e119f6d4d75ecb9ad53dfae51b3a488acc0e27b0e000000001976a9140635412d152fe80abbdf71e73ba569abe28dd92288ac00000000
#0100000001959af1e21ddcb1fe07a2c8de6c28a1645a3d586c8aa4541b697791f27548ffa3000000001976a914b0d7b19af5aee9a07ef6a147a0ec6a4e1fdf9e7188acffffffff02809dc29c000000001976a9148fb7de32f84e119f6d4d75ecb9ad53dfae51b3a488acc0e27b0e000000001976a9140635412d152fe80abbdf71e73ba569abe28dd92288ac0000000001000000

