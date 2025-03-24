from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from coincurve import PublicKey

import logging
import traceback

from classes.block import Block
from classes.coherence_block import CoherenceBlock
from classes.consensus import EntanglementConsensus
from classes.transaction import Transaction
from classes.zero_node import ZeroNode
from classes.wallet import Wallet

logging.basicConfig(
    level= logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('node_logs.log')
    ]
)

logger = logging.getLogger(__name__)

class Blockchain(BaseModel):
    chain: Optional[List[Block]] = Field(default_factory=list)
    coherence_chain: Optional[List[CoherenceBlock]] = Field(default_factory=list)
    entangled_blocks: Optional[Dict[str, tuple[Block, CoherenceBlock]]] = Field(default_factory=dict)
    current_chain_index: Optional[int] = 0
    current_coherence_chain_index: Optional[int] = 0
    pending_transactions: Optional[List[Transaction]] = Field(default_factory=list)
    transaction_limit: Optional[int] = 4
    balances: Optional[Dict[str, Dict[str, float]]] = Field(default_factory=dict)
    nfts: Optional[Dict[str, Dict[str, Any]]] = Field(default_factory=Dict)
    consensus: Any = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.consensus is None:
            self.consensus = EntanglementConsensus()
        if not self.chain:
            self.create_genesis_blocks()

    # Genesis functions

    def create_genesis_blocks(self):
        """
        Creates the genesis blocks for the blockchain

        Returns:
            None

        Workflow:
            1. Create the genesis transaction
            2. Create the genesis block
            3. Create the genesis coherence block
            4. Entangle the blocks

        Security:
            The entanglenment process is a critical part of the blockchain, if the entanglement fails the block will not be validated

        Recommendation:
            If the entanglement fails, restart the network
        """
        try:
            logger.info('Creating Genesis Blocks')
            kwargs = {
                'index': self.current_chain_index, 
                'previous_hash': "0", 
                'transactions': [self.create_genesis_transaction()]
                }
            epr_block = Block(**kwargs)
            zero_node = ZeroNode()
        
            epr_coherence_block = self.create_coherence_block(epr_block, zero_node.to_dict())

            epr_block.coherence_block_hash = epr_coherence_block.hash

            entangled_hash = self.consensus.entangle_blocks(epr_block, epr_coherence_block)

            epr_coherence_block.entangled_hash = entangled_hash

            if self.consensus.is_valid_block(epr_block, epr_coherence_block, entangled_hash):
                logger.info(f'Mining blocks')
                self.chain.append(epr_block)
                self.coherence_chain.append(epr_coherence_block)
                self.current_chain_index += 1
                self.current_coherence_chain_index += 1
                self.entangled_blocks[entangled_hash] = (epr_block, epr_coherence_block)
                logger.info(f'ERP Block: {epr_block.to_dict()}, ERP Coherence Block: {epr_coherence_block.to_dict()}, Entangled Hash: {entangled_hash}')
            else:
                self.entangled_blocks.pop(entangled_hash, None)
                logger.error('EPR Block and EPR Coherence Block Entanglement Failed, Please restart the network')
        except Exception as e:
            logger.error(f'Error creating genesis blocks: {e}\n{traceback.format_exc()}')

    def create_genesis_transaction(self) -> Transaction:
        """
        Creates the genesis transaction for the blockchain

        Returns:
            Transaction: The genesis transaction

        Workflow:
            1. Create a new wallet
            2. Create a new transaction
            3. Sign the transaction
            4. Verify the signature

        Security:
            The genesis transaction is a critical part of the blockchain, if the signature is not verified the block will not be validated

        Recommendation:
            If the signature is not verified, restart the network
        """
        try:
            logger.info(f'Creating genesis wallet')
            genesis_wallet = Wallet()
            if genesis_wallet:
                logger.info(f'Genesis wallet created')
            else:
                logger.warning(f'Genesis wallet not created')
                return None
            
            logger.info(f'Creating genesis transaction')
            kwargs = {
                'sender': '0', 
                'receiver': '0', 
                'amount': 0, 
                'contract_code': None,
                'nonce': 0
                }
            genesis_transaction = Transaction(**kwargs)

            if genesis_transaction:
                logger.info(f'Genesis transaction created, signing transaction')
                r, s, v = genesis_wallet.sign_transaction(genesis_transaction.hash)
                if r is None or s is None or v is None:
                    logger.warning(f'Genesis transaction not signed')
                    return None
                genesis_transaction.r = r
                genesis_transaction.s = s
                genesis_transaction.v = v
                genesis_transaction.public_key = genesis_wallet.public_key.hex()
                logger.info(f'Genesis transaction signed, verifying signature')
                if not genesis_wallet.verify_signature(genesis_transaction.r, genesis_transaction.s, genesis_transaction.v, genesis_transaction.hash):
                    logger.warning(f'Genesis transaction signature not verified')
                    return None
                logger.info(f'Genesis transaction verified')
                return genesis_transaction
            logger.warning(f'Genesis transaction not created')
            return None
        except Exception as e:
            logger.error(f'Error creating genesis transaction: {e}\n{traceback.format_exc()}')

    # Block functions

    def create_block(self, node):
        """
        Creates a new block for the blockchain

        Returns:
            Block: The new block
            CoherenceBlock: The new coherence block
            str: The entangled hash

        Workflow:
            1. Check if there are enough transactions to create a block
            2. Create a new block
            3. Create a new coherence block
            4. Entangle the blocks

        Security:
            The entanglenment process is a critical part of the blockchain, if the entanglement fails the block will not be validated

        Recommendation:
            If the entanglement fails, restart the network
        """
        try:
            if len(self.pending_transactions) < self.transaction_limit:
                logger.error(f'Not enough transactions available to create a block')
                return

            logger.info(f'Creating block')
            previous_block = self.chain[-1] if self.chain else None
            previous_hash = previous_block.hash if previous_block else '0'

            kwargs = {
                'index': self.current_chain_index,
                'previous_hash': previous_hash,
                'transactions': self.pending_transactions
            }
            block = Block(**kwargs)

            if block:
                logger.info(f'Block created: {block}')

                coherence_block = self.create_coherence_block(block, node)

                if coherence_block is None:
                    logger.warning('Without coherence block the block could not be validated')
                    return None, None, None

                block.coherence_block_hash = coherence_block.hash

                entangled_hash = self.consensus.entangle_blocks(block, coherence_block)

                coherence_block.entangled_hash = entangled_hash

                return block, coherence_block, entangled_hash
            
            logger.warning(f'Blocks not created')
            return None, None, None
        except Exception as e:
            logger.error(f'Error creating block: {e}\n{traceback.format_exc()}')
            
    def create_coherence_block(self, block: Block, node: dict) -> CoherenceBlock:
        """
        Creates a new coherence block for the blockchain

        Returns:
            CoherenceBlock: The new coherence block
        """
        try:
            logger.info(f'Creating coherence block')
            previous_coherence_block = self.coherence_chain[-1] if self.coherence_chain else None
            previous_coherence_block_hash = previous_coherence_block.hash if previous_coherence_block else "0"
            kwargs = {
                'index': self.current_coherence_chain_index,
                'previous_hash': previous_coherence_block_hash,
                'block_hash': block.hash,
                'node_key': node.get('key'),
                'entangled_node_key': node.get('entangled_pair_key'),
                'node_id': node.get('node_id'),
                'entangled_node_id': node.get('entangled_pair_id')
            }
            coherence_block = CoherenceBlock(**kwargs)
            if coherence_block:
                logger.info(f'Coherence block created: {coherence_block}')
                return coherence_block
            logger.warning(f'Coherence block not created')
            return None
        except Exception as e:
            logger.error(f'Error creating coherence block: {e}\n{traceback.format_exc()}')

    # Balance functions

    def update_balances(self, qtx: Transaction):
        """
        Updates the balances of the blockchain

        Args:
            qtx (Transaction): The transaction to update the balances

        Returns:
            None
        """
        self.balances.setdefault(qtx.sender, {'native': 0.0})
        self.balances.setdefault(qtx.receiver, {'native': 0.0})

        if self.balances[qtx.sender]['native'] >= qtx.amount:
            self.balances[qtx.sender] -= qtx.amount
            self.balances[qtx.receiver] += qtx.amount

    # NFT functions

    def update_nfts_balances(self, qtx: Transaction):
        """
        Updates the NFTs balances of the blockchain
        """
        self.nfts.setdefault(qtx.sender, {})
        self.nfts.setdefault(qtx.receiver, {})

        if qtx.contract_code:
            self.nfts[qtx.sender].pop(qtx.contract_code, None)  
            self.nfts[qtx.receiver][qtx.contract_code] = qtx.amount

    # Wallet functions

    def create_wallet(self) -> Wallet:
        """
        Creates a new wallet instance
        
        Returns:
            Wallet: A new wallet instance

        Security:
            This method should be used with caution as the wallet is a sensitive piece of information

        Recommendation:
            Store the wallet in a secure location
        """
        return Wallet()
    
    def recover_wallet_from_recovery_key(self, recovery_key: str, passphrase: str) -> Wallet:
        """
        Recovers a wallet from a recovery key

        Args:
            recovery_key (str): The recovery key
            passphrase (str): The passphrase

        Returns:
            Wallet: The recovered wallet

        Security:
            This method should be used with caution as the recovery key is a sensitive piece of information

        Recommendation:
            Store the recovery key in a secure location
        """
        return Wallet.from_recovery_key(recovery_key=recovery_key, passphrase=passphrase)
    
    def recover_wallet_from_mnemonic(self, mnemonic: str, passphrase: str) -> Wallet:
        """
        Recovers a wallet from a mnemonic

        Args:
            mnemonic (str): The mnemonic
            passphrase (str): The passphrase

        Returns:
            Wallet: The recovered wallet

        Security:
            This method should be used with caution as the mnemonic is a sensitive piece of information

        Recommendation:
            Store the mnemonic in a secure location
        """
        return Wallet(mnemonic=mnemonic, passphrase=passphrase)

    def get_recovery_key(self, wallet: Wallet) -> str:
        """
        Gets the recovery key from a wallet

        Args:
            wallet (Wallet): The wallet

        Returns:
            str: The recovery key

        Security:
            This method should be used with caution as the recovery key is a sensitive piece of information

        Recommendation:
            Store the recovery key in a secure location
        """
        recovery_key = wallet.get_recovery_key()
        wallet.wipe()
        return recovery_key

    def to_dict(self) -> dict:
        return {
            'chain': [block.to_dict() for block in self.chain] if self.chain else [],
            'coherence_chain': [coherence_block.to_dict() for coherence_block in self.coherence_chain] if self.coherence_chain else [],
            'entangled_blocks': self.entangled_blocks,
            'current_chain_index': self.current_chain_index,
            'current_coherence_chain_index': self.current_coherence_chain_index,
            'pending_transactions': [transaction.to_dict() for transaction in self.pending_transactions] if self.pending_transactions else [],
            'transaction_limit': self.transaction_limit
        }
