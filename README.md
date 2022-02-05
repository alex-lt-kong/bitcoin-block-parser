# bitcoin-block-parser

## Introduction

This project is based on the Python2 project
[blocktools](https://github.com/tenthirtyone/blocktools) which has not been 
updated since 2018-02-02 (as of 2022-02-02)

### Changes
* Upgrade syntax to Python3. Use type hints and `assert isinstance()` to facilitate the understanding of the code.
* Show both input's public key and its corresponding wallet address.
* Clarify the unit of `Difficulty`, show both difficulty value and raw value (as number of bits).
* Show Bitcoin `Script` the same way as [Bitcoin Wiki](https://en.bitcoin.it/wiki/Script), i.e., explicity show OP_CODEs as they are.
* Revise the section from `Script` to `Assembly` to match the term used by a few online Bitcoin block explorers'.
* Show `ScriptSig`'s hex representation, so that users can cross-reference the results from this script and some online Bitcoin block explorers'.
* Lengthen method names so that one does not have to be very familiar with the code to understand the purpose of them.
* Explicitly handle endianness of bytes, which is actually a pretty confusing part of Bitcoin's block structure.
* Change formatting and indentation to make the output more structured.
* Calculate the hash of the current block.

## Sample Output

```text
Parsing blk00003.dat[5: 11]
#################### Blocks[5] BEGIN ####################

  Magic No:          0XD9B4BEF9
  Blocksize (bytes): 19827
  Curr. Block Hash:  000000000000007CA0FD3EAE2AE31A9B22641A0FE3660ACFA481D4DF32062497 (Calculated)

  ########## Block Header BEGIN ##########
    Version           1
    Prev. Block Hash  0000000000000A21907A50AF01D3EB8BB52CC0B18EDEA7FACF0DCE4B31D8932A
    Merkle Root       1DFE926405B49BB0C6204D2B093601BA7C1A189D9BA7370887432462E744FBA6
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
      Output Count:	 1
      ## Outputs[0] ##
        Value:                 5,000,100,000 Satoshi (50.001 Bitcoin)
        Script Len:            67
        OP_CODE 65 is probably obselete pay to address
        Pubkey OP_CODE:	 None Bytes:65 tail_op_code:OP_CHECKSIG 
        Pure Pubkey:	   04C33AEE0DB6314A7982626BD04C3C5A4A327F2B08AB0CF3B97832737E83165E5EBE3BAC0261C54B3D75A3884747D5FE0CD5B0CDB491A42E24EB51EA630434B80D
        ScriptPubkey(hex):     4104C33AEE0DB6314A7982626BD04C3C5A4A327F2B08AB0CF3B97832737E83165E5EBE3BAC0261C54B3D75A3884747D5FE0CD5B0CDB491A42E24EB51EA630434B80DAC
        Lock Time:	 0
    ##### Transactions[1] #####
      Transaction Version:     1
      Input Count:             1
      ## Inputs[0] ##
        Prev. Tx Hash:         5AA4E1C739DCF4E0C5D608E6DA4E4984EB418F4B2D1422D86BB24DF0513CFA50
        Transaction Out Index: 0 
        Script Length:         140
        Script:                3046022100D33332233EB2D019C8E61BA8DC99C106D37EC634677F8AAE406EA97688F2C670022100F8977A5832E8EA89029D3B60FD46E76ADDBCBDD46627D6250B4C13AEA81EB01C01
        Pubkey:              0490AAC0FF0A60DD22C9C8E5519CAD8EABFDC5F0D26350C05C36ED0239BCEA4966A1A19F126581A09FE4D23F9BC9DCEC3626DF58AD6173C7D7E85CA081D3DE73B7 (Addr: b'1P4tawEKyKUZiPMShpisQEo4xjCUC2pJn4')
        ScriptSig(hex):        493046022100d33332233eb2d019c8e61ba8dc99c106d37ec634677f8aae406ea97688f2c670022100f8977a5832e8ea89029d3b60fd46e76addbcbdd46627d6250b4c13aea81eb01c01410490aac0ff0a60dd22c9c8e5519cad8eabfdc5f0d26350c05c36ed0239bcea4966a1a19f126581a09fe4d23f9bc9dcec3626df58ad6173c7d7e85ca081d3de73b7
        Sequence:              4294967295 (== ffffffff, not in use)
      Output Count:	 1
      ## Outputs[0] ##
        Value:                 100,000,000,000 Satoshi (1000.0 Bitcoin)
        Script Len:            25
        Transaction Type:      Pay-to-PubkeyHash (P2PKH)
        PubkeyHash:            B372807DC1F43006813FE0989AB56BFBB2FA5237
        Assembly:              OP_DUP OP_HASH160 <PubkeyHash> OP_EQUALVERIFY OP_CHECKSIG
        ScriptPubkey(hex):     76A914B372807DC1F43006813FE0989AB56BFBB2FA523788AC
        Lock Time:	 0
    ##### Transactions[2] #####
      Transaction Version:     1
      Input Count:             3
      ## Inputs[0] ##
        Prev. Tx Hash:         C3B5A9BC8677ED2BA0BBA199277EC0F18BA80D8E5A57ED0FE81523CF23ED411A
        Transaction Out Index: 1 
        Script Length:         140
        Script:                30460221008F3956458CA215EFBA2B63764E78D044D2BBD48653ADF2F1E65332B0C18732A4022100AE1053885D4A84D8BA08E7C5898A6A0EE90ED7F68299081C4CF98CD72A6BC05101
        Pubkey:              04E25574D83983BF008BC7F3254844BBD0F1468D62845382EF9405412E405963501058C0F3FED12712E682CCFAF0D2A6181E81ABF7E02119A9CF38A403F7638267 (Addr: b'1MLpkfP1NhyJcueLyqgaF5XSy7BJCHaPbc')
        ScriptSig(hex):        4930460221008f3956458ca215efba2b63764e78d044d2bbd48653adf2f1e65332b0c18732a4022100ae1053885d4a84d8ba08e7c5898a6a0ee90ed7f68299081c4cf98cd72a6bc051014104e25574d83983bf008bc7f3254844bbd0f1468d62845382ef9405412e405963501058c0f3fed12712e682ccfaf0d2a6181e81abf7e02119a9cf38a403f7638267
        Sequence:              4294967295 (== ffffffff, not in use)
      ## Inputs[1] ##
        Prev. Tx Hash:         659E7EEE755CEE438A8B5653FB019490D77A96BBF2853BF15FE613A2E20D5390
        Transaction Out Index: 1 
        Script Length:         138
        Script:                304402206DB3FC79F4BAE738D8E888A28AD6C3911CF5A4D0C87E7A4C2C07D9C3A8B3718A0220462A73CDC75C01E12C0B1EC0F316ABEECD2AB99431D824501A3A6BF6D7610B9F01
        Pubkey:              04E25574D83983BF008BC7F3254844BBD0F1468D62845382EF9405412E405963501058C0F3FED12712E682CCFAF0D2A6181E81ABF7E02119A9CF38A403F7638267 (Addr: b'1MLpkfP1NhyJcueLyqgaF5XSy7BJCHaPbc')
        ScriptSig(hex):        47304402206db3fc79f4bae738d8e888a28ad6c3911cf5a4d0c87e7a4c2c07d9c3a8b3718a0220462a73cdc75c01e12c0b1ec0f316abeecd2ab99431d824501a3a6bf6d7610b9f014104e25574d83983bf008bc7f3254844bbd0f1468d62845382ef9405412e405963501058c0f3fed12712e682ccfaf0d2a6181e81abf7e02119a9cf38a403f7638267
        Sequence:              4294967295 (== ffffffff, not in use)
```
[remaining transaction data are truncated]

## References
<img src="./images/block_structure.png"></img>

* [scriptPubKey & scriptSig Explained](https://www.mycryptopedia.com/scriptpubkey-scriptsig/)
* [Litte Big Endian Converter](https://blockchain-academy.hs-mittweida.de/litte-big-endian-converter/)