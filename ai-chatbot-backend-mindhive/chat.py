from fastapi import APIRouter
from orchestrator import Orchestrator

router = APIRouter(tags=["Chat"])
orch = Orchestrator()

@router.post("/chat")
def chat(payload: dict):
    user_msg = payload["question"]
    return orch.handle(user_msg)
