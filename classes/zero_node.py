import hashlib
import random
from pydantic import BaseModel, Field
from typing import Optional

class ZeroNode(BaseModel):
    node_id: Optional[str] = '0'
    entangled_pair_id: Optional[str] = '0'  # Usamos Forward Declaration para evitar problemas de referencia circular
    key: Optional[str] = None
    entangled_pair_key: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.key is None:
            self.key = self.generate_entanglement_key()
        
        if self.entangled_pair_key is None:
            self.entangled_pair_key = self.generate_entanglement_key()

    def generate_entanglement_key(self):
        raw_key =  hashlib.sha256(str(self.node_id).encode('utf-8') + str(self.entangled_pair_id).encode('utf-8') + str(random.randint(1000, 9999)).encode('utf-8')).hexdigest()
        self.key = int(raw_key, 16) % 100000
        return self.key
    
    def get_entangled_key(self) -> Optional[str]:
        return self.generate_entanglement_key() if self.entangled_pair_id else None
    
    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "entangled_pair_id": self.entangled_pair_id if self.entangled_pair_id else None,
            "key": self.key,
            "entangled_pair_key": self.entangled_pair_key if self.entangled_pair_key else None,
        }

    class Config:
        # Asegura que se permite el uso de las referencias de tipo adelante
        arbitrary_types_allowed = True

# Para la instancia de blockchain puedes pasarla como un atributo adicional si es necesario.
