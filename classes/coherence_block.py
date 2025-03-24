import time
import hashlib
from pydantic import BaseModel, Field
from typing import Optional
import logging
import random
import traceback

logging.basicConfig(
    level= logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('node_logs.log')
    ]
)

logger = logging.getLogger(__name__)

class CoherenceBlock(BaseModel):
    index: int
    previous_hash: str
    node_id: str
    entangled_node_id: str
    node_key: int
    entangled_node_key: int
    block_hash: str
    coherence_key: Optional[int] = None
    entangled_hash: Optional[str] = None
    timestamp: Optional[float] = None
    hash: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.coherence_key is None:
            self.coherence_key = self.generate_coherence_key()
        if self.hash is None:
            self.hash = self.calculate_hash()
        if self.timestamp is None:
            self.timestamp = time.time()

    def generate_coherence_key(self) -> int:
        try:
            logger.info('Generating coherence key')
            raw_key = hashlib.sha256(str(self.node_key).encode('utf-8') + str(self.entangled_node_key).encode('utf-8') + str(random.randint(1000, 9999)).encode('utf-8')).hexdigest()
            coherence_key = int(raw_key, 16) % 100000
            logger.info('Coherence key generated')
            return coherence_key
        except Exception as e:
            logger.error(f'Error generating coherence key: {e}\n{traceback.format_exc()}')

    def calculate_hash(self) -> str:
        try:
            logger.info('Calculating coherence block hash')
            hash = 'Φx' + hashlib.sha256(
                str(self.index).encode('utf-8') +
                str(self.previous_hash).encode('utf-8') +
                str(self.node_id).encode('utf-8') + 
                str(self.entangled_node_id).encode('utf-8') +
                str(self.node_key).encode('utf-8') +
                str(self.entangled_node_key).encode('utf-8') +
                str(self.block_hash).encode('utf-8') +
                str(self.coherence_key).encode('utf-8') +
                str(self.timestamp).encode('utf-8')
            ).hexdigest()
            logger.info('Coherence block hash calculated')
            return hash
        except Exception as e:
            logger.error(f'Error calculating coherence block hash: {e}\n{traceback.format_exc()}')

    def to_dict(self) -> dict:
        try:
            logger.info('Converting coherence block to dictionary')
            to_dict = {
                'index': self.index,
                'previous_hash': self.previous_hash,
                'node_id': self.node_id,
                'entangled_node_id': self.entangled_node_id,
                'node_key': self.node_key,
                'entangled_node_key': self.entangled_node_key,
                'block_hash': self.block_hash,
                'coherence_key': self.coherence_key,
                'entangled_hash': self.entangled_hash,
                'timestamp': self.timestamp,
                'hash': self.hash
            }
            logger.info('Coherence block converted to dictionary')
            return to_dict
        except Exception as e:
            logger.error(f'Error converting coherence block to dictionary: {e}\n{traceback.format_exc()}')
