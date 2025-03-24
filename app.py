from fastapi import FastAPI, HTTPException
from routes.node_routes import node_router

app = FastAPI()

app.include_router(node_router)
