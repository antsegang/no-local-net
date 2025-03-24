from fastapi import APIRouter, HTTPException, Body
from fastapi.encoders import jsonable_encoder
from typing import Dict

from config.node_generation import run_node

from classes.transaction import Transaction

from schemas.pair_request import PairRequest
from schemas.pair_key import PairKey
from schemas.prediction import Prediction
from schemas.score import Score

node_router = APIRouter()
node = None

# Node routes

@node_router.post("/run_node")
def start_node(ip: str = '127.0.0.1', port: int = 5000, url: str = None):
    global node
    if node is None:
        node = run_node(ip, port, url)
        return {'message': 'Node running', 'Node': node}
    return {'message': 'Node is already running'}

@node_router.get("/node_info")
def get_node_info():
    global node
    if node is None:
        raise HTTPException(status_code=400, detail="El nodo no está inicializado.")
    return jsonable_encoder(node.to_dict())

# Pair routes

@node_router.get("/find_pair")
def find_pair():
    global node
    if node is None:
        raise HTTPException(status_code=400, detail="El nodo no está inicializado.")
    return node.find_pair()

@node_router.post("/entanglement_request")
def entanglement_request(pair_request: PairRequest):
    global node
    if node is None:
        raise HTTPException(status_code=400, detail="El nodo no está inicializado.")
    return node.entanglement_request(pair_request.remote_peer_id)

@node_router.post("/receive_pair_key")
def receive_key(key: PairKey):
    global node
    if node is None:
        raise HTTPException(status_code=400, detail="El nodo no está inicicializado.")
    return node.receive_key(key.key)

# Blockchain routes

@node_router.get("/blockchain")
def get_blockchain():
    global node
    if node is None:
        raise HTTPException(status_code=400, detail="El nodo no está inicializado. Llama primero a /run_node")
    return jsonable_encoder(node.blockchain.to_dict())

@node_router.get("/validate_blockchain")
def validate_blockchain():
    global node
    if node is None:
        raise HTTPException(status_code=400, detail="El nodo no esta inicializado.")
    return jsonable_encoder(node.validate_blockchain())

# Peers routes

@node_router.get("/peers")
def get_peers():
    global node
    if node is None:
        raise HTTPException(status_code=400, detail="El nodo no está inicializado.")
    return jsonable_encoder(node.peers)

@node_router.post("/receive_peers")
def receive_peers(peers: dict):
    global node
    if node is None:
        raise HTTPException(status_code=400, detail="El nodo no está inicializado.")
    
    node.receive_peers(peers)
    return {"message": "Peers received", "updated_peers": jsonable_encoder(node.peers)}

# Transaction routes

@node_router.post("/add_transaction")
def add_transaction(transaction: dict):
    global node
    if node is None:
        raise HTTPException(status_code=400, detail="El nodo no está inicializado.")
    
    return node.add_transaction(Transaction(**transaction))

@node_router.get("/transactions")
def get_transactions():
    global node
    if node is None:
        raise HTTPException(status_code=400, detail="El nodo no está inicializado.")
    return jsonable_encoder(node.blockchain.pending_transactions)

@node_router.post("/receive_transaction")
def receive_transaction(transaction: dict):
    global node
    if node is None:
        raise HTTPException(status_code=400, detail="El nodo no está inicializado.")
    node.receive_transaction(Transaction(**transaction))

# Prediction routes

@node_router.post("/receive_prediction")
def receive_prediction(prediction: Prediction):
    global node
    if node is None:
        raise HTTPException(status_code=400, detail="El nodo no está inicializado.")
    node.receive_prediction(prediction.node_id, prediction.prediction)

@node_router.post("/receive_score")
def receive_score(score: Score):
    global node
    if node is None:
        raise HTTPException(status_code=400, detail="El nodo no está inicializado.")
    node.receive_score(score.node_id, score.score)

@node_router.get("/predictions")
def get_predictions():
    global node
    if node is None:
        raise HTTPException(status_code=400, detail="El nodo no está inicializado.")
    return jsonable_encoder(node.consensus_predictions)

@node_router.get("/scores")
def get_scores():
    global node
    if node is None:
        raise HTTPException(status_code=400, detail="El nodo no está inicializado.")
    return jsonable_encoder(node.prediction_scores)

# Blocks routes

@node_router.post("/receive_blocks")
def receive_blocks(blocks: dict):
    global node
    if node is None:
        raise HTTPException(status_code=400, detail="El nodo no está inicializado.")
    node.receive_blocks(blocks.get('block'), blocks.get('coherence_block'), blocks.get('entangled_hash'), blocks.get('node_id'))

@node_router.get("/block/{hash}")
def get_blocks(hash: str):
    global node
    if node is None:
        raise HTTPException(status_code=400, detail="El nodo no está inicializado.")
    return jsonable_encoder(node.get_block(hash))

@node_router.get("/coherence_block/{hash}")
def get_blocks(hash: str):
    global node
    if node is None:
        raise HTTPException(status_code=400, detail="El nodo no está inicializado.")
    return jsonable_encoder(node.get_coherence_block(hash))