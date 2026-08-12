from fastapi import APIRouter, Depends
from supabase import Client

from app.core.supabase import get_supabase_client
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


def get_chat_service(client: Client = Depends(get_supabase_client)) -> ChatService:
    return ChatService(client)


@router.post("", response_model=ChatResponse)
def ask_portfolio_assistant(
    body: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    return service.ask(body)
