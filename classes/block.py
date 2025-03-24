import time
import hashlib
from pydantic import BaseModel, Field
from typing import Optional
import logging
import traceback

from classes.transaction import Transaction

logging.basicConfig(
    level= logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('node_logs.log')
    ]
)

logger = logging.getLogger(__name__)

class Block(BaseModel):
    index: int
    previous_hash: str
    coherence_block_hash: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)
    transactions: list[Transaction]
    hash: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.hash is None:
            self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        try:
            logger.info(f'Calculating hash')
            return 'Φx' + hashlib.sha256(
                str(self.index).encode("utf-8") +
                str(self.previous_hash).encode("utf-8") +
                str(self.timestamp).encode("utf-8") +
                str(self.transactions).encode("utf-8")
            ).hexdigest()
        except Exception as e:
            logger.error(f'Error calculating hash: {e}\n{traceback.format_exc}')

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "coherence_block_hash": self.coherence_block_hash,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "hash": self.hash,
        }
