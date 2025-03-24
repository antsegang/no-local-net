import hashlib
import random
import requests
import time
import logging
import traceback
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel 
from typing import Optional, Dict, Any

from classes.blockchain import Blockchain
from classes.transaction import Transaction
from classes.block import Block
from classes.coherence_block import CoherenceBlock
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

class Node(BaseModel):
    node_id: str
    ip: str
    port: int
    url: Optional[str] = None
    blockchain: Optional[Blockchain] = None
    peers: Optional[Dict[str, str]] = None
    entangled_pair_id: Optional[str] = None
    key: Optional[str] = None
    entangled_pair_key: Optional[str] = None
    consensus_predictions: Dict[str, int] = {}
    prediction_scores: Dict[str, int] = {}
    actual_block: Optional[Block] = None
    actual_coherence_block: Optional[CoherenceBlock] = None
    actual_entangled_hash: Optional[str] = None
    penalized_nodes: Optional[Dict[str, int]] = {}
    times_that_nodes_were_penalized: Optional[Dict[str, int]] = {}
    max_penalization_time: Optional[int] = 600
    max_penalties: Optional[int] = 3

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url = self.url or f'http://{self.ip}:{self.port}'
        self.peers = self.peers or {}
        if self.blockchain is None:
            self.blockchain = Blockchain()
        logger.info(f"Node {self.node_id} initialized with IP {self.ip} and port {self.port}")

        self.register_peer()

    # Peers functions

    def register_peer(self):
        try:
            logger.info(f'Registering peer {self.node_id}')
            self.peers[self.node_id] = self.url
            self.broadcast_peers()
        except Exception as e:
            logger.error(f'Failed to register peer {self.node_id}: {e}\n{traceback.format_exc()}')

    def broadcast_peers(self):
        try:
            peers = jsonable_encoder(self.peers)
            for peer_id, peer_url in self.peers.items():
                if peer_id != self.node_id:
                    try:
                        logger.info(f'Broadcasting peers to {peer_id}')
                        response = requests.post(f'{peer_url}/receive_peers', json=peers)
                        if response.status_code == 200:
                            logger.info(f'Peers synchronized with {peer_id}')
                        else:
                            logger.warning(f'Failed to sync with {peer_id}. Status Code: {response.status_code}')
                    except requests.Timeout:
                        logger.error(f'Timeout error: Could not sync with peer {peer_id}')
                    except requests.ConnectionError:
                        logger.error(f'Connection error: Could not reach peer {peer_id}')
                    except requests.RequestException as e:
                        logger.error(f'Unexpected error broadcasting peers to peer {peer_id}: {e}\n{traceback.format_exc()}') 
        except Exception as e:
                    logger.error(f'Error broadcasting peers: {e}\n{traceback.format_exc()}')

    def receive_peers(self, peers):
        try:
            if peers:
                for peer_id, peer_url in peers.items():
                    if peer_id not in self.peers:
                        logger.info(f'Receiving peer {peer_id}')
                        self.peers[peer_id] = peer_url
                        logger.info(f'peer {peer_id} added')
        except Exception as e:
            logger.error(f'Failed to receive peers: {e}\n{traceback.format_exc()}')

    # Entanglement key functions

    def generate_entanglement_key(self):
        try:
            logger.info(f'Generating entanglement key for current node')
            raw_key =  hashlib.sha256(str(self.node_id).encode('utf-8') + str(self.entangled_pair_id).encode('utf-8') + str(random.randint(1000, 9999)).encode('utf-8')).hexdigest()
            self.key = int(raw_key, 16) % 100000
            if self.broadcast_key(jsonable_encoder(self.key)):
                return True
        except Exception as e:
            logger.error(f'Failed to generate entanglement key: {e}\n{traceback.format_exc()}')

    def broadcast_key(self, key):
        try:
            logger.info('Broadcasting entanglement key to pair')
            pair_url = self.peers[self.entangled_pair_id]
            try:
                response = requests.post(f'{pair_url}/receive_pair_key', json={"key": key})
                if response.status_code == 200:
                    logger.info('Entangled Key synchronized with pair')
                    return True
                else:
                    logger.warning(f'Failed to sync entangled key with pair. Status Code: {response.status_code}')
            except requests.Timeout:
                logger.error(f'Timeout error: Could not sync with pair')
            except requests.ConnectionError:
                logger.error(f'Connection error: Could not reach pair')
            except requests.RequestException as e:
                logger.error(f'Unexpected error entangling with pair: {e}\n{traceback.format_exc()}') 
        except Exception as e:
            logger.error(f'An error occurs trying to connect pair: {e}\n{traceback.format_exc()}')
            return False
        
    def receive_key(self, key):
        try:
            logger.info('Receiving entanglement key from pair')
            self.entangled_pair_key = key
        except Exception as e:
            logger.error(f'Failed to receive entanglement key from pair: {e}\n{traceback.format_exc()}')
    
    # Pair functions
  
    def find_pair(self):
        try:
            if self.entangled_pair_id:
                logger.info('Node already entangled')
                return HTTPException(status_code=423, detail='Node already entangled')
            
            unentangled_peers = []
            selected_peer = None
        
            for peer_id, peer_url in self.peers.items():
                if peer_id !=  self.node_id:
                    try:
                        logger.info(f'Getting info from peer {peer_id}')
                        response = requests.get(
                            f'{peer_url}/node_info',
                            timeout=5
                            )
                        if response.status_code == 200:
                            logger.info(f'Info got from peer {peer_id}, verifying entangled pair id')
                            remote_data = response.json()
                            remote_entangled_pair_id = remote_data.get('entangled_pair_id')

                            if not remote_entangled_pair_id:
                                unentangled_peers.append(peer_id)
                                logger.info(f'Peer {peer_id} added to unentangled peers')
                        else:
                            logger.warning(f'Failed to get info from peer {peer_id}. Status Code: {response.status_code}')
                    except requests.Timeout:
                        logger.error(f'Timeout error: Could not sync  with peer {peer_id}')
                    except requests.ConnectionError:
                        logger.error(f'Connection error: Could not reach peer {peer_id}')
                    except requests.RequestException as e:
                        logger.error(f'Unexpected error getting info from peer {peer_id}: {e}\n{traceback.format_exc()}')
            if len(unentangled_peers) <= 0:
                logger.info(f'There is no peers availabe for entanglement request')
                return HTTPException(status_code=404, detail='There is no peers availabe for entanglement request')
            logger.info(f'Selecting random peer from unentangled peers list')
            random_selection = random.randint(0, len(unentangled_peers) - 1)
            selected_peer = unentangled_peers[random_selection]
            logger.info(f'Peer selected: Peer {selected_peer}')
            self.entangled_pair_id = selected_peer
            logger.info(f'Entangling with pair {selected_peer}')

            try:
                reponse = requests.post(
                    f'{self.peers[selected_peer]}/entanglement_request',
                    json={'remote_peer_id': self.node_id},
                    timeout=5
                    )
                if reponse.status_code == 200:
                    logger.info(f'Entangled with pair {selected_peer}')
                    return HTTPException(status_code=200, detail=f'Entangled with pair {selected_peer}')
            except requests.Timeout:
                logger.error(f'Timeout error: Could not sync  with peer {selected_peer}')
            except requests.ConnectionError:
                logger.error(f'Connection error: Could not reach peer {selected_peer}')
            except requests.RequestException as e:
                logger.error(f'Unexpected error getting info from peer {selected_peer}: {e}\n{traceback.format_exc()}')  
        except Exception as e:
            logger.error(f'An error occurs trying to connect node {selected_peer}: {e}\n{traceback.format_exc()}')

    def entanglement_request(self, remote_peer_id):
        try:
            if self.entangled_pair_id:
                logger.info(f'Current node already entangled')
                return HTTPException(status_code=423, detail='Current node already entangled')
            if remote_peer_id not in self.peers:
                logger.error(f'Peer {remote_peer_id} not found in peers list')
                return HTTPException(status_code=404, detail=f'Peer not found in peers list')
            if self.accept_entanglement(remote_peer_id) == True:
                self.entangled_pair_id = remote_peer_id
                logger.info(f'Entangled with pair {remote_peer_id}')
                return HTTPException(status_code=200, detail=f'Entangled with pair {remote_peer_id}')
            else:
                logger.info(f'Failed to entangle with pair {remote_peer_id}')
                return HTTPException(status_code=400, detail=f'Failed to entangle with pair {remote_peer_id}')
        except Exception as e:
            logger.error(f'Failed to pair with peer {remote_peer_id}: {e}\n{traceback.format_exc()}')

    def accept_entanglement(self, remote_peer_id):
        try:
            pair_url = self.peers[remote_peer_id]
            if not pair_url:
                logger.error(f'Peer {remote_peer_id} not found in peers list')
                return False
            try:
                response = requests.get(
                    f'{pair_url}/node_info',
                    timeout=5
                    )
                logger.info(f'Getting info from peer {remote_peer_id}')
                if response.status_code == 200:
                    logger.info(f'Info got from peer {remote_peer_id}, trying to entangle')
                    remote_data = response.json()
                    if remote_data.get('entangled_pair_id') == self.node_id:
                        logger.info(f'The entangled pair id of peer {remote_peer_id} matches the current node id, entangling')
                        return True
                    logger.info(f'Different entangled pair id from peer {remote_peer_id}, finding new pair')
                    return False
                else:
                    logger.warning(f'Failed to entangle with peer {remote_peer_id}, status code: {response.status_code}')
                    return False
            except requests.Timeout:
                logger.error(f'Timeout error: Could not sync  with peer {remote_peer_id}')
                return False
            except requests.ConnectionError:
                logger.error(f'Connection error: Could not reach peer {remote_peer_id}')
                return False
            except requests.RequestException as e:
                logger.error(f'Unexpected error entangling with peer {remote_peer_id}: {e}\n{traceback.format_exc()}')   
                return False         
        except Exception as e:
            logger.error(f'Failed to accept pair with peer {remote_peer_id}: {e}\n{traceback.format_exc()}')
            return False
        
    # Transactions functions

    def add_transaction(self, transaction: Transaction):
        try:
            logger.info(f'Validating transaction')
            if self.validate_transaction(transaction):
                logger.info(f'Adding transaction {transaction}')
                if len(self.blockchain.pending_transactions) < self.blockchain.transaction_limit:
                    self.blockchain.pending_transactions.append(transaction)
                    logger.info('Transaction added')
                    self.broadcast_transaction(jsonable_encoder(transaction.to_dict()))
                    if len(self.blockchain.pending_transactions) >= self.blockchain.transaction_limit:
                        self.generate_prediction()
                else:
                    logger.warning('Transaction limit reached')
                    self.generate_prediction()
        except Exception as e:
            logger.error(f'Failed to add transaction: {e}\n{traceback.format_exc()}')

    def validate_transaction(self, transaction: Transaction) -> bool:
        try:
            return isinstance(transaction, Transaction)
        except Exception as e:
            logger.error(f'Error validating transaction: {e}\n{traceback.format_exc()}')

    def restart_transactions(self):
        try:
            logger.info('Restarting transactions')
            self.blockchain.pending_transactions = []
            logger.info('Transactions restarted')
        except Exception as e:
            logger.error(f'Error restarting transactions: {e}\n{traceback.format_exc()}')

    def broadcast_transaction(self, transaction):
        try:
            for peer_id, peer_url in self.peers.items():
                if peer_id != self.node_id:
                    logger.info(f'Broadcasting transaction to {peer_id}')
                    try:
                        receive_response = requests.post(
                            f'{peer_url}/receive_transaction',
                            json=transaction,
                            timeout=5
                        )
                        if receive_response.status_code == 200:
                            logger.info(f'Pending Transactions synchronized with {peer_id}')
                        else:
                            logger.warning(f'Failed to sync transaction with peer {peer_id}. Status Code: {receive_response.status_code}')
                    except requests.Timeout:
                        logger.error(f'Timeout error: Could not sync transaction with peer {peer_id}')
                    except requests.ConnectionError:
                        logger.error(f'Connection error: Could not reach peer {peer_id}')
                    except requests.RequestException as e:
                        logger.error(f'Unexpected error broadcating transaction to peer {peer_id}: {e}\n{traceback.format_exc()}')           
        except Exception as e:
            logger.error(f'An error ocurred while broadcating transaction: {e}\n{traceback.format_exc()}')

    def receive_transaction(self, transaction: Transaction):
        try:
            if transaction not in self.blockchain.pending_transactions:
                logger.info(f'Receiving transaction {transaction}')
                self.blockchain.pending_transactions.append(transaction)
                if len(self.blockchain.pending_transactions) >= self.blockchain.transaction_limit:
                    self.generate_prediction()
        except Exception as e:
            logger.error(f'Failed to receive transaction: {e}\n{traceback.format_exc()}')
    
    # Prediction functions

    def generate_prediction(self):
        try:
            if not self.entangled_pair_id:
                logger.info('This node is not entangled with anotherone')
                return

            if self.generate_entanglement_key():
                logger.info('Generating prediction and score')
                block, coherence_block, entangled_hash = self.generate_blocks()
                    
                if block and coherence_block and entangled_hash:
                    self.set_actuals(block, coherence_block, entangled_hash)
                    self.set_prediction()
                    if self.broadcast_prediction(self.consensus_predictions[self.node_id]) == True:
                        if self.set_score(coherence_block.coherence_key) == True:
                            if self.broadcast_score(self.prediction_scores[self.node_id]) == True:
                                min_percentage = len(self.peers) * 0.5
                                if len(self.consensus_predictions) == len(self.prediction_scores) and len(self.prediction_scores) >= min_percentage and len(self.prediction_scores) != 1:
                                    winner_node = self.blockchain.consensus.find_best_prediction_score(self.prediction_scores)
                                    if winner_node == self.node_id:
                                        self.mine_blocks(block, coherence_block, entangled_hash)
                                        logger.info('Blocks mined by current node')
                                    else:
                                        logger.info(f'Blocks mined by node_id: {winner_node}')
                                else:
                                    logger.info('Waiting for new predictions')
                        else:
                            logger.info('Failed to set score, retrying')
                            self.generate_prediction()
                elif block is None or coherence_block is None or entangled_hash is None:
                    logger.warning(f'Blocks not created, retrying')
                    self.generate_prediction()
        except Exception as e:
            logger.error(f'Failed to generate prediction: {e}\n{traceback.format_exc()}')

    def broadcast_prediction(self, prediction):
        try:
            for peer_id, peer_url in self.peers.items():
                if peer_id != self.node_id:
                    logger.info(f'Broadcasting prediction to peer {peer_id}')
                    try:
                        response = requests.post(f'{peer_url}/receive_prediction', json={"node_id": self.node_id, "prediction": prediction})
                        if response.status_code == 200:
                            logger.info(f'Prediction synchronized with {peer_id}')
                            return True
                        else:
                            logger.warning(f'Failed to sync prediction with peer {peer_id}. Status Code: {response.status_code}')
                            return False
                    except requests.Timeout:
                        logger.error(f'Timeout error: Could not sync prediction with peer {peer_id}')
                        return False
                    except requests.ConnectionError:
                        logger.error(f'Connection error: Could not reach peer {peer_id}')
                        return False
                    except requests.RequestException as e:
                        logger.error(f'Unexpected error broadcating prediction to peer {peer_id}: {e}\n{traceback.format_exc()}')
                        return False
        except requests.RequestException:
            logger.error(f'An error occurs trying to connect node {peer_id}')
            return False

    def broadcast_score(self, score):
        try:
            for peer_id, peer_url in self.peers.items():
                if peer_id != self.node_id:
                    logger.info(f'Broadcasting score to peer {peer_id}')
                    try:
                        response = requests.post(f'{peer_url}/receive_score', json={"node_id": self.node_id, "score": score})
                        if response.status_code == 200:
                            logger.info(f'Score synchronized with {peer_id}')
                            return True
                        else:
                            logger.warning(f'Failed to sync score with peer {peer_id}. Status Code: {response.status_code}')
                            return False
                    except requests.Timeout:
                        logger.error(f'Timeout error: Could not sync score with peer {peer_id}')
                        return False
                    except requests.ConnectionError:
                        logger.error(f'Connection error: Could not reach peer {peer_id}')
                        return False
                    except requests.RequestException as e:
                        logger.error(f'Unexpected error broadcating score to peer {peer_id}: {e}\n{traceback.format_exc()}')
                        return False
        except requests.RequestException:
            logger.error(f'An error occurs trying to connect node {peer_id}')
            return False

    def receive_prediction(self, node_id, prediction):
        try:
            if len(self.blockchain.pending_transactions) < self.blockchain.transaction_limit:
                logger.info(f'Pending transactions limit not reached, penalty applied to node {node_id}')
                self.penalized_nodes[node_id] = time.time()
                self.times_that_nodes_were_penalized[node_id] += 1

            if len(self.penalized_nodes) > 0:
                if node_id in self.penalized_nodes:
                    if self.times_that_nodes_were_penalized[node_id] >= self.max_penalties:
                        logger.warning(f'Node {node_id} has been penalized too many times and cannot send predictions.')
                        return False
            
                    penalty_time_left = self.max_penalization_time - (time.time() - self.penalized_nodes[node_id])
                    if penalty_time_left > 0:
                        logger.warning(f'Node {node_id} is penalized, penalty time remaining: {penalty_time_left:.2f} seconds')
                        return False

                    self.penalized_nodes.pop(node_id)
                    logger.info(f'Node {node_id} penalty time has expired')

            logger.info(f'Receiving prediction from node {node_id}')
            self.consensus_predictions[node_id] = prediction
        except Exception as e:
            logger.error(f'Failed to receive prediction: {e}\n{traceback.format_exc()}')

    def receive_score(self, node_id, score):
        try:
            if len(self.blockchain.pending_transactions) < self.blockchain.transaction_limit:
                logger.info(f'Pending transactions limit not reached, penalty applied to node {node_id}')
                self.penalized_nodes[node_id] = time.time()
                self.times_that_nodes_were_penalized[node_id] += 1

            if len(self.penalized_nodes) > 0:
                if node_id in self.penalized_nodes:
                    if self.times_that_nodes_were_penalized[node_id] >= self.max_penalties:
                        logger.warning(f'Node {node_id} has been penalized too many times and cannot send predictions.')
                        return False
            
                    penalty_time_left = self.max_penalization_time - (time.time() - self.penalized_nodes[node_id])
                    if penalty_time_left > 0:
                        logger.warning(f'Node {node_id} is penalized, penalty time remaining: {penalty_time_left:.2f} seconds')
                        return False
            
                    self.penalized_nodes.pop(node_id)
                    logger.info(f'Node {node_id} penalty time has expired')

            logger.info(f'Receiving prediction from node {node_id}')
            self.prediction_scores[node_id] = score
            min_percentage = len(self.peers) * 0.5
            if len(self.consensus_predictions) == len(self.prediction_scores) and len(self.prediction_scores) >= min_percentage and len(self.prediction_scores) != 1:
                if len(self.consensus_predictions) == len(self.prediction_scores):
                    logger.info('Consensus reached, selecting winner node')
                    winner_node = self.blockchain.consensus.find_best_prediction_score(self.prediction_scores)
                    if winner_node == self.node_id:
                        self.mine_blocks(self.actual_block, self.actual_coherence_block, self.actual_entangled_hash)
                        logger.info('Blocks minded by current node')
                        return 
                    self.clear_actuals()
                    logger.info(f'Blocks mined by node_id: {winner_node}')
                    return
                logger.warning('Predictions and scores have different lengths')
            logger.info('Consensus not reached yet, waiting for more predictions')
        except Exception as e:
            logger.error(f'Failed to receive prediction: {e}\n{traceback.format_exc()}')

    def set_prediction(self):
        try:
            logger.info('Setting prediction')
            self.consensus_predictions[self.node_id] = self.blockchain.consensus.generate_node_prediction(self.node_id, self.entangled_pair_id)
            logger.info(f'Prediciton setled for current node')
            return True
        except Exception as e:
            logger.error(f'Failed to set prediction: {e}\n{traceback.format_exc()}')
            return False

    def set_score(self, coherence_key):
        try:
            logger.info('Setting score')
            score = self.blockchain.consensus.prediction_score(self.consensus_predictions[self.node_id], self.consensus_predictions[self.entangled_pair_id], self.key, self.entangled_pair_key, coherence_key)
            if score == None:
                return False
            self.prediction_scores[self.node_id] = score
            logger.info(f'Score setled for current node')
            return True
        except Exception as e:
            logger.error(f'Failed to set score: {e}\n{traceback.format_exc()}')
            return False

    # Blocks functions

    def generate_blocks(self):
        try:
            if not self.entangled_pair_id:
                return None, None, None
            return self.blockchain.create_block(self.to_dict())
        except Exception as e:
            logger.error(f'Failed to generate blocks: {e}\n{traceback.format_exc()}')

    def mine_blocks(self, block, coherence_block, entangled_hash):
        try:
            if self.blockchain.consensus.is_valid_block(block, coherence_block, entangled_hash):
                logger.info('Mining blocks')
                if block not in self.blockchain.chain and coherence_block not in self.blockchain.coherence_chain and not self.blockchain.entangled_blocks.get(entangled_hash, False):
                    self.blockchain.current_chain_index += 1
                    self.blockchain.current_coherence_chain_index +=1
                    self.blockchain.chain.append(block)
                    self.blockchain.coherence_chain.append(coherence_block)
                    self.blockchain.entangled_blocks[entangled_hash] = (block, coherence_block)
                    self.restart_transactions()
                    self.broadcast_blocks(block, coherence_block, entangled_hash)
                    self.clear_actuals()
                    self.restart_transactions()
                    self.validate_blockchain()
                logger.info(f'Blocks Mined: Block: {block}, Coherence Block: {coherence_block}, Entangled Hash: {entangled_hash}')
        except Exception as e:
            logger.error(f'Failed to mine blocks: {e}\n{traceback.format_exc()}')

    def broadcast_blocks(self, block, coherence_block, entangled_hash):
        try:
            for peer_id, peer_url in self.peers.items():
                if peer_id != self.node_id:
                    try:
                        logger.info(f'Broadcasting blocks to peer {peer_id}')
                        response = requests.get(f'{peer_url}/blockchain')
                        if response.status_code == 200:
                            remote_blockchain = response.json()
                        else:
                            logger.warning(f'Failed to get blockchain from peer {peer_id}. Statis Code: {response.status_code}')

                        if 'chain' not in remote_blockchain or 'coherence_chain' not in remote_blockchain:
                            logger.error(f'Invalid blockchain data got from peer {peer_id}')

                        if block not in remote_blockchain['chain'] or coherence_block not in remote_blockchain['coherence_chain']:
                            logger.info(f'Synchronizing blocks with peer {peer_id}')
                            receive_response = requests.post(f'{peer_url}/receive_blocks', json={'block': jsonable_encoder(block.to_dict()), 'coherence_block': jsonable_encoder(coherence_block.to_dict()), 'entangled_hash': jsonable_encoder(entangled_hash), 'node_id': jsonable_encoder(self.node_id)})
                            if receive_response.status_code == 200:
                                logger.info(f'Block and Coherence Block synchronized with {peer_id}')
                            else:
                                logger.warning(f'Failed to sync blocks with peer {peer_id}. Status Code: {receive_response.status_code}')
                    except requests.Timeout:
                        logger.error(f'Timeout error: Could not sync blocks with peer {peer_id}')
                    except requests.ConnectionError:
                        logger.error(f'Connection error: Could not reach peer {peer_id}')
                    except requests.RequestException as e:
                        logger.error(f'Unexpected error broadcasting block to peer {peer_id}: {e}\n{traceback.format_exc()}') 
        except Exception as e:
            logger.error(f'An error ocurred while broadcasting blocks: {e}\n{traceback.format_exc()}')
    
    def receive_blocks(self, block, coherence_block, entangled_hash, node_id):
        try:
            messages = []

            if len(self.consensus_predictions) < (len(self.peers) * 0.5) and len(self.prediction_scores) < (len(self.peers) * 0.5):
                messages.append(f'Denied blocks, consensus not reached, Penality applied to node {node_id}')
                self.penalized_nodes[node_id] = time.time()
                self.times_that_nodes_were_penalized[node_id] += 1
                
            block_transactions = []
                
            transactions = block.get('transactions')
            for transaction in transactions:
                block_transactions.append(Transaction(**transaction))
                
                block['transactions'] = block_transactions

                processed_block = Block(**block)
                processed_coherence_block = CoherenceBlock(**coherence_block)

                if processed_block not in self.blockchain.chain and processed_coherence_block not in self.blockchain.coherence_chain and not self.blockchain.entangled_blocks.get(entangled_hash, False):
                    if self.blockchain.consensus.is_valid_block(processed_block, processed_coherence_block, entangled_hash):
                        previous_block = self.blockchain.chain[-1] if self.blockchain.chain else None
                        if previous_block and processed_block.previous_hash != previous_block.hash:
                            logger.warning('Rejected block due to inccorect previous hash')
                            return
                
                        previous_coherence_block = self.blockchain.coherence_chain[-1] if self.blockchain.coherence_chain else None
                        if previous_coherence_block and processed_coherence_block.previous_hash != previous_coherence_block.hash:
                            logger.warning('Rejected coherence block due to incorrect previous hash')
                            return
                        
                        self.blockchain.current_chain_index += 1
                        self.blockchain.chain.append(processed_block)
                        self.clear_actuals()
                        self.restart_transactions()
                        messages.append('New Block synchronized ')
                        self.blockchain.current_coherence_chain_index +=1
                        self.blockchain.coherence_chain.append(processed_coherence_block)
                        messages.append('New Coherence Block synchronized ')
                        self.blockchain.entangled_blocks[entangled_hash] = (processed_block, processed_coherence_block)
                        messages.append('New Entangled Hash synchronized ')
                        self.validate_blockchain()
                    else:
                        logger.error('Invalid Blocks or Hash')
                        return
                else:
                    messages.append('All blocks and hashes already up to date ')
                    return
                logger.info(''.join(messages))
                return 
        except Exception as e:
            logger.error(f'Failed to receive blocks: {e}\n{traceback.format_exc()}')

    def get_block(self, hash):
        try:
            logger.info('Getting block')
            for block in self.blockchain.chain:
                if block.hash == hash:
                    logger.info('Block found')
                    return block
                logger.warning('Block not found')
                return None
        except Exception as e:
            logger.error(f'Failed to get block: {e}\n{traceback.format_exc()}')
            
    def get_coherence_block(self, hash):
        try:
            logger.info('Getting block')
            for coherence_block in self.blockchain.coherence_chain:
                if coherence_block.hash == hash:
                    logger.info('Coherence Block found')
                    return coherence_block
                logger.warning('Coherence Block not found')
                return None
        except Exception as e:
            logger.error(f'Failed to get block: {e}\n{traceback.format_exc()}')

    # Actuals functions

    def clear_actuals(self):
        try:
            logger.info('Clearing actuals')
            self.actual_block = None
            self.actual_coherence_block = None
            self.actual_entangled_hash = None
            self.consensus_predictions = {}
            self.prediction_scores = {}
        except Exception as e:
            logger.error(f'Failed to clear actuals: {e}\n{traceback.format_exc()}')    

    def set_actuals(self, block, coherence_block, entangled_hash):
        try:
            logger.info('Setting actuals')
            self.actual_block = block
            self.actual_coherence_block = coherence_block
            self.actual_entangled_hash = entangled_hash
        except Exception as e:
            logger.error(f'Failed to set actuals: {e}\n{traceback.format_exc()}')

    # Blockchain functions

    def validate_blockchain(self):
        try:
            logger.info('Validating blockchain')   
            return self.blockchain.consensus.validate_blockchain(self.blockchain)
        except Exception as e:
            logger.error(f'Failed to validate blockchain: {e}\n{traceback.format_exc()}')

    def sync_blockchain(self):
        try:
            longest_chain = self.blockchain.chain
            longest_coherence_chain = self.blockchain.coherence_chain
            source_peer = None
            peers_blockchain = {}

            for peer_id, peer_url in self.peers.items():
                try:
                    
                    logger.info(f'Getting blockchain from peer {peer_id}')
                    response = requests.get(
                        f'{peer_url}/blockchain',
                        timeout=5
                    )
                    response.raise_for_status()
                    response_data = response.json()
                    peers_blockchain[peer_id] = response_data
                except requests.Timeout:
                    logger.error(f'Timeout error: Could not get blockchain from peer {peer_id}')
                except requests.ConnectionError:
                    logger.error(f'Connection error: Could not reach peer {peer_id}')
                except requests.RequestException as e:
                    logger.error(f'Unexpected error: Failed to get blockchain from peer {peer_id}: {e}\n{traceback.format_exc()} ') 

                logger.info(f'Blcokchain got from peer {peer_id}')            
            
            for peer_id, peer_blockchain in peers_blockchain.items():
                if len(peer_blockchain.chain) > len(longest_chain) and (peer_blockchain.coherence_chain) > len(longest_coherence_chain):
                    logger.info(f'Peer {peer_id} has a longer chain, comparing with other peers')
                    nodes_validating_blockchain = 0
                    for peer_validating_id, peer_validating_blockchain in peers_blockchain.items():
                        logger.info(f'Validating blockchain with peer {peer_validating_id} blockchain')
                        if peer_blockchain.chain == peer_validating_blockchain.chain and peer_blockchain.coherence_chain == peer_validating_blockchain.coherence_chain:
                            nodes_validating_blockchain += 1
                    if nodes_validating_blockchain >= len(self.peers) * 0.5:
                        logger.info(f'Peer {peer_id} has the longest chain and coherence chain')
                        longest_chain = peer_blockchain.chain
                        longest_coherence_chain = peer_blockchain.coherence_chain
                        source_peer = peer_id
                    else:
                        logger.warning(f'Peer {peer_id} chain and coherence chain are not valid, penalty applied')
                        self.penalized_nodes[peer_id] = time.time()
                        self.times_that_nodes_were_penalized[peer_id] += 1
                        return

            updated = False
            messages = []

            if longest_chain != self.blockchain.chain and longest_coherence_chain != self.blockchain.coherence_chain:
                self.blockchain.chain = longest_chain
                self.blockchain.coherence_chain = longest_coherence_chain
                messages.append(f'Your chain and coherence chain was updated from peer {source_peer}')
                updated = True

            if not updated:
                logger.info('Your chain and coherence chain are up to date')
                return
        
            logger.info(''.join(messages))
            return 
        except Exception as e:
            logger.error(f'Failed to sync blockchain:{e}\n{traceback.format_exc()}')

    def get_blockchain(self):
        try:
            return self.blockchain.to_dict()
        except Exception as e:
            logger.error(f'Failed to get blockchain: {e}\n{traceback.format_exc()}')

    # Wallet functions

    def create_wallet(self) -> Wallet:
        try:
            logger.info('Creating wallet')
            return self.blockchain.create_wallet()
        except Exception as e:
            logger.error(f'Failed to create wallet: {e}\n{traceback.format_exc()}')

    def get_balance(self, address):
        try:
            logger.info('Getting balance')
            return self.blockchain.get_balance(address)
        except Exception as e:
            logger.error(f'Failed to get balance: {e}\n{traceback.format_exc()}')

    def recover_wallet_from_recovery_key(self, recovery_key: str, passphrase: str) -> Wallet:
        try:
            logger.info('Recovering wallet')
            return self.blockchain.recover_wallet_from_recovery_key(recovery_key, passphrase)
        except Exception as e:
            logger.error(f'Failed to recover wallet: {e}\n{traceback.format_exc()}')

    def recover_wallet_from_mnemonic(self, mnemonic: str, passphrase: str):
        try:
            logger.info('Recovering wallet')
            return self.blockchain.recover_wallet_from_mnemonic(mnemonic, passphrase)
        except Exception as e:
            logger.error(f'Failed to recover wallet: {e}\n{traceback.format_exc()}')


    def to_dict(self):
            try:
                return {
                    "node_id": self.node_id,
                    "ip": self.ip,
                    "port": self.port,
                    "url": self.url,
                    'blockchain': self.blockchain.to_dict(),
                    "entangled_pair_id": self.entangled_pair_id if self.entangled_pair_id else None,
                    "key": self.key if self.key else None,
                    "entangled_pair_key": self.entangled_pair_key if self.entangled_pair_key else None,
                    "peers": self.peers,
                    "consensus_predictions": self.consensus_predictions if self.consensus_predictions else None,
                    "prediction_scores": self.prediction_scores if self.prediction_scores else None,
                    "actual_block": self.actual_block if self.actual_block else None,
                    "actual_coherence_block": self.actual_coherence_block if self.actual_coherence_block else None,
                    "actual_entangled_hash": self.actual_entangled_hash if self.actual_entangled_hash else None,
                    "penalized_nodes": self.penalized_nodes if self.penalized_nodes else None,
                    "times_that_nodes_were_penalized": self.times_that_nodes_were_penalized if self.times_that_nodes_were_penalized else None,
                    "max_penalization_time": self.max_penalization_time,
                    "max_penalties": self.max_penalties
                }
            except Exception as e:
                logger.error(f'Failed to convert node to dict: {e}\n{traceback.format_exc()}')