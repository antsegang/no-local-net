import time
import hashlib
import json
import traceback
from pydantic import BaseModel, Field
from typing import Optional, Tuple
from coincurve import PublicKey
from classes.wallet import Wallet

from classes.wallet import Wallet

class Transaction(BaseModel):
    sender: str
    receiver: str
    amount: float
    contract_code: Optional[str] = None
    timestamp: Optional[float] = None
    nonce: int
    r: Optional[str] = None
    s: Optional[str] = None
    v: Optional[int] = None
    public_key: Optional[str] = None
    hash: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.hash is None:
            self.hash = self.calculate_hash()

    def calculate_hash(self):
        qtx_data = {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "contract_code": self.contract_code,
            "timestamp": self.timestamp,
            "nonce": self.nonce
        }
        return 'Φx' + hashlib.sha256((json.dumps(qtx_data, sort_keys=True)).encode()).hexdigest()

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "contract_code": self.contract_code,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "r": self.r,
            "s": self.s,
            "v": self.v,
            "public_key": self.public_key,
            "hash": self.hash
        }