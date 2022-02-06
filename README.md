# bitcoin-block-parser

## Introduction

This project is based on the Python2 project
[blocktools](https://github.com/tenthirtyone/blocktools) which has not been 
updated since 2018-02-02 (as of 2022-02-02)

### Usage

This project depends on the block files downloaded and validated by 
[Bitcoin Core](https://bitcoin.org/en/download). 



```
python3 ./src/examine.py --help
usage: examine.py [-h] --file-path FILE-PATH [--start START] [--offset OFFSET]

optional arguments:
  -h, --help            show this help message and exit
  --file-path FILE-PATH
                        The path of blk*.dat file as managed by Bitcoin Core.
  --start START         Start index of a block withIN the given data file.
  --offset OFFSET       Offset from start.
```

Example

```
python3 ./src/examine.py --file-path=~/bitcoin/blocks/blk00003.dat --start 5 --offset=6
```

### Changes compared with [blocktools](https://github.com/tenthirtyone/blocktools)
* Upgrade syntax to Python3. Use type hints and `assert isinstance()` to facilitate the understanding of the code.
* Show both input's public key and its corresponding wallet address.
* Clarify the unit of `Difficulty`, show both difficulty value and raw value (as number of bits).
* Show Bitcoin `Script` the same way as [Bitcoin Wiki](https://en.bitcoin.it/wiki/Script), i.e., explicity show OP_CODEs as they are.
* Revise the section from `Script` to `Assembly` to match the term used by a few online Bitcoin block explorers'.
* Show `ScriptSig`'s hex representation, so that users can cross-reference the results from this script and some online Bitcoin block explorers'.
* Lengthen method names so that one does not have to be very familiar with the code to understand the purpose of them.
* Explicitly handle endianness of bytes, which is actually a pretty confusing part of Bitcoin's block structure.
* Change formatting and indentation to make the output more structured.
* Calculate and show the hash of the current block and `Merkle root`.
* Calculate and show the target hash from `Difficulty`.

### Notes

While this project does some block and transaction validations,
it is more for research purpose and is meant to be cryptographically secure.

## Sample Output

```text
Parsing blk00003.dat[5: 11]
#################### Blocks[5] BEGIN ####################

  Magic No:          0XD9B4BEF9
  Blocksize (bytes): 19827
  Curr. Block Hash:  000000000000007ca0fd3eae2ae31a9b22641a0fe3660acfa481d4df32062497 (Derived from block)
  Target Hash        0000000000000abbcf0000000000000000000000000000000000000000000000 (Derived from block)

  ########## Block Header BEGIN ##########
    Version           1
    Prev. Block Hash  0000000000000a21907a50af01d3eb8bb52cc0b18edea7facf0dce4b31d8932a
    Merkle Root Hash  1dfe926405b49bb0c6204d2b093601ba7c1a189d9ba7370887432462e744fba6 (Verified)
    Timestamp         1311020242 / 0x4e2494d2 / 2011-07-18 20:17:22 (UTC)
    Difficulty        1563028.00 (436911055 bits / 0x1a0abbcf bits)
    Nonce             1801961169
  ########## Block Header END ##########

  ########## Transaction Count: 53 ##########

  ########## Transaction Data BEGIN ##########
    ##### Transactions[0] #####
      Transaction Version:     1
      Input Count:             1
      ## Inputs[0] ##
        Coinbase Text:         0000000000000000000000000000000000000000000000000000000000000000
        Transaction Out Index: 4294967295  Coinbase with special index
        Script Length:         8
        ScriptSig(hex):        04cfbb0a1a023908
        Sequence:              4294967295 (== ffffffff, not in use)
      Output Count:            1
      ## Outputs[0] ##
        Value:                 5,000,100,000 Satoshi (50.001 Bitcoin)
        Script Len:            67
        OP_CODE 65 is probably obselete pay to address
        Pubkey OP_CODE:	 None Bytes:65 tail_op_code:OP_CHECKSIG 
        Pure Pubkey:	   04C33AEE0DB6314A7982626BD04C3C5A4A327F2B08AB0CF3B97832737E83165E5EBE3BAC0261C54B3D75A3884747D5FE0CD5B0CDB491A42E24EB51EA630434B80D
        ScriptPubkey(hex):     4104C33AEE0DB6314A7982626BD04C3C5A4A327F2B08AB0CF3B97832737E83165E5EBE3BAC0261C54B3D75A3884747D5FE0CD5B0CDB491A42E24EB51EA630434B80DAC
        Lock Time:             0
    ##### Transactions[1] #####
      Transaction Version:     1
      Input Count:             1
      ## Inputs[0] ##
        Prev. Tx Hash:         5aa4e1c739dcf4e0c5d608e6da4e4984eb418f4b2d1422d86bb24df0513cfa50
        Transaction Out Index: 0 
        Script Length:         140
        Script:                3046022100D33332233EB2D019C8E61BA8DC99C106D37EC634677F8AAE406EA97688F2C670022100F8977A5832E8EA89029D3B60FD46E76ADDBCBDD46627D6250B4C13AEA81EB01C01
        Pubkey:              0490AAC0FF0A60DD22C9C8E5519CAD8EABFDC5F0D26350C05C36ED0239BCEA4966A1A19F126581A09FE4D23F9BC9DCEC3626DF58AD6173C7D7E85CA081D3DE73B7 (Addr: b'1P4tawEKyKUZiPMShpisQEo4xjCUC2pJn4')
        ScriptSig(hex):        493046022100d33332233eb2d019c8e61ba8dc99c106d37ec634677f8aae406ea97688f2c670022100f8977a5832e8ea89029d3b60fd46e76addbcbdd46627d6250b4c13aea81eb01c01410490aac0ff0a60dd22c9c8e5519cad8eabfdc5f0d26350c05c36ed0239bcea4966a1a19f126581a09fe4d23f9bc9dcec3626df58ad6173c7d7e85ca081d3de73b7
        Sequence:              4294967295 (== ffffffff, not in use)
      Output Count:            1
      ## Outputs[0] ##
        Value:                 100,000,000,000 Satoshi (1000.0 Bitcoin)
        Script Len:            25
        Transaction Type:      Pay-to-PubkeyHash (P2PKH)
        PubkeyHash:            B372807DC1F43006813FE0989AB56BFBB2FA5237
        Assembly:              OP_DUP OP_HASH160 <PubkeyHash> OP_EQUALVERIFY OP_CHECKSIG
        ScriptPubkey(hex):     76A914B372807DC1F43006813FE0989AB56BFBB2FA523788AC
        Lock Time:             0
```
[remaining transaction data are truncated]

## References
<img src="./images/block_structure.png"></img>

* [scriptPubKey & scriptSig Explained](https://www.mycryptopedia.com/scriptpubkey-scriptsig/)
* [Litte Big Endian Converter](https://blockchain-academy.hs-mittweida.de/litte-big-endian-converter/)
* [What is Nonce and Mining Difficulty?](https://pintu.co.id/en/academy/post/what-is-nonce-and-mining-difficulty)