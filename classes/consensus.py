import hashlib
from pydantic import BaseModel
import logging
import traceback
import random

logging.basicConfig(
    level= logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('node_logs.log')
    ]
)

logger = logging.getLogger(__name__)

class EntanglementConsensus(BaseModel):
    def generate_node_prediction(self, node_key: str, entangled_node_key: str) -> int:
        try:
            logger.info(f'Generating node prediction for Node Key: {node_key} and Entangled Node Key: {entangled_node_key}')
            raw_key = hashlib.sha256(
                str(node_key).encode('utf-8') + 
                str(entangled_node_key).encode('utf-8') + 
                str(random.randint(1000, 9999)).encode('utf-8')
            ).hexdigest()
            node_prediction = int(raw_key, 16) % 100000
            logger.info(f'Node prediction generated: {node_prediction}')
            return node_prediction
        except Exception as e:
            logger.error(f'Error generating node prediction: {e}\n{traceback.format_exc()}')
    
    def hash_predictions_and_keys(self, node_prediction: int, pair_prediction: int, node_key: str, pair_key: str) -> int:
        try:
            logger.info(f'Hashing predictions and keys')
            raw_key = hashlib.sha256(
                str(node_prediction).encode('utf-8') + 
                str(node_key).encode('utf-8') + 
                str(pair_key).encode('utf-8')
            ).hexdigest()
            hashed_predictions_and_keys = int(raw_key, 16) % 100000
            logger.info(f'Predictions and keys hashed')
            return hashed_predictions_and_keys
        except Exception as e:
            logger.error(f'Error hashing predictions and keys: {e}\n{traceback.format_exc()}')
    
    def hash_key(self, key: str, node_key: str, pair_key: str) -> int:
        try:
            logger.info(f'Hashing key')
            raw_key = hashlib.sha256(
                str(key).encode('utf-8') +
                str(node_key).encode('utf-8') + 
                str(pair_key).encode('utf-8')
            ).hexdigest()
            hashed_key = int(raw_key, 16) % 100000
            logger.info(f'Key hashed')
            return hashed_key
        except Exception as e:
            logger.error(f'Error hashing key: {e}\n{traceback.format_exc()}')

    def validate_score(self, prediction: int, hashed_key: int) -> bool:
        try:
            logger.info(f'Validating score')
            if prediction == hashed_key or (prediction >= hashed_key * 0.5 and prediction <= hashed_key * 1.5):
                logger.info(f'Score validated')
                return True
            logger.info(f'Score not validated')
            return False
        except Exception as e:
            logger.error(f'Error validating score: {e}\n{traceback.format_exc()}')

    def prediction_score(self, node_prediction: int, pair_prediction: int, node_key: str, pair_key: str, coherence_key: int) -> float:
        try:
            logger.info(f'Calculating prediction score')
            prediction = self.hash_predictions_and_keys(node_prediction, pair_prediction, node_key, pair_key)
            hashed_key = self.hash_key(coherence_key, node_key, pair_key)
            if self.validate_score(prediction, hashed_key) == True:
                prediction_score = prediction - hashed_key
                logger.info(f'Prediction score calculated')
                return prediction_score
            else:
                logger.info(f'Prediction score not calculated')
                return None
        except Exception as e:
            logger.error(f'Error calculating prediction score: {e}\n{traceback.format_exc()}')

    def validate_entanglement(self, node_prediction: int, entangled_node_prediction: int, coherence_key: int) -> bool:
        try:
            logger.info(f'Validating entanglement')
            total_prediction = abs(node_prediction + entangled_node_prediction)
            validation = (total_prediction == coherence_key or (total_prediction <= coherence_key + (coherence_key * 0.1) and total_prediction >= coherence_key * 0.9))
            if validation == True:
                logger.info(f'Entanglement validated')
                return True
            logger.info(f'Entanglement not validated')
            return False
        except Exception as e:
            logger.error(f'Error validating entanglement: {e}\n{traceback.format_exc()}')
    
    def entangle_blocks(self, block, coherence_block) -> str:
        try:
            logger.info(f'Entangling blokcs')
            entangled_hash = hashlib.sha256(
                str(block.hash).encode('utf-8') + 
                str(coherence_block.hash).encode('utf-8') + 
                str(coherence_block.node_key).encode('utf-8') + 
                str(coherence_block.entangled_node_key).encode('utf-8')
            ).hexdigest()
            logger.info(f'Blocks entangled')
            return entangled_hash
        except Exception as e:
            logger.error(f'Error entangling blocks: {e}\n{traceback.format_exc()}')
    
    def is_valid_block(self, block, coherence_block, entangled_hash: str) -> bool:
        try:
            logger.info(f'Validating blocks')
            validation = entangled_hash == hashlib.sha256(
                str(block.hash).encode('utf-8') + 
                str(coherence_block.hash).encode('utf-8') + 
                str(coherence_block.node_key).encode('utf-8') + 
                str(coherence_block.entangled_node_key).encode('utf-8')
            ).hexdigest()
            if validation == True:
                logger.info(f'Blocks validated')
                return True
            logger.info(f'Blocks not validated')
            return False
        except Exception as e:
            logger.error(f'Error validating blocks: {e}\n{traceback.format_exc()}')
    
    def find_best_prediction_score(self, prediction_scores: dict) -> str:
        try:
            logger.info(f'Finding best prediction score')
            best_score = float('inf')
            winner_node = None

            for node_id, prediction_score in prediction_scores.items():
                logger.info(f'Node ID: {node_id}, Prediction Score: {prediction_score}')
                if prediction_score < best_score:
                    logger.info(f'New best score found: {prediction_score}')
                    best_score = prediction_score
                    winner_node = node_id
            logger.info(f'Best prediction score found: {best_score} for Node ID: {winner_node}')
            return winner_node
        except Exception as e:
            logger.error(f'Error finding best prediction score: {e}\n{traceback.format_exc()}')

    def validate_blockchain(self, blockchain) -> bool:
        try:
            logger.info(f'Validating blockchain')
            if len(blockchain.chain) != len(blockchain.coherence_chain):
                logger.info(f'Coherence chain length does not match chain length')
                return False

            logger.info(f'Validating chain')
            for block in blockchain.chain:
                logger.info(f'Validating block: {block}')
                if block.index == 0 and block.previous_hash != '0':
                    logger.info(f'First block previous hash is not 0')
                    return False
                elif block.index > 0 and block.previous_hash != blockchain.chain[block.index - 1].hash:
                    logger.info(f'Block previous hash does not match previous block hash')
                    return False

            logger.info(f'Validating coherence chain')
            for coherence_block in blockchain.coherence_chain:
                logger.info(f'Validating coherence block: {coherence_block}')
                if coherence_block.index == 0 and coherence_block.previous_hash != '0':
                    logger.info(f'First coherence block previous hash is not 0')
                    return False
                elif coherence_block.index > 0 and coherence_block.previous_hash != blockchain.coherence_chain[coherence_block.index - 1].hash:
                    logger.info(f'Coherence block previous hash does not match previous coherence block hash')
                    return False
            
                if coherence_block.index != blockchain.chain[coherence_block.index].index:
                    logger.info(f'Coherence block index does not match chain index')
                    return False
                
                if blockchain.chain[coherence_block.index].coherence_block_hash != coherence_block.hash:
                    logger.info(f'Block coherence block hash does not match coherence block hash, correcting')
                    blockchain.chain[coherence_block.index].coherence_block_hash = coherence_block.hash

                if blockchain.chain[coherence_block.index].hash != coherence_block.block_hash:
                    logger.info(f'Block hash does not match coherence block block hash')
                    return False

                if coherence_block.entangled_hash not in blockchain.entangled_blocks or blockchain.entangled_blocks[coherence_block.entangled_hash] != (blockchain.chain[coherence_block.index], coherence_block):
                    logger.info(f'Entangled hash not found in entangled blocks')
                    return False

                if not self.is_valid_block(blockchain.chain[coherence_block.index], coherence_block, coherence_block.entangled_hash):
                    return False
            
            logger.info(f'Blockchain validated')
            return True
        except Exception as e:
            logger.error(f'Error validating blockchain: {e}\n{traceback.format_exc()}')



        
            