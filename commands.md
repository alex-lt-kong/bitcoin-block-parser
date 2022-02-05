# Commands

Common `bitcoin-cli` commands

* Get hash of the block in best-block-chain at height provided: `bitcoin-cli getblockhash [height]`
* Get header of a block (including its `merkleroot`, `previousblockhash`, `nextblockhash`) given its hash: `bitcoin-cli getblockheader [hash]`
* Returns the height of the most-work fully-validated chain: `bitcoin-cli getblockcount`