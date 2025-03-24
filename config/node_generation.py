import requests

from classes.node import Node
from classes.blockchain import Blockchain
from classes.block import Block
from classes.coherence_block import CoherenceBlock
from classes.transaction import Transaction

def set_blockchain(bootstrap_node):
    try:
        blockchain_response = requests.get(f'{bootstrap_node}/blockchain')
        if blockchain_response.status_code == 200:
            chain = []
            coherence_chain = []
            entangled_blocks = {}

            remote_chain = blockchain_response.json().get('chain')
            remote_coherence_chain = blockchain_response.json().get('coherence_chain')

            for block, coherence_block in zip(remote_chain, remote_coherence_chain):
                transactions = []
                
                block_transactions = block.get('transactions')
                for transaction in block_transactions:
                    transactions.append(Transaction(**transaction))

                processed_block = Block(**block)
                processed_block.transactions = block_transactions
                processed_coherence_block = CoherenceBlock(**coherence_block)

                entangled_hash = processed_coherence_block.entangled_hash
                chain.append(processed_block)
                coherence_chain.append(processed_coherence_block)
                entangled_blocks[entangled_hash] = (processed_block, processed_coherence_block)
                

            blockchain_kwargs = {
                'chain': chain,
                'coherence_chain': coherence_chain,
                'entangled_blocks': entangled_blocks,
                'current_chain_index': blockchain_response.json().get('current_chain_index'),
                'current_coherence_chain_index': blockchain_response.json().get('current_coherence_chain_index'),
                'pending_transactions': blockchain_response.json().get('pending_transactions')
            }
            blockchain = Blockchain(**blockchain_kwargs)
            return blockchain
    except requests.RequestException:
        pass
    bc_kwargs = {
        'chain': [],
        'coherence_chain': [],
        'entangled_blocks': {},
        'current_chain_index': 0,
        'current_coherence_chain_index': 0,
        'pending_transactions': [],
        'transaction_limit': 4,
        'balances': {},
        'nfts': {}
    }
    return Blockchain(**bc_kwargs)

def set_peers(bootstrap_node):
    try:   
        peers_response = requests.get(f'{bootstrap_node}/peers')
        if peers_response.status_code == 200:
            peers_data = peers_response.json()
            return peers_data
    except requests.RequestException:
        pass 
    return {}

def run_node(ip, port, url=None):
    bootstrap_node = 'http://127.0.0.1:5000'

    blockchain = set_blockchain(bootstrap_node)
    peers = set_peers(bootstrap_node)
    node_id = str(len(peers)) if isinstance(peers, dict) else '0'

    kwargs = {
        'node_id': node_id, 
        'ip':ip, 
        'port':port, 
        'url':url, 
        'blockchain':blockchain, 
        'peers':peers
        }
    node = Node(**kwargs)

    return node



